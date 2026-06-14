# Whisper.cpp 整合指南（MacBook Air M2）

## 概述

Whisper.cpp 是一個由 C++ 實作的 Whisper 模型，支援 Metal GPU 加速。
本專案用它作為 JARVIS 的「耳朵」，將語音轉為文字。

**效能**：11 秒音頻 → **0.57 秒** 轉寫（Metal GPU）18.6x 即時 ✅

---

## 1. 編譯 Whisper.cpp

### 前置依賴
```bash
brew install cmake ffmpeg
```

### 編譯（含 CoreML + Metal）
```bash
cd ~/Projects
git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
WHISPER_COREML=1 make -j$(nproc)
```

**注意**：`nproc` 在 macOS 上不存在，改用：
```bash
make -j$(sysctl -n hw.ncpu)
```

### 產出
- 二進位：`build/bin/whisper-cli`
- 靜態庫：`build/src/libwhisper.dylib`

---

## 2. 下載模型
### 快速方式（推薦）
```bash
cd ~/Projects/JARVIS-on-mac
bash scripts/download_whisper_model.sh       # 下載 base 模型
bash scripts/download_whisper_model.sh base.en  # 下載英文模型
```


### 多語言模型（支援中文）
```bash
cd whisper.cpp
bash models/download-ggml-model.sh base
# 產出：models/ggml-base.bin（147MB）
```

### 英文專用模型（更小更快）
```bash
bash models/download-ggml-model.sh base.en
# 產出：models/ggml-base.en.bin（141MB）
```

### 更多模型選擇
| 模型 | 大小 | 速度 | 準確度 |
|------|------|------|--------|
| tiny | ~75MB | 最快 | 較低 |
| base | ~147MB | 快 | 中等 |
| small | ~488MB | 中等 | 高 |
| medium | ~1.5GB | 慢 | 很高 |
| large | ~3.1GB | 最慢 | 最高 |

---

## 3. 基本使用（CLI）

```bash
# 英文音頻
./build/bin/whisper-cli -m models/ggml-base.en.bin -f audio.wav

# 中文音頻
./build/bin/whisper-cli -m models/ggml-base.bin -f audio.wav -l zh

# 只輸出文字（無時間戳）
./build/bin/whisper-cli -m models/ggml-base.bin -f audio.wav -nt

# 自動偵測語言
./build/bin/whisper-cli -m models/ggml-base.bin -f audio.wav -l auto
```

---

## 4. Python 整合（ASR Engine）

### 架構
```
ffmpeg (錄音) → WAV (16kHz mono) → whisper-cli (推論) → 文字
```

### 安裝依賴
```bash
brew install ffmpeg
```

### 使用方式
```python
from voice.asr_engine import WhisperASR

# 初始化（中文，普通話）
asr = WhisperASR(language="zh")

# 檔案轉寫
text = asr.transcribe("audio.wav")

# 麥克風轉寫（錄音 5 秒）
text = asr.transcribe_mic(duration=5.0)

# 效能測試
result = asr.benchmark("audio.wav")
print(f"耗時: {result['elapsed_seconds']}s")
```

### 環境變數
```bash
export WHISPER_CLI="/path/to/whisper-cli"
export WHISPER_MODEL="/path/to/ggml-base.bin"
```

---

## 5. macOS 麥克風權限

### 問題癥結
```
ffmpeg: Input/output error
```
→ macOS 拒絕背景程式存取麥克風。

### 解法
在「系統偏好設定 → 隱私與安全性 → 麥克風」中，
將 **終端機**（或 Python 應用程式）加入允許清單。

在 Terminal.app 中第一次執行時，macOS 會彈出權限對話框。

### 測試麥克風存取
```bash
# 查看可用裝置
ffmpeg -list_devices true -f avfoundation -i "" 2>&1

# 應該看到：
# [0] MacBook Air的麥克風
```

---

## 6. 常見問題

### Q: 模型載入失敗
```
error: failed to load model
```
→ 確認模型路徑正確：`ls models/ggml-base.bin`

### Q: 翻譯模式（translate）?
```bash
# 翻譯成英文（不轉寫原文）
whisper-cli -m models/ggml-base.bin -f audio.wav -tr
```

### Q: 有無 CoreML 加速？
```bash
# 查看是否使用 Metal GPU
whisper-cli -m models/ggml-base.bin -f audio.wav 2>&1 | grep MTL
# 應該看到：MTL0 (Apple M2)
```

### Q: 無法錄音（麥克風）?
→ 確認 ffmpeg 有麥克風權限（見第 5 節）
→ 測試：`ffmpeg -y -f avfoundation -i ":0" -t 1 test.wav`

---

## 7. 與 OpenAI Whisper 的比較

| 項目 | Whisper.cpp | OpenAI Whisper (pip) |
|------|------------|---------------------|
| 語言 | C++ + Metal GPU | PyTorch (CPU/GPU) |
| 速度 | ~0.05x 即時（快 10-20x）| ~0.5x 即時 |
| 準確度 | 相同 | 相同 |
| 安裝複雜度 | 需要編譯 | pip install 即可 |
| CoreML 支援 | ✅ 原生 | ❌ 無 |

**結論**：Whisper.cpp 是 Mac 上的最佳選擇（本專案已採用）。
OpenAI Whisper 適合快速原型驗證或無編譯環境。

---

## 8. 未來優化方向

1. **CoreML 量化模型**：使用 `convert-whisper-to-coreml.py` 轉換 CoreML 版本
2. **Streaming VAD**：整合 Silero VAD，實現真正的語音激活偵測
3. **whisper-server**：使用 HTTP server 模式，支援多客户端

---

_更新時間：2026-05-13（T004 實作日）_

---

## A1. JARVIS 專案目錄結構

```
~/Projects/JARVIS-on-mac/
├── dev/whisper.cpp          ← 完整開發環境（編譯用）
│   ├── Makefile / CMakeLists.txt
│   ├── src/ ggml/ cmake/    ← 原始碼
│   ├── build/bin/           ← 編譯產物
│   └── models/              ← 所有 GGML 模型
├── whisper.cpp/             ← 精簡運行環境（JARVIS 直接使用）
│   ├── bin/whisper-cli     ← 主要執行檔
│   ├── bin/whisper-server  ← HTTP server 模式
│   └── models/ggml-*.bin   ← 運行所需模型
└── voice/asr_engine.py      ← ASR 封裝
```

**規則**：前置開發需求放 `dev/`，運行環境放專案根目錄。
