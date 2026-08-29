# CrispASR

[![日本語](https://img.shields.io/badge/lang-日本語-red?style=for-the-badge)](README.md)
[![繁體中文](https://img.shields.io/badge/lang-繁體中文-blue?style=for-the-badge)](README.zh.md)
[![English](https://img.shields.io/badge/lang-English-green?style=for-the-badge)](README.en.md)

**1 個の C++ バイナリ、119 のバックエンド —— そのうち 62 は TTS エンジン ——に加えて多言語テキスト翻訳、Python 依存ゼロ。**

CrispASR は [whisper.cpp](https://github.com/ggml-org/whisper.cpp) のフォークとして始まりましたが、その基盤を、主要なオープンウェイトの ASR *および* TTS アーキテクチャのための完全な ggml C++ ランタイムに支えられた **統合音声エンジン** `crispasr` へと拡張しています。1 回のビルド、1 個のバイナリ、1 つの一貫した CLI —— バックエンドはコマンドラインで選択するか、GGUF ファイルから CrispASR に自動検出させることができます。TTS 側は [Text-to-Speech](#text-to-speech-models) を参照してください。

```console
$ crispasr -m ggml-base.en.bin          -f samples/jfk.wav                    # OpenAI Whisper
$ crispasr -m parakeet-tdt-0.6b.gguf    -f samples/jfk.wav                    # NVIDIA Parakeet
$ crispasr -m canary-1b-v2.gguf         -f samples/jfk.wav                    # NVIDIA Canary
$ crispasr -m voxtral-mini-3b-2507.gguf -f samples/jfk.wav                    # Mistral Voxtral
$ crispasr --backend qwen3 -m auto      -f samples/jfk.wav                    # -m auto はダウンロードする
$ crispasr --backend kokoro -m auto --tts "Hello world" --tts-output out.wav  # TTS
```

Python なし。PyTorch なし。モデルごとの別バイナリなし。`pip install` なし。ただ 1 個の C++ バイナリと 1 つの GGUF ファイルだけです。

**ブラウザ**: すべてのバックエンドは `build-wasm.sh` 経由で WebAssembly（4.3 MB）にコンパイルされます。
マルチスレッド対応で、COOP/COEP ヘッダーによりクライアント側で完全に実行されます。

**デモ**: [HuggingFace Space](https://huggingface.co/spaces/cstr/CrispASR) ——
ライブ文字起こし + TTS + 言語検出を `hf-space/` から自動デプロイ。

### エコシステム

| プロジェクト | 役割 |
|---|---|
| **[CrispASR](https://github.com/CrispStrobe/CrispASR)** | このリポジトリ —— C++ 音声エンジン。119 バックエンド（62 TTS）、CLI + HTTP サーバー + C-ABI + Python/Rust/Dart/Go/Ruby/Java バインディング。 |
| **[CrisperWeaver](https://github.com/CrispStrobe/CrisperWeaver)** | CrispASR 上に構築されたクロスプラットフォームの Flutter 文字起こしアプリ。デスクトップ + モバイル、ダウンロードキュー付きモデルブラウザ、マイクキャプチャ、SRT/VTT/JSON エクスポート、話者分離、バッチ処理。完全オフライン対応。 |
| **[CrispEmbed](https://github.com/CrispStrobe/CrispEmbed)** | ggml によるテキスト関連エンジン —— CrispASR と同じ哲学だが、埋め込み・検索・OCR と OMR・数式および楽譜記向け。多数のアーキテクチャ（XLM-R、Qwen3-Embed、Gemma3、ModernBERT、...）、密 + 疎 + ColBERT + リランキング。PP-OCR、Tesseract、EasyOCR、InternVL2 など。Python/Rust/Dart バインディング。 |
| **[Susurrus](https://github.com/CrispStrobe/Susurrus)** | 9 バックエンド（faster-whisper、mlx-whisper、voxtral、insanely-fast-whisper、...）を備えた Python ASR GUI。CrispASR の C++ アプローチに対応する Python 版。 |

---

## 目次

- [**ここから始める**](#start-here) —— CrispASR は初めてですか？ リポジトリをクローンせずに、2 つのコマンドで初めての動作する音声到手順
- [対応バックエンド](#supported-backends) —— [ASR](#asr-backends) + [TTS](#text-to-speech-models) + [翻訳](#translation) + [ポストプロセッシング](#post-processing-models) + [音楽・音声解析](#music--audio-analysis)
- [機能マトリクス](#feature-matrix)
- [インストールとビルド](#install--build) —— クイックインストール（完全ガイドは [docs/install.md](docs/install.md)）; **[どの Linux プリビルド tarball をダウンロードすべきか](docs/install.md#prebuilt-linux-tarballs--which-one-to-download-355)** —— `-hip` / `-vulkan` ビルドは対応する GPU ドライバーを必要とし、CPU には**フォールバックしません**（`-cuda` tarball は v0.8.30 以降フォールバックします）
- [クイックスタート —— ASR](#quick-start)
- [トラブルシューティング](docs/troubleshooting.md) —— バナー表示後に停止した、終了コードの読み方、`--no-gpu` バイセクト、どの Windows zip か
- [**Text-to-Speech (TTS)**](docs/tts.md) —— 52 エンジン: Kokoro、Qwen3-TTS、VibeVoice、dots.tts、Orpheus、Chatterbox、IndexTTS、Irodori、VoxCPM2、CosyVoice3、CSM、Dia、Zonos、Bark、Piper、MeloTTS など
- [ストリーミングとライブ文字起こし](docs/streaming.md)
- [サーバーモード（HTTP API）](docs/server.md)
- [並行性・並列化・スケーリング](docs/concurrency.md) —— 1 回の文字起こしが複数コアを使う方法、同時サーバーリクエスト（`--server-workers`）、バッチのオフライン文字起こし、ロードバランサー後のレプリカ
- [CLI リファレンス](docs/cli.md) —— フラグ、VAD、CTC アライメント、出力フォーマット、自動ダウンロード、音声フォーマット
- [環境変数](docs/environment-variables.md) —— `CRISPASR_<BACKEND>_<FEATURE>` の規約、グローバルな調整項目、および各バックエンドの変数
- [言語バインディング](docs/bindings.md) —— Python / Rust / Dart / Go / Java / JavaScript / Ruby / モバイル
- [CrispASR のベンチマーク](docs/benchmarking.md) —— 文字起こし時間（コールドスタートではない）の測定方法: サーバー／インプロセスの繰り返し、proof-of-work ルール、フェーズ計測の環境変数
- [アーキテクチャ](docs/architecture.md) —— 層状レイアウト、`src/core/` プリミティブ、リグレッション規律
- [コントリビューティング —— 新しいバックエンドの追加](docs/contributing.md) —— 5 ファイルのレシピ、グラウンドトゥルース差分ワークフロー
- [リグレッションマトリクス](docs/regression-matrix.md) —— `tools/test-all-backends.py` のケイパビリティ階層
- [**EU AI Act**](docs/eu-ai-act.md) —— 合成音声マーキング（ウォーターマーク + C2PA + 読み上げによる免責）、ボイスクローンと見なされる範囲、話者生体認証の境界、感情認識が存在しない理由、およびデプロイヤーとして残るあなたの責務
- [モデルの量子化](docs/quantize.md) —— すべてのバックエンド向けの `crispasr-quantize`
- [GPU バックエンド選択](#gpu-backend-selection)
- [デバッグとプロファイリング](#debugging--profiling)
- [クレジット](#credits)

---

<a id="start-here"></a>
## ここから始める

このセクションより下はすべてカタログです —— 100 以上のバックエンド、必要になったときに探してください。ただ CrispASR を*動かしたい*だけなら、これが全手順です。リポジトリのクローンなし、Python なし、モデル探しなし。

プロジェクトは初めてですか？**[docs/getting-started.md](docs/getting-started.md)** が同じ手順を一歩ずつ辿り、想定される出力とよくある 3 つの初回実行失敗を説明します。

### 1. バイナリを取得する

[**Releases**](https://github.com/CrispStrobe/CrispASR/releases/latest) から 1 ファイルをダウンロードして解凍します:

| プラットフォーム | ダウンロード | 備考 |
|---|---|---|
| **Windows** | `crispasr-windows-x86_64-cpu.zip` | AVX2 が必要（2013+ Intel / 2015+ AMD）。古い CPU → `…-cpu-legacy.zip` |
| **Windows + NVIDIA** | `crispasr-windows-x86_64-cuda.zip` | 自己完結型; CUDA Toolkit のインストールは**不要**。CUDA-13 ネイティブビルド: `…-cuda13.zip`（Turing+） |
| **macOS** | `crispasr-macos.tar.gz` | Metal GPU サポート内蔵 |
| **Linux** | `crispasr-linux-x86_64.tar.gz` | GPU 向けは `…-cuda.tar.gz` / `…-vulkan.tar.gz` |

自分でビルドしたい場合は [インストールとビルド](#install--build) を参照してください。`-hip` および `-vulkan` ビルドは対応するドライバーを必要とし、CPU には**フォールバックしません**; Linux の `-cuda` tarball はフォールバックします。

動作確認 —— バージョンバナーが表示されて終了するはずです:

```bash
crispasr --version          # Windows: .\crispasr.exe --version
```

CUDA ビルドは `cuda toolkit` と `cuda runtime ABI` も表示するため、このコマンドは DLL を調べずに CUDA 12 と CUDA 13 のパッケージを区別できます。

### 2. 話させる

`-m auto` は初回使用時にモデルをダウンロードし（ここでは約 135 MB）、以降それを再利用します —— 探したりインストールしたりするものは何もありません。`~/.cache/crispasr/`（Windows では `%USERPROFILE%\.cache\crispasr`）に保存されます。

```bash
crispasr --backend kokoro -m auto --tts "The quick brown fox jumps over the lazy dog." --tts-output hello.wav
# crispasr: TTS output written to 'hello.wav' (78000 samples @ 24000 Hz, 3.25 sec)
```

`hello.wav` を再生してください。これで TTS 側が動作しています。

### 3. 今度は文字起こしする

```bash
crispasr --backend parakeet -m auto -f hello.wav -l en
# crispasr: transcribed 3.2s audio in 0.32s (10.1x realtime)
# The quick brown fox jumps over the lazy dog.
```

（初回実行で約 467 MB。`-l en` は言語自動検出をスキップします。スキップしないと小さな追加モデルを取得します。）両方が動作するようになりました —— 自分の `.wav` に置き換えれば実行できます。

### 次に進む場所

| やりたいこと | 参照先 |
|---|---|
| 録音からボイスクローンする | [docs/tts.md](docs/tts.md) —— まず[同意ルール](docs/eu-ai-act.md)を読む; クローンには `--i-have-rights` が必要 |
| より良い ASR モデルを選ぶ | [どのバックエンドを選ぶべき？](#which-backend-should-i-pick) |
| 単語タイムスタンプ、SRT/VTT で文字起こし | [docs/cli.md](docs/cli.md) |
| ライブマイク / ストリーミング | [docs/streaming.md](docs/streaming.md) |
| HTTP サーバーとして実行 | [docs/server.md](docs/server.md) |
| このバイナリが持つ全バックエンドを見る | `crispasr --list-backends` |

### もし何も起きなかったら

 任意のコマンドに `-v` を追加すると詳細な進行状況が表示され、`--dry-run-resolve` を追加すると、何も読み込まずにどのモデルファイルを開くか（およびディスク上にあるか）が表示されます。

コマンドがバナーを表示した後に単純に停止した場合 —— エラーも出力ファイルもない —— それは拒否ではなくクラッシュであり、終了コードが 1 ステップでそれを識別します。**[docs/troubleshooting.md](docs/troubleshooting.md)** を参照してください。

---

<a id="supported-backends"></a>
## 対応バックエンド

CrispASR は **119 バックエンド**を同梱します（自動計数された信頼できる一覧は[生成された機能マトリクス](docs/feature-matrix.md)を参照）—— 大多数は文字起こし／翻訳用で、**62 の TTS エンジン**は合成用です。また、Sidon 復元や VoxCPM2 AudioVAE 音声アップスケーラーを含む、音声から音声への S2S バックエンドも同梱します; 完全なケイパビリティ一覧は[機能マトリクス](docs/feature-matrix.md)を参照してください。
CLI で `--backend NAME` を選択するか、省略してバイナリに GGUF メタデータから自動検出させることができます。合成側は下の [TTS テーブル](#text-to-speech-models)にジャンプしてください。

<a id="asr-backends"></a>
### ASR バックエンド

| バックエンド | モデル | アーキテクチャ | 言語 | ライセンス |
|---|---|---|---|---|
| **whisper** | [`ggml-base.en.bin`](https://huggingface.co/ggerganov/whisper.cpp/) とすべての OpenAI Whisper 変種 | エンコーダ＝デコーダ トランスフォーマ | 99 | MIT |
| **whisper** | [`distil-whisper/distil-large-v3`](https://huggingface.co/cstr/distil-large-v3-GGUF) | 蒸留 Whisper: 32L エンコーダ + 2L デコーダ（6.3 倍高速） | 英語 | MIT |
| **dolphin** | [`DataoceanAI1/dolphin-cn-dialect-small-streaming`](https://huggingface.co/cstr/dolphin-cn-dialect-small-streaming-GGUF)（`-m dolphin`） | E-Branchformer + トランスフォーマデコーダ + CTC; CTC プレフィック beams + attention rescoring | 標準中国語 + 中国語方言（言語/地域を予測） | Apache-2.0 |
| **xasr** | [`GilgameshWind/X-ASR-zh-en`](https://huggingface.co/cstr/x-asr-zh-en-GGUF)（`-m xasr`） | ストリーミング Zipformer2 トランスデューサ（icefall）; 160 / 480 / 960 / 1920 ms チャンク、リアルタイム WebSocket セッション | zh, en（句読点 + 大文字小文字） | Apache-2.0 |
| **parakeet** | [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) | FastConformer + TDT | 25 EU（自動検出） | CC-BY-4.0 |
| **parakeet** | [`oruk/orukeet`](https://huggingface.co/cstr/orukeet-GGUF)（`-m orukeet`） | parakeet-tdt-0.6b-v3 のファインチューン、エンコーダの depthwise カーネルの半分がフィッティング済み Gabor 関数に置き換え | 25 EU（自動検出） | CC-BY-SA-4.0 |
| **parakeet** | [`moondream/parakeet-ultra`](https://huggingface.co/cstr/parakeet-ultra-GGUF)（`-m parakeet-ultra`） | transformers フォーマットで提供される parakeet-tdt-0.6b-v3 アーキテクチャ; `--hf` で変換 | 25 EU（自動検出） | CC-BY-4.0 |
| **parakeet** | [`moondream/parakeet-redux`](https://huggingface.co/cstr/parakeet-redux-GGUF)（`-m parakeet-redux`） | 3 値（base-3 パック）エンコーダを備えた parakeet-tdt-0.6b-v3、変換器によって正確に逆量子化 | 25 EU（自動検出） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt-0.6b-v2`](https://huggingface.co/cstr/parakeet-tdt-0.6b-v2-GGUF) | FastConformer + TDT、元の Open ASR Leaderboard 首位 | en（混成大文字小文字 + 句読点） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt-1.1b`](https://huggingface.co/cstr/parakeet-tdt-1.1b-GGUF) | 42L FastConformer + TDT、より大きな英語変種 | en（小文字） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-110m`](https://huggingface.co/cstr/parakeet-tdt_ctc-110m-GGUF) | 17L FastConformer + TDT+CTC ハイブリッド; 最小変種、自動 CTC デコード | en | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-1.1b`](https://huggingface.co/cstr/parakeet-tdt_ctc-1.1b-GGUF) | 42L FastConformer + TDT+CTC ハイブリッド; 最大、混成大文字小文字 + 句読点 | en | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-0.6b-ja`](https://huggingface.co/cstr/parakeet-tdt-0.6b-ja-GGUF) | FastConformer-TDT-CTC、xscaling、80 mel | 日本語 | CC-BY-4.0 |
| **reazonspeech** | [`reazon-research/reazonspeech-nemo-v2`](https://huggingface.co/cstr/reazonspeech-nemo-v2-GGUF) | FastConformer-RNNT、局所 attention（w=256）、80 mel、619M パラメータ | 日本語 | Apache-2.0 |
| **fastconformer-ctc** | [`nvidia/parakeet-ctc-0.6b`](https://huggingface.co/cstr/parakeet-ctc-0.6b-GGUF) | 24L FastConformer + CTC、80 mel（fc-ctc-xlarge と同一アーキテクチャ） | en | CC-BY-4.0 |
| **fastconformer-ctc** | [`nvidia/parakeet-ctc-1.1b`](https://huggingface.co/cstr/parakeet-ctc-1.1b-GGUF) | 42L FastConformer + CTC、80 mel | en | CC-BY-4.0 |
| **fastconformer-ctc** | [`grider-transwithai/parakeet-ctc-1.1b-ja`](https://huggingface.co/cstr/parakeet-ctc-1.1b-ja-GGUF) | 42L FastConformer + CTC、80 mel、日本語ファインチューン | 日本語 | Apache-2.0 |
| **canary** | [`nvidia/canary-1b-v2`](https://huggingface.co/nvidia/canary-1b-v2) | FastConformer + トランスフォーマデコーダ | 25 EU（明示的な `-sl/-tl`） | CC-BY-4.0 |
| **canary-qwen** | [`nvidia/canary-qwen-2.5b`](https://huggingface.co/nvidia/canary-qwen-2.5b) | FastConformer + Qwen3-1.7B SALM | en | CC-BY-4.0 |
| **lfm2-audio** | [`LiquidAI/LFM2.5-Audio-1.5B`](https://huggingface.co/cstr/lfm2-audio-1.5b-GGUF) | FastConformer + LFM2 ハイブリッド conv+attention バックボーン（ASR+TTS） | en | LFM Open v1.0 |
| **lfm2-audio** | [`LiquidAI/LFM2.5-Audio-1.5B-JP`](https://huggingface.co/cstr/lfm2-audio-1.5b-jp-GGUF) | FastConformer + LFM2 ハイブリッド conv+attention バックボーン（ASR+TTS） | ja | LFM Open v1.0 |
| **mini-omni2** | [`gpt-omni/mini-omni2`](https://huggingface.co/gpt-omni/mini-omni2) | Whisper-small + Qwen2-0.5B（ASR+TTS+S2S） | en | MIT |
| **cohere** | [`CohereLabs/cohere-transcribe-03-2026`](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | Conformer + トランスフォーマ | 13 | Apache-2.0 |
| **cohere** | [`efwkjn/cohere-asr-ja-v0.1`](https://huggingface.co/TransWithAI/cohere-transcribe-ja-v0.1-GGUF) | cohere-transcribe-03-2026 の日本語ファインチューン（TedX/JSUT チューニング済み） | 日本語 | Apache-2.0 |
| **granite** | [`ibm-granite/granite-speech-{3.2-8b,3.3-2b,3.3-8b}`](https://huggingface.co/ibm-granite/granite-speech-3.3-2b)、[`granite-4.0-1b-speech`](https://huggingface.co/ibm-granite/granite-4.0-1b-speech) | Conformer + Q-Former + Granite LLM（μP）（[詳細](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt ja | Apache-2.0 |
| **granite-4.1** | [`ibm-granite/granite-speech-4.1-2b`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | 16L Conformer + Q-Former + Granite LLM; 単一 ggml グラフ（[詳細](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt ja | Apache-2.0 |
| **granite-4.1-plus** | [`ibm-granite/granite-speech-4.1-2b-plus`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus) | 4.1 + 隠れ状態の連結; 句読点付き出力（[詳細](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt | Apache-2.0 |
| **granite-4.1-nar** | [`ibm-granite/granite-speech-4.1-2b-nar`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-nar) | 非自己回帰: 単一 LLM 前方伝播 + スロット argmax（[詳細](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt | Apache-2.0 |
| **fastconformer-ctc** | [`nvidia/stt_en_fastconformer_ctc_large`](https://huggingface.co/nvidia/stt_en_fastconformer_ctc_large) | FastConformer + CTC（NeMo ファミリー、全サイズ） | en | CC-BY-4.0 |
| **voxtral** | [`mistralai/Voxtral-Mini-3B-2507`](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | Whisper エンコーダ + Mistral 3B LLM | 8 | Apache-2.0 |
| **voxtral4b** | [`mistralai/Voxtral-Mini-4B-Realtime-2602`](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602) | 因果的エンコーダ + 3.4B LLM、スライディングウィンドウ | 13、リアルタイムストリーミング | Apache-2.0 |
| **qwen3** | [`Qwen/Qwen3-ASR-0.6B`](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | Whisper スタイルの音声エンコーダ + Qwen3 0.6B LLM | 30 + 22 の中国語方言 | Apache-2.0 |
| **qwen3-1.7b** | [`Qwen/Qwen3-ASR-1.7B`](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) | Whisper スタイルの音声エンコーダ + Qwen3 1.7B LLM | 30 + 22 の中国語方言 | Apache-2.0 |
| **confucius4-r2t2** | [`netease-youdao/Confucius4-R2T2`](https://huggingface.co/cstr/confucius4-r2t2-GGUF) | Qwen3-ASR-1.7B ストリーミングファインチューン; 追加のみリアルタイムセッション（プレフィックス巻き戻し） | 30 言語 | NetEase Youdao Model Use License |
| **raon-speech** | [`KRAFTON/Raon-Speech-9B`](https://huggingface.co/cstr/raon-speech-9b-GGUF) | Qwen3-Omni 音声タワー + アダプタ + Qwen3 36L LLM（音声テキスト変換サブセット; 24 kHz で 8 s チャンク） | en, ko | CC-BY-NC-4.0（非商業） |
| **qwen3-ja-anime** | [`jaykwok/Qwen3-ASR-1.7B-JA-Anime-Galgame-hf`](https://huggingface.co/jaykwok/Qwen3-ASR-1.7B-JA-Anime-Galgame-hf) | 日本語アニメ/ギャルゲ音声向けにファインチューンされた Qwen3-ASR-1.7B | ja + 30 言語 | Apache-2.0 |
| **mega-asr** | [`zhifeixie/Mega-ASR`](https://huggingface.co/zhifeixie/Mega-ASR) | Qwen3-ASR-1.7B + マージ済み頑健性 LoRA; 常時稼働の頑健パス | 騒音 / 劣化した音声 | Apache-2.0 |
| **higgs-stt** | [`bosonai/higgs-audio-v3-stt`](https://huggingface.co/bosonai/higgs-audio-v3-stt) | Whisper-large-v3 エンコーダ（4 s チャンク）+ Qwen3-1.7B LLM（[詳細](docs/architecture.md#higgs-stt)） | en | Apache-2.0 |
| **wav2vec2** | [`jonatasgrosman/wav2vec2-large-xlsr-53-english`](https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-english) | CNN + 24L トランスフォーマ + CTC ヘッド（任意の Wav2Vec2ForCTC） | モデルごと | Apache-2.0 |
| **wav2vec2** | [`facebook/data2vec-audio-base-960h`](https://huggingface.co/cstr/data2vec-audio-960h-GGUF) | Data2Vec Audio（79 MB Q4_K） | 英語 | Apache-2.0 |
| **wav2vec2** | [`facebook/hubert-large-ls960-ft`](https://huggingface.co/cstr/hubert-large-ls960-ft-GGUF) | HuBERT Large（212 MB Q4_K） | 英語 | Apache-2.0 |
| **glm-asr** | [`zai-org/GLM-ASR-Nano-2512`](https://huggingface.co/zai-org/GLM-ASR-Nano-2512) | Whisper エンコーダ + 4 フレームプロジェクタ + Llama 1.5B（GQA） | 標準中国語（+ 中国語方言）、英語、広東語 | MIT |
| **kyutai-stt** | [`kyutai/stt-1b-en_fr`](https://huggingface.co/kyutai/stt-1b-en_fr) | Mimi コーデック（SEANet + RVQ）+ 16L 因果 LM | en, fr | MIT |
| **kyutai-stt** | [`kyutai/stt-2.6b-en`](https://huggingface.co/kyutai/stt-2.6b-en) | Mimi コーデック + 48L 因果 LM（2.6B、英語のみ; 3.5 s リックアヘッド） | en | MIT |
| **firered-asr** | [`FireRedTeam/FireRedASR2-AED`](https://huggingface.co/FireRedTeam/FireRedASR2-AED) | Conformer + CTC + beams search; LID も可（120 言語） | 標準中国語、英語、20+ の中国語方言 | Apache-2.0 |
| **moonshine** | [`UsefulSensors/moonshine-{tiny,base}`](https://huggingface.co/cstr/moonshine-base-GGUF) | Conv + 6L enc + 6L dec; 多言語変種 | 英語 + 6 言語 | MIT |
| **moonshine&#8209;de** | [`fidoriel/moonshine-base-de`](https://huggingface.co/cstr/moonshine-base-de-fidoriel-GGUF) | moonshine-base のドイツ語ファインチューン（CV22 で WER 6.9%） | ドイツ語 | CC&#8209;BY&#8209;NC&#8209;SA&#8209;4.0 |
| **moonshine&#8209;tiny&#8209;de** | [`fidoriel/moonshine-tiny-de`](https://huggingface.co/cstr/moonshine-tiny-de-fidoriel-GGUF) | moonshine-tiny のドイツ語ファインチューン（CV22 で WER 11.4%） | ドイツ語 | CC&#8209;BY&#8209;NC&#8209;SA&#8209;4.0 |
| **moonshine-streaming** | [`UsefulSensors/moonshine-streaming-{tiny,small,medium}`](https://huggingface.co/cstr/moonshine-streaming-tiny-GGUF) | ストリーミング: スライディングウィンドウエンコーダ + AR デコーダ（34–245M） | 英語 | MIT |
| **gemma4-e2b** | [`google/gemma-4-E2B-it`](https://huggingface.co/cstr/gemma4-e2b-it-GGUF) | USM Conformer 12L + Gemma4 LLM 35L（GQA、PLE） | 140+ 言語 | Apache-2.0 |
| **gemma4-e4b** | [`google/gemma-4-E4B-it`](https://huggingface.co/cstr/gemma4-e4b-it-GGUF) | 同一 USM Conformer 12L + より大きな Gemma4 LLM 42L（GQA、PLE）; `--backend gemma4-e2b` で実行 | 140+ 言語 | Apache-2.0 |
| **omniasr** | [`omniASR-CTC-1B-v2`](https://huggingface.co/cstr/omniASR-CTC-1B-v2-GGUF) | wav2vec2 CNN + 48L トランスフォーマ + CTC（[詳細](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr&#8209;300m** | [`omniASR-CTC-300M-v2`](https://huggingface.co/cstr/omniASR-CTC-300M-v2-GGUF) | 同一アーキテクチャ、24L、約 194 MB Q4_K; 7 s 超を自動チャンク（[詳細](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr-llm** | [`omniASR-LLM-300M-v2`](https://huggingface.co/cstr/omniasr-llm-300m-v2-GGUF) | 同一エンコーダ + 12L LLaMA デコーダ（[詳細](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr-llm** | [`omniASR-LLM-Unlimited-300M-v2`](https://huggingface.co/cstr/omniasr-llm-unlimited-300m-v2-GGUF) | ストリーミング: 15s セグメントプロトコル、無制限音声（[詳細](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **vibevoice** | [`microsoft/VibeVoice-ASR`](https://huggingface.co/cstr/vibevoice-asr-GGUF) | σ-VAE ConvNeXt + Qwen2.5-7B（[詳細](docs/architecture.md#vibevoice)） | 50+ | MIT |
| **vibevoice-streaming** | [`microsoft/VibeVoice-ASR-Streaming-1.5B`](https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-1.5B) | σ-VAE ConvNeXt + Qwen2.5-1.5B; 永続 KV で 2.93 s チャンク、0.53 s リックアヘッド（[詳細](docs/architecture.md#vibevoice)） | 多言語 | MIT |
| **vibevoice-bitnet** | [`VibeVoice-ASR-BitNet`](https://huggingface.co/cstr/vibevoice-asr-bitnet-GGUF) | 同一アーキテクチャ、TQ2_0 3 値 LM（1.6 GB）（[詳細](docs/architecture.md#vibevoice)） | 7+ | MIT |
| **mimo-asr** | [`XiaomiMiMo/MiMo-V2.5-ASR`](https://huggingface.co/cstr/mimo-asr-GGUF) | 6L トランスフォーマ + 36L Qwen2 LM + RVQ コーデック（[詳細](docs/architecture.md#mimo-asr)） | 標準中国語 + 方言 + 英語 | MIT |
| **ark-asr** ⚠️*実験的/WIP* | [`cstr/ark-asr-3b-GGUF`](https://huggingface.co/cstr/ark-asr-3b-GGUF)（ベース [`AutoArk-AI/ARK-ASR-3B`](https://huggingface.co/AutoArk-AI/ARK-ASR-3B)） | Whisper-large-v3 enc（部分 RoPE）+ Qwen2.5-3B LM（[詳細](docs/architecture.md#ark-asr)） | 19（zh, en, de, ja, fr, ko, es, pl, it, ro, hu, cs, nl, fi, hr, sk, sl, et, lt） | ベースを参照 |
| **moss-audio** | [`OpenMOSS-Team/MOSS-Audio-4B-Instruct`](https://huggingface.co/cstr/MOSS-Audio-4B-Instruct-GGUF) | 32L Whisper エンコーダ + DeepStack 3 タップ + 36L Qwen3 LM; 音声理解 + ASR（[詳細](docs/architecture.md#moss-audio)） | zh, en | Apache-2.0 |
| **hojo-asr** | [`HojoAI/Hojo-ASR-Multi-V1`](https://huggingface.co/cstr/Hojo-ASR-Multi-V1-GGUF) | Qwen3-Omni 音声タワー（32L）+ 2 ブロック WeNet Conformer アダプタ + Qwen3-4B LM; 多言語 ASR（[詳細](docs/architecture.md#hojo-asr)） | de, fr, it, pt, es, ja, ar, ko, ru | Apache-2.0 |
| **moss-transcribe** | [`OpenMOSS-Team/MOSS-Transcribe-preview-2B`](https://huggingface.co/cstr/MOSS-Transcribe-preview-2B-GGUF) | Qwen3-Omni 音声エンコーダ（32L、ウィンドウ attention）+ GatedMLP アダプタ + Qwen3-1.7B LM; ASR（[詳細](docs/architecture.md#moss-transcribe)） | zh, en | Apache-2.0 |
| **moss-diarize** | [`OpenMOSS-Team/MOSS-Transcribe-Diarize-0.9B`](https://huggingface.co/cstr/MOSS-Transcribe-Diarize-0.9B-GGUF) | ストック Whisper エンコーダ（24L、80 mel）+ 4x マージ + VQAdaptor + Qwen3-0.6B LM; 同時 ASR + 話者分離 + タイムスタンプ | 多言語 | Apache-2.0 |
| **whisper** *(tiron)* ⚠️*実験的* | [`Trelis/tiron`](https://huggingface.co/cstr/tiron-GGML)（ベース [`Trelis/tiron`](https://huggingface.co/Trelis/tiron)） | 拡張ボキャブを持つ Whisper large-v3: 制約付きデコーディング grammar により、インラインの `<|speakerN|>` マーカー + 20 ms タイムスタンプを発行し、文字起こしとウィンドウ単位の話を同時に行い、ウィンドウ横のリンクで安定した話者へ帰属（#295） | 多言語（en 中心） | Apache-2.0 |
| **funasr** | [`FunAudioLLM/Fun-ASR-Nano-2512`](https://huggingface.co/cstr/funasr-nano-GGUF) | 70 ブロック SANM エンコーダ + 2 ブロックトランスフォーマアダプタ + Qwen3-0.6B LLM | zh, yue, en, ja, ko | FunASR Model License v1.1（帰属条件付きで商業 OK） |
| **fun-asr-mlt-nano** | [`FunAudioLLM/Fun-ASR-MLT-Nano-2512`](https://huggingface.co/cstr/funasr-mlt-nano-GGUF) | 同一アーキテクチャ、多言語デコーダ | de, fr, es, pt, ru, ar, hi, vi, th, ko を含む 31 言語 | FunASR Model License v1.1 |
| **paraformer** | [`funasr/paraformer-zh`](https://huggingface.co/cstr/paraformer-zh-GGUF) | 50 ブロック SANM エンコーダ + CIF 予測子 + 16 ブロック NAR デコーダ（単一パス、非自己回帰）; 文字レベルボキャブ（8404）; 220M パラメータ | zh, en | FunASR Model License（帰属条件付きで商業 OK） |
| **foxnose** *(話者分離)* | [`Wespeaker/wespeaker-voxceleb-resnet34-LM`](https://huggingface.co/cstr/wespeaker-resnet34-lm-GGUF) | `--diarize-method foxnose` による話者分離: WeSpeaker ResNet34-LM 256 次元埋め込み + GMM/BIC 話者数推定 + スペクトルクラスタリング + Viterbi 時間平滑化（[詳細](docs/architecture.md#foxnose-diarize)）。VoxConverse dev で 3.18 % DER、上流参照実装の 3.07 % に対して | 任意 | 重み CC-BY-4.0 |
| **gigaam** | [`ai-sage/GigaAM-v3`](https://huggingface.co/cstr/gigaam-v3-GGUF)（ベース [`ai-sage/GigaAM-v3`](https://huggingface.co/ai-sage/GigaAM-v3)） | 16 層 rotary Conformer（220M）+ CTC または RNN-T ヘッド; 4 リビジョン —— `e2e_rnnt` / `e2e_ctc` は SentencePiece ボキャブから句読点 + 大文字小文字 + ITN を出力、`rnnt` / `ctc` は生のキリル小文字を出力（[詳細](docs/architecture.md#gigaam)） | en ru | MIT |
| **sensevoice** | [`FunAudioLLM/SenseVoiceSmall`](https://huggingface.co/cstr/sensevoice-small-GGUF) | 70 ブロック SANM エンコーダ + CTC ヘッド; 単一の前方伝播で文字起こし + 言語 ID + 音声イベントを出力（非 AR、Whisper-Large より 15× 高速）; 構造化 C ABI + `-oj` JSON がタグを別フィールドとして公開。上流の感情分類器は**公開されていません** —— [EU AI Act](docs/eu-ai-act.md#41-emotion-recognition--removed-not-gated) を参照 | 50+ 言語; ネイティブ LID + 音声イベントタグ | FunASR Model License v1.1 |

### 音声から音声へのアップスケーリングと復元

| バックエンド | モデル | アーキテクチャ | 入力 / 出力 | ライセンス |
|---|---|---|---|---|
| **sidon** | [`KevinAHM/Sidon-GGUF`](https://huggingface.co/KevinAHM/Sidon-GGUF)（ベース [`sarulab-speech/sidon-v0.1`](https://huggingface.co/sarulab-speech/sidon-v0.1)） | w2v-BERT 2.0 予測子 + 連続 DAC デコーダ（[詳細](docs/architecture.md#sidon)） | 16 kHz モノ → 復元された 48 kHz モノ | MIT |
| **voxcpm2-vae** | [`openbmb/VoxCPM2`](https://huggingface.co/openbmb/VoxCPM2) の AudioVAE V2、`--vae-only` で変換 | 分離された因果的 AudioVAE エンコーダ + デコーダ（[詳細](docs/architecture.md#voxcpm2-vae)） | 16 kHz モノ → アップスケールされた 48 kHz モノ | Apache-2.0 |

```bash
huggingface-cli download KevinAHM/Sidon-GGUF sidon-v0.1-f16.gguf --local-dir models
crispasr -m models/sidon-v0.1-f16.gguf -f input.wav --s2s --s2s-output restored.wav

python models/convert-voxcpm2-to-gguf.py --input openbmb/VoxCPM2 \
  --output models/voxcpm2-vae-f32.gguf --vae-only
crispasr -m models/voxcpm2-vae-f32.gguf -f input.wav --s2s \
  --s2s-output upscaled.wav
```

<a id="text-to-speech-models"></a>
### Text-to-Speech モデル

合成バックエンドは、`--tts` フラグと `--tts-output PATH.wav` で駆動されます。
クイックスタートコマンドとエンジン選択のガイダンスは、下の専用セクション [Text-to-Speech](#text-to-speech-models) を参照してください。

| バックエンド | モデル | アーキテクチャ | 言語 | ライセンス |
|---------|--------|-------------|-----------|---------|
| **bt2-tts** | [`breeze-tts-2`](https://huggingface.co/cstr/breeze-tts-2-GGUF) | T5Gemma2 テキストエンコーダ + Qwen3 バックボーン + 16 コードブック @ 12.5 Hz 上の 12L depth デコーダ; ボイスクローン。コーデックの同伴は同梱の qwen3-tts トークナイザ。**非商業ウェイト** —— `--accept-license other` が必要。BreezeBlue による Breeze TTS 2 から派生し、研究および非商業用途に限定されたライセンス。 | en, zh | other（BreezeBlue Research & Non-Commercial） |
| **miotts** | [`MioTTS-0.6B`](https://huggingface.co/cstr/miotts-0.6b-GGUF) | Qwen3 LLM + MioCodec-v2 FSQ コーデック（25 Hz、44.1 kHz 出力） | ja, en | Apache-2.0 |
| **vibevoice-tts** | [`VibeVoice-Realtime-0.5B`](https://huggingface.co/cstr/vibevoice-realtime-0.5b-GGUF)、[`VibeVoice-1.5B`](https://huggingface.co/cstr/vibevoice-1.5b-GGUF) | DPM-Solver++ + σ-VAE デコーダ; 音声プリセットまたはクローン | en, zh | MIT |
| **kugelaudio** | [`kugelaudio-0-open`](https://huggingface.co/cstr/kugelaudio-0-open-GGUF) | Qwen2.5-7B LM + 4L DiT 拡散 + 音響 VAE デコーダ; ボイスクローン | 多言語 | Apache-2.0 |
| **qwen3-tts** | [`Qwen3-TTS-12Hz-0.6B-Base`](https://huggingface.co/cstr/qwen3-tts-0.6b-base-GGUF)、[`1.7B-Base`](https://huggingface.co/cstr/qwen3-tts-1.7b-base-GGUF)、[`1.7B-VoiceDesign`](https://huggingface.co/cstr/qwen3-tts-1.7b-voicedesign-GGUF) | Qwen3 talker LM + 12 Hz RVQ（[詳細](docs/architecture.md#qwen3-tts)） | 多言語 | Apache-2.0 |
| **qwen3-tts-customvoice** | [`1.7B-CustomVoice`](https://huggingface.co/cstr/qwen3-tts-1.7b-customvoice-GGUF) | 同一 talker + 9 のプレミアム内蔵話者（`--voice <name>`）; `--instruct` によるオプションのスタイル（例 "spoke very slowly"）（[詳細](docs/architecture.md#qwen3-tts)） | 多言語 | Apache-2.0 |
| **moss-tts** | [`OpenMOSS-Team/MOSS-TTS-v1.5`](https://huggingface.co/cstr/moss-tts-v1.5-GGUF) | Qwen3-8B バックボーンが遅延パターン下で 32 RVQ 音声コードブックを発行し、1.6B 純トランスフォーマコーデック同伴が復号; `--voice ref.wav` によるボイスクローン; `--backend moss-tts -m <backbone> --codec-model <codec>` | 多言語 | Apache-2.0 |
| **moss-tts-local** | [`OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5`](https://huggingface.co/cstr/moss-tts-local-v1.5-GGUF) | Qwen3-4B バックボーン; 1 層のローカル/depth トランスフォーマが自己回帰的にフレームあたり 12 RVQ コードブックを発行（RQ-Transformer、遅延なし）、MOSS-Audio-Tokenizer-v2 で 48 kHz へ復号（モノへダウンミックス）; `--backend moss-tts-local -m <backbone> --codec-model <codec>` | 多言語 | Apache-2.0 |
| **omnivoice** | [`k2-fsa/OmniVoice`](https://huggingface.co/cstr/omnivoice-GGUF) | Qwen3-0.6B + マスク反復型 8 コードブック TTS（SoundStorm スタイル）; ボイスクローン; 600+ 言語（[詳細](docs/architecture.md#omnivoice)） | 600+ 言語 | Apache-2.0 |
| **melotts** | [`myshell-ai/MeloTTS`](https://github.com/myshell-ai/MeloTTS) EN_V2 | VITS2（6L トランスフォーマ + SDP/DP + トランスフォーマ coupling flow + HiFi-GAN）; 44.1 kHz、102 MB + 52 MB BERT Q4_K 同伴（合計 154 MB）; ニューラル G2P; 4 の EN 話者（[詳細](docs/architecture.md#melotts)） | en | MIT |
| **piper** | [`rhasspy/piper`](https://github.com/rhasspy/piper) コミュニティ音声 | VITS（6L トランスフォーマ + SDP + 4 ブロック coupling flow + HiFi-GAN）; 22 kHz モノ、音声あたり 30 MB F16; EN/DE/FR/ES/RU 向け内蔵 G2P（`--g2p-dict`） | 30+ 言語（内蔵 + espeak dlopen） | MIT |
| **kokoro** | [`hexgrad/Kokoro-82M`](https://huggingface.co/hexgrad/Kokoro-82M) + ドイツ語バックボーン | StyleTTS2 / iSTFTNet（82M）; 音声ごとの GGUF（[詳細](docs/architecture.md#kokoro)） | en, es, fr, hi, it, ja, pt, zh, de | Apache-2.0 |
| **orpheus** | [`Orpheus-3B-FT`](https://huggingface.co/cstr/orpheus-3b-0.1-ft-GGUF) + [`SNAC 24 kHz`](https://huggingface.co/cstr/snac-24khz-GGUF) | Llama-3.2-3B + SNAC RVQ コーデック; 8 話者（[詳細](docs/architecture.md#orpheus)） | en, de | Llama 3.2 Community License / MIT |
| **chatterbox** | [`cstr/chatterbox-GGUF`](https://huggingface.co/cstr/chatterbox-GGUF) + Nano/turbo/fine-tune 変種 | T3 AR + S3Gen flow-matching（[詳細](docs/architecture.md#chatterbox--chatterbox-turbo--chatterbox-nano--chatterbox-finnish-nano--kartoffelbox-turbo--lahgtna-chatterbox)） | 23 多言語; アラビア語、ドイツ語、フィンランド語（`chatterbox-finnish-nano`）の個別ファインチューン | MIT |
| **indextts** | [`cstr/indextts-1.5-GGUF`](https://huggingface.co/cstr/indextts-1.5-GGUF) | GPT-2 AR（24L/1280d）+ Conformer 条件付け + BigVGAN ボコーダ; 参照音声によるボイスクローン | zh, en | Apache-2.0 |
| **voxcpm2-tts** | [`cstr/voxcpm2-GGUF`](https://huggingface.co/cstr/voxcpm2-GGUF) | トークナイザフリーの CFM 拡散 AR（TSLM + RALM + LocDiT）、48 kHz ネイティブ; ゼロショット + `--voice <wav>` によるボイスクローン | 30 言語 | Apache-2.0 |
| **voxtral-tts** | [`mistralai/Voxtral-4B-TTS-2603`](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603) | Ministral-3B AR（26L GQA）+ 3L FM 音響トランスフォーマ（7 ステップ Euler ODE）+ Voxtral コーデックデコーダ @ 24 kHz; 20 のプリセット音声; SOTA のフランス語技術テキスト | en, fr, de, es, it, pt, nl, ar, hi | CC&#8209;BY&#8209;NC&#8209;4.0 |
| **cosyvoice3-tts** | [`cstr/cosyvoice3-0.5b-2512-GGUF`](https://huggingface.co/cstr/cosyvoice3-0.5b-2512-GGUF) | Qwen2-0.5B AR 音声トークン LM + DiT-CFM（10 ステップ Euler）+ HiFT（NSF + iSTFT）@ 24 kHz; `--voice <name>` によるベークド音声のゼロショットクローン、または任意の WAV を `--voice ref.wav --ref-text "<exact transcript>"`。`--backend cosyvoice3-tts-rl` は上流の RL チューニング済み talker を選択（同一同伴） | 9 言語 + 18 の zh 方言 | Apache-2.0 |
| **csm** | [`cstr/csm-1b-GGUF`](https://huggingface.co/cstr/csm-1b-GGUF) | Sesame CSM-1B 会話型 TTS: Llama-3.2 1B バックボーン + 100M depth デコーダ（32 コードブック RVQ）+ Kyutai Mimi コーデック @ 24 kHz（[詳細](docs/architecture.md#csm)） | en | Apache-2.0 |
| **lfm2-audio** | [`cstr/lfm2-audio-1.5b-GGUF`](https://huggingface.co/cstr/lfm2-audio-1.5b-GGUF) + [`jp`](https://huggingface.co/cstr/lfm2-audio-1.5b-jp-GGUF) | LFM2.5-Audio ASR+TTS+S2S: FastConformer enc + LFM2 ハイブリッドバックボーン + depthformer（8 コードブック Mimi）+ ISTFT デトークナイザ @ 24 kHz; テキスト + 音声の交互生成 | en, ja | LFM Open v1.0 |
| **dia** | [`nari-labs/Dia-1.6B`](https://huggingface.co/cstr/dia-1.6b-GGUF) | バイトレベルテキストエンコーダ（12L）+ AR 音声デコーダ（18L GQA + CFG）→ 9 遅延 DAC コードブック + 44.1 kHz DAC コーデック; `[S1]`/`[S2]` タグによる対話スタイル（100 文字超のプロンプトを使用） | en | Apache-2.0 |
| **zonos-tts** | [`cstr/zonos-v0.1-transformer-GGUF`](https://huggingface.co/cstr/zonos-v0.1-transformer-GGUF) + [`cstr/dac-44khz-GGUF`](https://huggingface.co/cstr/dac-44khz-GGUF) | Zyphra Zonos-v0.1: 26L GQA AR トランスフォーマ（2B）+ 9 コードブック DAC @ 44.1 kHz; CFG ガイド; 参照 WAV によるボイスクローン（[詳細](docs/architecture.md#zonos-tts)） | en | Apache-2.0 |
| **bark** | [`cstr/bark-small-GGUF`](https://huggingface.co/cstr/bark-small-GGUF) | Suno Bark 3 ステージ GPT-2 TTS: text→semantic（12L）→ coarse EnCodec（12L、2 コードブック）→ fine（12L、8 コードブック）→ EnCodec 24 kHz デコーダ; `.npz` プロンプトによる話者条件付け（`--voice <file.npz>`） | 多言語 | MIT |
| **speecht5** | [`cstr/speecht5-tts-GGUF`](https://huggingface.co/cstr/speecht5-tts-GGUF) | SpeechT5 80M: 文字レベルエンコーダ（12L）+ AR mel デコーダ（6L）+ 5 層 conv postnet + HiFi-GAN @ 16 kHz; 512 次元 x-vector による話者（`--voice <xvector.bin>`） | en | MIT |
| **fastpitch** | [`cstr/fastpitch-en-GGUF`](https://huggingface.co/cstr/fastpitch-en-GGUF) | NVIDIA FastPitch 60M: 非自己回帰並列 TTS —— 6L エンコーダ + duration/pitch 予測子 + 6L デコーダ + HiFi-GAN @ 22 kHz; 決定論的、単一前方伝播（[詳細](docs/architecture.md#fastpitch)） | en | CC-BY-4.0 |
| **bananamind-tts** | `Banaxi-Tech/BananaMind-TTS-V2.1-Preview` | BananaMind-TTS 13M: Tacotron-lite 文字レベルエンコーダ（Conv+BN+BiLSTM）+ 位置感性 attention を備えた AR GRU デコーダ + postnet + HiFi-GAN @ 22 kHz; ロケールごとに固定音声（[詳細](docs/architecture.md#bananamind-tts)） | en, de | Apache-2.0 |
| **parler-tts** | [`cstr/parler-tts-mini-v1.1-GGUF`](https://huggingface.co/cstr/parler-tts-mini-v1.1-GGUF) | Parler TTS Mini v1.1（約 900M）: T5 エンコーダ + MusicGen デコーダ + DAC 44.1 kHz; プロンプト条件付け（`--instruct` で音声をテキストで記述） | en | Apache-2.0 |
| **outetts** | [`cstr/outetts-0.3-1b-GGUF`](https://huggingface.co/cstr/outetts-0.3-1b-GGUF) | OLMo-1B talker + WavTokenizer 単一コードブック VQ-GAN @ 24 kHz; 話者プロファイル JSON によるボイスクローン（`--voice <speaker.json>`） | en | CC-BY-NC-SA-4.0 |
| **pocket-tts** | [`cstr/pocket-tts-GGUF`](https://huggingface.co/cstr/pocket-tts-GGUF) | Kyutai Pocket TTS 100M: 12.5 Hz での連続潜在 AR + 1 ステップ LSD flow + Mimi VAE 24 kHz; 参照音声または公式の準備済み `.safetensors` 音声によるボイスクローン（[詳細](docs/architecture.md#pocket-tts)） | en, de, es, it, pt; fr（24L プレビュー） | CC-BY-4.0 + 利用条件あり |
| **tada** | [`cstr/tada-tts-1b-GGUF`](https://huggingface.co/cstr/tada-tts-1b-GGUF) + `HumeAI/tada-3b-ml` | Llama-3.2 1B/3B バックボーン + トークン単位 FM 拡散ヘッド + TADA コーデック @ 24 kHz; 1:1 のテキスト＝音響アライメント; `tada-ref.gguf` によるデフォルトプロンプト、`models/convert-tada-ref-to-gguf.py` で構築した `--voice <tada-ref.gguf>` によるカスタム音声（[詳細](docs/architecture.md#tada)） | en | Llama 3.2 Community License |

<details>
<summary><b>TTS 機能マトリクス</b></summary>

| バックエンド | ボイスクローン | サンプリング | kHz | 自動ダウンロード | Flash attn |
|---------|:---:|:---:|:---:|:---:|:---:|
| vibevoice-tts | はい | temp | 24 | はい | はい |
| qwen3-tts | はい* | temp | 24 | はい | はい |
| omnivoice | はい | temp | 24 | — | — |
| kokoro | — | — | 24 | はい | — |
| orpheus | — | temp | 24 | はい | はい |
| chatterbox | はい | temp | 24 | はい | はい |
| outetts | はい（JSON） | temp | 24 | はい | はい |
| indextts | はい | temp | 24 | はい | はい |
| voxcpm2-tts | はい | — | 48 | はい | — |
| cosyvoice3-tts | はい | temp | 24 | はい | はい |
| f5-tts | はい | — | 24 | はい | — |
| irodori-tts | はい（WAV） | VoiceDesign: `--instruct` | 48 | はい | — |
| supertonic | プリセット F1-F5/M1-M5 | `--tts-speed`、`--tts-steps` | 44.1 | はい | — |
| csm | — | temp | 24 | はい | — |
| dia | — | temp | 44 | はい | — |
| bark | はい（.npz） | temp | 24 | はい | — |
| speecht5 | はい（xvec） | — | 16 | はい | — |
| parler-tts | — | temp | 44 | はい | — |
| fastpitch | — | — | 22 | — | — |
| piper | — | — | 22 | — | — |
| pocket-tts | はい | temp | 24 | はい | — |
| tada | はい | temp | 24 | はい | — |
| dots-tts | はい（`--voice ref.wav`） | 16 ステップ CFG Euler | 48 | はい | — |
| fireredtts3 | はい（`--voice ref.wav --ref-text "..."`） | 10 ステップ CFG Euler | 24 | はい | — |
| confucius4-tts | はい（`--voice ref.wav`） | 25 ステップ CFG Euler | 22.05 | はい | — |

\* CustomVoice 変種のみ; Base は `--voice <name>` 経由でベークド話者を使用します。

**出力言語。** `-tl <lang>`（または `-l`）は話すべき言語を選択します;
`cosyvoice3-tts`、`qwen3-tts`、`moss-tts` はこれをネイティブに扱います。
跨言語**クローン** —— 英語の参照クリップがドイツ語を話すケース、字幕吹替ケース —— では、
参照が話されている言語を示す `-sl <lang>` も渡してください; cosyvoice3 はアクセントを引き継ぐ代わりに
参照トランスクリプトを落とします。HTTP 経由: `POST /v1/audio/speech` の `"language"` + `"source_lang"`。
[`docs/tts.md`](docs/tts.md#output-language-and-cross-lingual-cloning--tl---sl) を参照。

</details>

<a id="translation"></a>
### 翻訳

テキストからテキストへの翻訳で、音声側の `--translate` フラグ（whisper / canary などで音声 → 英語テキストへルーティング）とは異なります。`--text "..." -sl <src> -tl <tgt>` で駆動します。

| バックエンド | モデル | アーキテクチャ | 言語 | ライセンス |
|---|---|---|---|---|
| **m2m100** | [`facebook/m2m100_418M`](https://huggingface.co/cstr/m2m100-418m-GGUF) | 12L enc + 12L dec トランスフォーマ、SentencePiece 128K（[詳細](docs/architecture.md#m2m100--wmt21)） | 100 言語、任意⇔任意 | MIT |
| **m2m100-wmt21** | [`facebook/wmt21-dense-24-wide-en-x`](https://huggingface.co/cstr/wmt21-dense-24-wide-en-x-GGUF) + [`facebook/wmt21-dense-24-wide-x-en`](https://huggingface.co/cstr/wmt21-dense-24-wide-x-en-GGUF) | m2m100 と同一、4.7B（24L enc）へスケール（[詳細](docs/architecture.md#m2m100--wmt21)） | 英語 ↔ 7 言語（個別の `en-x` / `x-en` チェックポイント） | MIT |
| **madlad** | [`google/madlad400-3b-mt`](https://huggingface.co/cstr/madlad400-3b-mt-GGUF) | T5 enc-dec（12L+12L、d=2048、gated-GELU、RMSNorm）（[詳細](docs/architecture.md#madlad)） | 419 言語 | Apache-2.0 |

```bash
# m2m100 base（プロダクション対応）
./build/bin/crispasr --backend m2m100 -m auto \
    --text "Hello world, how are you today?" \
    -sl en -tl de
# → Hallo Welt, wie bist du heute?

# WMT21 dense（英語 ↔ X、4.7B —— 約 2.5 GB を自動ダウンロード）。
# 個別の 2 チェックポイント: 英語ソース向けに en-x、英語ターゲット向けに x-en。
# `-sl`/`-tl` の方向に一致する方を選択してください
# （または明示的な `-m <path>` を渡して手動で他方を読み込む）。
./build/bin/crispasr --backend m2m100-wmt21 -m auto \
    --text "The president said he would not attend." \
    -sl en -tl de   # wmt21-dense-24-wide-en-x を使用

./build/bin/crispasr --backend m2m100-wmt21 \
    -m models/wmt21-dense-24-wide-x-en-q4_k.gguf \
    --text "Le président a dit qu'il ne serait pas présent." \
    -sl fr -tl en   # wmt21-dense-24-wide-x-en を使用

# MADLAD-400 3B（419 言語、Python SP とビット単位で同一）
./build/bin/crispasr --backend madlad -m auto \
    --text "Hello world." \
    -sl en -tl ta
```

2 ステージのパイプライン（例: ASR → m2m100）では、専用の
`--tr-sl` / `--tr-tl` フラグを使用してください; 未設定時は `-sl` / `-tl` に
フォールバックするので、単一ステージのスタンドアロン利用は `-sl/-tl` のみで十分です。

<a id="post-processing-models"></a>
### ポストプロセッシングモデル

すべてのバックエンドで動作します。

| モデル | タスク | アーキテクチャ | 言語 | ライセンス | HuggingFace |
|---|---|---|---|---|---|
| **FireRedPunc** | 句読点復元 | BERT-base（12L、d=768）、5 クラス | 中国語 + 英語 | Apache-2.0 | [`cstr/fireredpunc-GGUF`](https://huggingface.co/cstr/fireredpunc-GGUF) |
| **fullstop-punc** | 句読点復元 | XLM-RoBERTa-large（24L、d=1024）、6 クラス | EN, DE, FR, IT | MIT | [`cstr/fullstop-punc-multilang-GGUF`](https://huggingface.co/cstr/fullstop-punc-multilang-GGUF) |
| **punctuate-all** | 句読点復元 | XLM-RoBERTa-base（12L、d=768）、6 クラス | 12 言語 | MIT | [`cstr/punctuate-all-GGUF`](https://huggingface.co/cstr/punctuate-all-GGUF) |
| **PCS** | 句読点 + truecase + SBD | XLM-RoBERTa-base（12L）、4 ヘッド | 47 言語 | Apache-2.0 | `--punc-model pcs` |
| **truecaser&#8209;lstm** | ドイツ語 truecasing（最良） | BiLSTM 文字レベル（2×150、3.2 MB、F1 97.9%） | ドイツ語 | Apache-2.0 | `--truecase-model lstm` |
| **truecaser&#8209;crf** | ドイツ語 truecasing | CRF + コンテキスト特徴量（8.5 MB） | ドイツ語 | MIT | `--truecase-model crf` |
| **truecaser&#8209;de** | ドイツ語 truecasing（簡易） | 統計的単語頻度（71K エントリ、1.7 MB） | ドイツ語 | MIT | `--truecase-model auto` |
| **CLD3** | テキスト言語 ID | Embedding-bag → FC + ReLU → softmax（約 1.5 MB F32） | 109 ISO 639-1 | Apache-2.0 | [`cstr/cld3-GGUF`](https://huggingface.co/cstr/cld3-GGUF) |
| **GlotLID-V3** | テキスト言語 ID | fastText 教師あり、フラット softmax | 2102 ISO 639-3 + スクリプト | Apache-2.0 | [`cstr/glotlid-GGUF`](https://huggingface.co/cstr/glotlid-GGUF) |
| **LID-176** | テキスト言語 ID | fastText 教師あり、階層 softmax | 176 ISO 639-1 | CC-BY-NC-4.0 | [`cstr/fasttext-lid176-GGUF`](https://huggingface.co/cstr/fasttext-lid176-GGUF) |

### 音声コーデック

TTS バックエンドが共有するコーデックモジュール。encode/decode 用に単体でも利用可能です。

| モデル | アーキテクチャ | サンプリングレート | トークンレート | ライセンス | HuggingFace |
|---|---|---|---|---|---|
| **MioCodec v2** | WavLM エンコーダ → FSQ(12800) → トランスフォーマデコーダ + AdaLN-Zero + SnakeBeta アップサンプラ + iSTFT | 44.1 kHz | 25 Hz（341 bps） | MIT | [`cstr/miocodec-v2-44k-GGUF`](https://huggingface.co/cstr/miocodec-v2-44k-GGUF) |
| **SNAC 24 kHz** | 3 コードブック RVQ + デコーダブロック（stride 8/8/4/2） | 24 kHz | 3×12.5 Hz | MIT | [`cstr/snac-24khz-GGUF`](https://huggingface.co/cstr/snac-24khz-GGUF) |

すべてのランタイムは ggml ベースの推論を共有します。音声 LLM バックエンド（**qwen3**、**voxtral**、**voxtral4b**、**granite**、**glm-asr**、**kyutai-stt**）は、専用の CTC/トランスデューサ/seq2seq デコーダを使う代わりに、音声エンコーダのフレームを自己回帰言語モデルの入力埋め込みへ直接注入します。**fastconformer-ctc** バックエンドは、NeMo FastConformer-CTC のスタンドアロン ASR ファミリー —— `stt_en_fastconformer_ctc_{large,xlarge,xxlarge}` とアーキテクチャ上同一の `parakeet-ctc-{0.6b,1.1b}`（学習データとトークナイザが異なり、エンコーダ + ヘッド形状は同一）—— をグリーディ CTC デコードでホストします。canary-ctc アライナと同じ C++ ランタイムです。

<a id="music--audio-analysis"></a>
### 音楽・音声解析

音声を超えて、CrispASR は複数の音楽／音声解析タスクを実行します —— それぞれ小さな GGUF で、アーキテクチャは自動検出、Python なし。タスク別のフラグと出力フォーマットは [`docs/cli.md`](docs/cli.md) を参照してください。

- **ソース分離**（`--separate`）—— ミックスをステムへ分離（`<input>_<stem>.wav`）、**mel-band-roformer**（vocal/instrumental、MIT）または **htdemucs**（4 ステーム）経由。`--stems vocals,drums` でサブセットを選択;
  `--sep-output-dir` で出力先を設定。
- **ピアノ転写**（`--backend piano-transcription`）—— ピアノ音声 → ノートイベント（88 キー @ 100 fps、ByteDance/Kong CRNN; F16 GGUF 約 77 MB）。
- **ポリフォニックノートイベント**（`--backend basic-pitch`）—— Spotify Basic Pitch、任意の楽器 → ノートイベント（約 110 KB モデル）。
- **多楽器転写**（`--backend mt3`、エイリアス `music-transcription`）—— MT3 の T5 エンコーダ/デコーダが楽器別プログラムを伴うノートイベントを発行（F16 GGUF 約 96 MB）。
- **Onsets & Frames**（`--backend onsets-and-frames`）—— Hawthorne らのピアノ転写器（MIT）、ここメガバイトあたり最良のソロピアノモデル:
  **MusicNet のピアノ曲でノート F1 69.0%、Basic Pitch の 57.5% に対して**、f32 と Q8_0 では ONNX エクスポートと F1 同一。Q4_0 GGUF 18.6 MiB、Q8_0 30.8 MiB、F32 101.9 MiB。
  [docs/music-transcription/ONSETS_AND_FRAMES.md](docs/music-transcription/ONSETS_AND_FRAMES.md) を参照。
- **hFT-Transformer**（`--backend hft-transformer`）—— Toyama らの階層周波数＝時間トランスフォーマ（MIT）、ここ最精度のソロピアノモデルかつ断トツで最小:
  **MusicNet のピアノ曲でノート F1 70.5%**、5.5 M パラメータから、Q8_0 GGUF 7.0 MiB、Q4_0 4.5 MiB、F32 21.8 MiB。また実行コストが最も高い —— 2 s の音声あたり 249 GFLOP の行列乗算、かつ量子化は int8 ドット積命令のない CPU では速度を*上げる*のではなく*下げる*。`onsets-and-frames` よりこれを選ぶ前に
  [docs/music-transcription/HFT_TRANSFORMER.md](docs/music-transcription/HFT_TRANSFORMER.md) をお読みください。
- 5 つすべてが `--piano-format text|json|midi` を受け取り、`midi` は Standard MIDI File を書き込みます。
- **ギタータブ譜**（`--tab`）—— フレーム単位の弦別フレットグリッドを **TabCNN** 経由で（Wiggins & Kim、ISMIR 2019; 重みは CC BY 4.0）。バックエンドは弦別発火スコアを出力し、確定したタブ譜ではない ——
  `crispasr_session_tab_emissions()` 経由で自前の制約付き Viterbi を実行して演奏可能な出力にしてください。
- **ビート／ダウンビート追跡**（`--beats`）—— ビートグリッドを **Beat This!** 経由で（CPJKU、ISMIR 2024; コード*および*重みに MIT、特許絡みの DBN なし）。
- **コード認識**（`--chords`）—— コードタイムライン（`.lab`）を **BTC**（ISMIR 2019）経由で。重みは CC-BY-NC-SA、`--accept-license cc-by-nc-sa-4.0` のゲートの後ろ。
- **ピッチ / F0 推定**（`--pitch`）—— 単音ピッチトラックを **CREPE**（MIT）経由で。

<a id="feature-matrix"></a>
## 機能マトリクス

`crispasr --list-backends` でライブ表示できます。各バックエンドは実行時にケイパビリティを宣言します; 選択したバックエンドがサポートしない機能を要求すると、CrispASR は警告を表示してそのフラグを静かに無視します。

**ソート／フィルタ可能なビュー:** [`docs/feature-matrix.html`](docs/feature-matrix.html) —— 任意の列ヘッダーをクリックでソート、入力で行をフィルタ、cap ピルをクリックでケイパビリティを必須化。`crispasr --list-backends-json` から生成（単一の信頼源 —— ドリフト不可能）。`python tools/gen-feature-matrix.py` で再生成。Markdown 版は [`docs/feature-matrix.md`](docs/feature-matrix.md) にあります。

下の静的テーブルは、ASR バックエンドと ASR パイプラインで重要な横断的機能に焦点を当てた厳選サブセットです。完全な 119 バックエンド × 27 cap の面は生成ビューにあります。

<!-- Generated from `crispasr --list-backends` + cross-cutting features. -->

| 機能 | whisper | parakeet | canary | cohere | granite | granite&#8209;4.1 | voxtral | voxtral4b | qwen3 | fc&#8209;ctc | wav2vec2 | glm&#8209;asr | kyutai&#8209;stt | firered | moonshine | moon&#8209;stream | omniasr | omniasr&#8209;llm | vibevoice | gemma4&#8209;e2b | mimo&#8209;asr | funasr | paraformer | sensevoice |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| ネイティブタイムスタンプ | ✔ | ✔ | ✔ | ✔ | | | | | | | | | ✔ | | | | | | | | | | | |
| CTC タイムスタンプ | | | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 単語レベルタイミング | ✔ | ✔ | ✔ | ✔ | `-am` | ✔† | `-am` | `-am` | `-am` | `-am` | `-am` | `-am` | ✔ | `-am` | `-am` | `-am` | `-am` | `-am` | | `-am` | `-am` | `-am` | | `-am` |
| トークン単位信頼度 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | |
| 言語自動検出 | ✔ | ✔ | LID | LID | LID | LID | LID | LID | ✔ | LID | LID | ✔ | LID | LID | LID | LID | LID | LID | LID | ✔ | LID | LID | LID | ✔ |
| 音声翻訳 | ✔ | | ✔ | | ✔ | ✔ | ✔ | | ✔ | | | | | | | | | | | | | | | |
| 話者分離 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| グラムマ（GBNF） | ✔ | | | | | | | | | | | | | | | | | | | | | | | |
| 温度サンプリング | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | |
| beams search | ✔ | | | | ✔ | ✔ | ✔ | | ✔ | | | ✔ | ✔ | ✔ | ✔ | | ✔ | ✔ | | | | | | |
| Flash attention | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 句読点トグル | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | ✔ | | ✔ | ✔ | | | | ✔ | | ✔ |
| 句読点復元 | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp |
| ソース／ターゲット言語 | | | ✔ | | ✔ | ✔ | ✔ | | ✔ | | | | | | | | | | | | | | | |
| 音声 Q&A（`--ask`） | | | | | * | * | ✔ | | * | | | * | | | | | | | | * | * | | | |
| ストリーミング | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 自動ダウンロード（`-m auto`） | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| KV 量子化（`CRISPASR_KV_QUANT`、加えて半別 `_K` / `_V`） | | | | | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | | | | | | ✔ | | ✔ | ✔ | ✔ | | |
| mmap ウェイト（`CRISPASR_GGUF_MMAP`） | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| TTS | | | | | | | | | | | | | | | | | | | ✔ | | | | | |

上のマトリクスは 24 の ASR バックエンドをカバーします。**表示されていない追加の ASR バックエンド**: `nemotron`（キャッシュ対応 FastConformer + RNN-T による 39 言語ストリーミング ASR）、`lfm2-audio`（1 モデルで ASR + TTS + S2S）、`moss-audio`（音声理解 + ASR）、`moss-transcribe`（Qwen3-Omni エンコーダ + Qwen3-1.7B ASR）、`hojo-asr`（Qwen3-Omni エンコーダ + Conformer アダプタ + Qwen3-4B 多言語 ASR）、`mini-omni2`（ASR + TTS + S2S）、`kugelaudio`（7B 音声理解）。完全な 109 バックエンドマトリクスは [`docs/feature-matrix.md`](docs/feature-matrix.md) を参照。**TTS 専用バックエンド**（`kokoro`、`qwen3-tts` + 変種、`vibevoice-tts`、`orpheus` + DE 変種、`chatterbox` / `chatterbox-turbo` / `chatterbox-nano` / `kartoffelbox-turbo` / `lahgtna-chatterbox`、`dia`、`bark`、`outetts`、`zonos`、`csm`、`f5-tts`、`irodori-tts`、`supertonic`、`parler-tts`、`speecht5`、`piper`、`fastpitch`、`pocket-tts`、`melotts`、`cosyvoice3`、`voxcpm2`、`tada-tts`）はすべて TTS、AUTO_DOWNLOAD、TEMPERATURE、FLASH_ATTN の cap を持ちます; バックエンド単位のクローン + 音声パック対応は上の [Text-to-Speech モデル](#text-to-speech-models)テーブルと [`docs/tts.md`](docs/tts.md) に記載。vibevoice と lfm2-audio の列はデュアルモード（ASR + TTS）バックエンドを示します。

**凡例:** ✔ = ネイティブ／内蔵、`-am` = CTC 強制アライナ経由（`-am canary-ctc-aligner.gguf` または `-am qwen3-forced-aligner.gguf`）、**LID** = 外部言語識別の前処理ステップ経由（`-l auto`）、**pp** = `--punc-model` ポストプロセッサ経由（FireRedPunc または fullstop-punc）、* = 実験的または部分的サポート、† = PLUS 変種のみ（`-owts` でのネイティブ `[T:N]` 単語タイムスタンプ; base は `-am`）。granite-4.1 は通常と `-plus` の両変種をカバー; granite-4.1-nar はエンコーダ + プロジェクタのみの非自己回帰変種（LLM デコード機能なし）です。**KV 量子化**行は `CRISPASR_KV_QUANT={f16,q8_0,q4_0}` を尊重するバックエンドを示します —— KV キャッシュを持たない CTC スタイルのバックエンド（parakeet、fc-ctc、wav2vec2、kyutai-stt、firered、moonshine 変種、omniasr-CTC）は該当しません。同じバックエンドは、非対称な K と V の精度向けに半別 `CRISPASR_KV_QUANT_K` / `CRISPASR_KV_QUANT_V` オーバーライド（llama.cpp `--cache-type-k` / `--cache-type-v` とのパリティ）も尊重します; 共通のレシピ `K=q8_0 V=q4_0` は対称 Q8_0 より KV メモリを約 40% 節約します。**mmap ウェイト**行は `core_gguf::load_weights()` を消費し、それゆえ `CRISPASR_GGUF_MMAP=1` を尊重するバックエンドを示します; whisper 自体は上流のローダを使い影響を受けません。使用方法 + 推奨の組み合わせは [`docs/cli.md`](docs/cli.md) の Memory footprint を参照。

**話者分離**はポストプロセッシングステップ `--diarize` 経由:
- `energy` / `xcorr` —— ステレオのみ、追加依存なし
- `foxnose` —— **最精度、外部依存なし**: WeSpeaker ResNet34-LM 埋め込み + GMM/BIC 話者数推定 + スペクトルクラスタリング + Viterbi 平滑化。事前に話者数を必要とせず推定する; `--diarize-embedder auto` は GGUF を取得（24 MB、CC-BY-4.0）。VoxConverse dev で 7.3 % DER、`pyannote` + TitaNet は 7.8 %、ターンで採点すると上流参照の 3.07 % に対して 3.18 %（[詳細](docs/architecture.md#foxnose-diarize)）
- `pyannote` —— ネイティブ GGUF（Python なし、sherpa-onnx なし）; `--diarize-embedder auto`（TitaNet）または `--diarize-embedder indextts`（ECAPA-TDNN）を追加すると長いファイル全体でグローバルに安定した話者 ID
- `sherpa` / `ecapa` —— 外部の [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) サブプロセス; 一貫した話者 ID ため全音声上でグローバルに 1 回だけ実行（#110）
- `vad-turns` —— モノ対応のギャップベースプロキシ

サーバーエンドポイントは、正規化された話者文字（A, B, C …）付きの構造化話者ラベル出力のため `response_format=diarized_json` をサポートします —— [`docs/server.md`](docs/server.md#diarized-json-format-206) を参照。

完全なリファレンス + チューニング項目（クラスタ閾値、最大話者数、プラグ可能なエンベッダアダプタ）は [`docs/cli.md#diarization`](docs/cli.md#diarization) を参照。

**ネイティブ LID を持たないバックエンド向けの言語識別**: `--lid-backend whisper`（デフォルト、75 MB ggml-tiny.bin）、`--lid-backend silero`（ネイティブ GGUF、16 MB、95 言語）、または `--lid-backend firered`（FireRedLID、1.7 GB、120 言語 —— Conformer エンコーダ + トランスフォーマデコーダ）。

**音声活性検出**: `--vad` はデフォルトの Silero VAD（約 885 KB、自動ダウンロード）を使用します。各 VAD セグメントは独立して文字起こしされ、正しいタイムスタンプで個別の SRT/VTT エントリを生成します。最良の字幕出力には `--vad --split-on-punct` を使用。4 つの VAD バックエンド: Silero（デフォルト）、FireRedVAD（`-vm firered`、推奨）、MarbleNet（`-vm marblenet`、439 KB、6 言語）、Whisper-VAD-EncDec（`-vm whisper-vad`、実験的）。

**句読点復元**（`--punc-model`）: CTC ベースのバックエンドは句読点なしの小文字で出力します。名前付きショートカット: `auto`/`firered`（中国語 + 英語）、`fullstop`（EN/DE/FR/IT、XLM-R-large）、`punctuate-all`（12 言語、XLM-R-base）、`pcs`（47 言語、1 モデルで句読点 + truecase + 文境界検出）。または GGUF パスを直接渡します。Python/Rust/Dart ラッパ経由でも利用可能（`crispasr.PuncModel`）。

**Truecasing**（`--truecase-model`）: 小文字の ASR 出力でドイツ語の名詞/固有名詞の大文字を復元。品質昇順の 3 択: `auto`（統計的、1.7 MB）、`crf`（コンテキスト付き CRF、8.5 MB）、`lstm`（BiLSTM 文字レベル、3.2 MB、**推奨** —— F1 97.9%、形容詞/名詞の区別と格式ある "Ihnen" を処理）。すべて [`cstr/truecaser-de`](https://huggingface.co/cstr/truecaser-de) から自動ダウンロード。または `--punc-model pcs` で 1 パスのニューラル punc + truecasing（47 言語）。

<details>
<summary>どのバックエンドが句読点をネイティブに生成しますか？</summary>

| バックエンド | 句読点 | 大文字小文字 | 備考 |
|---|:-:|:-:|---|
| whisper | ✔ | ✔ | 完全な句読点と大文字小文字 |
| parakeet | ✔ | ✔ | |
| canary | ✔ | ✔ | |
| cohere | ✔ | ✔ | `--no-punctuation` でトグル可能 |
| granite | ✔ | ✔ | LLM 出力 |
| voxtral | ✔ | ✔ | LLM 出力 |
| voxtral4b | ✔ | ✔ | LLM 出力 |
| qwen3 | ✔ | ✔ | LLM 出力 |
| funasr | ✔ | ✔ | LLM 出力（Qwen3-0.6B デコーダ）。中国語文字は全角ピリオドを伴う; mlt-nano 変種はラテン文字の大文字小文字 + 句読点を追加。 |
| sensevoice | ✔ | ✔ | ネイティブ ITN 付き CTC 出力 —— `--no-punctuation` でオフにでき、アラビア数字 vs 綴り数字 + カンマ/ピリオド発出を制御。 |
| paraformer | **いいえ** | **いいえ** | NAR 文字レベル出力 —— `--punc-model` を追加 |
| gigaam | ✔（`e2e_*`） | ✔（`e2e_*`） | `e2e_*` リビジョンは SentencePiece ボキャブラリに句読点 + 大文字小文字 + 逆テキスト正規化（ITN）を運びます。文字単位の `ctc` / `rnnt` リビジョンは句読点なしのキリル小文字を発行しますが、自動復元は依然として抑制されます —— 自動有効化される FireRedPunc は中国語/英語モデルで、ロシア語に全角 CJK 句読点を注入するからです。句読点付き出力には `e2e_*` リビジョンを使うか、明示的な `--punc-model` を渡してください。 |
| glm-asr | ✔ | ✔ | LLM 出力 |
| kyutai-stt | ✔ | ✔ | LLM 出力 |
| moonshine | ✔ | ✔ | エンコーダ＝デコーダ出力 |
| **fastconformer-ctc** | **いいえ** | **いいえ** | CTC —— `--punc-model` を追加 |
| **wav2vec2** | **いいえ** | **いいえ** | CTC —— `--punc-model` を追加 |
| **firered-asr** | **いいえ** | **いいえ** | CTC —— `--punc-model` を追加 |
| **omniasr**（CTC） | **いいえ** | **いいえ** | CTC —— `--punc-model` を追加 |
| **omniasr**（LLM） | ✔ | ✔ | 自己回帰デコーダ |

追加し得る他の自由にライセンスされた代替: [felflare/bert-restore-punctuation](https://huggingface.co/felflare/bert-restore-punctuation)（MIT、英語、truecasing 同梱）、[xashru/punctuation-restoration](https://github.com/xashru/punctuation-restoration)（Apache-2.0、40+ 言語、BiLSTM-CRF）。

</details>

**プログレッシブ字幕出力**（`--flush-after`）: デフォルトでは、whisper 以外のバックエンドは全セグメントをバッファし最後に出力します。リアルタイム字幕消費（PotPlayer、カスタムメディアプレイヤー）には `--flush-after 1` を使い、各 VAD セグメントの文字起こし直後に SRT エントリを stdout へ即座に出力します:

```bash
crispasr --backend parakeet -m parakeet.gguf --vad --flush-after 1 -osrt -f long_audio.wav
# SRT entries appear progressively as each segment finishes
```

**言語検出付き JSON 出力**: `-l auto -oj` を使用すると、JSON 出力に検出された言語情報が含まれます:
```json
{
  "crispasr": {
    "backend": "cohere",
    "language": "en",
    "language_detected": "en",
    "language_confidence": 0.977,
    "language_source": "ecapa"
  },
  "transcription": [...]
}
```

<a id="which-backend-should-i-pick"></a>
### どのバックエンドを選ぶべき？

| 必要なこと | 選択 |
|---|---|
| 実績、全機能を公開 | **whisper** |
| 最低の英語 WER | **cohere** |
| **最速**（CPU でリアルタイム 16x） | **moonshine**（tiny）、**fc-ctc**（10x） |
| 多言語 + 単語タイムスタンプ + 高速 | **parakeet**（2.9x RT） |
| 多言語で**明示的な言語制御** | **canary** |
| **音声翻訳**（X→en または en→X） | **canary**、**voxtral**、**qwen3** |
| **30 言語 + 中国語方言** | **qwen3** |
| **1600+ 言語** | **omniasr**（CTC または LLM） |
| **リアルタイムストリーミング ASR**（ネイティブ増分エンコーダ、約 2× RT フィード; サブ秒トークンはフェーズ 2 へ延期） | **voxtral4b** |
| 最高品質のオフライン音声 LLM | **voxtral** |
| Apache ライセンスの音声 LLM | **granite**、**voxtral**、**qwen3**、**omniasr-llm** |
| **軽量 CTC のみ**（高速、デコーダなし） | **wav2vec2**、**fc-ctc**、**data2vec**、**omniasr** |
| **ロシア語** | **gigaam**（`e2e_rnnt` —— 平均 WER 8.4 %、句読点 + ITN）、**whisper**、**qwen3** |
| **標準中国語 + 中国語方言** | **firered-asr**、**qwen3**、**glm-asr**、**funasr**、**paraformer**、**sensevoice** |
| **多言語（31 言語）音声 LLM** | **fun-asr-mlt-nano**、**qwen3**、**omniasr-llm**、**gemma4-e2b** |
| **多言語（50+ 言語）+ LID + 1 パスで音声イベント** | **sensevoice**（エンコーダのみ CTC、非 AR、Whisper-Large より 15× 高速） |

### CPU パフォーマンスのコツ

音声 LLM バックエンド（`qwen3`、`voxtral`、`granite`、`glm-asr` など）は完全なトランスフォーマデコーダスタック（28+ 層、2048 次元）を実行するため、エンコーダのみバックエンドより **CPU では劇的に遅く**なります。古いデュアルコアハードウェアでは 0.01× リアルタイム以下に落ちることもあります。CPU のみのハードウェアなら:

- 実用的な速度のため **moonshine**（16× RT）、**fc-ctc**（10× RT）、**parakeet**（2.9× RT）、
  または **whisper** を優先してください。
- ファイル全体を待つ代わりに、各 VAD スライス完了時に結果を見るため `--flush-after 1` を使用。
- すべてのバックエンドでスライス単位の進行状況を表示するため `-pp` / `--print-progress` を使用
  （統合バックエンドはスライス単位の進行、whisper はエンコーダ単位の進行を表示）。
- メモリと計算を減らすためモデルを Q4_K または Q5_K に量子化。

### ネイティブに言語検出しないバックエンド向けの言語検出

Cohere、canary、granite、voxtral、voxtral4b は事前に明示的な言語コードを必要とします。
言語が不明な場合、`-l auto` を渡すと crispasr は主な transcribe() 呼び出しの前に
オプションの LID 前処理を実行します:

```bash
# 初回使用時に ggml-tiny.bin（75 MB、99 言語）をダウンロード
crispasr --backend cohere -m $TC/cohere-transcribe-q5_0.gguf \
         -f unknown.wav -l auto
# crispasr[lid]: detected 'en' (p=0.977) via whisper-tiny
# crispasr: LID -> language = 'en' (whisper, p=0.977)
```

これらの LID プロバイダが利用可能です:

- `--lid-backend whisper`（デフォルト）—— crispasr C API 経由で小さな多言語 ggml-*.bin モデルを使用。初回使用時に約 75 MB を自動ダウンロード。99 言語。
- `--lid-backend silero` —— Silero の 95 言語分類器のネイティブ GGUF ポート。16 MB F32。ggml グラフとして実行（CPU ではマルチスレッド SIMD、Metal/CUDA では GPU オフロード; Vulkan では上流カーネル修正待ちのためグラフは CPU へルーティング）。音声の先頭 30 s を解析（`CRISPASR_SILERO_LID_MAX_S` で上書き）; `CRISPASR_SILERO_LID_LEGACY=1` で旧スカラーパスを復元。
- `--lid-backend ecapa` —— **推奨**: ECAPA-TDNN（Apache-2.0）。言語 ID 専用に設計。TTS ベンチマークで非常に高い精度。`--lid-model` 経由の 2 変種:
  - [`cstr/ecapa-lid-107-GGUF`](https://huggingface.co/cstr/ecapa-lid-107-GGUF) —— VoxLingua107、43 MB F16、107 言語、ISO コード（en, de, ...）。**デフォルト。**
  - [`cstr/ecapa-lid-commonlanguage-GGUF`](https://huggingface.co/cstr/ecapa-lid-commonlanguage-GGUF) —— CommonLanguage、40 MB F16、45 言語、正式名（English, German, ...）。
- `--lid-backend firered` —— FireRedLID（Conformer エンコーダ + トランスフォーマデコーダ）。Q4_K（544 MB）、中国語方言を含む 120 言語。遅いがより多くの言語をカバー。
- `--lid-backend probe` —— 第 2 のモデルを一切使わない: **ASR モデル自身**に尋ねます。モデルが宣言する言語ごとに 20 s クリップを 1 回文字起こしし、最高スコア候補（長さ × テキスト LID 一致 × 語数比²、最後の項は誤言語プロンプトが生む反拍出力を捉える）を保持。現在 **cohere** が実装。優先する理由は速度ではなく正確性 —— 外部検出器は 99 言語を知るが Cohere Transcribe は 14 を受け付け、そのアラビア語ファインチューンは `en`/`ar` のみ —— よって外部 LID はモデルが訓練されていない言語を高頻度で返し、Cohere は誤言語に対して失敗ではなく*流暢に*答えます。probe はそれができません。コストは候補あたり 1 エンコード + 1 短いデコードなので、言語数が 4 以下のモデルでのみ自動実行（`CRISPASR_COHERE_PROBE_MAX_LANGS`）; `CRISPASR_COHERE_PROBE_TEXTLID=0` でテキスト LID 一致項を削除。

  **上限は精度ではなくコストについてです。** 実モデルで測定: 2 言語のアラビア語ファインチューンはアラビア語クリップで `ar`（p=0.675）、`samples/jfk.wav` で `en`（p=0.647）を選択; 14 言語ベースモデルを 14 すべてで probe すると両方正解（`en` p=0.169、`ar` p=0.254）—— 単に外部検出器より遅いだけです。エンコーダ出力は言語非依存なので、probe は**1 回**エンコードし候補ごとにデコード（エンコードは 1 パスの約 87 %）; 14 候補 probe は候補ごとエンコードに対し **12 s → 4-5 s**、バイト単位同一の出力。`CRISPASR_COHERE_PROBE_REUSE_ENC=0` で素朴なパスを復元。

  知る価値のある唯一の弱点: モデルが訓練されていない言語を要求すると、ゴミではなくクリーンな翻訳が得られ得る —— テキスト LID はそれを確認します、「流暢なフランス語出力」はフランス語入力の証拠ではない。これが不一致のホワイトリストを危険にする点で、測定可能です: 2 言語のアラビア語ファインチューンに 14 言語リストを強制すると、その `fr` probe は本物のフランス語を返し勝ちます。実ベースモデルの `fr` probe はコードスイッチングし（"Et so, my fellow Americans…"、一致 0.00）、あるべきように負けます。

これらの VAD プロバイダが利用可能です:

- **Silero VAD**（デフォルト）—— 約 885 KB、`--vad` 経由で自動ダウンロード。業界標準、十分にテスト済み。
- **FireRedVAD** —— DFSMN ベース、2.4 MB、F1=97.57%。`--vad -vm firered` を渡すと自動ダウンロード。推奨。
- **MarbleNet** —— NVIDIA 1D 分離 CNN、439 KB、6 言語（EN/DE/FR/ES/RU/ZH）。`--vad -vm marblenet` で自動ダウンロード。最小モデル。（[`cstr/marblenet-vad-GGUF`](https://huggingface.co/cstr/marblenet-vad-GGUF)）
  - ⚠ **既知の不具合。** その forward は長さに依存 —— フレームの logits が*合計*クリップ長さで変化、そのグラフのどの層も正当にできない（すべて same-padding conv または 1×1 linear）。CPU と CUDA は 6 桁一致、よってグラフか ggml スケジューラの不具合でカーネルではない。影響: `-vm marblenet` はほぼ空または誤ったスライス一覧を返し、VAD フェイルオーバーが静かに全クリップチャンクへフォールバック。再現は `src/marblenet_vad.cpp` の `mbn_forward` 上のノート参照。Silero または FireRedVAD を使用。
- **Whisper-VAD-EncDec** *（実験的）* —— Whisper-base エンコーダ + TransformerDecoder ヘッド、22 MB Q4_K。日本語 ASMR で訓練; 全ドメインに汎化しない可能性。`--vad -vm whisper-vad`。他より遅い（約 1s vs 約 50ms）。（[`cstr/whisper-vad-encdec-asmr-GGUF`](https://huggingface.co/cstr/whisper-vad-encdec-asmr-GGUF)）

**デバイスとバッチング。** Silero、FireRedVAD、MarbleNet はデバイスとバッチサイズを取ります: `--vad-gpu`（または `CRISPASR_VAD_GPU=cuda|vulkan|metal`）と `--vad-batch N`。570 s クリップ / GTX 1050 Ti での測定（全行でスパンはバイト単位同一）:

| VAD | CPU | GPU | 備考 |
|---|---|---|---|
| FireRedVAD | 36.8 s | **2.7 s** | 13.6×; グラフパスは完全な ggml DFSMN |
| Silero | 5.7 s | 8.9 s | launch-bound —— 32 ms ウィンドウあたり約 83 グラフノード |
| MarbleNet | 2.1 s | — | 下の警告を参照 |

FireRedVAD は GPU が明確に報われる唯一のもので、CPU では桁違いに最も遅い VAD —— それがオフロードする価値がある理由。Silero の GPU パスは完全性のためのもので速度のためではない: その LSTM 再帰は逐次的なので `--vad-batch` は仕事を統合できず、グラフ境界をより大きなグラフと交換するだけ（測定: 幅 1 で 2.73 s、幅 512 で 3.89 s）。よってデフォルトは 1 —— 既存のウィンドウごと 1 グラフの挙動。

Silero の `batch_size` は **64 で上限**; 以上を要求すると警告を表示し 64 を使用。上限はモデルの性質ではなくメモリ制限 —— Silero は任意のバッチで動作しバッチングは任意のバッチで厳密。それはバッチ済みグラフの表現方法とランタイムの計上方法に起因: B ウィンドウをアンロールするとグラフは 83×B ノードになり、ggml のスケジューラは `context_buffer` を `graph_size × 30 × 2 × sizeof(ggml_tensor)` で eager に malloc する、つまりグラフノードあたり約 24.8 KB のコミット課金 —— バッチ 1 で 507 MB、64 で 657 MB、512 で 1.7 GB、4096 で約 9 GB。より広いグラフはここで*遅い*ので、上限により失われるものはない。

FireRedVAD と MarbleNet にそうした上限は不要: それらはフレーム軸をアンロールではなく分割するため、グラフのノード数は固定で、アクティベーションメモリのみバッチで増加。FireRedVAD は 32768 フレームまで検証済み（570 s クリップ: GPU で 3.70 s、43 スパン、他の全幅とバイト単位同一）。WebRTC VAD はモデルファイルのない GMM で常に CPU で実行。

バッチングは答えを変えません。Silero は N LSTM ステップを 1 グラフへアンロール（再帰は逐次なので、これは N× 少ない launch で同じ演算）。FireRedVAD と MarbleNet はフレーム軸を、モデルの受容野のコンテキストを運ぶブロックへ分割し、ブロック端に依存する出力を破棄 —— FireRedVAD ではこれが ggml の conv ごと im2col 行列（T × N × P 浮動小数、10 分ファイルで 1 conv 約 580 MB）を有界に保つ所以でもある。

VAD 実行中は進行状況を stderr へ 1 秒に 1 行表示します。モデルはアトミックカウンタを更新するだけで、バックグラウンドスレッドがそれをサンプリングするため、ホットループは I/O に触れません。`CRISPASR_VAD_PROGRESS=0` で沈黙、`CRISPASR_VAD_PROGRESS_MS` で周期変更。

`--lid-backend off` を渡すと LID を完全にスキップ。

### テキスト言語識別（ASR 後 / スタンドアロン）

音声 LID（上）は**話された内容**をタグ付けし、テキスト LID は**書かれた内容**をタグ付けします。テキスト LID はトランスクリプトまたは任意の UTF-8 文字列上で動作し、音声モデルを再実行せずに ASR 後パイプライン（翻訳、句読点、サブタイトル選択）をルーティングするのに有用です。3 つの GGUF ファミリー、1 バイナリ —— ディスパッチャは `general.architecture` で選択します:

| バックエンド | ラベル | サイズ（F16） | ライセンス | HF repo |
|---|---:|---:|---|---|
| **CLD3**（Google compact language detector v3） | 109 ISO 639-1 | **440 KB** | Apache-2.0 | [`cstr/cld3-GGUF`](https://huggingface.co/cstr/cld3-GGUF) |
| **GlotLID-V3**（cis-lmu fastText） | 2102 ISO 639-3 + スクリプト | 250 MB | Apache-2.0 | [`cstr/glotlid-GGUF`](https://huggingface.co/cstr/glotlid-GGUF) |
| **LID-176**（Facebook fastText） | 176 ISO 639-1 | 63 MB | CC-BY-NC-4.0¹ | [`cstr/fasttext-lid176-GGUF`](https://huggingface.co/cstr/fasttext-lid176-GGUF) |

¹ LID-176 は **CC-BY-NC-4.0** —— 非商業用途のみ。CLD3 + GlotLID-V3 は Apache-2.0 でそうした制約なし。最小・最速パスなら CLD3;最大カバレッジ（低リソース言語）なら GlotLID;固有の 176 ラベル空間が必要で非商業条件を受け入れる場合のみ LID-176。

**スタンドアロン CLI** —— GGUF arch で自動ルーティング、自動ダウンロード付き:

```bash
crispasr-lid -m auto --text "Bonjour le monde"        # → cstr/cld3-GGUF（デフォルト、約 440 KB）
crispasr-lid -m auto:glotlid --text "Bonjour le monde" -k 5
crispasr-lid -m auto:lid-fasttext176 --text "Hallo Welt"
# または明示的なパス / 正規ファイル名（レジストリで検索）を渡す:
crispasr-lid -m cld3-f16.gguf --text "你好世界"
# zh	0.997816
echo "Привет мир" | crispasr-lid -m auto --quiet
# ru	0.907322
```

**ASR 後パイプライン** —— `--lid-on-transcript` は組み上がったトランスクリプトに同じディスパッチャを実行（`auto[:variant]` も受付）:

```bash
crispasr -m ggml-tiny.bin -f speech.wav --lid-on-transcript auto
# (transcript on stdout)
# lang=de	conf=0.997123	backend=lid-cld3
```

ディスパッチャ（`src/text_lid_dispatch.{h,cpp}`）は薄い C ABI ファーサード —— 呼び出しあたり整数比較 1 回; ステージ別 diff ハーネスは 8 つの多言語スモークサンプルで cos≥0.999 グリーン。

---

<a id="install--build"></a>
## インストールとビルド

**ビルドしたくない場合?** Windows、macOS、Linux 向けのプリビルドバイナリは
[releases ページ](https://github.com/CrispStrobe/CrispASR/releases/latest) にあります ——
どのファイルを取得するかは [ここから始める](#start-here) を参照。このセクションの残りはソースからビルドする場合向けです。

```bash
git clone --recursive https://github.com/CrispStrobe/CrispASR
cd CrispASR
# --recursive なしでクローンした場合? 同梱の ggml サブモジュールを初期化:
#   git submodule update --init --recursive
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

`ggml/` サブモジュールは必須です。`--recursive` なしでクローンした場合、まず
`git submodule update --init --recursive` を実行してください —— そうでなければ CMake は、まさにそのことを伝えるメッセージで停止します。

`build/bin/crispasr`（メイン CLI）、`build/bin/crispasr-quantize`、
`build/bin/crispasr-diff` を生成します。ランタイムに Python、PyTorch、pip は不要 ——
C++17 コンパイラと CMake 3.14+ だけです。

GPU アクセラレーションのため、configure 時に対応する ggml フラグを追加します:

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON     # NVIDIA
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON    # Apple Silicon
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_VULKAN=ON   # クロスベンダー
```

**[`docs/install.md`](docs/install.md)** に完全なガイドを参照:
すべての GPU バックエンド（CUDA / Metal / Vulkan / MUSA / SYCL）、Windows
用 Convenience スクリプト、ffmpeg 取り込み、オプションの BLAS、glibc ノート、
そして `scripts/dev-build.sh` ラッパ。

ビルドが通ってもバイナリが出力なしで終了する場合、
[`docs/troubleshooting.md`](docs/troubleshooting.md) を参照。

---

<a id="quick-start"></a>
## クイックスタート

より詳しい ASR の例は下記。初回実行なら代わりに
[ここから始める](#start-here) を使用してください。TTS の実行可能ガイドは
[docs/tts.md](docs/tts.md)（下の [Text-to-Speech](#text-to-speech-models) は
モデルカタログです）。

### Whisper（歴史的パス、上流 whisper.cpp とバイト単位同一）

```bash
# whisper モデルをダウンロード（上流 whisper.cpp と同じ）
./models/download-ggml-model.sh base.en

./build/bin/crispasr -m models/ggml-base.en.bin -f samples/jfk.wav
# [00:00:00.000 --> 00:00:07.940]   And so my fellow Americans ask not what your country can do for you
# [00:00:07.940 --> 00:00:10.760]   ask what you can do for your country.
```

### Parakeet（多言語、無料の単語タイムスタンプ、最速）

```bash
# 量子化モデルを取得（約 467 MB）
curl -L -o parakeet.gguf \
    https://huggingface.co/cstr/parakeet-tdt-0.6b-v3-GGUF/resolve/main/parakeet-tdt-0.6b-v3-q4_k.gguf

./build/bin/crispasr -m parakeet.gguf -f samples/jfk.wav
# Auto-detected backend 'parakeet' from GGUF metadata.
# And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.

# 単語レベルタイムスタンプ（単語ごとに 1 行）
./build/bin/crispasr -m parakeet.gguf -f samples/jfk.wav -ml 1
```

### Canary（明示的な言語、音声翻訳）

```bash
# 文字起こし（ソース == ターゲット）
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -sl de -tl de

# 翻訳（ドイツ語音声 → 英語テキスト）
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -sl de -tl en

# ...またはお馴染みの crispasr フラグを使用:
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -l de --translate
```

### Voxtral（自動ダウンロード付き音声 LLM）

```bash
# 初回実行は約 2.5 GB を ~/.cache/crispasr/ へ curl でダウンロード後実行
./build/bin/crispasr --backend voxtral -m auto -f samples/jfk.wav

# 以降の実行はキャッシュ済みファイルを使用
./build/bin/crispasr --backend voxtral -m auto -f samples/jfk.wav -l en
```

### Qwen3-ASR（30 言語 + 中国語方言）

```bash
# 0.6B（デフォルト、約 500 MB）
./build/bin/crispasr --backend qwen3 -m auto -f audio.zh.wav

# 1.7B（高品質、約 1.3 GB）—— -hf と非 -hf の両ソースモデルをサポート
./build/bin/crispasr --backend qwen3 -m qwen3-1.7b --auto-download -f audio.wav

# 日本語アニメ/ギャルゲファインチューン（約 1.3 GB）
./build/bin/crispasr --backend qwen3 -m qwen3-ja-anime --auto-download -f anime.wav
```

**長尺音声:** デフォルトは安全な 30 s チャンク。`--chunk-seconds 0` はファイル全体を
1 パスでデコード（複数分クリップで参照モデルと一字一句一致、#218）—— ただしエンコーダの
完全 attention は音声長の O(N²) なので、16 GB マシンでは単一パスクリップを約 10 分以内に
保ってください。長尺用途はモデルカードにある通り `-imatrix` 変種より素の `-q4_k`/`-q8_0` GGUF を優先。

### GLM-ASR-Nano（標準中国語 + 方言 + 広東語 + 英語、1.5B）

```bash
./build/bin/crispasr --backend glm-asr -m auto -f audio.wav

# 1 パスでの長尺音声（最大 655 s —— 30 s エンコーダウィンドウ、1 LLM プロンプト、
# HF/zai 参照と同じレイアウト; #218 クリップで一字一句一致）:
./build/bin/crispasr --backend glm-asr -m auto --chunk-seconds 0 -f long.wav
```

注意: 単一パスモードではモデル（参照と同じく）先頭の非音声音声をスキップします;
デフォルトの 30 s チャンクモードはそうしたクリップをより多く文字起こしします。
カスタム `--ask` / 非英語 `--language` の指示は、ベークド BPE マージを備えた GGUF が
必要です（2026-07 に再公開; 古い GGUF はデフォルトの文字起こしプロンプトへ警告付きでフォールバック）。

### MiMo-V2.5-ASR（標準中国語 + 方言 + 英語、7.5B Qwen2 LM）

```bash
# LM + 音声トークナイザ（トークナイザは別のモデル）をダウンロード
huggingface-cli download cstr/mimo-asr-GGUF mimo-asr-q4_k.gguf \
    --local-dir ~/.cache/crispasr
huggingface-cli download cstr/mimo-tokenizer-GGUF mimo-tokenizer-q4_k.gguf \
    --local-dir ~/.cache/crispasr

# 文字起こし（LM の隣にあればトークナイザを自動発見）
./build/bin/crispasr \
    --backend mimo-asr \
    -m ~/.cache/crispasr/mimo-asr-q4_k.gguf \
    --codec-model ~/.cache/crispasr/mimo-tokenizer-q4_k.gguf \
    -f samples/jfk.wav
# Output: And so, my fellow Americans, ask not what your country can do
# for you. Ask what you can do for your country.
```

4.5 GB の Q4_K が推奨量子化; F16（14.9 GB）は推論中約 16 GB の RAM を必要。
JFK は上流 Python の `MimoAudio.asr_sft` 参照と一字一句一致; M1+Metal でのパフォーマンスは
約 0.3× リアルタイム（Q4_K のステップ時逆量子化がボトルネック —— F16 + KV 再利用の
フォローアップは PLAN #51a/b/c のキュー入り）。

### Wav2Vec2（軽量 CTC、任意の HF Wav2Vec2ForCTC モデル）

```bash
# 英語（Q4_K 量子化、212 MB —— F16 より 6 倍小さい）
curl -L -o wav2vec2-en-q4k.gguf \
    https://huggingface.co/cstr/wav2vec2-large-xlsr-53-english-GGUF/resolve/main/wav2vec2-xlsr-en-q4_k.gguf

./build/bin/crispasr -m wav2vec2-en-q4k.gguf -f samples/jfk.wav
# and so my fellow americans ask not what your country can do for you ask what you can do for your country

# ドイツ語
curl -L -o wav2vec2-de-q4k.gguf \
    https://huggingface.co/cstr/wav2vec2-large-xlsr-53-german-GGUF/resolve/main/wav2vec2-xlsr-de-q4_k.gguf

./build/bin/crispasr -m wav2vec2-de-q4k.gguf -f audio.de.wav

# 任意の HuggingFace Wav2Vec2ForCTC モデルを変換:
python models/convert-wav2vec2-to-gguf.py \
    --model-dir jonatasgrosman/wav2vec2-large-xlsr-53-german \
    --output wav2vec2-de.gguf --dtype f32
# その後オプションで量子化:
./build/bin/crispasr-quantize wav2vec2-de.gguf wav2vec2-de-q4k.gguf q4_k
```

---

## ストリーミング、TTS、HTTP サーバー

CrispASR には独自のドキュメントページを必要とする 3 つの機能領域があります:

- **[ストリーミングとライブ文字起こし](docs/streaming.md)** —— `--stream`、
  `--mic`、`--live`、スライディングウィンドウチャンク、トークン単位信頼度。
- **[Text-to-Speech (TTS)](docs/tts.md)** —— Kokoro（多言語、最小）、Qwen3-TTS（最高忠実度、ボイスクローン）、VibeVoice
  （最低遅延ストリーミング）、Orpheus（3 B Llama + SNAC）、Chatterbox
  （flow-matching + HiFT ボコーダ、Kartoffelbox 経由でドイツ語）、IndexTTS、
  VoxCPM2、CosyVoice3（9 言語 + 18 の zh 方言; ベークド音声バンク +
  任意 WAV クローン）。音声パック、言語ルーティング、qwen3-tts
  環境スイッチ。すべての TTS 出力はウォーターマーク付き; 埋め込み後
  検証で信頼度が低い場合警告します。任意の WAV の AI ウォーターマークを確認するには
  `--detect-watermark file.wav` を使用。
- **[サーバーモード（HTTP API）](docs/server.md)** —— 永続モデル、
  OpenAI 互換の `/v1/audio/transcriptions`（ASR）と
  `/v1/audio/speech` + `/v1/voices`（TTS、読み込んだ CAP_TTS バックエンドで自動有効）、
  リクエスト単位の音声 + 速度 + 指示、CORS、
  長尺文チャンク化、API キー、Docker Compose、プリビルド
  CUDA イメージ。
- **[並行性・並列化・スケーリング](docs/concurrency.md)** —— 1 回の
  文字起こしはすでに複数コアを使用; サーバーはリクエストを並行して受け付けるが
  デフォルトでは 1 モデル上の推論を直列化;
  `--server-workers N` は N モデルインスタンスを実行し純 ASR リクエストを
  並行実行; バッチ/スループットワークロードでは、プロセレベルのファンアウト
  （`xargs -P` / GNU `parallel`）またはロードバランサー後の N レプリカ。また
  サポートされていないもの（バッチ化マルチストリーム推論、
  PagedAttention）とその理由もカバー。

各最も素早く試す:

```bash
# マイクからストリーミング
crispasr --mic -m model.gguf

# 自動ダウンロードの VibeVoice 経由で TTS（初回実行で約 636 MB）
crispasr --backend vibevoice-tts -m auto --tts "Hello world" --tts-output hello.wav

# GPU 上の CosyVoice3; 同伴は LLM の隣に自動ダウンロード
crispasr --backend cosyvoice3-tts -m auto --tts "Hello world" --tts-output cosy.wav

# CosyVoice3 高速モード: 品質デフォルトの 10 ではなく 5 flow ステップ
COSYVOICE3_FLOW_STEPS=5 crispasr --backend cosyvoice3-tts -m auto \
  --tts "Hello world" --tts-output cosy-fast.wav

# 永続 HTTP サーバー、OpenAI 互換
crispasr --server -m model.gguf --port 8080
curl -F "file=@audio.wav" http://localhost:8080/v1/audio/transcriptions

# HTTP 経由の TTS —— TTS バックエンドを読み込み、/v1/audio/speech を hits
crispasr --server --backend qwen3-tts-customvoice -m auto --voice-dir ./voices --port 8080
curl http://localhost:8080/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"input":"Hello world","voice":"vivian"}' -o out.wav
```

CosyVoice3 はデフォルトでバッチ化 classifier-free guidance とリクエストサイズ KV
キャッシングを使用します。ベークド音声は LLM、flow、HiFT、音声バンクのみ読み込み;
より大きな S3 トークナイザと CAMPPlus 同伴は `.wav` クローン音が最初に
要求された時に遅延読み込みされます。

---

## CLI リファレンス

よく使うフラグ:

```bash
crispasr -m auto --backend parakeet -f audio.wav --vad -osrt --split-on-punct
```

| フラグ | 意味 |
|---|---|
| `-m FNAME` / `--backend NAME` | モデルパス（または `auto`）と強制バックエンド |
| `-f FNAME` | 入力音声（繰り返し可; 位置引数も受付） |
| `--vad` | Silero VAD チャンク —— 数分音声に強く推奨 |
| `-osrt` / `-ovtt` / `-otxt` / `-oj` / `-ojf` | 出力フォーマット（`-ocsv`、`-olrc` も） |
| `-am FNAME` | LLM バックエンドで単語レベルタイムスタンプ用的 CTC アライナ GGUF |
| `--align-only` | スタンドアロン強制アライメント: テキスト/`.srt` + 音声 → タイムスタンプ付き SRT/JSON（ASR 不要）; `.srt` 入力はキュー保持で再タイミング（`--align-granularity auto\|word\|segment`） |
| `-tp F` / `-bs N` | サンプリング温度 / beams search 幅 |
| `-n N` / `--frequency-penalty F` | 生成トークン上限 / 対応する自己回帰 ASR バックエンド向けのオプトインな反復トークンペナルティ |
| `-l auto` / `--detect-language` | ネイティブの言語検出を持たないバックエンド向けの LID 前処理 |
| `--hotwords "A,B,C"` | 文脈バイアス —— CTC/TDT デコードまたは LLM プロンプト中の固有名詞をブースト |
| `-ck N` | VAD オフ時のフォールバックチャンクサイズ（デフォルト 30 s） |
| `--list-backends` | ケイパビリティマトリクスを表示して終了 |

**[`docs/cli.md`](docs/cli.md)** に完全なリファレンス: あらゆる
フラグ、VAD 詳細、CTC アライメントワークフロー、出力 JSON レイアウト、
自動ダウンロードレジストリ、サポートされる音声フォーマット。**[`docs/bindings.md`](docs/bindings.md)**
は Python / Rust / Dart / Go / Java / JavaScript / Ruby / モバイル。

---

## アーキテクチャ、コントリビューティング、リグレッションマトリクス

CrispASR は `src/` の安定した C-ABI（あらゆるアルゴリズム:
VAD、分離、LID、アライメント、キャッシュ、レジストリ）をすべての
言語ラッパが消費し、`examples/cli/` に薄いプレゼンテーションレイヤを置く
構造です。モデル別のランタイムは `src/{whisper,parakeet,canary,...}.cpp` にあり、
`src/core/` のプリミティブ（mel、ffn、attention、GGUF
ローダ、FastConformer / Conformer / Granite-LLM ブロックなど）を共有します。

- **[`docs/architecture.md`](docs/architecture.md)** —— 完全な層状
  レイアウト、`src/` と `examples/cli/` のファイル別ツアー、
  バックエンド内部テーブル、リグレッション規律。
- **[`docs/contributing.md`](docs/contributing.md)** —— 5 ファイルで
  新しいバックエンドを追加、clang-format-18 セットアップ、
  `crispasr-diff` PyTorch グラウンドトゥルースワークフロー、そして
  TTS 音声コサイン vs 参照のリグレッションターゲット。
- **[`docs/regression-matrix.md`](docs/regression-matrix.md)** ——
  `tools/test-all-backends.py` のケイパビリティ階層、キャッシュモード
  （`keep` / `ephemeral`）、CI 向けの `--skip-missing`。

**共有ライブラリ**（CrispEmbed とのクロスリポジトリ）:
- `crisp_audio/` —— Whisper-shape 音声エンコーダ（Conv-stem + トランスフォーマ）
- `crisp_punc/` —— 句読点復元（FireRedPunc + PCS）
- `crisp_lid/` —— テキストベースの言語識別（fastText + CLD3）
- `crisp_truecase/` —— truecasing（統計 + CRF + BiLSTM）

両者とも CMakeLists.txt を備えた自己完結の静的ライブラリ。CrispEmbed は
`add_subdirectory(../CrispASR/crisp_*/)` 経由でリンク; CrispASR は直接使用。
共有ディレクトリが存在しない場合、両リポジトリともソースファイルの
ローカルコピーへフォールバックします。

ベンチマークは [`PERFORMANCE.md`](PERFORMANCE.md); セッション別の
ポートログとバグクラスの教訓は [`LEARNINGS.md`](LEARNINGS.md) を参照。

---

## モデルの量子化

`build/bin/crispasr-quantize` は、サポートされる全モデルファミリー
（Whisper、Parakeet、Canary、Cohere、Voxtral、Qwen3、Granite、Wav2Vec2、
MiMo-ASR、GLM-ASR、Moonshine、VibeVoice、Kokoro、Qwen3-TTS、…）で動作する
単一のモデル非依存 GGUF 再量子化ツールです:

```bash
./build/bin/crispasr-quantize input.gguf output.gguf q4_k
```

**[`docs/quantize.md`](docs/quantize.md)** に完全なガイド:
サポートされる量子化タイプ、K-quant アライメントフォールバック、
バックエンド別の推奨量子化、そしてアーキテクチャ別の作例。

---

<a id="gpu-backend-selection"></a>
## GPU バックエンド選択

すべてのバックエンドは `ggml_backend_init_best()` を使い、最も優先度の高いコンパイル済みバックエンドを自動選択: CUDA > Metal > Vulkan > CPU。特定のバックエンドを強制するには:

```bash
# CUDA が利用可能でも Vulkan を強制
crispasr --gpu-backend vulkan -m model.gguf -f audio.wav

# 特定の GPU をピン留め（iGPU + dGPU の Vulkan システムで有用）
crispasr --gpu-backend vulkan -dev 1 -m model.gguf -f audio.wav

# CPU を強制（ベンチマークに有用）
crispasr -ng -m model.gguf -f audio.wav

# CUDA 統一メモリ（VRAM 枯渇時に RAM へスワップ）
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 crispasr -m model.gguf -f audio.wav
```

ビルドフラグ: `-DGGML_CUDA=ON`、`-DGGML_METAL=ON`、`-DGGML_VULKAN=ON`。

備考:
- `--gpu-backend vulkan` は Vulkan バックエンドを選択しますが、どの物理 GPU を使うかは選びません。Vulkan デバイスインデックスを選ぶには `-dev N` を使用。
- 一部の Windows ノートPCでは、Vulkan デバイス `0` が Intel iGPU で NVIDIA GPU が `1` です。Vulkan が想定外に遅く見える場合、`-dev 1` で再実行。
- Windows 用 Convenience スクリプト `build-vulkan.bat` は `build-vulkan\bin\crispasr.exe` に Vulkan 対応バイナリを別作成します。

---

<a id="debugging--profiling"></a>
## デバッグとプロファイリング

ほとんどのバックエンドで、`-v` / `--verbose` はステージ別のタイミングとデバイス選択を表示します。ヘッドレス / ライブラリ利用（CLI フラグが通らない場合）では、代わりに `CRISPASR_VERBOSE=1` を設定。

```bash
# ステージ別のタイミング内訳（mel / encoder / prefill / decode）:
crispasr -v --backend gemma4-e2b -m model.gguf -f audio.wav
# gemma4_e2b: mel 128x1099 (17.2 ms)
# gemma4_e2b: encoder done: 1536x275 (719.0 ms)
# gemma4_e2b: prefill done, first_token=3133 (1464.0 ms)
# gemma4_e2b: decoded 25 tokens (7748.3 ms total)
# crispasr: transcribed 11.0s audio in 7.75s (1.4x realtime)

# ゲート付きモデルへの Hugging Face アクセス（Voxtral、Gemma4-E2B、…）:
HF_TOKEN=hf_xxx crispasr -m auto --backend gemma4-e2b -f audio.wav
```

サーバーには独自認証環境変数 `CRISPASR_API_KEYS` があります（
[サーバーモード](docs/server.md) 参照）。

<details>
<summary><b>バックエンド別のデバッグ / ベンチ / ダンプディレクトリ環境変数（開発者向け）</b></summary>

これらは新しいバックエンドのポートやリグレッション追跡時に有用です。
`*_BENCH=1` トグルは `-v` なしでもステージ別のタイミングを発行; `*_DEBUG=1`
トグルはステップ別の診断表示を発行; `*_DUMP_DIR=` パスは PyTorch 参照への
diff 測試用にステージ別 F32 テンソルを書き込みます（[Debug a new backend against PyTorch ground truth](docs/contributing.md#debug-a-new-backend-against-pytorch-ground-truth) 参照）。

| 環境変数 | 目的 |
| --- | --- |
| `CRISPASR_VERBOSE=1` | 任意のバックエンドで詳細モードを強制（`-v` フラグと並列）。 |
| `CRISPASR_DUMP_DIR=path/` | `crispasr-diff` ハーネス向けの汎用ステージ別 F32 テンソルダンプ。 |
| `GEMMA4_E2B_BENCH=1` | Gemma-4-E2B バックエンドのステージ別タイミング。 |
| `COHERE_BENCH=1` / `COHERE_DEBUG=1` | Cohere transcribe のステージ別タイミング / ステップ別診断。 |
| `COHERE_PROF=1` | Cohere のグラフレベルプロファイリング（オペ別タイミング）。 |
| `COHERE_THREADS=N` | Cohere バックエンドのスレッド数を上書き。 |
| `COHERE_DEVICE=cpu\|cuda\|metal\|vulkan` | Cohere バックエンドを特定デバイスへ強制。 |
| `COHERE_DUMP_ATTN=path/` | Cohere の attention 活性をダンプ（diff ハーネスで使用）。 |
| `FIRERED_BENCH=1` | FireRedASR バックエンドのステージ別タイミング。 |
| `FIREREDPUNC_DEBUG=1` | FireRed 句読点ポストステップのステップ別診断。 |
| `MOONSHINE_STREAMING_BENCH=1` | moonshine-streaming のステージ別タイミング。 |
| `OMNIASR_BENCH=1` / `OMNIASR_DEBUG=1` / `OMNIASR_DUMP_DIR=` | OmniASR のステージ別タイミング、診断、ステージダンプ。 |
| `PARAKEET_DEBUG=1` | Parakeet TDT のステップ別診断（joint ネットワーク、blank-id サニティ）。 |
| `QWEN3_TTS_BENCH=1` / `QWEN3_TTS_DEBUG=1` / `QWEN3_TTS_DUMP_DIR=` | Qwen3-TTS のステージ別タイミング、診断、ステージダンプ。 |
| `VIBEVOICE_BENCH=1` / `VIBEVOICE_DEBUG=1` / `VIBEVOICE_DUMP_DIR=` | VibeVoice ASR のステージ別タイミング、診断、ステージダンプ。 |
| `VIBEVOICE_REF_FEATURES=path` | 保存済み特徴テンソルでライブエンコーダを置換（リグレッションハーネス）。 |
| `VIBEVOICE_TTS_DUMP=path/` | VibeVoice TTS のステージ別ダンプ（トークン ID、base/TTS 隠れ層、neg 条件、frame-0 noise/v_cfg/latent/acoustic_embed）を diff ハーネス用。 |
| `VIBEVOICE_TTS_DUMP_PERFRAME=1` | フレーム別の VibeVoice TTS ダンプを `perframe_<stage>_f<NNN>.bin` として書き込み。`VIBEVOICE_TTS_DUMP=path/` と `VIBEVOICE_TTS_NOISE=path` と組み合わせ、`tools/run_official_vibevoice.py` against ステージ別 AR diff。 |
| `VIBEVOICE_TTS_TRACE=1` | 追加の 1 行トレース（negative-condition prefill rms、scaling/bias 係数読み込み）。ライブラリ verbose ≥ 2 と同じ効果; 対応する CLI フラグなし（`-v` は verbose を 1 で上限）。 |
| `VIBEVOICE_VOICE_AUDIO=path.wav` | `.gguf` 音声キャッシュなしで 1.5B-base TTS する参照音声 WAV。 |
| `VIBEVOICE_TTS_NOISE=path` | フレーム別の Gaussian 初期ノイズを上書き。平坦なリトルエンディアン float32 `[N_frames, vae_dim]` —— 通常 `tools/run_official_vibevoice.py` が書く `noise.bin`。 |
| `VIBEVOICE_VAE_BACKEND=cpu\|metal\|cuda\|vulkan` | VAE デコーダを特定バックエンドへピン留め。 |
| `WAV2VEC2_BENCH=1` / `WAV2VEC2_VERBOSE=1` / `WAV2VEC2_DUMP_DIR=` | wav2vec2 のステージ別タイミング、verbose グラフトレース、ステージダンプ。 |
| `CRISPASR_VOXTRAL4B_STREAM_TIMING=1` | voxtral4b ストリーミングパスのステージ別タイミング（エンコーダ drain / prefill / first-text-token / decode-step p50/p95）。 |
| `CRISPASR_VOXTRAL4B_STREAM_CHUNK_MS=N` | 内部エンコーダチャンクサイズを上書き（デフォルト 240 ms）。80 ms の倍数であること。大きいほどフィードは速い（カーネル launch 償却）が、ライブ字幕遅延の下限が長い。 |
| `CRISPASR_VOXTRAL4B_STREAM_BATCH_ENCODER=1` | リグレッションデバッグ: ストリーミングエンコーダの audio_embeds を無視し、flush 時にバッチエンコーダ全体を再実行。 |
| `CRISPASR_VOXTRAL4B_STREAM_DEBUG=1` / `CRISPASR_VOXTRAL4B_STREAM_DIFF=1` | ステップ別デコード表示 / バッチエンコーダ against 並列エンコーダコサイン。 |
| `CRISPASR_VOXTRAL4B_STREAM_LIVE=1` | フィード中デコードのライブ字幕（PLAN #7 フェーズ 3）。フィード中にポーリングされた `get_text()` は進行中のトランスクリプトを返す。デフォルト OFF（PTT セマンティクス）。ラッパ: Python `Session.stream_open(live=True)`、Rust `stream_open_ex(.., live: true)`。 |
| `CRISPASR_VOXTRAL4B_STREAM_DECODER_THREAD=1` | デコーダワーカースレッド（PLAN #7 フェーズ 4、ライブモードを暗示）。`feed()` はデコードループを待たずエンコーダチャンク間で return —— マイク駆動ワークロードに有用。M1 では Metal キューがエンコーダとデコーダを直列化するため総 wall-clock は不変; カーネルレベル並列性のある高速 GPU では実際のオーバーラップが見える。 |
| `CRISPASR_VOXTRAL4B_FUSED_QKV=0` | ランタイム fused-QKV LLM パスをオプトアウト（デフォルトオン、M1 Q4_K でデコード約 7-8 % 高速、約 500 MB 追加メモリ）。 |
| `CRISPASR_QWEN3_ASR_FUSED_QKV=0` | qwen3-asr のランタイム fused-QKV LLM パスをオプトアウト（デフォルトオン; F16/F32/Q4_K/Q8_0/... で動作）。 |
| `CRISPASR_VOXTRAL_FUSED_QKV=1` | voxtral 3B のランタイム fused-QKV LLM パスをオプト**イン**。デフォルトオフ（JFK-shape デコードでは計測可能な速度向上なし; デコードが支配的な長尺ワークロードで有用）。 |
| `QWEN3_TTS_FUSED_QKV=1` | ランタイム fused-QKV talker パスをオプトイン。 |
| `GRANITE_DISABLE_ENCODER_GRAPH=1` | granite-speech / -plus / -nar エンコーダを層別 CPU ループへ強制（遅いがデバッグ用に維持）。層別 Shaw RPE を備えた単一 ggml-graph エンコーダがデフォルトで、3 変種全てで end-to-end 約 2× 速い層別 CPU ループとビット近似一致。 |
| `CRISPASR_NO_REL_POS=1` | Gemma-4 音声エンコーダの相対位置バイアスを除去（開発のみ）。 |
| `ECAPA_REF_FBANK=path` | ECAPA-TDNN LID モデル向けの参照フィルタバンクテンソル（リグレッションハーネス）。 |
| `CRISPASR_SHERPA_LID_BIN=path` | 自動検出した sherpa-onnx LID バイナリを上書き。 |
| `CRISPASR_ARG_DEVICE=N` | `-dev` を渡さない時のデフォルト GPU デバイスインデックス。 |
| `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` | VRAM 枯渇時に CUDA が RAM へスワップする。 |
| `GGML_VK_VISIBLE_DEVICES` / `CUDA_VISIBLE_DEVICES` | 標準的な ggml/CUDA デバイス可視性フィルタ。 |

ゲート付きモデルのダウンロードでは `HF_TOKEN` と `HUGGING_FACE_HUB_TOKEN` の両方が
（その順序で）尊重されます。

</details>

---

<a id="credits"></a>
## クレジット

- **[whisper.cpp](https://github.com/ggml-org/whisper.cpp)** —— このフォークが築かれた元々の ggml 推論エンジンと Whisper ランタイム
- **[ggml](https://github.com/ggml-org/ggml)** —— すべてが動作するテンソルライブラリ
- **NVIDIA NeMo** —— parakeet-tdt-{0.6b-v2,0.6b-v3,1.1b}、parakeet-tdt_ctc-{110m,1.1b,0.6b-ja}、parakeet-ctc-{0.6b,1.1b}、canary-1b-v2、canary-ctc アライナ、そして FastConformer-CTC ファミリー（stt_en_fastconformer_ctc_{large,xlarge,xxlarge} に stt_*_fastconformer_hybrid_large[_pc] フリート（en-pc, de, es, fr, it, nl, pl, ru, ua, hr, be, ar, fa, ka, hy, uz, kk-ru）の CTC ブランチを加えたもの —— すべて ASR バックエンドとしても、コンパクトな約 82 MB の `-am` 強制アライナとしても使用可）
- **Cohere** —— cohere-transcribe-03-2026
- **Qwen team (Alibaba)** —— Qwen3-ASR-0.6B、Qwen3-ASR-1.7B、Qwen3-ForcedAligner-0.6B
- **Mistral AI** —— Voxtral Mini 3B と 4B Realtime
- **IBM Granite team** —— Granite Speech 3.2-8b、3.3-2b、3.3-8b、4.0-1b
- **Meta / wav2vec2** —— wav2vec2 CTC モデル（XLSR-53 英語、ドイツ語、任意の Wav2Vec2ForCTC チェックポイント経由の多言語）
- **[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)** —— サブプロセス経由のオプション分離（ONNX モデル）
- **[Silero](https://github.com/snakers4/silero-vad)** —— VAD（ネイティブ GGUF）と言語識別（ネイティブ GGUF、95 言語）
- **[pyannote](https://github.com/pyannote/pyannote-audio)** —— 話者分離セグメンテーション（ネイティブ GGUF ポート）
- **[miniaudio](https://miniaud.io/)** + **[stb_vorbis](https://github.com/nothings/stb)** + **[libopus/opusfile](https://opus-codec.org/)** —— 内蔵/リンク音声デコーダ（WAV/MP3/FLAC/AIFF/OGG/Opus、ffmpeg なし; AAC/M4A/ALAC は Apple AudioToolbox 経由）
- **[glint](https://github.com/CrispStrobe/glint)**（MIT）—— ツリー内クリーンルームコーデックスイート: MP3/AAC-LC/Ogg-Opus 出力エンコーダ（TTS `.mp3`/`.aac`/`.opus`）とクロスプラットフォーム ADTS AAC-LC + Ogg Opus 入力デコーダ（libopus 不要）
- **[Claude Code](https://claude.ai/claude-code)**（Anthropic）—— crispasr 統合レイヤの重要な部分、全モデルコンバータ、そして FastConformer/attention/mel/FFN/BPE コアヘルパの多くは Claude と共著

---

## ライセンス

上流 whisper.cpp と同じ: **MIT**。

モデル別の重みは各自の HuggingFace モデルライセンスにカバーされます（[対応バックエンド](#supported-backends) 参照）。`crispasr` バイナリ自体は、主に寛容なライセンス（重みは MIT / Apache-2.0 / CC-BY-4.0）のモデルランタイムをリンクします。
