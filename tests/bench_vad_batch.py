#!/usr/bin/env python3
"""Sweep a VAD's batch width: spans, wall time, peak RSS.

The Silero graph is unrolled once per window, and the ggml scheduler sizes its
bookkeeping arrays from `graph_size` — so a wide batch is not free the way it is
for the frame-axis models. This measures both sides of that trade so the cap
(CRISPASR_VAD_MAX_BATCH) and the default can be picked from data.

Usage:
    python tests/bench_vad_batch.py --models silero --batches 1,8,32,64,128,256,512 --gpu
"""
from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CRISPASR = HERE.parent
REPO = CRISPASR.parents[1]
DEFAULT_LIB = CRISPASR / "build_win" / "bin" / "Release" / "crispasr.dll"
DEFAULT_AUDIO = (
    REPO / "speaker_inversion_example" / "data" / "speaker-inversion-dataset" / "test" / "01_cut_test2.mp3"
)
SR = 16000


def peak_mem_mb() -> tuple:
    """(peak working set, peak commit) of this process, via kernel32.

    Both matter: the ggml scheduler mallocs its per-node bookkeeping eagerly, so
    a wide batch shows up as commit charge long before it is touched (and hence
    resident). Reporting only RSS would make a wide batch look free.
    """
    if os.name != "nt":
        import resource

        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        return rss, rss
    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]

    c = PROCESS_MEMORY_COUNTERS()
    c.cb = ctypes.sizeof(c)
    fn = ctypes.windll.kernel32.K32GetProcessMemoryInfo
    fn.argtypes = [ctypes.c_void_p, ctypes.POINTER(PROCESS_MEMORY_COUNTERS), ctypes.c_ulong]
    fn.restype = ctypes.c_int
    if not fn(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb):
        raise OSError("K32GetProcessMemoryInfo failed")
    return c.PeakWorkingSetSize / 1048576.0, c.PeakPagefileUsage / 1048576.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=str(DEFAULT_AUDIO))
    ap.add_argument("--lib", default=str(DEFAULT_LIB))
    ap.add_argument("--models", default="silero")
    ap.add_argument("--batches", default="1,8,32,64,128,256,512")
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--seconds", type=float, default=0, help="0 = whole file")
    args = ap.parse_args()

    os.environ["CRISPASR_LIB_PATH"] = args.lib
    sys.path.insert(0, str(CRISPASR / "python"))
    import crispasr._binding as cb

    with tempfile.TemporaryDirectory() as td:
        raw = Path(td) / "a.f32"
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", args.audio,
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-c:a", "pcm_f32le", str(raw)], check=True)
        pcm = np.ascontiguousarray(np.fromfile(raw, dtype="<f4"), dtype=np.float32)
    if args.seconds:
        pcm = pcm[: int(args.seconds * SR)]
    r0, c0 = peak_mem_mb()
    print(f"{args.audio}  {pcm.size / SR:.1f}s   at import: rss {r0:.0f} MB, commit {c0:.0f} MB\n")

    for key in args.models.split(","):
        import importlib

        sys.path.insert(0, str(HERE))
        mod = importlib.import_module("test_vad_gpu_batch")
        fname, url = mod.VAD_MODELS[key]
        path = cb.cache_ensure_file(fname, url, quiet=True)
        ref = None
        for gpu in ([0, 1] if args.gpu else [0]):
            for b in (int(x) for x in args.batches.split(",")):
                try:
                    t0 = time.perf_counter()
                    spans = cb.vad_slices(pcm, path, threshold=0.5, use_gpu=gpu, batch_size=b)
                    el = time.perf_counter() - t0
                    if ref is None:
                        ref = spans
                    same = len(spans) == len(ref)
                    if same:
                        same = all(abs(x.start - y.start) < 1e-3 and abs(x.end - y.end) < 1e-3
                                   for x, y in zip(ref, spans))
                    rss, commit = peak_mem_mb()
                    print(f"{key:10s} gpu={gpu} batch={b:5d} -> {len(spans):4d} spans "
                          f"{el:7.2f}s  peak rss {rss:6.0f} MB commit {commit:6.0f} MB  "
                          f"{'same' if same else 'DIFFERS'}")
                except Exception as e:  # noqa: BLE001 - report and keep sweeping
                    print(f"{key:10s} gpu={gpu} batch={b:5d} -> FAILED: {type(e).__name__}: {e}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
