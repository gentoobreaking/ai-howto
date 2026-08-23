# Qwen 模型下載（HuggingFace）

> **狀態**：✅ 已完成（T002 完成）
> **最後更新**：2026-05-13
> **執行者**：寶寶

## Context

從 HuggingFace Hub 下載 MNN 量化模型，這是 JARVIS 大腦的核心。
目前支援 **雙模型**，可自由切換：

| 模型 | Repo ID | 目錄 |
|------|---------|------|
| Qwen3.5-0.8B（較強）| `taobao-mnn/Qwen3.5-0.8B-MNN` | `models/` |
| Qwen1.5-0.5B（較快）| `taobao-mnn/Qwen1.5-0.5B-Chat-MNN` | `models_qwen1.5/` |

> **切換方式**：詳見 [qwen-model-switch.md](qwen-model-switch.md)

---

## 1. 快速下載（一鍵指令）

```bash
cd ~/Projects/JARVIS-on-mac
bash scripts/download_qwen_model.sh
```

此腳本會：
1. 檢查並安裝 `huggingface_hub`
2. 下載模型至 `models/`（約 449 MB）
3. 驗證必要檔案（`config.json`、`llm.mnn`、`tokenizer.txt`）

---

## 2. 手動下載（Python 指令）

如需自訂，可直接執行：
```python
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="taobao-mnn/Qwen3.5-0.8B-MNN",
    local_dir="~/Projects/JARVIS-on-mac/models/",
    local_dir_use_symlinks=False,
)
```

---

## 3. 模型存放位置

```
~/Projects/JARVIS-on-mac/models/
├── config.json          # 模型組態（供 BrainEngine 使用）
├── llm.mnn              # MNN 量化模型（本體）
├── llm.mnn.weight       # 模型權重
├── llm_config.json      # LLM 推理參數
├── tokenizer.txt        # 分詞器
├── visual.mnn           # 視覺模組（VL 模型）
└── ...
```

**模型大小**：約 448.6 MB

---

## 4. 驗證下載成功

```bash
# 方式 1：腳本自動驗證（已在下載時執行）

# 方式 2：手動檢查
ls -lh ~/Projects/JARVIS-on-mac/models/config.json
ls -lh ~/Projects/JARVIS-on-mac/models/llm.mnn

# 方式 3：BrainEngine 測試
cd ~/Projects/JARVIS-on-mac
python3 -c "
import sys; sys.path.insert(0, '.')
from brain.brain_engine import BrainEngine
b = BrainEngine()
b.load()
print('模型載入成功 ✅')
"
```

---

## 5. 常見問題

| 問題 | 解法 |
|------|------|
| 下載失敗 | 檢查網路或使用 VPN |
| 磁碟空間不足 | 確保有至少 1GB 可用空間 |
| huggingface_hub 未安裝 | 自動由腳本安裝，或手動 `pip3 install huggingface_hub` |

---

_相關：[qwen-model-switch.md](qwen-model-switch.md)（模型切換指南）_
