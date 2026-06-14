# JARVIS-on-mac 技術流水線

> **最後更新**：2026-05-13

## 系統架構

```
使用者輸入 → Whisper（語音→文字） → JARVIS Brain（MNN-LLM） → 回覆
                                        ↑
                                   本地模型，零網路延遲
```

## 模型矩陣

| 模型 | 目錄 | 用途 | 大小 | 備註 |
|------|------|------|------|------|
| Whisper | GGML（本地） | 語音辨識 | ~75 MB | Tiny/Base |
| Qwen3.5-0.8B | `models/` | 大腦（預設較強） | ~984 MB（含 VL） | 較慢但智力高 |
| Qwen1.5-0.5B | `models_qwen1.5/` | 大腦（預設較快） | ~554 MB | 較快，預設模型 |

### 模型切換

詳見：[howto/qwen-model-switch.md](qwen-model-switch.md)

**環境變數方式（推薦）**：
```bash
export BRAIN_MODEL=models/              # 切 Qwen3.5
export BRAIN_MODEL=models_qwen1.5/     # 切 Qwen1.5
```

**修改程式碼**：
```python
# brain/brain_engine.py
_DEFAULT_MODEL = os.environ.get("BRAIN_MODEL", "models_qwen1.5/")
```

---

## 技術棧

| 層 | 技術 | 狀態 |
|----|------|------|
| 語音辨識 | Whisper.cpp（GGML） | T003 |
| LLM 推理 | MNN-LLM + Metal | T002 ✅ |
| 前端 | 待定（T006-T007）| TODO |

---

## 下載模型

```bash
cd ~/Projects/JARVIS-on-mac

# Qwen3.5（較強較慢）
bash scripts/download_qwen_model.sh

# Qwen1.5（較小較快，預設）
bash scripts/download_qwen1.5_model.sh

# Whisper
bash scripts/download_whisper_model.sh
```

---

## 核心模組

- `brain/brain_engine.py` — MNN-LLM 大腦引擎（自動偵測模型 + prompt 格式）
- `speech/` — Whisper 整合模組

---

## 下一步

1. T003：Whisper 整合（T003 尚未開始）
2. T004-T005：後端流水線串接
3. T006-T007：前端 HUD + 整合測試

詳見：[~/Tasks/Javis/README.md](~/Tasks/Javis/README.md)
