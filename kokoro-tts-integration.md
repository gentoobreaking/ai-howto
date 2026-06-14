# Kokoro-82M TTS 整合（2026-05-13）

> 對應任務：T005（TTS 整合）
> 環境：MacBook Air M2，Python 3.11，Metal（MPS）加速

## 環境準備

### 1. Python 版本

Kokoro 0.9.4 需要 Python 3.10–3.12，不支援 Python 3.9。

```bash
# 確認或安裝 Python 3.11
/opt/homebrew/bin/python3.11 --version
# 若無，安裝：
brew install python@3.11
```

### 2. 安裝相依套件

```bash
/opt/homebrew/bin/python3.11 -m pip install \
  "kokoro>=0.9.4" \
  soundfile \
  pypinyin \
  cn2an \
  jieba
```

> ⚠️ **重要**：必須用 `python3.11` 而非系統的 `python3`（系統為 3.9，不相容）。

### 3. 下載模型權重

```bash
mkdir -p voice/models
cd voice/models

# 方法一：huggingface_hub（推薦，自動處理 LFS）
/opt/homebrew/bin/python3.11 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='hexgrad/Kokoro-82M',
    local_dir='voice/models',
    local_dir_use_symlinks=False,
)
"
# 等待下載（72 個檔案，~349MB）

# 方法二：git clone（需 git-lfs）
git lfs install
git clone https://huggingface.co/hexgrad/Kokoro-82M voice/models
```

### 4. 安裝 espeak-ng（Linux/macOS 都需要）

**macOS（Homebrew）：**
```bash
brew install espeak-ng
```

**驗證：**
```bash
espeak-ng --version
```

---

## 語音合成實作

### 基本用法

```python
from voice.voice_engine import TTSEngine

# 初始化（中文化，zf_xiaoxiao 發音人）
engine = TTSEngine(lang_code="z", voice="zf_xiaoxiao")

# 文字 → WAV 檔案
audio_path = engine.speak("你好，這是 JARVIS 的語音測試")
# 輸出：/assets/audio/tts_xxxxxxxx.wav
```

### 快速函式

```python
from voice.voice_engine import speak

# 一行搞定
speak("測試文字")
```

### 流式輸出（數位人口型驅動用）

```python
def on_chunk(chunk, progress):
    print(f"收到 {len(chunk)} 樣本，進度 {progress:.0%}")

audio_path = engine.speak_streaming("很長的文字測試", callback=on_chunk)
```

### speak_to_array（直接取 numpy 音頻）

```python
audio, sr = engine.speak_to_array("測試")
# audio: numpy.ndarray (float32, [-1, 1])
# sr: 24000
```

---

## 發音人列表

### 中文發音人（lang_code='z'）

| 名稱 | 性別 | 風格 |
|------|------|------|
| `zf_xiaoxiao` | 女 | 標準普通話（推薦預設）|
| `zf_xiaobei` | 女 | 北方口音 |
| `zf_xiaoni` | 女 | 少女感 |
| `zf_xiaoyi` | 女 | 輕柔 |
| `zm_yunjian` | 男 | 標準男聲 |
| `zm_yunxi` | 男 | 年輕男聲 |
| `zm_yunxia` | 女 | 小女孩 |
| `zm_yunyang` | 男 | 新聞播報風 |

### 英文發音人（lang_code='a'）

| 名稱 | 性別 |
|------|------|
| `af_heart` | 女，溫暖（推薦預設）|
| `af_bella` | 女，活潑 |
| `af_nova` | 女，科技感 |
| `am_adam` | 男，沉穩 |
| `am_puck` | 男，俏皮 |

### 其他語言

| lang_code | 語言 | 發音人數 |
|-----------|------|---------|
| `b` | 英國英文 | 4 |
| `e` | 歐洲混合 | 3 |
| `f` | 法語 | 1 |
| `h` | 混合 | 4 |
| `i` | 義大利文 | 2 |
| `j` | 日語 | 5 |
| `p` | 葡萄牙文 | 3 |

---

## 效能參考（Mac M2，GPU）

| 文字長度 | 生成時間 | 音頻長度 |
|---------|---------|---------|
| ~20 字 | 2.2 秒 | 3.4 秒 |
| ~30 字 | 3.0 秒 | 3.6 秒 |

推理設備自動偵測：CUDA → MPS → CPU

---

## 已知問題

### 1. Python 3.9 不相容

錯誤：`ERROR: No matching distribution found for kokoro>=0.9.4`
解決：用 Python 3.11

```bash
/opt/homebrew/bin/python3.11 -m pip install "kokoro>=0.9.4"
```

### 2. 缺少 pypinyin / cn2an / jieba

錯誤：`ModuleNotFoundError: No module named 'xxx'`
解決：手動安裝相依套件（見上方第 2 步）

### 3. 第一次執行很慢

正常。jieba 需要建立字典快取（約 0.3 秒），模型首次載入約 5-10 秒。
之後重複執行會使用快取。

### 4. macOS 麥克風權限

TTS 音頻播放需要 macOS 系統權限設定。

---

## 與後端流水線整合

### PipelineResult 中的 TTS 欄位

```python
# pipeline/jarvis_pipeline.py 中，PipelineResult 結構：
@dataclass
class PipelineResult:
    transcription: Optional[str]  # ASR 結果（語音輸入時）
    response: str                 # LLM 回應文字
    audio: Optional[Path]        # TTS 音頻檔案（新增）
    error: Optional[str]

# 整合方式：
result.audio = tts_engine.speak(result.response)
```

### WebSocket 回應格式（更新）

```json
{
  "type": "response",
  "transcription": null,
  "response": "台灣最高的山是玉山...",
  "audio": "/assets/audio/tts_3e6d6dfa.wav",
  "audio_duration": 3.5,
  "error": null
}
```

---

## 檔案結構

```
voice/
├── __init__.py
├── voice_engine.py      # TTSEngine 類別
├── asr_engine.py       # Whisper ASR
├── requirements.txt    # Kokoro 相依套件
└── models/             # Kokoro-82M 模型權重（~349MB）
    ├── kokoro-v1_0.pth  # 主模型（312MB）
    └── voices/
        ├── zf_xiaoxiao.pt  # 中文女聲
        ├── af_heart.pt     # 英文女聲
        └── ...             # 其他發音人

assets/
└── audio/              # TTS 輸出目錄
    └── tts_*.wav
```

---

## 下一步

- [x] `voice/voice_engine.py` — Kokoro-82M 實作
- [x] `tests/test_tts.py` — 單元測試覆蓋
- [ ] 後端流水線整合（T003 完成後，接入 PipelineResult.audio）
- [ ] 前端 HUD 播放 TTS 音頻（T005）
- [ ] 評估 ONNX 量化版本（進一步加速？）
