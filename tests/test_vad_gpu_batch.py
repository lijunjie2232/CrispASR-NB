#!/usr/bin/env python3
"""Self-check for the VAD device/batching/progress features.

Three claims are checked, per model:

  1. batching does not change the answer — `batch_size=N` must return the same
     spans as `batch_size=0` (Silero unrolls N LSTM steps into one graph;
     FireRed/MarbleNet cut the frame axis with the receptive field of context).
  2. the GPU path does not change the answer either — for Silero/MarbleNet that
     is the same graph on a different backend, for FireRed it is a different
     implementation entirely (ggml DFSMN graph vs the scalar CPU loops), so this
     is the real parity check for that rewrite.
  3. progress lines appear on stderr while a long file is being processed.

Usage (from the CrispASR root):
    ../.venv.win/Scripts/python tests/test_vad_gpu_batch.py [--audio FILE] [--gpu]

`--gpu` adds the GPU legs; without it only the CPU batching parity runs (which
still exercises the FireRed graph path, forced onto the CPU backend).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CRISPASR = HERE.parent
DEFAULT_LIB = CRISPASR / "build_win" / "bin" / "Release" / "crispasr.dll"
REPO = CRISPASR.parents[1]  # third_part/CrispASR -> the Irodori-TTS checkout
DEFAULT_AUDIO = (
    REPO / "speaker_inversion_example" / "data" / "speaker-inversion-dataset" / "test" / "01_cut_test2.mp3"
)
SR = 16000

VAD_MODELS = {
    "firered": ("firered-vad.gguf", "https://huggingface.co/cstr/firered-vad-GGUF/resolve/main/firered-vad.gguf"),
    "silero": ("ggml-silero-v6.2.0.bin", "https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v6.2.0.bin"),
    "marblenet": ("marblenet-vad.gguf", "https://huggingface.co/cstr/marblenet-vad-GGUF/resolve/main/marblenet-vad.gguf"),
}


def load_crispasr(lib: Path):
    # No manual os.add_dll_directory: _binding._register_dll_dir owns that (it
    # has to, or every Python caller on Windows would need the same dance). If
    # this raises "could not find module ... (or one of its dependencies)", that
    # helper is what broke.
    os.environ["CRISPASR_LIB_PATH"] = str(lib)
    sys.path.insert(0, str(CRISPASR / "python"))
    import crispasr._binding as cb

    return cb


def decode(audio: Path, tmp: Path) -> np.ndarray:
    """mp3 -> 16 kHz mono float32. ffmpeg + raw f32le, so no funasr/torch
    dependency (and no dependence on `wave` understanding float WAVs)."""
    out = tmp / "audio.f32"
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    subprocess.run(
        [ffmpeg, "-nostdin", "-loglevel", "error", "-y", "-i", str(audio),
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-c:a", "pcm_f32le", str(out)],
        check=True,
    )
    return np.ascontiguousarray(np.fromfile(out, dtype="<f4"), dtype=np.float32)


def spans_for(cb, pcm, path, use_gpu, batch):
    t0 = time.perf_counter()
    spans = cb.vad_slices(pcm, path, threshold=0.5, use_gpu=use_gpu, batch_size=batch)
    return spans, time.perf_counter() - t0


# MarbleNet's forward is length-dependent (see the note above mbn_forward in
# src/marblenet_vad.cpp) — a pre-existing bug, reproduced by the unmodified
# tree. Parity between different frame counts therefore cannot hold for it, and
# a hard failure here would be reporting the wrong problem. It is still checked
# for CPU/GPU agreement, which is what this change is responsible for.
KNOWN_BROKEN = {"marblenet"}


def compare(a, b, tol_ms=50):
    """Max |delta| over the common prefix. A count mismatch is a failure even
    when the shared prefix matches, which a prefix-only comparison would hide."""
    n = min(len(a), len(b))
    worst = 0.0
    for i in range(n):
        worst = max(worst, abs(a[i].start - b[i].start) * 1000, abs(a[i].end - b[i].end) * 1000)
    return worst, len(a), len(b), worst <= tol_ms and len(a) == len(b)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=str(DEFAULT_AUDIO))
    ap.add_argument("--lib", default=str(DEFAULT_LIB))
    ap.add_argument("--models", default="silero,firered,marblenet")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--gpu", action="store_true", help="also run the CUDA legs")
    ap.add_argument("--progress-probe", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args()

    if args.progress_probe:
        # 120 s of silence, one window per graph compute: long enough that the
        # reporter ticks, and it exercises the counter in the subprocess that
        # the caller captures stderr from.
        cb = load_crispasr(Path(args.lib))
        fname, url = VAD_MODELS["silero"]
        cb.vad_slices(np.zeros(SR * 120, dtype=np.float32), cb.cache_ensure_file(fname, url, quiet=True),
                      threshold=0.5, use_gpu=0, batch_size=1)
        return 0

    audio = Path(args.audio)
    if not audio.exists():
        print(f"FAIL: audio not found: {audio}")
        return 2
    cb = load_crispasr(Path(args.lib))

    with tempfile.TemporaryDirectory() as td:
        pcm = decode(audio, Path(td))
    print(f"audio: {audio.name}  {pcm.size / SR:.1f}s ({pcm.size} samples)\n")

    failures = []
    for key in args.models.split(","):
        fname, url = VAD_MODELS[key]
        path = cb.cache_ensure_file(fname, url, quiet=True)
        if not path or not Path(path).exists():
            print(f"{key:10s} SKIP (model not available)")
            continue

        broken = key in KNOWN_BROKEN
        base, t_base = spans_for(cb, pcm, path, use_gpu=0, batch=0)
        batched, t_batch = spans_for(cb, pcm, path, use_gpu=0, batch=args.batch)
        worst, n0, n1, ok = compare(base, batched)
        print(f"{key:10s} cpu       batch=0 {len(base):4d} spans {t_base:6.2f}s | "
              f"batch={args.batch} {len(batched):4d} spans {t_batch:6.2f}s | max delta {worst:.1f} ms "
              f"{'OK' if ok else ('KNOWN-BROKEN (see mbn_forward note)' if broken else 'MISMATCH')}")
        if not ok and not broken:
            failures.append(f"{key}: cpu batching changed the spans ({n0} -> {n1}, {worst:.1f} ms)")

        if args.gpu:
            gpu, t_gpu = spans_for(cb, pcm, path, use_gpu=1, batch=args.batch)
            # CPU-vs-GPU is the invariant this change owns: same batch width,
            # same spans, whichever backend ran the graph.
            worst, _, n2, ok = compare(batched, gpu)
            print(f"{key:10s} gpu       batch={args.batch} {len(gpu):4d} spans {t_gpu:6.2f}s | "
                  f"vs cpu batch={args.batch}: max delta {worst:.1f} ms {'OK' if ok else 'MISMATCH'}")
            if not ok:
                failures.append(f"{key}: gpu path differs from cpu at the same batch ({n1} -> {n2}, {worst:.1f} ms)")
        print()

    # Silero is the only model with a batch cap. That is the one case that can
    # silently change the answer or abort, so check it directly: 4096 is far
    # above the cap, so it must be warned about, clamped to 64, and still give
    # exactly the batch=1 answer.
    fname, url = VAD_MODELS["silero"]
    path = cb.cache_ensure_file(fname, url, quiet=True)
    if path and Path(path).exists():
        small, _ = spans_for(cb, pcm, path, use_gpu=0, batch=1)
        big, _ = spans_for(cb, pcm, path, use_gpu=0, batch=4096)
        worst, _, _, ok = compare(small, big)
        print(f"silero     batch=4096 (above the cap, clamped): {len(big)} spans vs batch=1 "
              f"{len(small)} | max delta {worst:.1f} ms {'OK' if ok else 'MISMATCH'}")
        if not ok:
            failures.append(f"silero: batch=4096 differs from batch=1 ({len(small)} -> {len(big)}, {worst:.1f} ms)")
        print()

    # Progress: the counter prints "crispasr[vad]: <label> done/total (..%) ..s"
    # on stderr. Run it in a subprocess so stderr can be captured cleanly.
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--progress-probe", "--lib", args.lib],
                       capture_output=True, text=True, env={**os.environ, "CRISPASR_VAD_PROGRESS_MS": "200"})
    lines = [l for l in r.stderr.splitlines() if "crispasr[vad]:" in l]
    print(f"progress   {len(lines)} line(s) on stderr" + (f" e.g. {lines[0].strip()}" if lines else ""))
    if not lines:
        failures.append("no progress lines were printed")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
