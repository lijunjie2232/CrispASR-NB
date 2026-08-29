# CrispASR

[![日本語](https://img.shields.io/badge/lang-日本語-red?style=for-the-badge)](README.md)
[![繁體中文](https://img.shields.io/badge/lang-繁體中文-blue?style=for-the-badge)](README.zh.md)
[![English](https://img.shields.io/badge/lang-English-green?style=for-the-badge)](README.en.md)

**一個 C++ 二進位檔、119 個後端 —— 其中 62 個是 TTS 引擎 —— 外加多語文字翻譯，零 Python 相依。**

CrispASR 起初是 [whisper.cpp](https://github.com/ggml-org/whisper.cpp) 的分支（fork），並將那個基礎擴充成一個名為 `crispasr` 的**統一語音引擎**，由針對主要開放權重 ASR *與* TTS 架構的完整 ggml C++ 執行期支撐。一次建置、一個二進位檔、一套一致的 CLI —— 在命令列挑選後端，或讓 CrispASR 從你的 GGUF 檔案自動偵測。TTS 部分請見 [Text-to-Speech](#text-to-speech-models)。

```console
$ crispasr -m ggml-base.en.bin          -f samples/jfk.wav                    # OpenAI Whisper
$ crispasr -m parakeet-tdt-0.6b.gguf    -f samples/jfk.wav                    # NVIDIA Parakeet
$ crispasr -m canary-1b-v2.gguf         -f samples/jfk.wav                    # NVIDIA Canary
$ crispasr -m voxtral-mini-3b-2507.gguf -f samples/jfk.wav                    # Mistral Voxtral
$ crispasr --backend qwen3 -m auto      -f samples/jfk.wav                    # -m auto 會下載
$ crispasr --backend kokoro -m auto --tts "Hello world" --tts-output out.wav  # TTS
```

沒有 Python。沒有 PyTorch。沒有每個模型各自的二進位檔。沒有 `pip install`。只有一個 C++ 二進位檔和一個 GGUF 檔案。

**瀏覽器**：所有後端都能透過 `build-wasm.sh` 編譯成 WebAssembly（4.3 MB）。
多執行緒，搭配 COOP/COEP 標頭完全在客戶端執行。

**示範**：[HuggingFace Space](https://huggingface.co/spaces/cstr/CrispASR) ——
即時轉錄 + TTS + 語種偵測，由 `hf-space/` 自動部署。

### 生態系

| 專案 | 用途 |
|---|---|
| **[CrispASR](https://github.com/CrispStrobe/CrispASR)** | 本倉庫 —— C++ 語音引擎。119 個後端（62 個 TTS），CLI + HTTP 伺服器 + C-ABI + Python/Rust/Dart/Go/Ruby/Java 綁定。 |
| **[CrisperWeaver](https://github.com/CrispStrobe/CrisperWeaver)** | 基於 CrispASR 打造的跨平台 Flutter 轉錄 app。桌面 + 行動，含下載佇列的模型瀏覽器、麥克風擷取、SRT/VTT/JSON 匯出、說話者分離、批次處理。完全離線。 |
| **[CrispEmbed](https://github.com/CrispStrobe/CrispEmbed)** | 透過 ggml 的文字相關引擎 —— 與 CrispASR 同一哲學，但用於嵌入、檢索、OCR 與 OMR、數學與樂譜記號。眾多架構（XLM-R、Qwen3-Embed、Gemma3、ModernBERT、...），dense + sparse + ColBERT + 重排序。PP-OCR、Tesseract、EasyOCR、InternVL2 等。Python/Rust/Dart 綁定。 |
| **[Susurrus](https://github.com/CrispStrobe/Susurrus)** | 含 9 個後端（faster-whisper、mlx-whisper、voxtral、insanely-fast-whisper、...）的 Python ASR GUI。CrispASR 的 C++ 作法的 Python 對應版本。 |

---

## 目錄

- [**從這裡開始**](#start-here) —— 剛接觸 CrispASR？兩條命令讓你產出第一段可用的音訊，不必複製倉庫
- [支援的後端](#supported-backends) —— [ASR](#asr-backends) + [TTS](#text-to-speech-models) + [翻譯](#translation) + [後處理](#post-processing-models) + [音樂與音訊分析](#music--audio-analysis)
- [功能矩阵](#feature-matrix)
- [安裝與建置](#install--build) —— 快速安裝（完整指南見 [docs/install.md](docs/install.md)）；**[該下載哪個預建 Linux tarball](docs/install.md#prebuilt-linux-tarballs--which-one-to-download-355)** —— `-hip` / `-vulkan` 建置需要對應的 GPU 驅動，並**不會**退回 CPU（`-cuda` tarball 會，自 v0.8.30 起）
- [快速上手 —— ASR](#quick-start)
- [疑難排解](docs/troubleshooting.md) —— 印了橫幅就停止、讀取離開碼、`--no-gpu` 二分法、該選哪個 Windows zip
- [**文字轉語音（TTS）**](docs/tts.md) —— 52 個引擎：Kokoro、Qwen3-TTS、VibeVoice、dots.tts、Orpheus、Chatterbox、IndexTTS、Irodori、VoxCPM2、CosyVoice3、CSM、Dia、Zonos、Bark、Piper、MeloTTS 等
- [串流與即時轉錄](docs/streaming.md)
- [伺服器模式（HTTP API）](docs/server.md)
- [併發、平行與擴展](docs/concurrency.md) —— 一次轉錄如何使用多核心、併發伺服器請求（`--server-workers`）、大量離線轉錄、負載平衡器後的副本
- [CLI 參考](docs/cli.md) —— 旗標、VAD、CTC 對齊、輸出格式、自動下載、音訊格式
- [環境變數](docs/environment-variables.md) —— `CRISPASR_<BACKEND>_<FEATURE>` 慣例、全域開關，以及每個後端的變數
- [語言綁定](docs/bindings.md) —— Python / Rust / Dart / Go / Java / JavaScript / Ruby / 行動
- [為 CrispASR 做基準測試](docs/benchmarking.md) —— 如何量測轉錄時間（而非冷啟動）：伺服器/程序內重複、proof-of-work 規則、階段計時環境變數
- [架構](docs/architecture.md) —— 分層佈局、`src/core/` 原語、迴歸紀律
- [貢獻 —— 新增後端](docs/contributing.md) —— 5 檔配方、ground-truth 差分工作流程
- [迴歸矩陣](docs/regression-matrix.md) —— `tools/test-all-backends.py` 能力分級
- [**EU AI Act**](docs/eu-ai-act.md) —— 合成音訊標記（浮水印 + C2PA + 語音免責聲明）、什麼算聲音複製、說話者生物辨識的界線、為什麼沒有情緒辨識，以及作為部署者你仍须承擔的責任
- [量化模型](docs/quantize.md) —— 適用於所有後端的 `crispasr-quantize`
- [GPU 後端選取](#gpu-backend-selection)
- [除錯與剖析](#debugging--profiling)
- [致謝](#credits)

---

<a id="start-here"></a>
## 從這裡開始

本節以下全部都是目錄 —— 100 多個後端，需要時再瀏覽。如果你只是想讓 CrispASR *跑起來*，這便是完整路徑。不必複製倉庫、不必 Python、不必到处找模型。

初次接觸本專案？**[docs/getting-started.md](docs/getting-started.md)** 會一步步走同樣的路徑，附上預期輸出與三種常見的初次執行失敗。

### 1. 取得二進位檔

從 [**Releases**](https://github.com/CrispStrobe/CrispASR/releases/latest) 下載一個檔案並解壓縮：

| 平台 | 下載 | 備註 |
|---|---|---|
| **Windows** | `crispasr-windows-x86_64-cpu.zip` | 需要 AVX2（2013+ Intel / 2015+ AMD）。較舊 CPU → `…-cpu-legacy.zip` |
| **Windows + NVIDIA** | `crispasr-windows-x86_64-cuda.zip` | 自包含；**不**需要安裝 CUDA Toolkit。CUDA-13 原生建置：`…-cuda13.zip`（Turing+） |
| **macOS** | `crispasr-macos.tar.gz` | 內建 Metal GPU 支援 |
| **Linux** | `crispasr-linux-x86_64.tar.gz` | GPU 用 `…-cuda.tar.gz` / `…-vulkan.tar.gz` |

想自己建置？見[安裝與建置](#install--build)。`-hip` 與 `-vulkan` 建置需要對應驅動，並**不會**退回 CPU；Linux 的 `-cuda` tarball 會退回。

確認它能執行 —— 這應該會印出版本橫幅並結束：

```bash
crispasr --version          # Windows: .\crispasr.exe --version
```

CUDA 建置也會印出 `cuda toolkit` 與 `cuda runtime ABI`，因此這條命令無需檢查 DLL 就能區分 CUDA 12 與 CUDA 13 套件。

### 2. 讓它說話

`-m auto` 會在首次使用時下載模型（這裡約 135 MB），之後重複使用 —— 不必尋找或安裝任何東西。它會落在 `~/.cache/crispasr/`（Windows 上是 `%USERPROFILE%\.cache\crispasr`）。

```bash
crispasr --backend kokoro -m auto --tts "The quick brown fox jumps over the lazy dog." --tts-output hello.wav
# crispasr: TTS output written to 'hello.wav' (78000 samples @ 24000 Hz, 3.25 sec)
```

播放 `hello.wav`。這就代表 TTS 那一半成功了。

### 3. 再把它轉錄回來

```bash
crispasr --backend parakeet -m auto -f hello.wav -l en
# crispasr: transcribed 3.2s audio in 0.32s (10.1x realtime)
# The quick brown fox jumps over the lazy dog.
```

（首次執行約 467 MB。`-l en` 跳過語種自動偵測，否則會多抓一個小模型。）兩半現在都能用了 —— 換成你自己的 `.wav` 就能開跑。

### 接下來去哪裡

| 你想…… | 前往 |
|---|---|
| 從錄音複製聲音 | [docs/tts.md](docs/tts.md) —— 並先讀[同意規則](docs/eu-ai-act.md)；複製需要 `--i-have-rights` |
| 挑選更好的 ASR 模型 | [我該選哪個後端？](#which-backend-should-i-pick) |
| 帶單字時間戳、SRT/VTT 的轉錄 | [docs/cli.md](docs/cli.md) |
| 即時麥克風 / 串流 | [docs/streaming.md](docs/streaming.md) |
| 以 HTTP 伺服器執行 | [docs/server.md](docs/server.md) |
| 查看這個二進位檔的所有後端 | `crispasr --list-backends` |

### 如果沒有任何反應

在任何命令加上 `-v` 可顯示詳細進度，加上 `--dry-run-resolve` 可列出它會開啟哪些模型檔案（以及它們是否在磁碟上），而不實際載入任何東西。

如果某條命令印出橫幅然後就單純停止 —— 沒有錯誤、沒有輸出檔案 —— 那是當機，不是拒絕，離開碼會一步指出原因。見 **[docs/troubleshooting.md](docs/troubleshooting.md)**。

---

<a id="supported-backends"></a>
## 支援的後端

CrispASR 內建 **119 個後端**（權威、自動計數的清單見[產生的功能矩阵](docs/feature-matrix.md)）—— 大多數用於轉錄/翻譯，另有 **62 個 TTS 引擎**用於合成。它也內建音訊到音訊的 S2S 後端，包含 Sidon 修復與 VoxCPM2 AudioVAE 語音升頻器；完整能力清單見[功能矩阵](docs/feature-matrix.md)。
在 CLI 用 `--backend NAME` 挑選，或省略它讓二進位檔從 GGUF 中繼資料自動偵測。合成端請跳到下方的 [TTS 表格](#text-to-speech-models)。

<a id="asr-backends"></a>
### ASR 後端

| 後端 | 模型 | 架構 | 語種 | 授權 |
|---|---|---|---|---|
| **whisper** | [`ggml-base.en.bin`](https://huggingface.co/ggerganov/whisper.cpp/) 與所有 OpenAI Whisper 變體 | Encoder-decoder transformer | 99 | MIT |
| **whisper** | [`distil-whisper/distil-large-v3`](https://huggingface.co/cstr/distil-large-v3-GGUF) | 蒸餾 Whisper：32L encoder + 2L decoder（快 6.3 倍） | 英文 | MIT |
| **dolphin** | [`DataoceanAI1/dolphin-cn-dialect-small-streaming`](https://huggingface.co/cstr/dolphin-cn-dialect-small-streaming-GGUF)（`-m dolphin`） | E-Branchformer + Transformer decoder + CTC；CTC prefix beam + attention rescoring | 國語 + 中文方言（預測語種/地區） | Apache-2.0 |
| **xasr** | [`GilgameshWind/X-ASR-zh-en`](https://huggingface.co/cstr/x-asr-zh-en-GGUF)（`-m xasr`） | 串流 Zipformer2 transducer（icefall）；160 / 480 / 960 / 1920 ms 區塊，即時 WebSocket session | zh, en（標點 + 大小寫） | Apache-2.0 |
| **parakeet** | [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) | FastConformer + TDT | 25 歐洲語（自動偵測） | CC-BY-4.0 |
| **parakeet** | [`oruk/orukeet`](https://huggingface.co/cstr/orukeet-GGUF)（`-m orukeet`） | parakeet-tdt-0.6b-v3 微調，encoder 一半的 depthwise kernel 被擬合的 Gabor 函數取代 | 25 歐洲語（自動偵測） | CC-BY-SA-4.0 |
| **parakeet** | [`moondream/parakeet-ultra`](https://huggingface.co/cstr/parakeet-ultra-GGUF)（`-m parakeet-ultra`） | 以 transformers 格式釋出的 parakeet-tdt-0.6b-v3 架構；用 `--hf` 轉換 | 25 歐洲語（自動偵測） | CC-BY-4.0 |
| **parakeet** | [`moondream/parakeet-redux`](https://huggingface.co/cstr/parakeet-redux-GGUF)（`-m parakeet-redux`） | 帶有ternary（base-3 打包）encoder 的 parakeet-tdt-0.6b-v3，由轉換器精確反量化 | 25 歐洲語（自動偵測） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt-0.6b-v2`](https://huggingface.co/cstr/parakeet-tdt-0.6b-v2-GGUF) | FastConformer + TDT，原 Open ASR Leaderboard 冠軍 | en（混合大小寫 + 標點） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt-1.1b`](https://huggingface.co/cstr/parakeet-tdt-1.1b-GGUF) | 42L FastConformer + TDT，較大的英文變體 | en（小寫） | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-110m`](https://huggingface.co/cstr/parakeet-tdt_ctc-110m-GGUF) | 17L FastConformer + TDT+CTC 混合；最小變體，自動 CTC 解碼 | en | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-1.1b`](https://huggingface.co/cstr/parakeet-tdt_ctc-1.1b-GGUF) | 42L FastConformer + TDT+CTC 混合；最大，混合大小寫 + 標點 | en | CC-BY-4.0 |
| **parakeet** | [`nvidia/parakeet-tdt_ctc-0.6b-ja`](https://huggingface.co/cstr/parakeet-tdt-0.6b-ja-GGUF) | FastConformer-TDT-CTC，xscaling，80 mel | 日文 | CC-BY-4.0 |
| **reazonspeech** | [`reazon-research/reazonspeech-nemo-v2`](https://huggingface.co/cstr/reazonspeech-nemo-v2-GGUF) | FastConformer-RNNT，local attn（w=256），80 mel，619M 參數 | 日文 | Apache-2.0 |
| **fastconformer-ctc** | [`nvidia/parakeet-ctc-0.6b`](https://huggingface.co/cstr/parakeet-ctc-0.6b-GGUF) | 24L FastConformer + CTC，80 mel（與 fc-ctc-xlarge 同架構） | en | CC-BY-4.0 |
| **fastconformer-ctc** | [`nvidia/parakeet-ctc-1.1b`](https://huggingface.co/cstr/parakeet-ctc-1.1b-GGUF) | 42L FastConformer + CTC，80 mel | en | CC-BY-4.0 |
| **fastconformer-ctc** | [`grider-transwithai/parakeet-ctc-1.1b-ja`](https://huggingface.co/cstr/parakeet-ctc-1.1b-ja-GGUF) | 42L FastConformer + CTC，80 mel，日文微調 | 日文 | Apache-2.0 |
| **canary** | [`nvidia/canary-1b-v2`](https://huggingface.co/nvidia/canary-1b-v2) | FastConformer + Transformer decoder | 25 歐洲語（明確 `-sl/-tl`） | CC-BY-4.0 |
| **canary-qwen** | [`nvidia/canary-qwen-2.5b`](https://huggingface.co/nvidia/canary-qwen-2.5b) | FastConformer + Qwen3-1.7B SALM | en | CC-BY-4.0 |
| **lfm2-audio** | [`LiquidAI/LFM2.5-Audio-1.5B`](https://huggingface.co/cstr/lfm2-audio-1.5b-GGUF) | FastConformer + LFM2 混合 conv+attention 骨幹（ASR+TTS） | en | LFM Open v1.0 |
| **lfm2-audio** | [`LiquidAI/LFM2.5-Audio-1.5B-JP`](https://huggingface.co/cstr/lfm2-audio-1.5b-jp-GGUF) | FastConformer + LFM2 混合 conv+attention 骨幹（ASR+TTS） | ja | LFM Open v1.0 |
| **mini-omni2** | [`gpt-omni/mini-omni2`](https://huggingface.co/gpt-omni/mini-omni2) | Whisper-small + Qwen2-0.5B（ASR+TTS+S2S） | en | MIT |
| **cohere** | [`CohereLabs/cohere-transcribe-03-2026`](https://huggingface.co/CohereLabs/cohere-transcribe-03-2026) | Conformer + Transformer | 13 | Apache-2.0 |
| **cohere** | [`efwkjn/cohere-asr-ja-v0.1`](https://huggingface.co/TransWithAI/cohere-transcribe-ja-v0.1-GGUF) | cohere-transcribe-03-2026 的日文微調（TedX/JSUT 調教） | 日文 | Apache-2.0 |
| **granite** | [`ibm-granite/granite-speech-{3.2-8b,3.3-2b,3.3-8b}`](https://huggingface.co/ibm-granite/granite-speech-3.3-2b)、[`granite-4.0-1b-speech`](https://huggingface.co/ibm-granite/granite-4.0-1b-speech) | Conformer + Q-Former + Granite LLM（μP）（[更多](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt ja | Apache-2.0 |
| **granite-4.1** | [`ibm-granite/granite-speech-4.1-2b`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b) | 16L Conformer + Q-Former + Granite LLM；單一 ggml 圖（[更多](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt ja | Apache-2.0 |
| **granite-4.1-plus** | [`ibm-granite/granite-speech-4.1-2b-plus`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-plus) | 4.1 + 隱狀態串接；帶標點輸出（[更多](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt | Apache-2.0 |
| **granite-4.1-nar** | [`ibm-granite/granite-speech-4.1-2b-nar`](https://huggingface.co/ibm-granite/granite-speech-4.1-2b-nar) | 非自迴歸：單次 LLM 前向 + slot argmax（[更多](docs/architecture.md#granite--granite-41--granite-41-plus--granite-41-nar)） | en fr de es pt | Apache-2.0 |
| **fastconformer-ctc** | [`nvidia/stt_en_fastconformer_ctc_large`](https://huggingface.co/nvidia/stt_en_fastconformer_ctc_large) | FastConformer + CTC（NeMo 系列，所有尺寸） | en | CC-BY-4.0 |
| **voxtral** | [`mistralai/Voxtral-Mini-3B-2507`](https://huggingface.co/mistralai/Voxtral-Mini-3B-2507) | Whisper encoder + Mistral 3B LLM | 8 | Apache-2.0 |
| **voxtral4b** | [`mistralai/Voxtral-Mini-4B-Realtime-2602`](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602) | 因果 encoder + 3.4B LLM，滑動視窗 | 13，即時串流 | Apache-2.0 |
| **qwen3** | [`Qwen/Qwen3-ASR-0.6B`](https://huggingface.co/Qwen/Qwen3-ASR-0.6B) | Whisper 風格音訊 encoder + Qwen3 0.6B LLM | 30 + 22 種中文方言 | Apache-2.0 |
| **qwen3-1.7b** | [`Qwen/Qwen3-ASR-1.7B`](https://huggingface.co/Qwen/Qwen3-ASR-1.7B) | Whisper 風格音訊 encoder + Qwen3 1.7B LLM | 30 + 22 種中文方言 | Apache-2.0 |
| **confucius4-r2t2** | [`netease-youdao/Confucius4-R2T2`](https://huggingface.co/cstr/confucius4-r2t2-GGUF) | Qwen3-ASR-1.7B 串流微調；僅追加的即時 session（prefix 回滾） | 30 語 | NetEase Youdao Model Use License |
| **raon-speech** | [`KRAFTON/Raon-Speech-9B`](https://huggingface.co/cstr/raon-speech-9b-GGUF) | Qwen3-Omni 音訊塔 + adaptor + Qwen3 36L LLM（speech-to-text 子集；24 kHz 下 8 s 區塊） | en, ko | CC-BY-NC-4.0（非商業） |
| **qwen3-ja-anime** | [`jaykwok/Qwen3-ASR-1.7B-JA-Anime-Galgame-hf`](https://huggingface.co/jaykwok/Qwen3-ASR-1.7B-JA-Anime-Galgame-hf) | 為日文動漫/美少女遊戲語音微調的 Qwen3-ASR-1.7B | ja + 30 語 | Apache-2.0 |
| **mega-asr** | [`zhifeixie/Mega-ASR`](https://huggingface.co/zhifeixie/Mega-ASR) | Qwen3-ASR-1.7B + 合併的穩健性 LoRA；恆開的穩健路徑 | 嘈雜 / 劣化語音 | Apache-2.0 |
| **higgs-stt** | [`bosonai/higgs-audio-v3-stt`](https://huggingface.co/bosonai/higgs-audio-v3-stt) | Whisper-large-v3 encoder（4 s 區塊）+ Qwen3-1.7B LLM（[更多](docs/architecture.md#higgs-stt)） | en | Apache-2.0 |
| **wav2vec2** | [`jonatasgrosman/wav2vec2-large-xlsr-53-english`](https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-english) | CNN + 24L transformer + CTC head（任何 Wav2Vec2ForCTC） | 依模型 | Apache-2.0 |
| **wav2vec2** | [`facebook/data2vec-audio-base-960h`](https://huggingface.co/cstr/data2vec-audio-960h-GGUF) | Data2Vec Audio（79 MB Q4_K） | 英文 | Apache-2.0 |
| **wav2vec2** | [`facebook/hubert-large-ls960-ft`](https://huggingface.co/cstr/hubert-large-ls960-ft-GGUF) | HuBERT Large（212 MB Q4_K） | 英文 | Apache-2.0 |
| **glm-asr** | [`zai-org/GLM-ASR-Nano-2512`](https://huggingface.co/zai-org/GLM-ASR-Nano-2512) | Whisper encoder + 4-frame projector + Llama 1.5B（GQA） | 國語（+ 中文方言）、英文、粵語 | MIT |
| **kyutai-stt** | [`kyutai/stt-1b-en_fr`](https://huggingface.co/kyutai/stt-1b-en_fr) | Mimi codec（SEANet + RVQ）+ 16L 因果 LM | en, fr | MIT |
| **kyutai-stt** | [`kyutai/stt-2.6b-en`](https://huggingface.co/kyutai/stt-2.6b-en) | Mimi codec + 48L 因果 LM（2.6B，僅英文；3.5 s 前瞻） | en | MIT |
| **firered-asr** | [`FireRedTeam/FireRedASR2-AED`](https://huggingface.co/FireRedTeam/FireRedASR2-AED) | Conformer + CTC + beam search；亦可 LID（120 語） | 國語、英文、20+ 中文方言 | Apache-2.0 |
| **moonshine** | [`UsefulSensors/moonshine-{tiny,base}`](https://huggingface.co/cstr/moonshine-base-GGUF) | Conv + 6L enc + 6L dec；多語變體 | 英文 + 6 語 | MIT |
| **moonshine&#8209;de** | [`fidoriel/moonshine-base-de`](https://huggingface.co/cstr/moonshine-base-de-fidoriel-GGUF) | moonshine-base 的德文微調（CV22 WER 6.9%） | 德文 | CC&#8209;BY&#8209;NC&#8209;SA&#8209;4.0 |
| **moonshine&#8209;tiny&#8209;de** | [`fidoriel/moonshine-tiny-de`](https://huggingface.co/cstr/moonshine-tiny-de-fidoriel-GGUF) | moonshine-tiny 的德文微調（CV22 WER 11.4%） | 德文 | CC&#8209;BY&#8209;NC&#8209;SA&#8209;4.0 |
| **moonshine-streaming** | [`UsefulSensors/moonshine-streaming-{tiny,small,medium}`](https://huggingface.co/cstr/moonshine-streaming-tiny-GGUF) | 串流：滑動視窗 encoder + AR decoder（34–245M） | 英文 | MIT |
| **gemma4-e2b** | [`google/gemma-4-E2B-it`](https://huggingface.co/cstr/gemma4-e2b-it-GGUF) | USM Conformer 12L + Gemma4 LLM 35L（GQA、PLE） | 140+ 語 | Apache-2.0 |
| **gemma4-e4b** | [`google/gemma-4-E4B-it`](https://huggingface.co/cstr/gemma4-e4b-it-GGUF) | 同 USM Conformer 12L + 較大的 Gemma4 LLM 42L（GQA、PLE）；以 `--backend gemma4-e2b` 執行 | 140+ 語 | Apache-2.0 |
| **omniasr** | [`omniASR-CTC-1B-v2`](https://huggingface.co/cstr/omniASR-CTC-1B-v2-GGUF) | wav2vec2 CNN + 48L transformer + CTC（[更多](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr&#8209;300m** | [`omniASR-CTC-300M-v2`](https://huggingface.co/cstr/omniASR-CTC-300M-v2-GGUF) | 同架構，24L，約 194 MB Q4_K；自動區塊化 >7 s（[更多](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr-llm** | [`omniASR-LLM-300M-v2`](https://huggingface.co/cstr/omniasr-llm-300m-v2-GGUF) | 同 encoder + 12L LLaMA decoder（[更多](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **omniasr-llm** | [`omniASR-LLM-Unlimited-300M-v2`](https://huggingface.co/cstr/omniasr-llm-unlimited-300m-v2-GGUF) | 串流：15s 段落通訊協定，無限音訊（[更多](docs/architecture.md#omniasr-ctc--llm--unlimited)） | **1600+** | Apache-2.0 |
| **vibevoice** | [`microsoft/VibeVoice-ASR`](https://huggingface.co/cstr/vibevoice-asr-GGUF) | σ-VAE ConvNeXt + Qwen2.5-7B（[更多](docs/architecture.md#vibevoice)） | 50+ | MIT |
| **vibevoice-streaming** | [`microsoft/VibeVoice-ASR-Streaming-1.5B`](https://huggingface.co/microsoft/VibeVoice-ASR-Streaming-1.5B) | σ-VAE ConvNeXt + Qwen2.5-1.5B；持久 KV 的 2.93 s 區塊，含 0.53 s 前瞻（[更多](docs/architecture.md#vibevoice)） | 多語 | MIT |
| **vibevoice-bitnet** | [`VibeVoice-ASR-BitNet`](https://huggingface.co/cstr/vibevoice-asr-bitnet-GGUF) | 同架構，TQ2_0 三元 LM（1.6 GB）（[更多](docs/architecture.md#vibevoice)） | 7+ | MIT |
| **mimo-asr** | [`XiaomiMiMo/MiMo-V2.5-ASR`](https://huggingface.co/cstr/mimo-asr-GGUF) | 6L transformer + 36L Qwen2 LM + RVQ codec（[更多](docs/architecture.md#mimo-asr)） | 國語 + 方言 + 英文 | MIT |
| **ark-asr** ⚠️*實驗性/WIP* | [`cstr/ark-asr-3b-GGUF`](https://huggingface.co/cstr/ark-asr-3b-GGUF)（基礎 [`AutoArk-AI/ARK-ASR-3B`](https://huggingface.co/AutoArk-AI/ARK-ASR-3B)） | Whisper-large-v3 enc（部分 RoPE）+ Qwen2.5-3B LM（[更多](docs/architecture.md#ark-asr)） | 19（zh, en, de, ja, fr, ko, es, pl, it, ro, hu, cs, nl, fi, hr, sk, sl, et, lt） | 見基礎 |
| **moss-audio** | [`OpenMOSS-Team/MOSS-Audio-4B-Instruct`](https://huggingface.co/cstr/MOSS-Audio-4B-Instruct-GGUF) | 32L Whisper encoder + DeepStack 3-tap + 36L Qwen3 LM；音訊理解 + ASR（[更多](docs/architecture.md#moss-audio)） | zh, en | Apache-2.0 |
| **hojo-asr** | [`HojoAI/Hojo-ASR-Multi-V1`](https://huggingface.co/cstr/Hojo-ASR-Multi-V1-GGUF) | Qwen3-Omni 音訊塔（32L）+ 2 區塊 WeNet Conformer adapter + Qwen3-4B LM；多語 ASR（[更多](docs/architecture.md#hojo-asr)） | de, fr, it, pt, es, ja, ar, ko, ru | Apache-2.0 |
| **moss-transcribe** | [`OpenMOSS-Team/MOSS-Transcribe-preview-2B`](https://huggingface.co/cstr/MOSS-Transcribe-preview-2B-GGUF) | Qwen3-Omni 音訊 encoder（32L，視窗 attn）+ GatedMLP adapter + Qwen3-1.7B LM；ASR（[更多](docs/architecture.md#moss-transcribe)） | zh, en | Apache-2.0 |
| **moss-diarize** | [`OpenMOSS-Team/MOSS-Transcribe-Diarize-0.9B`](https://huggingface.co/cstr/MOSS-Transcribe-Diarize-0.9B-GGUF) | 標準 Whisper encoder（24L，80 mel）+ 4x merge + VQAdaptor + Qwen3-0.6B LM；同時 ASR + 說話者分離 + 時間戳 | 多語 | Apache-2.0 |
| **whisper** *(tiron)* ⚠️*實驗性* | [`Trelis/tiron`](https://huggingface.co/cstr/tiron-GGML)（基礎 [`Trelis/tiron`](https://huggingface.co/Trelis/tiron)） | 擴充詞彙表的 Whisper large-v3：透過約束解碼文法，發出內嵌的 `<|speakerN|>` 標記 + 20 ms 時間戳，同時做轉錄 + 視窗級說話者歸屬，並跨視窗連結到穩定的說話者（#295） | 多語（以 en 為重心） | Apache-2.0 |
| **funasr** | [`FunAudioLLM/Fun-ASR-Nano-2512`](https://huggingface.co/cstr/funasr-nano-GGUF) | 70 區塊 SANM encoder + 2 區塊 Transformer adaptor + Qwen3-0.6B LLM | zh, yue, en, ja, ko | FunASR Model License v1.1（註明出處可商業使用） |
| **fun-asr-mlt-nano** | [`FunAudioLLM/Fun-ASR-MLT-Nano-2512`](https://huggingface.co/cstr/funasr-mlt-nano-GGUF) | 同架構，多語 decoder | 31 語，含 de, fr, es, pt, ru, ar, hi, vi, th, ko | FunASR Model License v1.1 |
| **paraformer** | [`funasr/paraformer-zh`](https://huggingface.co/cstr/paraformer-zh-GGUF) | 50 區塊 SANM encoder + CIF predictor + 16 區塊 NAR decoder（單次、非自迴歸）；字元級詞彙表（8404）；220M 參數 | zh, en | FunASR Model License（註明出處可商業使用） |
| **foxnose** *(說話者分離)* | [`Wespeaker/wespeaker-voxceleb-resnet34-LM`](https://huggingface.co/cstr/wespeaker-resnet34-lm-GGUF) | 透過 `--diarize-method foxnose` 做說話者分離：WeSpeaker ResNet34-LM 256 維嵌入 + GMM/BIC 說話者計數 + 光譜群集 + Viterbi 時間平滑（[更多](docs/architecture.md#foxnose-diarize)）。VoxConverse dev 上 DER 3.18 %，相對於上游參考實作的 3.07 % | 任意 | weights CC-BY-4.0 |
| **gigaam** | [`ai-sage/GigaAM-v3`](https://huggingface.co/cstr/gigaam-v3-GGUF)（基礎 [`ai-sage/GigaAM-v3`](https://huggingface.co/ai-sage/GigaAM-v3)） | 16 層 rotary Conformer（220M）+ CTC 或 RNN-T head；四個修訂版 —— `e2e_rnnt` / `e2e_ctc` 從 SentencePiece 詞彙表發出標點 + 大小寫 + ITN，`rnnt` / `ctc` 發出裸小寫西里爾（[更多](docs/architecture.md#gigaam)） | en ru | MIT |
| **sensevoice** | [`FunAudioLLM/SenseVoiceSmall`](https://huggingface.co/cstr/sensevoice-small-GGUF) | 70 區塊 SANM encoder + CTC head；單次前向即發出轉錄稿 + 語種 ID + 音訊事件（非 AR，比 Whisper-Large 快 15×）；結構化 C ABI + `-oj` JSON 將標籤呈現為個別欄位。上游的情緒分類器**未開放** —— 見 [EU AI Act](docs/eu-ai-act.md#41-emotion-recognition--removed-not-gated) | 50+ 語；原生 LID + 音訊事件標籤 | FunASR Model License v1.1 |

### 語音到語音的升頻與修復

| 後端 | 模型 | 架構 | 輸入 / 輸出 | 授權 |
|---|---|---|---|---|
| **sidon** | [`KevinAHM/Sidon-GGUF`](https://huggingface.co/KevinAHM/Sidon-GGUF)（基礎 [`sarulab-speech/sidon-v0.1`](https://huggingface.co/sarulab-speech/sidon-v0.1)） | w2v-BERT 2.0 predictor + 連續 DAC decoder（[更多](docs/architecture.md#sidon)） | 16 kHz 單聲道 → 修復的 48 kHz 單聲道 | MIT |
| **voxcpm2-vae** | 來自 [`openbmb/VoxCPM2`](https://huggingface.co/openbmb/VoxCPM2) 的 AudioVAE V2，用 `--vae-only` 轉換 | 獨立的因果 AudioVAE encoder + decoder（[更多](docs/architecture.md#voxcpm2-vae)） | 16 kHz 單聲道 → 升頻的 48 kHz 單聲道 | Apache-2.0 |

```bash
huggingface-cli download KevinAHM/Sidon-GGUF sidon-v0.1-f16.gguf --local-dir models
crispasr -m models/sidon-v0.1-f16.gguf -f input.wav --s2s --s2s-output restored.wav

python models/convert-voxcpm2-to-gguf.py --input openbmb/VoxCPM2 \
  --output models/voxcpm2-vae-f32.gguf --vae-only
crispasr -m models/voxcpm2-vae-f32.gguf -f input.wav --s2s \
  --s2s-output upscaled.wav
```

<a id="text-to-speech-models"></a>
### Text-to-Speech 模型

合成後端由 `--tts` 旗標與 `--tts-output PATH.wav` 驅動。
快速上手命令與引擎選擇指引，請見下方專章 [Text-to-Speech](#text-to-speech-models)。

| 後端 | 模型 | 架構 | 語種 | 授權 |
|---------|--------|-------------|-----------|---------|
| **bt2-tts** | [`breeze-tts-2`](https://huggingface.co/cstr/breeze-tts-2-GGUF) | T5Gemma2 文字 encoder + Qwen3 骨幹 + 12L depth decoder，涵蓋 16 個 codebook @ 12.5 Hz；聲音複製。codec 夥伴是內建的 qwen3-tts tokenizer。**非商業權重** —— 需要 `--accept-license other`。由 BreezeBlue 的 Breeze TTS 2 衍生，僅授權研究與非商業用途。 | en, zh | other（BreezeBlue Research & Non-Commercial） |
| **miotts** | [`MioTTS-0.6B`](https://huggingface.co/cstr/miotts-0.6b-GGUF) | Qwen3 LLM + MioCodec-v2 FSQ codec（25 Hz，44.1 kHz 輸出） | ja, en | Apache-2.0 |
| **vibevoice-tts** | [`VibeVoice-Realtime-0.5B`](https://huggingface.co/cstr/vibevoice-realtime-0.5b-GGUF)、[`VibeVoice-1.5B`](https://huggingface.co/cstr/vibevoice-1.5b-GGUF) | DPM-Solver++ + σ-VAE decoder；聲音預設或複製 | en, zh | MIT |
| **kugelaudio** | [`kugelaudio-0-open`](https://huggingface.co/cstr/kugelaudio-0-open-GGUF) | Qwen2.5-7B LM + 4L DiT 擴散 + 聲學 VAE decoder；聲音複製 | 多語 | Apache-2.0 |
| **qwen3-tts** | [`Qwen3-TTS-12Hz-0.6B-Base`](https://huggingface.co/cstr/qwen3-tts-0.6b-base-GGUF)、[`1.7B-Base`](https://huggingface.co/cstr/qwen3-tts-1.7b-base-GGUF)、[`1.7B-VoiceDesign`](https://huggingface.co/cstr/qwen3-tts-1.7b-voicedesign-GGUF) | Qwen3 talker LM + 12 Hz RVQ（[更多](docs/architecture.md#qwen3-tts)） | 多語 | Apache-2.0 |
| **qwen3-tts-customvoice** | [`1.7B-CustomVoice`](https://huggingface.co/cstr/qwen3-tts-1.7b-customvoice-GGUF) | 同 talker + 9 個高級內建說話者（`--voice <name>`）；用 `--instruct` 的可選風格（例如 "spoke very slowly"）（[更多](docs/architecture.md#qwen3-tts)） | 多語 | Apache-2.0 |
| **moss-tts** | [`OpenMOSS-Team/MOSS-TTS-v1.5`](https://huggingface.co/cstr/moss-tts-v1.5-GGUF) | Qwen3-8B 骨幹在延遲模式下發出 32 個 RVQ 音訊 codebook，由 1.6B 純 transformer codec 夥伴解碼；透過 `--voice ref.wav` 做聲音複製；`--backend moss-tts -m <backbone> --codec-model <codec>` | 多語 | Apache-2.0 |
| **moss-tts-local** | [`OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5`](https://huggingface.co/cstr/moss-tts-local-v1.5-GGUF) | Qwen3-4B 骨幹；一個 1 層的 local/depth transformer 以自迴歸方式每影格發出 12 個 RVQ codebook（RQ-Transformer，無延遲），由 MOSS-Audio-Tokenizer-v2 解碼到 48 kHz（混合為單聲道）；`--backend moss-tts-local -m <backbone> --codec-model <codec>` | 多語 | Apache-2.0 |
| **omnivoice** | [`k2-fsa/OmniVoice`](https://huggingface.co/cstr/omnivoice-GGUF) | Qwen3-0.6B + 遮罩式迭代 8-codebook TTS（SoundStorm 風格）；聲音複製；600+ 語（[更多](docs/architecture.md#omnivoice)） | 600+ 語 | Apache-2.0 |
| **melotts** | [`myshell-ai/MeloTTS`](https://github.com/myshell-ai/MeloTTS) EN_V2 | VITS2（6L transformer + SDP/DP + transformer coupling flow + HiFi-GAN）；44.1 kHz，102 MB + 52 MB BERT Q4_K 夥伴（共 154 MB）；類神經 G2P；4 個英文說話者（[更多](docs/architecture.md#melotts)） | en | MIT |
| **piper** | [`rhasspy/piper`](https://github.com/rhasspy/piper) 社群聲音 | VITS（6L transformer + SDP + 4 區塊 coupling flow + HiFi-GAN）；22 kHz 單聲道，每個聲音 30 MB F16；EN/DE/FR/ES/RU 內建 G2P（`--g2p-dict`） | 30+ 語（內建 + espeak dlopen） | MIT |
| **kokoro** | [`hexgrad/Kokoro-82M`](https://huggingface.co/hexgrad/Kokoro-82M) + 德文骨幹 | StyleTTS2 / iSTFTNet（82M）；每個聲音各自的 GGUF（[更多](docs/architecture.md#kokoro)） | en, es, fr, hi, it, ja, pt, zh, de | Apache-2.0 |
| **orpheus** | [`Orpheus-3B-FT`](https://huggingface.co/cstr/orpheus-3b-0.1-ft-GGUF) + [`SNAC 24 kHz`](https://huggingface.co/cstr/snac-24khz-GGUF) | Llama-3.2-3B + SNAC RVQ codec；8 個說話者（[更多](docs/architecture.md#orpheus)） | en, de | Llama 3.2 Community License / MIT |
| **chatterbox** | [`cstr/chatterbox-GGUF`](https://huggingface.co/cstr/chatterbox-GGUF) + Nano/turbo/fine-tune 變體 | T3 AR + S3Gen flow-matching（[更多](docs/architecture.md#chatterbox--chatterbox-turbo--chatterbox-nano--chatterbox-finnish-nano--kartoffelbox-turbo--lahgtna-chatterbox)） | 23 多語；另有獨立的阿拉伯文、德文與芬蘭文（`chatterbox-finnish-nano`）微調 | MIT |
| **indextts** | [`cstr/indextts-1.5-GGUF`](https://huggingface.co/cstr/indextts-1.5-GGUF) | GPT-2 AR（24L/1280d）+ Conformer conditioning + BigVGAN 聲碼器；透過參考音訊做聲音複製 | zh, en | Apache-2.0 |
| **voxcpm2-tts** | [`cstr/voxcpm2-GGUF`](https://huggingface.co/cstr/voxcpm2-GGUF) | 免 tokenizer 的 CFM 擴散 AR（TSLM + RALM + LocDiT），原生 48 kHz；零樣本 + 透過 `--voice <wav>` 做聲音複製 | 30 語 | Apache-2.0 |
| **voxtral-tts** | [`mistralai/Voxtral-4B-TTS-2603`](https://huggingface.co/mistralai/Voxtral-4B-TTS-2603) | Ministral-3B AR（26L GQA）+ 3L FM 聲學 transformer（7 步 Euler ODE）+ Voxtral codec decoder @ 24 kHz；20 個預設聲音；SOTA 法文技術文本 | en, fr, de, es, it, pt, nl, ar, hi | CC&#8209;BY&#8209;NC&#8209;4.0 |
| **cosyvoice3-tts** | [`cstr/cosyvoice3-0.5b-2512-GGUF`](https://huggingface.co/cstr/cosyvoice3-0.5b-2512-GGUF) | Qwen2-0.5B AR 語音 token LM + DiT-CFM（10 步 Euler）+ HiFT（NSF + iSTFT）@ 24 kHz；透過 `--voice <name>` 的燒錄聲音零樣本複製，或任意 WAV 透過 `--voice ref.wav --ref-text "<exact transcript>"`。`--backend cosyvoice3-tts-rl` 選取上游 RL 調教的 talker（相同夥伴） | 9 語 + 18 種中文方言 | Apache-2.0 |
| **csm** | [`cstr/csm-1b-GGUF`](https://huggingface.co/cstr/csm-1b-GGUF) | Sesame CSM-1B 對話式 TTS：Llama-3.2 1B 骨幹 + 100M depth decoder（32-codebook RVQ）+ Kyutai Mimi codec @ 24 kHz（[更多](docs/architecture.md#csm)） | en | Apache-2.0 |
| **lfm2-audio** | [`cstr/lfm2-audio-1.5b-GGUF`](https://huggingface.co/cstr/lfm2-audio-1.5b-GGUF) + [`jp`](https://huggingface.co/cstr/lfm2-audio-1.5b-jp-GGUF) | LFM2.5-Audio ASR+TTS+S2S：FastConformer enc + LFM2 混合骨幹 + depthformer（8-codebook Mimi）+ ISTFT detokenizer @ 24 kHz；文字+音訊交錯生成 | en, ja | LFM Open v1.0 |
| **dia** | [`nari-labs/Dia-1.6B`](https://huggingface.co/cstr/dia-1.6b-GGUF) | 位元組級文字 encoder（12L）+ AR 音訊 decoder（18L GQA + CFG）→ 9 個延遲 DAC codebook + 44.1 kHz DAC codec；以 `[S1]`/`[S2]` 標籤的對話風格（使用 >100 字元的提示） | en | Apache-2.0 |
| **zonos-tts** | [`cstr/zonos-v0.1-transformer-GGUF`](https://huggingface.co/cstr/zonos-v0.1-transformer-GGUF) + [`cstr/dac-44khz-GGUF`](https://huggingface.co/cstr/dac-44khz-GGUF) | Zyphra Zonos-v0.1：26L GQA AR transformer（2B）+ 9-codebook DAC @ 44.1 kHz；CFG 引導；透過參考 WAV 做聲音複製（[更多](docs/architecture.md#zonos-tts)） | en | Apache-2.0 |
| **bark** | [`cstr/bark-small-GGUF`](https://huggingface.co/cstr/bark-small-GGUF) | Suno Bark 三段式 GPT-2 TTS：text→semantic（12L）→ coarse EnCodec（12L，2 codebook）→ fine（12L，8 codebook）→ EnCodec 24 kHz decoder；透過 `.npz` 提示做說話者條件化（`--voice <file.npz>`） | 多語 | MIT |
| **speecht5** | [`cstr/speecht5-tts-GGUF`](https://huggingface.co/cstr/speecht5-tts-GGUF) | SpeechT5 80M：字元級 encoder（12L）+ AR mel decoder（6L）+ 5 層 conv postnet + HiFi-GAN @ 16 kHz；透過 512 維 x-vector 指定說話者（`--voice <xvector.bin>`） | en | MIT |
| **fastpitch** | [`cstr/fastpitch-en-GGUF`](https://huggingface.co/cstr/fastpitch-en-GGUF) | NVIDIA FastPitch 60M：非自迴歸平行 TTS —— 6L encoder + duration/pitch predictor + 6L decoder + HiFi-GAN @ 22 kHz；確定性、單次前向（[更多](docs/architecture.md#fastpitch)） | en | CC-BY-4.0 |
| **bananamind-tts** | `Banaxi-Tech/BananaMind-TTS-V2.1-Preview` | BananaMind-TTS 13M：Tacotron-lite 字元級 encoder（Conv+BN+BiLSTM）+ 帶位置敏感 attention 的 AR GRU decoder + postnet + HiFi-GAN @ 22 kHz；每個語區固定聲音（[更多](docs/architecture.md#bananamind-tts)） | en, de | Apache-2.0 |
| **parler-tts** | [`cstr/parler-tts-mini-v1.1-GGUF`](https://huggingface.co/cstr/parler-tts-mini-v1.1-GGUF) | Parler TTS Mini v1.1（約 900M）：T5 encoder + MusicGen decoder + DAC 44.1 kHz；提示條件化（用 `--instruct` 以文字描述聲音） | en | Apache-2.0 |
| **outetts** | [`cstr/outetts-0.3-1b-GGUF`](https://huggingface.co/cstr/outetts-0.3-1b-GGUF) | OLMo-1B talker + WavTokenizer 單 codebook VQ-GAN @ 24 kHz；透過說話者描述檔 JSON 做聲音複製（`--voice <speaker.json>`） | en | CC-BY-NC-SA-4.0 |
| **pocket-tts** | [`cstr/pocket-tts-GGUF`](https://huggingface.co/cstr/pocket-tts-GGUF) | Kyutai Pocket TTS 100M：12.5 Hz 連續潛變數 AR + 一步 LSD flow + Mimi VAE 24 kHz；透過參考音訊或官方準備好的 `.safetensors` 聲音做聲音複製（[更多](docs/architecture.md#pocket-tts)） | en, de, es, it, pt；fr（24L 預覽） | CC-BY-4.0 + 使用條件 |
| **tada** | [`cstr/tada-tts-1b-GGUF`](https://huggingface.co/cstr/tada-tts-1b-GGUF) + `HumeAI/tada-3b-ml` | Llama-3.2 1B/3B 骨幹 + 每 token FM 擴散頭 + TADA codec @ 24 kHz；1:1 文字對聲學對齊；用 `tada-ref.gguf` 作預設提示，用 `models/convert-tada-ref-to-gguf.py` 建立的 `--voice <tada-ref.gguf>` 作自訂聲音（[更多](docs/architecture.md#tada)） | en | Llama 3.2 Community License |

<details>
<summary><b>TTS 功能矩陣</b></summary>

| 後端 | 聲音複製 | 取樣 | kHz | 自動下載 | Flash attn |
|---------|:---:|:---:|:---:|:---:|:---:|
| vibevoice-tts | 是 | temp | 24 | 是 | 是 |
| qwen3-tts | 是* | temp | 24 | 是 | 是 |
| omnivoice | 是 | temp | 24 | — | — |
| kokoro | — | — | 24 | 是 | — |
| orpheus | — | temp | 24 | 是 | 是 |
| chatterbox | 是 | temp | 24 | 是 | 是 |
| outetts | 是（JSON） | temp | 24 | 是 | 是 |
| indextts | 是 | temp | 24 | 是 | 是 |
| voxcpm2-tts | 是 | — | 48 | 是 | — |
| cosyvoice3-tts | 是 | temp | 24 | 是 | 是 |
| f5-tts | 是 | — | 24 | 是 | — |
| irodori-tts | 是（WAV） | VoiceDesign：`--instruct` | 48 | 是 | — |
| supertonic | 預設 F1-F5/M1-M5 | `--tts-speed`、`--tts-steps` | 44.1 | 是 | — |
| csm | — | temp | 24 | 是 | — |
| dia | — | temp | 44 | 是 | — |
| bark | 是（.npz） | temp | 24 | 是 | — |
| speecht5 | 是（xvec） | — | 16 | 是 | — |
| parler-tts | — | temp | 44 | 是 | — |
| fastpitch | — | — | 22 | — | — |
| piper | — | — | 22 | — | — |
| pocket-tts | 是 | temp | 24 | 是 | — |
| tada | 是 | temp | 24 | 是 | — |
| dots-tts | 是（`--voice ref.wav`） | 16 步 CFG Euler | 48 | 是 | — |
| fireredtts3 | 是（`--voice ref.wav --ref-text "..."`） | 10 步 CFG Euler | 24 | 是 | — |
| confucius4-tts | 是（`--voice ref.wav`） | 25 步 CFG Euler | 22.05 | 是 | — |

\* 僅 CustomVoice 變體；Base 使用透過 `--voice <name>` 燒錄的說話者。

**輸出語言。** `-tl <lang>`（或 `-l`）選取要說的語言；
`cosyvoice3-tts`、`qwen3-tts` 與 `moss-tts` 原生對其作用。若要跨語言**複製** ——
一段英文參考剪輯卻說德文，即字幕配音的情境 —— 也請一併傳入參考片段所用語言的
`-sl <lang>`，如此 cosyvoice3 會丟掉參考轉錄稿而非保留其口音。
透過 HTTP：`POST /v1/audio/speech` 上的 `"language"` + `"source_lang"`。
見 [`docs/tts.md`](docs/tts.md#output-language-and-cross-lingual-cloning--tl---sl)。

</details>

<a id="translation"></a>
### 翻譯

文字到文字翻譯，有別於音訊端的 `--translate` 旗標（它在 whisper / canary 等模型上將音訊 → 英文文字）。由 `--text "..." -sl <src> -tl <tgt>` 驅動。

| 後端 | 模型 | 架構 | 語種 | 授權 |
|---|---|---|---|---|
| **m2m100** | [`facebook/m2m100_418M`](https://huggingface.co/cstr/m2m100-418m-GGUF) | 12L enc + 12L dec transformer，SentencePiece 128K（[更多](docs/architecture.md#m2m100--wmt21)） | 100 語，任意對任意 | MIT |
| **m2m100-wmt21** | [`facebook/wmt21-dense-24-wide-en-x`](https://huggingface.co/cstr/wmt21-dense-24-wide-en-x-GGUF) + [`facebook/wmt21-dense-24-wide-x-en`](https://huggingface.co/cstr/wmt21-dense-24-wide-x-en-GGUF) | 同 m2m100，擴展到 4.7B（24L enc）（[更多](docs/architecture.md#m2m100--wmt21)） | 英文 ↔ 7 語（個別 `en-x` / `x-en` checkpoint） | MIT |
| **madlad** | [`google/madlad400-3b-mt`](https://huggingface.co/cstr/madlad400-3b-mt-GGUF) | T5 enc-dec（12L+12L，d=2048，gated-GELU，RMSNorm）（[更多](docs/architecture.md#madlad)） | 419 語 | Apache-2.0 |

```bash
# m2m100 base（可投產）
./build/bin/crispasr --backend m2m100 -m auto \
    --text "Hello world, how are you today?" \
    -sl en -tl de
# → Hallo Welt, wie bist du heute?

# WMT21 dense（英文 ↔ X，4.7B —— 自動下載約 2.5 GB）。
# 兩個個別 checkpoint：英文來源用 en-x，英文目標用 x-en。
# 選與你的 `-sl`/`-tl` 方向相符的那個
# （或傳入明確的 `-m <path>` 手動載入另一個）。
./build/bin/crispasr --backend m2m100-wmt21 -m auto \
    --text "The president said he would not attend." \
    -sl en -tl de   # 使用 wmt21-dense-24-wide-en-x

./build/bin/crispasr --backend m2m100-wmt21 \
    -m models/wmt21-dense-24-wide-x-en-q4_k.gguf \
    --text "Le président a dit qu'il ne serait pas présent." \
    -sl fr -tl en   # 使用 wmt21-dense-24-wide-x-en

# MADLAD-400 3B（419 語，與 Python SP 位元組完全相同）
./build/bin/crispasr --backend madlad -m auto \
    --text "Hello world." \
    -sl en -tl ta
```

若做兩段式管線（例如 ASR → m2m100），請使用專用的
`--tr-sl` / `--tr-tl` 旗標；它們在未設定時會退回 `-sl` / `-tl`，
所以單段獨立的用法只要 `-sl/-tl` 即可。

<a id="post-processing-models"></a>
### 後處理模型

適用於所有後端。

| 模型 | 任務 | 架構 | 語種 | 授權 | HuggingFace |
|---|---|---|---|---|---|
| **FireRedPunc** | 標點恢復 | BERT-base（12L，d=768），5 類 | 中文 + 英文 | Apache-2.0 | [`cstr/fireredpunc-GGUF`](https://huggingface.co/cstr/fireredpunc-GGUF) |
| **fullstop-punc** | 標點恢復 | XLM-RoBERTa-large（24L，d=1024），6 類 | EN, DE, FR, IT | MIT | [`cstr/fullstop-punc-multilang-GGUF`](https://huggingface.co/cstr/fullstop-punc-multilang-GGUF) |
| **punctuate-all** | 標點恢復 | XLM-RoBERTa-base（12L，d=768），6 類 | 12 語 | MIT | [`cstr/punctuate-all-GGUF`](https://huggingface.co/cstr/punctuate-all-GGUF) |
| **PCS** | 標點 + truecase + 句子邊界 | XLM-RoBERTa-base（12L），4 個 head | 47 語 | Apache-2.0 | `--punc-model pcs` |
| **truecaser&#8209;lstm** | 德文 truecasing（最佳） | BiLSTM 字元級（2×150，3.2 MB，F1 97.9%） | 德文 | Apache-2.0 | `--truecase-model lstm` |
| **truecaser&#8209;crf** | 德文 truecasing | CRF + 脈絡特徵（8.5 MB） | 德文 | MIT | `--truecase-model crf` |
| **truecaser&#8209;de** | 德文 truecasing（簡易） | 統計詞頻（71K 條目，1.7 MB） | 德文 | MIT | `--truecase-model auto` |
| **CLD3** | 文字語種 ID | Embedding-bag → FC + ReLU → softmax（約 1.5 MB F32） | 109 ISO 639-1 | Apache-2.0 | [`cstr/cld3-GGUF`](https://huggingface.co/cstr/cld3-GGUF) |
| **GlotLID-V3** | 文字語種 ID | fastText 監督式，平面 softmax | 2102 ISO 639-3 + 文字系統 | Apache-2.0 | [`cstr/glotlid-GGUF`](https://huggingface.co/cstr/glotlid-GGUF) |
| **LID-176** | 文字語種 ID | fastText 監督式，階層式 softmax | 176 ISO 639-1 | CC-BY-NC-4.0 | [`cstr/fasttext-lid176-GGUF`](https://huggingface.co/cstr/fasttext-lid176-GGUF) |

### 音訊 codec

由 TTS 後端共用的 codec 模組。也可獨立用於 encode/decode。

| 模型 | 架構 | 取樣率 | Token 率 | 授權 | HuggingFace |
|---|---|---|---|---|---|
| **MioCodec v2** | WavLM encoder → FSQ(12800) → Transformer decoder + AdaLN-Zero + SnakeBeta upsampler + iSTFT | 44.1 kHz | 25 Hz（341 bps） | MIT | [`cstr/miocodec-v2-44k-GGUF`](https://huggingface.co/cstr/miocodec-v2-44k-GGUF) |
| **SNAC 24 kHz** | 3-codebook RVQ + decoder 區塊（stride 8/8/4/2） | 24 kHz | 3×12.5 Hz | MIT | [`cstr/snac-24khz-GGUF`](https://huggingface.co/cstr/snac-24khz-GGUF) |

所有執行期共用基於 ggml 的推論。speech-LLM 後端（**qwen3**、**voxtral**、**voxtral4b**、**granite**、**glm-asr**、**kyutai-stt**）將音訊 encoder 的影格直接注入自迴歸語言模型的輸入嵌入，而不是使用專用的 CTC/transducer/seq2seq decoder。**fastconformer-ctc** 後端承載 NeMo FastConformer-CTC 的獨立 ASR 系列 —— `stt_en_fastconformer_ctc_{large,xlarge,xxlarge}` 與架構相同的 `parakeet-ctc-{0.6b,1.1b}`（不同訓練資料 + tokenizer，相同 encoder + head 形狀）—— 以貪婪 CTC 解碼。與 canary-ctc aligner 相同的 C++ 執行期。

<a id="music--audio-analysis"></a>
### 音樂與音訊分析

除了語音，CrispASR 還執行數種音樂/音訊分析任務 —— 每個都是小 GGUF，架構自動偵測，無需 Python。各任務的旗標與輸出格式見 [`docs/cli.md`](docs/cli.md)。

- **音源分離**（`--separate`）—— 將混音拆成 stem（`<input>_<stem>.wav`），透過 **mel-band-roformer**（人聲/伴奏，MIT）或 **htdemucs**（4 軌）。`--stems vocals,drums` 選取子集；`--sep-output-dir` 設定輸出位置。
- **鋼琴轉錄**（`--backend piano-transcription`）—— 鋼琴音訊 → 音符事件（88 鍵 @ 100 fps，ByteDance/Kong CRNN；F16 GGUF 約 77 MB）。
- **複音音符事件**（`--backend basic-pitch`）—— Spotify Basic Pitch，任意樂器 → 音符事件（約 110 KB 模型）。
- **多樂器轉錄**（`--backend mt3`，別名 `music-transcription`）—— MT3 的 T5 encoder/decoder 發出帶各樂器 program 的音符事件（F16 GGUF 約 96 MB）。
- **Onsets & Frames**（`--backend onsets-and-frames`）—— Hawthorne 等人的鋼琴轉錄器（MIT），依每 MB 計是這裡最好的獨奏鋼琴模型：**在 MusicNet 鋼琴曲目上音符 F1 69.0%，對比 Basic Pitch 的 57.5%**，且在 f32 與 Q8_0 下與其 ONNX 匯出 F1 完全相同。Q4_0 GGUF 18.6 MiB，Q8_0 30.8 MiB，F32 101.9 MiB。見 [docs/music-transcription/ONSETS_AND_FRAMES.md](docs/music-transcription/ONSETS_AND_FRAMES.md)。
- **hFT-Transformer**（`--backend hft-transformer`）—— Toyama 等人的階層式頻-時 transformer（MIT），是這裡最準確的獨奏鋼琴模型，也是迄今最小的：**在 MusicNet 鋼琴曲目上音符 F1 70.5%**，僅 5.5 M 參數，Q8_0 GGUF 7.0 MiB，Q4_0 4.5 MiB，F32 21.8 MiB。但它也是執行上最昂貴的 —— 每 2 秒音訊需 249 GFLOP 矩陣乘法，且在沒有 int8 點積指令的 CPU 上，量化會讓它*更慢*而非更快。選它而非 `onsets-and-frames` 前先讀 [docs/music-transcription/HFT_TRANSFORMER.md](docs/music-transcription/HFT_TRANSFORMER.md)。
- 以上五者都接受 `--piano-format text|json|midi`；`midi` 會寫出 Standard MIDI File。
- **吉他六線譜**（`--tab`）—— 透過 **TabCNN** 輸出每影格的逐弦指格（Wiggins & Kim，ISMIR 2019；權重 CC BY 4.0）。後端發出的是逐弦發分數，而非決定的六線譜 —— 需透過 `crispasr_session_tab_emissions()` 自行跑約束式 Viterbi 才能得到可演奏的輸出。
- **節拍 / downbeat 追蹤**（`--beats`）—— 透過 **Beat This!** 產生節拍網格（CPJKU，ISMIR 2024；程式碼*與*權重皆 MIT，無專利牽連的 DBN）。
- **和弦辨識**（`--chords`）—— 透過 **BTC**（ISMIR 2019）產生和弦時間軸（`.lab`）。權重為 CC-BY-NC-SA，受 `--accept-license cc-by-nc-sa-4.0` 閘門限制。
- **音高 / F0 估計**（`--pitch`）—— 透過 **CREPE**（MIT）產生單音旋律音高軌。

<a id="feature-matrix"></a>
## 功能矩陣

執行 `crispasr --list-backends` 即可即時檢視。每個後端在執行期宣告能力；若你要求所選後端不支援的功能，CrispASR 會印出警告並靜默忽略該旗標。

**可排序 / 可篩選檢視：** [`docs/feature-matrix.html`](docs/feature-matrix.html) —— 點擊任一欄標題即可排序，輸入即可篩選列，點擊 cap 膠囊可要求某項能力。由 `crispasr --list-backends-json` 產生（單一權威來源 —— 不可能漂移）。透過 `python tools/gen-feature-matrix.py` 重新產生。Markdown 孿生檔位於 [`docs/feature-matrix.md`](docs/feature-matrix.md)。

下方的靜態表格是精選子集，聚焦於 ASR 後端與對 ASR 管線重要的跨領域功能。完整的 119 後端 × 27 能力介面在產生的檢視中。

<!-- Generated from `crispasr --list-backends` + cross-cutting features. -->

| 功能 | whisper | parakeet | canary | cohere | granite | granite&#8209;4.1 | voxtral | voxtral4b | qwen3 | fc&#8209;ctc | wav2vec2 | glm&#8209;asr | kyutai&#8209;stt | firered | moonshine | moon&#8209;stream | omniasr | omniasr&#8209;llm | vibevoice | gemma4&#8209;e2b | mimo&#8209;asr | funasr | paraformer | sensevoice |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 原生時間戳 | ✔ | ✔ | ✔ | ✔ | | | | | | | | | ✔ | | | | | | | | | | | |
| CTC 時間戳 | | | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 單字級計時 | ✔ | ✔ | ✔ | ✔ | `-am` | ✔† | `-am` | `-am` | `-am` | `-am` | `-am` | `-am` | ✔ | `-am` | `-am` | `-am` | `-am` | `-am` | | `-am` | `-am` | `-am` | | `-am` |
| 每 token 信心度 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | |
| 語種自動偵測 | ✔ | ✔ | LID | LID | LID | LID | LID | LID | ✔ | LID | LID | ✔ | LID | LID | LID | LID | LID | LID | LID | ✔ | LID | LID | LID | ✔ |
| 語音翻譯 | ✔ | | ✔ | | ✔ | ✔ | ✔ | | ✔ | | | | | | | | | | | | | | | |
| 說話者分離 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 文法（GBNF） | ✔ | | | | | | | | | | | | | | | | | | | | | | | |
| 溫度取樣 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | |
| Beam search | ✔ | | | | ✔ | ✔ | ✔ | | ✔ | | | ✔ | ✔ | ✔ | ✔ | | ✔ | ✔ | | | | | | |
| Flash attention | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 標點開關 | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | ✔ | | ✔ | | ✔ | ✔ | | | | ✔ | | ✔ |
| 標點恢復 | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp | pp |
| 來源 / 目標語種 | | | ✔ | | ✔ | ✔ | ✔ | | ✔ | | | | | | | | | | | | | | | |
| 音訊問答（`--ask`） | | | | | * | * | ✔ | | * | | | * | | | | | | | | * | * | | | |
| 串流 | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| 自動下載（`-m auto`） | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| KV 量化（`CRISPASR_KV_QUANT`，另有各半 `_K` / `_V`） | | | | | ✔ | ✔ | ✔ | ✔ | ✔ | | | ✔ | | | | | | ✔ | | ✔ | ✔ | ✔ | | |
| mmap 權重（`CRISPASR_GGUF_MMAP`） | | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |
| TTS | | | | | | | | | | | | | | | | | | ✔ | | | | | |

上方矩陣涵蓋 24 個 ASR 後端。**未顯示的額外 ASR 後端**：`nemotron`（39 語串流 ASR，具快取意識的 FastConformer + RNN-T）、`lfm2-audio`（單一模型整合 ASR + TTS + S2S）、`moss-audio`（音訊理解 + ASR）、`moss-transcribe`（Qwen3-Omni encoder + Qwen3-1.7B ASR）、`hojo-asr`（Qwen3-Omni encoder + Conformer adapter + Qwen3-4B 多語 ASR）、`mini-omni2`（ASR + TTS + S2S）、`kugelaudio`（7B 音訊理解）。完整的 109 後端矩陣見 [`docs/feature-matrix.md`](docs/feature-matrix.md)。**僅 TTS 的後端**（`kokoro`、`qwen3-tts` + 變體、`vibevoice-tts`、`orpheus` + DE 變體、`chatterbox` / `chatterbox-turbo` / `chatterbox-nano` / `kartoffelbox-turbo` / `lahgtna-chatterbox`、`dia`、`bark`、`outetts`、`zonos`、`csm`、`f5-tts`、`irodori-tts`、`supertonic`、`parler-tts`、`speecht5`、`piper`、`fastpitch`、`pocket-tts`、`melotts`、`cosyvoice3`、`voxcpm2`、`tada-tts`）都帶有 TTS、AUTO_DOWNLOAD、TEMPERATURE 與 FLASH_ATTN 能力；各後端的複製 + 聲音包支援記錄於上方的 [Text-to-Speech 模型](#text-to-speech-models) 表格與 [`docs/tts.md`](docs/tts.md)。vibevoice 與 lfm2-audio 欄標示的是雙模式（ASR + TTS）後端。

**圖例：** ✔ = 原生/內建，`-am` = 透過 CTC 強制對齊器（`-am canary-ctc-aligner.gguf` 或 `-am qwen3-forced-aligner.gguf`），**LID** = 透過外部的語種識別前置步驟（`-l auto`），**pp** = 透過 `--punc-model` 後處理器（FireRedPunc 或 fullstop-punc），* = 實驗性或部分支援，† = 僅 PLUS 變體（用 `-owts` 的原生 `[T:N]` 單字時間戳；base 用 `-am`）。granite-4.1 涵蓋一般與 `-plus` 兩種變體；granite-4.1-nar 是僅有 encoder+projector 的非自迴歸變體（無 LLM 解碼功能）。**KV 量化** 列標示遵循 `CRISPASR_KV_QUANT={f16,q8_0,q4_0}` 的後端 —— 沒有 KV 快取的 CTC 式後端（parakeet、fc-ctc、wav2vec2、kyutai-stt、firered、moonshine 變體、omniasr-CTC）不適用。相同的後端也遵循各半的 `CRISPASR_KV_QUANT_K` / `CRISPASR_KV_QUANT_V` 覆寫（對應 llama.cpp 的 `--cache-type-k` / `--cache-type-v`），用於 K 對 V 的非對稱精度；常見配方 `K=q8_0 V=q4_0` 比對稱 Q8_0 多省約 40 % 的 KV 記憶體。**mmap 權重** 列標示使用 `core_gguf::load_weights()` 因而遵循 `CRISPASR_GGUF_MMAP=1` 的後端；whisper 本身使用上游的載入器，不受影響。用法 + 建議組合見 [`docs/cli.md`](docs/cli.md) 的記憶體佔用。

**說話者分離**作為後處理步驟，透過 `--diarize`：
- `energy` / `xcorr` —— 僅限立體聲，無額外相依
- `foxnose` —— **最佳精度，無外部相依**：WeSpeaker ResNet34-LM 嵌入 + GMM/BIC 說話者計數 + 光譜群集 + Viterbi 平滑。它會估計說話者人數，而不需事先提供；`--diarize-embedder auto` 會抓取 GGUF（24 MB，CC-BY-4.0）。在 VoxConverse dev 上 DER 7.3 %，而 `pyannote` + TitaNet 為 7.8 %，以輪次計分時對比上游參考的 3.07 % 為 3.18 %（[更多](docs/architecture.md#foxnose-diarize)）
- `pyannote` —— 原生 GGUF（無 Python、無 sherpa-onnx）；加上 `--diarize-embedder auto`（TitaNet）或 `--diarize-embedder indextts`（ECAPA-TDNN）即可在長檔案間獲得全域穩定的說話者 ID
- `sherpa` / `ecapa` —— 外部 [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) 子程序；對完整音訊全域執行一次以獲得一致的說話者 ID（#110）
- `vad-turns` —— 適用單聲道的間隙式代理

伺服器端點支援 `response_format=diarized_json`，輸出帶有正規化說話者字母（A, B, C …）的結構化說話者標記結果 —— 見 [`docs/server.md`](docs/server.md#diarized-json-format-206)。

完整參考 + 調校開關（群集閾值、最大說話者數、可插換的 embedder 適配器）：見 [`docs/cli.md#diarization`](docs/cli.md#diarization)。

**對沒有原生 LID 的後端做語種識別**：`--lid-backend whisper`（預設，75 MB ggml-tiny.bin）、`--lid-backend silero`（原生 GGUF，16 MB，95 語），或 `--lid-backend firered`（FireRedLID，1.7 GB，120 語 —— Conformer encoder + Transformer decoder）。

**音訊活性偵測**：`--vad` 使用預設的 Silero VAD（約 885 KB，自動下載）。每個 VAD 區段獨立轉錄，產生帶正確時間戳的個別 SRT/VTT 條目。要最佳的字幕輸出請用 `--vad --split-on-punct`。四種 VAD 後端：Silero（預設）、FireRedVAD（`-vm firered`，建議）、MarbleNet（`-vm marblenet`，439 KB，6 語）、Whisper-VAD-EncDec（`-vm whisper-vad`，實驗性）。

**標點恢復**（`--punc-model`）：基於 CTC 的後端輸出小寫且無標點。具名捷徑：`auto`/`firered`（中文+英文）、`fullstop`（EN/DE/FR/IT，XLM-R-large）、`punctuate-all`（12 語，XLM-R-base）、`pcs`（47 語，單一模型整合標點 + truecase + 句子邊界偵測）。或直接傳入 GGUF 路徑。也可透過 Python/Rust/Dart 包装器使用（`crispasr.PuncModel`）。

**Truecasing**（`--truecase-model`）：在小寫 ASR 輸出中恢復德文名詞/專有名詞的大寫。品質遞增的三個選項：`auto`（統計式，1.7 MB）、`crf`（帶脈絡的 CRF，8.5 MB）、`lstm`（BiLSTM 字元級，3.2 MB，**建議** —— F1 97.9%，可處理形容詞/名詞區分與正式的 "Ihnen"）。皆從 [`cstr/truecaser-de`](https://huggingface.co/cstr/truecaser-de) 自動下載。或用 `--punc-model pcs` 一次完成類神經標點 + truecasing（47 語）。

<details>
<summary>哪些後端會原生產出標點？</summary>

| 後端 | 標點 | 大小寫 | 備註 |
|---|:-:|:-:|---|
| whisper | ✔ | ✔ | 完整標點與大小寫 |
| parakeet | ✔ | ✔ | |
| canary | ✔ | ✔ | |
| cohere | ✔ | ✔ | 可用 `--no-punctuation` 切換 |
| granite | ✔ | ✔ | LLM 輸出 |
| voxtral | ✔ | ✔ | LLM 輸出 |
| voxtral4b | ✔ | ✔ | LLM 輸出 |
| qwen3 | ✔ | ✔ | LLM 輸出 |
| funasr | ✔ | ✔ | LLM 輸出（Qwen3-0.6B decoder）。中文字元帶有全形句點；mlt-nano 變體增加拉丁字元的大小寫 + 標點。 |
| sensevoice | ✔ | ✔ | 帶原生 ITN 的 CTC 輸出 —— 可用 `--no-punctuation` 關閉，它控制阿拉伯數字 vs 拼寫數字 + 逗號/句點的發出。 |
| paraformer | **否** | **否** | NAR 字元級輸出 —— 請加 `--punc-model` |
| gigaam | ✔（`e2e_*`） | ✔（`e2e_*`） | `e2e_*` 修訂版在 SentencePiece 詞彙表中帶有標點 + 大小寫 + 逆文字正規化。字元級的 `ctc` / `rnnt` 修訂版發出無標點的小寫西里爾 —— 但對它們仍會抑制自動恢復，因為自動啟用的 FireRedPunc 是中/英模型，會向俄文注入全形 CJK 標點。要帶標點的輸出請用 `e2e_*` 修訂版，或傳入明確的 `--punc-model`。 |
| glm-asr | ✔ | ✔ | LLM 輸出 |
| kyutai-stt | ✔ | ✔ | LLM 輸出 |
| moonshine | ✔ | ✔ | Encoder-decoder 輸出 |
| **fastconformer-ctc** | **否** | **否** | CTC —— 請加 `--punc-model` |
| **wav2vec2** | **否** | **否** | CTC —— 請加 `--punc-model` |
| **firered-asr** | **否** | **否** | CTC —— 請加 `--punc-model` |
| **omniasr**（CTC） | **否** | **否** | CTC —— 請加 `--punc-model` |
| **omniasr**（LLM） | ✔ | ✔ | 自迴歸 decoder |

其他可自由授權、未來可加入的替代方案：[felflare/bert-restore-punctuation](https://huggingface.co/felflare/bert-restore-punctuation)（MIT，英文，含 truecasing）、[xashru/punctuation-restoration](https://github.com/xashru/punctuation-restoration)（Apache-2.0，40+ 語，BiLSTM-CRF）。

</details>

**漸進式字幕輸出**（`--flush-after`）：預設下，非 whisper 後端會緩衝所有區段並在最後才印出輸出。若要即時字幕消費（PotPlayer、自訂播放器），請用 `--flush-after 1`，在它轉錄完每個 VAD 區段後立即將該 SRT 條目印至 stdout：

```bash
crispasr --backend parakeet -m parakeet.gguf --vad --flush-after 1 -osrt -f long_audio.wav
# SRT entries appear progressively as each segment finishes
```

**帶語種偵測的 JSON 輸出**：使用 `-l auto -oj` 時，JSON 輸出會包含偵測到的語種資訊：
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
### 我該選哪個後端？

| 需求 | 選擇 |
|---|---|
| 久經實戰、所有功能都開放 | **whisper** |
| 最低英文 WER | **cohere** |
| **最快**（CPU 上即時 16x） | **moonshine**（tiny）、**fc-ctc**（10x） |
| 多語 + 單字時間戳 + 快 | **parakeet**（2.9x RT） |
| 多語且需**明確語種控制** | **canary** |
| **語音翻譯**（X→en 或 en→X） | **canary**、**voxtral**、**qwen3** |
| **30 語 + 中文方言** | **qwen3** |
| **1600+ 語** | **omniasr**（CTC 或 LLM） |
| **即時串流 ASR**（原生增量 encoder，約 2× RT 餵入；次秒 token 目標延至第二階段） | **voxtral4b** |
| 最高品質離線 speech-LLM | **voxtral** |
| Apache 授權的 speech-LLM | **granite**、**voxtral**、**qwen3**、**omniasr-llm** |
| **輕量僅 CTC**（快、無 decoder） | **wav2vec2**、**fc-ctc**、**data2vec**、**omniasr** |
| **俄文** | **gigaam**（`e2e_rnnt` —— 平均 WER 8.4 %，標點 + ITN）、**whisper**、**qwen3** |
| **國語 + 中文方言** | **firered-asr**、**qwen3**、**glm-asr**、**funasr**、**paraformer**、**sensevoice** |
| **多語（31 語）speech-LLM** | **fun-asr-mlt-nano**、**qwen3**、**omniasr-llm**、**gemma4-e2b** |
| **多語（50+ 語）+ LID + 單次前向的音訊事件** | **sensevoice**（僅 encoder 的 CTC、非 AR，比 Whisper-Large 快 15×） |

### CPU 效能提示

Audio-LLM 後端（`qwen3`、`voxtral`、`granite`、`glm-asr` 等）執行完整的 transformer decoder 堆疊（28+ 層，2048 維），在 CPU 上比僅 encoder 的後端**慢非常多**。在較舊的雙核心硬體上它們可能跌到 0.01× 即時以下。若你只有 CPU：

- 優先選 **moonshine**（16× RT）、**fc-ctc**（10× RT）、**parakeet**（2.9× RT），
  或 **whisper** 以獲得可用速度。
- 用 `--flush-after 1` 在每個 VAD 切片完成時就看到結果，而不必等整個檔案。
- 用 `-pp` / `--print-progress` 在所有後端顯示逐切片進度指標（統一化後端顯示切片級進度；whisper 顯示 encoder 級進度）。
- 將模型量化到 Q4_K 或 Q5_K 以減少記憶體與運算。

### 對不原生做語種偵測的後端做語種偵測

Cohere、canary、granite、voxtral 與 voxtral4b 需要事先提供明確的語種碼。若你不知道語種，請傳 `-l auto`，crispasr 會在主要的 transcribe() 呼叫前先跑一個可選的 LID 前置步驟：

```bash
# 首次使用時下載 ggml-tiny.bin（75 MB，99 語）
crispasr --backend cohere -m $TC/cohere-transcribe-q5_0.gguf \
         -f unknown.wav -l auto
# crispasr[lid]: detected 'en' (p=0.977) via whisper-tiny
# crispasr: LID -> language = 'en' (whisper, p=0.977)
```

可用的 LID 提供者：

- `--lid-backend whisper`（預設）—— 透過 crispasr C API 使用一個小的多語 ggml-*.bin 模型。首次使用時自動下載約 75 MB。99 語。
- `--lid-backend silero` —— Silero 95 語分類器的原生 GGUF 移植。16 MB F32。以 ggml 圖執行（CPU 上多執行緒 SIMD，Metal/CUDA 上 GPU 卸載；Vulkan 上因待上游 kernel 修正，圖被路由到 CPU）。分析前 30 秒音訊（`CRISPASR_SILERO_LID_MAX_S` 可覆寫）；`CRISPASR_SILERO_LID_LEGACY=1` 恢復舊的純量路徑。
- `--lid-backend ecapa` —— **建議**：ECAPA-TDNN（Apache-2.0）。專為語種 ID 而建。在 TTS 基準上精度非常高。透過 `--lid-model` 提供兩個變體：
  - [`cstr/ecapa-lid-107-GGUF`](https://huggingface.co/cstr/ecapa-lid-107-GGUF) —— VoxLingua107，43 MB F16，107 語，ISO 碼（en, de, ...）。**預設。**
  - [`cstr/ecapa-lid-commonlanguage-GGUF`](https://huggingface.co/cstr/ecapa-lid-commonlanguage-GGUF) —— CommonLanguage，40 MB F16，45 語，全名（English, German, ...）。
- `--lid-backend firered` —— FireRedLID（Conformer encoder + Transformer decoder）。Q4_K（544 MB），120 語含中文方言。較慢但涵蓋更多語種。
- `--lid-backend probe` —— 完全不用第二個模型：問 **ASR 模型本身**。對模型宣告的每個語種將 20 秒剪輯轉錄一次，保留得分最高的候選（長度 × 文字 LID 一致度 × 相異 token 比例²，最後一項可捕捉錯誤語種提示所產生的重複輸出）。目前由 **cohere** 實作。偏好它的原因是正確性，而不只是省下下載：外部偵測器認識 99 語，而 Cohere Transcribe 只接受 14 —— 且其阿拉伯文微調只接受 `en`/`ar` —— 所以外部 LID 經常回傳模型從未訓練過的語種，而 Cohere 對錯誤語種會*流利地*回答而非失敗。probe 做不到這點。成本是每個候選一次 encode + 一次短 decode，所以它只對 ≤ 4 語的模型自動執行（`CRISPASR_COHERE_PROBE_MAX_LANGS`）；`CRISPASR_COHERE_PROBE_TEXTLID=0` 會去掉文字 LID 一致項。

  **上限的關鍵在於成本而非精度。** 在真實模型上量測：兩語的阿拉伯文微調對阿拉伯文剪輯選 `ar`（p=0.675）、對 `samples/jfk.wav` 選 `en`（p=0.647）；14 語 base 模型對全部 14 語 probe，兩者也都正確（`en` p=0.169、`ar` p=0.254）—— 只是比外部偵測器慢。encoder 輸出與語種無關，所以 probe **只 encode 一次**、逐候選 decode（encode 約占一次前向的 87 %）；對 14 候選的 probe 量測到 **12 s → 4-5 s**（對比每候選都 encode），輸出位元組相同。`CRISPASR_COHERE_PROBE_REUSE_ENC=0` 恢復素朴路徑。

  唯一值得知道的軟肋：要求模型輸出它*未*訓練過的語種時，可能得到乾淨的翻譯而非亂碼，而文字 LID 接著會確認它 —— 「流利的法文輸出」並不代表輸入是法文。這就是為何不相符的白名單很危險，且可量測：將 14 語清單強制套到兩語的阿拉伯文微調，其 `fr` probe 會回傳真正的法文並勝出。而真實 base 模型的 `fr` probe 則會語碼切換（"Et so, my fellow Americans…"，一致度 0.00）並落敗，如預期所願。

可用的 VAD 提供者：

- **Silero VAD**（預設）—— 約 885 KB，透過 `--vad` 自動下載。業界標準，久經測試。
- **FireRedVAD** —— 基於 DFSMN，2.4 MB，F1=97.57%。傳 `--vad -vm firered` 即自動下載。建議。
- **MarbleNet** —— NVIDIA 1D 可分離 CNN，439 KB，6 語（EN/DE/FR/ES/RU/ZH）。傳 `--vad -vm marblenet` 即自動下載。最小模型。（[`cstr/marblenet-vad-GGUF`](https://huggingface.co/cstr/marblenet-vad-GGUF)）
  - ⚠ **已知損壞。** 其 forward 長度相關 —— 一影格的 logits 會隨*總*剪輯長度改變，而該圖中沒有任何一層能合理地這樣做（全是 same-padding conv 或 1×1 linear）。CPU 與 CUDA 一致到 6 位，所以問題在圖或 ggml 的排定器，而非 kernel。影響：`-vm marblenet` 回傳接近空或錯誤的切片清單，而 VAD 失效移轉接著悄悄退回整段剪輯切片。重現方式見 `src/marblenet_vad.cpp` 中 `mbn_forward` 上方的註解。請改用 Silero 或 FireRedVAD。
- **Whisper-VAD-EncDec** *（實驗性）* —— Whisper-base encoder + TransformerDecoder head，22 MB Q4_K。於日文 ASMR 訓練；可能無法良好泛化到所有領域。傳 `--vad -vm whisper-vad`。比其他慢（約 1s vs 約 50ms）。（[`cstr/whisper-vad-encdec-asmr-GGUF`](https://huggingface.co/cstr/whisper-vad-encdec-asmr-GGUF)）

**裝置與批次。** Silero、FireRedVAD 與 MarbleNet 接受一個裝置與一個批次大小：`--vad-gpu`（或 `CRISPASR_VAD_GPU=cuda|vulkan|metal`）與 `--vad-batch N`。在 570 s 剪輯 / GTX 1050 Ti 上量測（每一行的 spans 都位元組相同）：

| VAD | CPU | GPU | 備註 |
|---|---|---|---|
| FireRedVAD | 36.8 s | **2.7 s** | 13.6×；圖路徑是完整的 ggml DFSMN |
| Silero | 5.7 s | 8.9 s | launch-bound —— 每個 32 ms 視窗約 83 個圖節點 |
| MarbleNet | 2.1 s | — | 見下方警告 |

FireRedVAD 是 GPU 明顯劃得來的那個，而且它在 CPU 上慢一個數量級 —— 這正是它值得卸載的原因。Silero 的 GPU 路徑存在是為了完整性而非速度：其 LSTM 遞迴是序列式的，所以 `--vad-batch` 無法合併任何工作，只能以圖邊界換取更大的圖（量測：寬度 1 時 2.73 s，寬度 512 時 3.89 s）。因此它預設為 1 —— 即既有的每視窗一個圖的行為。

Silero 的 `batch_size` **上限為 64**；要求更多會印出警告並使用 64。上限是記憶體限制，而非模型的性質 —— Silero 在任何批次都能跑，且在任何批次下批次化都是精確的。它來自批次化圖如何表達，加上執行期如何計價：展開 B 個視窗會使圖變成 83×B 個節點，而 ggml 的排定器會 eager 地 malloc 一個 `graph_size × 30 × 2 × sizeof(ggml_tensor)` 的 `context_buffer`，即每個圖節點約 24.8 KB 的 commit 計價 —— 批次 1 時 507 MB、64 時 657 MB、512 時 1.7 GB、4096 時約 9 GB。設上限不會損失什麼，因為在這裡更寬的圖反而*更慢*。

FireRedVAD 與 MarbleNet 不需要這種上限：它們切分影格軸而非展開它，所以它們的圖有固定的節點數，只有啟動記憶體隨批次增長。FireRedVAD 已驗證到 32768 影格（570 s 剪輯：GPU 上 3.70 s、43 個 spans，與所有其他寬度位元組相同）。WebRTC VAD 是一個無模型檔的 GMM，永遠在 CPU 上執行。

批次化永遠不會改變答案。Silero 將 N 個 LSTM 步驟展開進一個圖（遞迴是序列式的，所以這是同樣的算術、僅 launch 次數少 N 倍）。FireRedVAD 與 MarbleNet 將影格軸切進帶有模型收受脈絡的區塊，並丟棄依賴區塊邊緣的輸出 —— 對 FireRedVAD 這也正是使 ggml 每個 conv 的 im2col 矩陣保持有界（T × N × P 個浮點數，10 分鐘檔案單一 conv 約 580 MB）的原因。

VAD 執行期間，它每秒向 stderr 印一行進度。模型只 bump 一個 atomic 計數器；背景執行緒對其取樣，所以熱循環從不觸碰 I/O。`CRISPASR_VAD_PROGRESS=0` 可靜音，`CRISPASR_VAD_PROGRESS_MS` 可改頻率。

傳 `--lid-backend off` 可完全跳過 LID。

### 文字語種識別（ASR 後 / 獨立）

音訊 LID（上方）標記的是**說了什麼**；文字 LID 標記的是**寫了什麼**。文字 LID 在轉錄稿或任何 UTF-8 字串上執行，無需重跑音訊模型就能路由 ASR 後的管線（翻譯、標點、字幕選用）。三個 GGUF 家族、一支二進位檔 —— 派發器依 `general.architecture` 選取：

| 後端 | 標籤 | 大小（F16） | 授權 | HF repo |
|---|---:|---:|---|---|
| **CLD3**（Google compact language detector v3） | 109 ISO 639-1 | **440 KB** | Apache-2.0 | [`cstr/cld3-GGUF`](https://huggingface.co/cstr/cld3-GGUF) |
| **GlotLID-V3**（cis-lmu fastText） | 2102 ISO 639-3 + 文字系統 | 250 MB | Apache-2.0 | [`cstr/glotlid-GGUF`](https://huggingface.co/cstr/glotlid-GGUF) |
| **LID-176**（Facebook fastText） | 176 ISO 639-1 | 63 MB | CC-BY-NC-4.0¹ | [`cstr/fasttext-lid176-GGUF`](https://huggingface.co/cstr/fasttext-lid176-GGUF) |

¹ LID-176 是 **CC-BY-NC-4.0** —— 僅限非商業使用。CLD3 + GlotLID-V3 為 Apache-2.0，無此限制。要最小、最快的路徑選 CLD3；要最大涵蓋（低資源語種）選 GlotLID；僅在你需要它特定的 176 標籤空間並接受其非商業條款時才選 LID-176。

**獨立 CLI** —— 依 GGUF arch 自動路由，具自動下載：

```bash
crispasr-lid -m auto --text "Bonjour le monde"        # → cstr/cld3-GGUF（預設，約 440 KB）
crispasr-lid -m auto:glotlid --text "Bonjour le monde" -k 5
crispasr-lid -m auto:lid-fasttext176 --text "Hallo Welt"
# 或傳入明確的路徑 / 正規檔名（於註冊表查詢）：
crispasr-lid -m cld3-f16.gguf --text "你好世界"
# zh	0.997816
echo "Привет мир" | crispasr-lid -m auto --quiet
# ru	0.907322
```

**ASR 後管線** —— `--lid-on-transcript` 在組好的轉錄稿上執行同樣的派發器（也接受 `auto[:variant]`）：

```bash
crispasr -m ggml-tiny.bin -f speech.wav --lid-on-transcript auto
# (transcript on stdout)
# lang=de	conf=0.997123	backend=lid-cld3
```

派發器（`src/text_lid_dispatch.{h,cpp}`）是一個很薄的 C ABI 門面 —— 每次呼叫僅一個整數比較；逐階段 diff 檢測台在 8 個多語 smoke 樣本上以 cos≥0.999 全綠。

---

<a id="install--build"></a>
## 安裝與建置

**不想自己建置？** Windows、macOS 與 Linux 的預建二進位檔在
[releases 頁面](https://github.com/CrispStrobe/CrispASR/releases/latest) ——
該取哪個檔案見[從這裡開始](#start-here)。本節其餘部分是從原始碼建置用的。

```bash
git clone --recursive https://github.com/CrispStrobe/CrispASR
cd CrispASR
# 已在沒有 --recursive 的情況下 clone？初始化內附的 ggml 子模組：
#   git submodule update --init --recursive
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j$(nproc)
```

`ggml/` 子模組為必要。若你 clone 時沒有 `--recursive`，請先執行
`git submodule update --init --recursive` —— 否則 CMake 會停下並告訴你正是要做這件事。

會產出 `build/bin/crispasr`（主 CLI）、`build/bin/crispasr-quantize`、
以及 `build/bin/crispasr-diff`。執行期不需 Python、PyTorch 或 pip —— 只需 C++17 編譯器與 CMake 3.14+。

若要 GPU 加速，於 configure 時加入對應的 ggml 旗標：

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_CUDA=ON     # NVIDIA
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_METAL=ON    # Apple Silicon
cmake -B build -DCMAKE_BUILD_TYPE=Release -DGGML_VULKAN=ON   # 跨廠牌
```

**完整指南見 [`docs/install.md`](docs/install.md)**：
所有 GPU 後端（CUDA / Metal / Vulkan / MUSA / SYCL）、Windows
便利腳本、ffmpeg 攝取、可選的 BLAS、glibc 說明，
以及 `scripts/dev-build.sh` 包装器。

若建置成功但二進位檔無輸出就離開，見
[`docs/troubleshooting.md`](docs/troubleshooting.md)。

---

<a id="quick-start"></a>
## 快速上手

下方是更深入的 ASR 例子。若這是你的初次執行，請改用
[從這裡開始](#start-here)。TTS 的可執行指南是 [docs/tts.md](docs/tts.md)
（下方的 [Text-to-Speech](#text-to-speech-models) 是模型目錄）。

### Whisper（歷史路徑，與上游 whisper.cpp 位元組相同）

```bash
# 下載一個 whisper 模型（與上游 whisper.cpp 相同）
./models/download-ggml-model.sh base.en

./build/bin/crispasr -m models/ggml-base.en.bin -f samples/jfk.wav
# [00:00:00.000 --> 00:00:07.940]   And so my fellow Americans ask not what your country can do for you
# [00:00:07.940 --> 00:00:10.760]   ask what you can do for your country.
```

### Parakeet（多語、免費單字時間戳、最快）

```bash
# 抓取量化模型（約 467 MB）
curl -L -o parakeet.gguf \
    https://huggingface.co/cstr/parakeet-tdt-0.6b-v3-GGUF/resolve/main/parakeet-tdt-0.6b-v3-q4_k.gguf

./build/bin/crispasr -m parakeet.gguf -f samples/jfk.wav
# Auto-detected backend 'parakeet' from GGUF metadata.
# And so, my fellow Americans, ask not what your country can do for you, ask what you can do for your country.

# 單字級時間戳（每個單字一行）
./build/bin/crispasr -m parakeet.gguf -f samples/jfk.wav -ml 1
```

### Canary（明確語種、語音翻譯）

```bash
# 轉錄（來源 == 目標）
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -sl de -tl de

# 翻譯（德文語音 → 英文文字）
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -sl de -tl en

# …或用熟悉的 crispasr 旗標：
./build/bin/crispasr --backend canary -m canary-1b-v2-q5_0.gguf -f audio.de.wav -l de --translate
```

### Voxtral（具自動下載的 speech-LLM）

```bash
# 首次執行會用 curl 下載約 2.5 GB 到 ~/.cache/crispasr/，然後執行
./build/bin/crispasr --backend voxtral -m auto -f samples/jfk.wav

# 後續執行使用已快取的檔案
./build/bin/crispasr --backend voxtral -m auto -f samples/jfk.wav -l en
```

### Qwen3-ASR（30 語 + 中文方言）

```bash
# 0.6B（預設，約 500 MB）
./build/bin/crispasr --backend qwen3 -m auto -f audio.zh.wav

# 1.7B（更高品質，約 1.3 GB）—— 同時支援 -hf 與非 -hf 來源模型
./build/bin/crispasr --backend qwen3 -m qwen3-1.7b --auto-download -f audio.wav

# 日文動漫/美少女遊戲微調（約 1.3 GB）
./build/bin/crispasr --backend qwen3 -m qwen3-ja-anime --auto-download -f anime.wav
```

**長音訊：** 預設是安全的 30 s 分塊。`--chunk-seconds 0` 會將整個檔案以**單次**前向解碼
（在多分鐘剪輯上與參考模型逐字相同，#218）—— 但 encoder 的完整 attention 是音訊長度的
O(N²)，所以在 16 GB 機器上請將單次剪輯控制在約 10 分鐘內。長篇請優先使用一般的
`-q4_k`/`-q8_0` GGUF 而非 `-imatrix` 變體（見模型卡）。

### GLM-ASR-Nano（國語 + 方言 + 粵語 + 英文，1.5B）

```bash
./build/bin/crispasr --backend glm-asr -m auto -f audio.wav

# 單次前向的長音訊（最多 655 s —— 30 s encoder 視窗、單一 LLM 提示，
# 與 HF/zai 參考相同的佈局；在 #218 剪輯上與它逐字相同）：
./build/bin/crispasr --backend glm-asr -m auto --chunk-seconds 0 -f long.wav
```

注意：單次前向模式下模型（如同參考）會跳過開頭的非語音音訊；預設的 30 s 分塊
模式會轉錄這類剪輯的更多内容。自訂 `--ask` / 非英文 `--language` 提示需要一個
內嵌 BPE 合併（baked merges）的 GGUF（2026-07 重新發布；舊 GGUF 會連同警告退回預設轉錄提示）。

### MiMo-V2.5-ASR（國語 + 方言 + 英文，7.5B Qwen2 LM）

```bash
# 下載 LM + 音訊 tokenizer（tokenizer 是一個獨立的模型）
huggingface-cli download cstr/mimo-asr-GGUF mimo-asr-q4_k.gguf \
    --local-dir ~/.cache/crispasr
huggingface-cli download cstr/mimo-tokenizer-GGUF mimo-tokenizer-q4_k.gguf \
    --local-dir ~/.cache/crispasr

# 轉錄（若 tokenizer 就在 LM 旁邊會自動發現）
./build/bin/crispasr \
    --backend mimo-asr \
    -m ~/.cache/crispasr/mimo-asr-q4_k.gguf \
    --codec-model ~/.cache/crispasr/mimo-tokenizer-q4_k.gguf \
    -f samples/jfk.wav
# Output: And so, my fellow Americans, ask not what your country can do
# for you. Ask what you can do for your country.
```

建議的量化是 4.5 GB 的 Q4_K；F16（14.9 GB）在推論時需要約 16 GB RAM。
JFK 與上游 Python `MimoAudio.asr_sft` 參考逐字相同；在 M1+Metal 上的效能
約 0.3× 即時（Q4_K 每步反量化是瓶頸 —— F16 + KV 重用的後續改善排在 PLAN #51a/b/c）。

### Wav2Vec2（輕量 CTC，任何 HF Wav2Vec2ForCTC 模型）

```bash
# 英文（Q4_K 量化，212 MB —— 比 F16 小 6 倍）
curl -L -o wav2vec2-en-q4k.gguf \
    https://huggingface.co/cstr/wav2vec2-large-xlsr-53-english-GGUF/resolve/main/wav2vec2-xlsr-en-q4_k.gguf

./build/bin/crispasr -m wav2vec2-en-q4k.gguf -f samples/jfk.wav
# and so my fellow americans ask not what your country can do for you ask what you can do for your country

# 德文
curl -L -o wav2vec2-de-q4k.gguf \
    https://huggingface.co/cstr/wav2vec2-large-xlsr-53-german-GGUF/resolve/main/wav2vec2-xlsr-de-q4_k.gguf

./build/bin/crispasr -m wav2vec2-de-q4k.gguf -f audio.de.wav

# 轉換任何 HuggingFace Wav2Vec2ForCTC 模型：
python models/convert-wav2vec2-to-gguf.py \
    --model-dir jonatasgrosman/wav2vec2-large-xlsr-53-german \
    --output wav2vec2-de.gguf --dtype f32
# 之後可選量化：
./build/bin/crispasr-quantize wav2vec2-de.gguf wav2vec2-de-q4k.gguf q4_k
```

---

## 串流、TTS 與 HTTP 伺服器

CrispASR 有三個值得各自擁有文件頁的功能領域：

- **[串流與即時轉錄](docs/streaming.md)** —— `--stream`、
  `--mic`、`--live`、滑動視窗分塊、每 token 信心度。
- **[文字轉語音（TTS）](docs/tts.md)** —— Kokoro（多語、最小）、Qwen3-TTS（最高保真度、聲音複製）、VibeVoice
  （最低延遲串流）、Orpheus（3 B Llama + SNAC）、Chatterbox
  （flow-matching + HiFT 聲碼器，透過 Kartoffelbox 支援德文）、IndexTTS、
  VoxCPM2，以及 CosyVoice3（9 語 + 18 種中文方言；燒錄聲音庫 +
  任意 WAV 複製）。聲音包、語種路由，以及 qwen3-tts
  環境開關。所有 TTS 輸出都會加浮水印；嵌入後
  驗證若在信心度低時會警告。用
  `--detect-watermark file.wav` 可檢查任何 WAV 的 AI 浮水印。
- **[伺服器模式（HTTP API）](docs/server.md)** —— 持久模型，
  OpenAI 相容的 `/v1/audio/transcriptions`（ASR）與
  `/v1/audio/speech` + `/v1/voices`（TTS，在任何已載入的
  CAP_TTS 後端上自動啟用）、逐請求的聲音 + 速度 + 指示、CORS、
  長句分塊、API 金鑰、Docker Compose、預建
  CUDA 映像。
- **[併發、平行與擴展](docs/concurrency.md)** —— 一次
  轉錄已使用多核心；伺服器可併發接受請求，但
  預設在單一模型上將推論序列化；
  `--server-workers N` 會執行 N 個模型實例，使純 ASR 請求
  能併發執行；而對大量/吞吐量工作負載，則用行程級扇出
  （`xargs -P` / GNU `parallel`）或負載平衡器後的 N 個副本。也涵蓋
  *不*支援的项目（批次化多串流推論、
  PagedAttention）及其原因。

每個最快的尝试：

```bash
# 從麥克風串流
crispasr --mic -m model.gguf

# 透過自動下載的 VibeVoice 做 TTS（首次執行約 636 MB）
crispasr --backend vibevoice-tts -m auto --tts "Hello world" --tts-output hello.wav

# GPU 上的 CosyVoice3；夥伴模型在 LLM 旁自動下載
crispasr --backend cosyvoice3-tts -m auto --tts "Hello world" --tts-output cosy.wav

# CosyVoice3 快速模式：5 個 flow 步驟，而非品質預設的 10
COSYVOICE3_FLOW_STEPS=5 crispasr --backend cosyvoice3-tts -m auto \
  --tts "Hello world" --tts-output cosy-fast.wav

# 持久 HTTP 伺服器，OpenAI 相容
crispasr --server -m model.gguf --port 8080
curl -F "file=@audio.wav" http://localhost:8080/v1/audio/transcriptions

# 透過 HTTP 的 TTS —— 載入一個 TTS 後端，打 /v1/audio/speech
crispasr --server --backend qwen3-tts-customvoice -m auto --voice-dir ./voices --port 8080
curl http://localhost:8080/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"input":"Hello world","voice":"vivian"}' -o out.wav
```

CosyVoice3 預設使用批次化的 classifier-free guidance 與請求大小的 KV
快取。燒錄聲音只載入 LLM、flow、HiFT 與聲音庫；較大的 S3 tokenizer 與 CAMPPlus
夥伴會在首次請求 `.wav` 複製聲音時延遲載入。

---

## CLI 參考

常用旗標：

```bash
crispasr -m auto --backend parakeet -f audio.wav --vad -osrt --split-on-punct
```

| 旗標 | 意義 |
|---|---|
| `-m FNAME` / `--backend NAME` | 模型路徑（或 `auto`）與強制後端 |
| `-f FNAME` | 輸入音訊（可重複；接受位置引數） |
| `--vad` | Silero VAD 分塊 —— 對多分鐘音訊強烈建議 |
| `-osrt` / `-ovtt` / `-otxt` / `-oj` / `-ojf` | 輸出格式（也有 `-ocsv`、`-olrc`） |
| `-am FNAME` | 用於 LLM 後端單字時間戳的 CTC 對齊器 GGUF |
| `--align-only` | 獨立強制對齊：文字/`.srt` + 音訊 → 帶時間戳的 SRT/JSON（不需 ASR）；`.srt` 輸入保留其 cue 並重新計時（`--align-granularity auto\|word\|segment`） |
| `-tp F` / `-bs N` | 取樣溫度 / beam search 寬度 |
| `-n N` / `--frequency-penalty F` | 產生 token 上限 / 受支援自迴歸 ASR 後端的選入重複 token 懲罰 |
| `-l auto` / `--detect-language` | 對無原生語種偵測的後端做 LID 前置 |
| `--hotwords "A,B,C"` | 脈絡偏置 —— 在 CTC/TDT 解碼或 LLM 提示期間提升命名術語 |
| `-ck N` | VAD 關閉時的退回分塊大小（預設 30 s） |
| `--list-backends` | 印出能力矩陣並離開 |

**完整參考見 [`docs/cli.md`](docs/cli.md)**：每個
旗標、VAD 細節、CTC 對齊工作流程、輸出 JSON 佈局、
自動下載註冊表，以及支援的音訊格式。**見
[`docs/bindings.md`](docs/bindings.md)** 瞭解 Python / Rust / Dart /
Go / Java / JavaScript / Ruby / 行動。

---

## 架構、貢獻、迴歸矩陣

CrispASR 結構為 `src/` 中穩定的 C-ABI（每個演算法：
VAD、分離、LID、對齊、快取、註冊表），由所有語言
包装器消費，在 `examples/cli/` 中則是薄的呈現層。
每個模型的執行期位於 `src/{whisper,parakeet,canary,...}.cpp`，
共用 `src/core/` 的原語（mel、ffn、attention、GGUF
載入器、FastConformer / Conformer / Granite-LLM 區塊等）。

- **[`docs/architecture.md`](docs/architecture.md)** —— 完整的分層
  佈局、`src/` 與 `examples/cli/` 的逐檔導覽、
  逐後端內部表格、迴歸紀律。
- **[`docs/contributing.md`](docs/contributing.md)** —— 以五個檔案
  新增一個後端、clang-format-18 設定、
  `crispasr-diff` 的 PyTorch ground-truth 工作流程，以及
  TTS 音訊餘弦 vs 參考的迴歸目標。
- **[`docs/regression-matrix.md`](docs/regression-matrix.md)** ——
  `tools/test-all-backends.py` 能力分級、快取模式
  （`keep` / `ephemeral`）、CI 用的 `--skip-missing`。

**共用函式庫**（與 CrispEmbed 跨倉庫）：
- `crisp_audio/` —— Whisper 形狀的音訊 encoder（Conv-stem + Transformer）
- `crisp_punc/` —— 標點恢復（FireRedPunc + PCS）
- `crisp_lid/` —— 基於文字的語種識別（fastText + CLD3）
- `crisp_truecase/` —— truecasing（統計式 + CRF + BiLSTM）

兩者都是自包含、附 CMakeLists.txt 的靜態函式庫。CrispEmbed
透過 `add_subdirectory(../CrispASR/crisp_*/)` 連結它們；CrispASR 直接
使用它們。若共用目錄不存在，兩個倉庫都會退回來源檔的本地
副本。

基準測試見 [`PERFORMANCE.md`](PERFORMANCE.md)；逐 session 的 port 日誌
與 bug 類別的教訓，見 [`LEARNINGS.md`](LEARNINGS.md)。

---

## 量化模型

`build/bin/crispasr-quantize` 是一個單一的、模型無關的 GGUF
重新量化工具，適用於所有支援的模型家族
（Whisper、Parakeet、Canary、Cohere、Voxtral、Qwen3、Granite、Wav2Vec2、
MiMo-ASR、GLM-ASR、Moonshine、VibeVoice、Kokoro、Qwen3-TTS、…）：

```bash
./build/bin/crispasr-quantize input.gguf output.gguf q4_k
```

**完整指南見 [`docs/quantize.md`](docs/quantize.md)**：
支援的量化類型、K-quant 對齊退回、每個後端的建議量化，
以及每個架構的實例。

---

<a id="gpu-backend-selection"></a>
## GPU 後端選取

所有後端都使用 `ggml_backend_init_best()`，它會自動選取優先度最高的已編譯後端：CUDA > Metal > Vulkan > CPU。若要強制特定後端：

```bash
# 即使有 CUDA 也強制 Vulkan
crispasr --gpu-backend vulkan -m model.gguf -f audio.wav

# 釘選特定 GPU（對有 iGPU + dGPU 的 Vulkan 系統很有用）
crispasr --gpu-backend vulkan -dev 1 -m model.gguf -f audio.wav

# 強制 CPU（對基準測試很有用）
crispasr -ng -m model.gguf -f audio.wav

# CUDA 統一記憶體（VRAM 耗盡時交換到 RAM）
GGML_CUDA_ENABLE_UNIFIED_MEMORY=1 crispasr -m model.gguf -f audio.wav
```

建置旗標：`-DGGML_CUDA=ON`、`-DGGML_METAL=ON`、`-DGGML_VULKAN=ON`。

備註：
- `--gpu-backend vulkan` 選取 Vulkan 後端，但不選取要用哪個實體 GPU。用 `-dev N` 選取 Vulkan 裝置索引。
- 在某些 Windows 筆電上，Vulkan 裝置 `0` 是 Intel iGPU，NVIDIA GPU 是 `1`。若 Vulkan 意外地慢，用 `-dev 1` 重跑。
- Windows 便利腳本 `build-vulkan.bat` 會在 `build-vulkan\bin\crispasr.exe` 建立一個獨立支援 Vulkan 的二進位檔。

---

<a id="debugging--profiling"></a>
## 除錯與剖析

對大多數後端，`-v` / `--verbose` 會呈現逐階段計時與裝置選擇。對無頭 / 函式庫使用（CLI 旗標未貫通的地方），請改用 `CRISPASR_VERBOSE=1`。

```bash
# 逐階段計時分解（mel / encoder / prefill / decode）：
crispasr -v --backend gemma4-e2b -m model.gguf -f audio.wav
# gemma4_e2b: mel 128x1099 (17.2 ms)
# gemma4_e2b: encoder done: 1536x275 (719.0 ms)
# gemma4_e2b: prefill done, first_token=3133 (1464.0 ms)
# gemma4_e2b: decoded 25 tokens (7748.3 ms total)
# crispasr: transcribed 11.0s audio in 7.75s (1.4x realtime)

# 對受閘門模型（Voxtral、Gemma4-E2B、…）的 Hugging Face 存取：
HF_TOKEN=hf_xxx crispasr -m auto --backend gemma4-e2b -f audio.wav
```

伺服器有自己的驗證環境變數：`CRISPASR_API_KEYS`（見
[伺服器模式](docs/server.md)）。

<details>
<summary><b>逐後端的除錯 / 基準 / dump-dir 環境變數（開發者）</b></summary>

這些在 port 新後端或追查迴歸時很有用。
`*_BENCH=1` 開關即使沒有 `-v` 也會發出逐階段計時；`*_DEBUG=1`
開關會發出逐步診斷印出；`*_DUMP_DIR=` 路徑會寫出逐階段 F32 張量，
以便與 PyTorch 參考做 diff 測試（見 [Debug a new backend against PyTorch ground truth](docs/contributing.md#debug-a-new-backend-against-pytorch-ground-truth)）。

| 環境變數 | 用途 |
| --- | --- |
| `CRISPASR_VERBOSE=1` | 對任何後端強制詳細模式（與 `-v` 旗標並行）。 |
| `CRISPASR_DUMP_DIR=path/` | 供 `crispasr-diff` 檢測台使用的一般逐階段 F32 張量 dump。 |
| `GEMMA4_E2B_BENCH=1` | Gemma-4-E2B 後端的逐階段計時。 |
| `COHERE_BENCH=1` / `COHERE_DEBUG=1` | Cohere transcribe 的逐階段計時 / 逐步診斷。 |
| `COHERE_PROF=1` | Cohere 圖層級剖析（逐 op 計時）。 |
| `COHERE_THREADS=N` | 覆寫 Cohere 後端的執行緒數。 |
| `COHERE_DEVICE=cpu\|cuda\|metal\|vulkan` | 強制 Cohere 後端到特定裝置。 |
| `COHERE_DUMP_ATTN=path/` | Dump Cohere 的 attention 啟動值（由 diff 檢測台使用）。 |
| `FIRERED_BENCH=1` | FireRedASR 後端的逐階段計時。 |
| `FIREREDPUNC_DEBUG=1` | FireRed 標點後處理步驟的逐步診斷。 |
| `MOONSHINE_STREAMING_BENCH=1` | moonshine-streaming 的逐階段計時。 |
| `OMNIASR_BENCH=1` / `OMNIASR_DEBUG=1` / `OMNIASR_DUMP_DIR=` | OmniASR 的逐階段計時、診斷與階段 dump。 |
| `PARAKEET_DEBUG=1` | Parakeet TDT 的逐步診斷（joint 網路、blank-id 合理性檢查）。 |
| `QWEN3_TTS_BENCH=1` / `QWEN3_TTS_DEBUG=1` / `QWEN3_TTS_DUMP_DIR=` | Qwen3-TTS 的逐階段計時、診斷與階段 dump。 |
| `VIBEVOICE_BENCH=1` / `VIBEVOICE_DEBUG=1` / `VIBEVOICE_DUMP_DIR=` | VibeVoice ASR 的逐階段計時、診斷與階段 dump。 |
| `VIBEVOICE_REF_FEATURES=path` | 以已存的特徵張量取代即時 encoder（迴歸檢測台）。 |
| `VIBEVOICE_TTS_DUMP=path/` | VibeVoice TTS 的逐階段 dump（token ID、base/TTS 隱層、neg 條件、frame-0 noise/v_cfg/latent/acoustic_embed）供 diff 檢測台使用。 |
| `VIBEVOICE_TTS_DUMP_PERFRAME=1` | 以 `perframe_<stage>_f<NNN>.bin` 寫出逐影格的 VibeVoice TTS dump。與 `VIBEVOICE_TTS_DUMP=path/` 和 `VIBEVOICE_TTS_NOISE=path` 搭配，對 `tools/run_official_vibevoice.py` 做逐階段 AR diff。 |
| `VIBEVOICE_TTS_TRACE=1` | 額外的一行 trace（negative-condition prefill rms、已載入的 scaling/bias 因子）。效果同函式庫詳細度 ≥ 2；它沒有 CLI 旗標（`-v` 將詳細度上限為 1）。 |
| `VIBEVOICE_VOICE_AUDIO=path.wav` | 供 1.5B-base TTS 在無 `.gguf` 聲音快取時的參考聲音 WAV。 |
| `VIBEVOICE_TTS_NOISE=path` | 覆寫逐影格的高斯初始噪聲。扁平的小端 float32 `[N_frames, vae_dim]` —— 通常是 `tools/run_official_vibevoice.py` 寫出的 `noise.bin`。 |
| `VIBEVOICE_VAE_BACKEND=cpu\|metal\|cuda\|vulkan` | 將 VAE decoder 釘選到特定後端。 |
| `WAV2VEC2_BENCH=1` / `WAV2VEC2_VERBOSE=1` / `WAV2VEC2_DUMP_DIR=` | wav2vec2 的逐階段計時、詳細圖 trace 與階段 dump。 |
| `CRISPASR_VOXTRAL4B_STREAM_TIMING=1` | voxtral4b 串流路徑的逐階段計時（encoder drain / prefill / first-text-token / decode-step p50/p95）。 |
| `CRISPASR_VOXTRAL4B_STREAM_CHUNK_MS=N` | 覆寫內部 encoder 分塊大小（預設 240 ms）。必須是 80 ms 的倍數。越大=餵入越快（kernel-launch 分攤），但即時字幕延遲下限越長。 |
| `CRISPASR_VOXTRAL4B_STREAM_BATCH_ENCODER=1` | 迴歸除錯：忽略串流 encoder 的 audio_embeds，於 flush 時重跑整個批次 encoder。 |
| `CRISPASR_VOXTRAL4B_STREAM_DEBUG=1` / `CRISPASR_VOXTRAL4B_STREAM_DIFF=1` | 逐步 decode 印出 / 與批次 encoder 並排的 encoder 餘弦。 |
| `CRISPASR_VOXTRAL4B_STREAM_LIVE=1` | 餵入期間解碼的即時字幕（PLAN #7 第 3 階段）。餵入期間輪詢的 `get_text()` 會回傳漸進式轉錄稿。預設 OFF（PTT 語意）。包装器：Python `Session.stream_open(live=True)`、Rust `stream_open_ex(.., live: true)`。 |
| `CRISPASR_VOXTRAL4B_STREAM_DECODER_THREAD=1` | 解碼器工作執行緒（PLAN #7 第 4 階段，暗示 live 模式）。讓 `feed()` 能在 encoder 分塊間 return 而不等解碼循環 —— 對麥克風驅動的工作負載很有用。在 M1 上 Metal 佇列會將 encoder 與 decoder 序列化，因此總-wall-clock 不變；具 kernel 級平行的更快 GPU 才會看到真正的重疊。 |
| `CRISPASR_VOXTRAL4B_FUSED_QKV=0` | 退出執行期的 fused-QKV LLM 路徑（預設開，在 M1 Q4_K 上約 7-8 % 解碼加速、約 500 MB 額外記憶體）。 |
| `CRISPASR_QWEN3_ASR_FUSED_QKV=0` | 退出 qwen3-asr 的執行期 fused-QKV LLM 路徑（預設開；在 F16/F32/Q4_K/Q8_0/... 上皆可行）。 |
| `CRISPASR_VOXTRAL_FUSED_QKV=1` | 加入 voxtral 3B 的執行期 fused-QKV LLM 路徑。預設關（在 JFK 形狀的解碼上無可測量的加速；對解碼占主的長篇工作負載有用）。 |
| `QWEN3_TTS_FUSED_QKV=1` | 加入執行期的 fused-QKV talker 路徑。 |
| `GRANITE_DISABLE_ENCODER_GRAPH=1` | 強制 granite-speech / -plus / -nar 的 encoder 回到逐層 CPU 循環（較慢，但保留下來供除錯）。帶逐層 Shaw RPE 的單一 ggml-graph encoder 是預設，且與 CPU 循環幾近位元相同，同時三種變體端到端都快約 2×。 |
| `CRISPASR_NO_REL_POS=1` | 去除 Gemma-4 音訊 encoder 的相對位置偏差（僅限開發）。 |
| `ECAPA_REF_FBANK=path` | 供 ECAPA-TDNN LID 模型使用的參考 filterbank 張量（迴歸檢測台）。 |
| `CRISPASR_SHERPA_LID_BIN=path` | 覆寫自動偵測到的 sherpa-onnx LID 二進位檔。 |
| `CRISPASR_ARG_DEVICE=N` | 未傳 `-dev` 時的預設 GPU 裝置索引。 |
| `GGML_CUDA_ENABLE_UNIFIED_MEMORY=1` | 讓 CUDA 在 VRAM 耗盡時交換到 RAM。 |
| `GGML_VK_VISIBLE_DEVICES` / `CUDA_VISIBLE_DEVICES` | 標準的 ggml/CUDA 裝置可見度過濾器。 |

對受閘門模型的下載，`HF_TOKEN` 與 `HUGGING_FACE_HUB_TOKEN` 都會被
承認（依此順序）。

</details>

---

<a id="credits"></a>
## 致謝

- **[whisper.cpp](https://github.com/ggml-org/whisper.cpp)** —— 本分支所基於的原始 ggml 推論引擎與 Whisper 執行期
- **[ggml](https://github.com/ggml-org/ggml)** —— 一切賴以運行的張量函式庫
- **NVIDIA NeMo** —— parakeet-tdt-{0.6b-v2,0.6b-v3,1.1b}、parakeet-tdt_ctc-{110m,1.1b,0.6b-ja}、parakeet-ctc-{0.6b,1.1b}、canary-1b-v2、canary-ctc 對齊器，以及 FastConformer-CTC 家族（stt_en_fastconformer_ctc_{large,xlarge,xxlarge}，加上 stt_*_fastconformer_hybrid_large[_pc] 機群的 CTC 分支：en-pc, de, es, fr, it, nl, pl, ru, ua, hr, be, ar, fa, ka, hy, uz, kk-ru —— 全部既可作 ASR 後端，也可作約 82 MB 的緊湊 `-am` 強制對齊器）
- **Cohere** —— cohere-transcribe-03-2026
- **Qwen 團隊（Alibaba）** —— Qwen3-ASR-0.6B、Qwen3-ASR-1.7B、Qwen3-ForcedAligner-0.6B
- **Mistral AI** —— Voxtral Mini 3B 與 4B Realtime
- **IBM Granite 團隊** —— Granite Speech 3.2-8b、3.3-2b、3.3-8b、4.0-1b
- **Meta / wav2vec2** —— wav2vec2 CTC 模型（XLSR-53 英文、德文，透過任何 Wav2Vec2ForCTC checkpoint 的多語）
- **[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)** —— 透過子程序的可選分離（ONNX 模型）
- **[Silero](https://github.com/snakers4/silero-vad)** —— VAD（原生 GGUF）與語種識別（原生 GGUF，95 語）
- **[pyannote](https://github.com/pyannote/pyannote-audio)** —— 說話者分離分段（原生 GGUF 移植）
- **[miniaudio](https://miniaud.io/)** + **[stb_vorbis](https://github.com/nothings/stb)** + **[libopus/opusfile](https://opus-codec.org/)** —— 內嵌/連結的音訊解碼器（WAV/MP3/FLAC/AIFF/OGG/Opus，無需 ffmpeg；AAC/M4A/ALAC 透過 Apple AudioToolbox）
- **[glint](https://github.com/CrispStrobe/glint)**（MIT）—— 樹內 clean-room codec 套件：MP3/AAC-LC/Ogg-Opus 輸出编码器（TTS `.mp3`/`.aac`/`.opus`）與跨平台 ADTS AAC-LC + Ogg Opus 輸入解碼器（無需 libopus）
- **[Claude Code](https://claude.ai/claude-code)**（Anthropic）—— crispasr 整合層的重要部分、所有模型轉換器，以及 FastConformer/attention/mel/FFN/BPE 核心助手有大量是與 Claude 共同撰寫

---

## 授權

與上游 whisper.cpp 相同：**MIT**。

各模型的權重受各自 HuggingFace 模型授權涵蓋（見[支援的後端](#supported-backends)）。`crispasr` 二進位檔本身連結的模型執行期大多採寬容授權（權重為 MIT / Apache-2.0 / CC-BY-4.0）。
