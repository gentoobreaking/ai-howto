# Qwen 模型切換指南（MNN LLM）

> **最後更新**：2026-05-13
> **執行者**：寶寶

## 已下載模型

| 模型 | 目錄 | 參數量 | 大小 | HuggingFace |
|------|------|--------|------|-------------|
| Qwen3.5-0.8B-MNN | `models/` | 0.8B | ~449 MB | `taobao-mnn/Qwen3.5-0.8B-MNN` |
| Qwen1.5-0.5B-Chat-MNN | `models_qwen1.5/` | 0.5B | ~554 MB | `taobao-mnn/Qwen1.5-0.5B-Chat-MNN` |

---

## 切換方式

### 方式一：環境變數（推薦）

```bash
# 使用 Qwen1.5（預設）
export BRAIN_MODEL=models_qwen1.5/

# 切換到 Qwen3.5
export BRAIN_MODEL=models/

# 啟動
cd ~/Projects/JARVIS-on-mac
python3 app.py
```

### 方式二：修改程式碼

編輯 `brain/brain_engine.py`：

```python
_DEFAULT_MODEL = os.environ.get(
    "BRAIN_MODEL",
    "models_qwen1.5/"   # ← 改這行：models/ 或 models_qwen1.5/
)
```

---

## Prompt 格式自動偵測

`brain/brain_engine.py` 會自動偵測模型類型並套用正確的 prompt 格式：

| 模型 | model_type | Prompt 格式 |
|------|-----------|------------|
| Qwen1.5-0.5B | `default`（config 無 model_type） | `<\|im_start\|>user\n{prompt}<\|im_end\|>\n<\|im_start\|>assistant\n` |
| Qwen3.5-0.8B | `default`（config 無 model_type） | 同上 |

> 兩個模型都使用相同的 `<|im_start|>...` 格式，自動偵測為 "default" 並正確生成回應。

---

## 驗證切換

```bash
# Qwen1.5（預設）
cd ~/Projects/JARVIS-on-mac
python3 -c "
import sys; sys.path.insert(0, '.'); from brain.brain_engine import BrainEngine
b = BrainEngine(); b.load(); print(b.chat('說一個笑話')); b.release()
"

# Qwen3.5（切換後）
BRAIN_MODEL=models/ python3 -c "
import sys, os; sys.path.insert(0, '.'); from brain.brain_engine import BrainEngine
b = BrainEngine(); b.load(); print(b.chat('說一個笑話')); b.release()
"
```

---

## 比較

| 項目 | Qwen1.5-0.5B | Qwen3.5-0.8B |
|------|-------------|-------------|
| 參數量 | 0.5B | 0.8B |
| 模型大小 | ~554 MB | ~449 MB |
| 回應速度 | 較快 | 較慢 |
| 回應風格 | 直接簡短 | 可能包含思考過程 |
| 繁體中文 | ✅ | ✅ |

---

## 下載腳本

```bash
cd ~/Projects/JARVIS-on-mac

# Qwen3.5
bash scripts/download_qwen_model.sh

# Qwen1.5
bash scripts/download_qwen1.5_model.sh
```

---

## 常見問題

### Q：下載失敗？
A：檢查網路，或設 `HF_TOKEN` 環境變數提升下載速度：
```bash
export HF_TOKEN=your_token_here
bash scripts/download_qwen1.5_model.sh
```

### Q：兩個模型可以同時存在嗎？
A：可以！放在不同目錄，不會互相覆蓋。

### Q：Prompt 格式為何重要？
A：Qwen1.5 若不套用 `<|im_start|>...` 格式，回應會是空的。這是 MNN LLM 的設計特性。
