# Tasks 自動執行機制設計

## 流程架構

```
每日 09:00 lifecycle.py 掃描
    ↓
發現待處理 ideas → Telegram 通知（含按鈕）
    ↓
用戶點擊「確認建立」→ 寶寶建立 tasks
    ↓
自動 spawn 對應 agent 執行
    ↓
完成後 Telegram 彙報結果
```

## 實作方案

### 1. 修改 lifecycle.py
- 輸出 Telegram 友善格式（簡潔、Emoji、分段）
- 寫入 `lifecycle_status.json` 供後續讀取

### 2. 新增 tasks_executor.py
- 讀取 `lifecycle_status.json`
- 自動建立 tasks 目錄結構
- 根據 assignee spawn 對應 agent
- 彙報執行結果

### 3. Telegram 互動格式

**掃描通知範例**：
```
📋 Ideas 掃描 — 2026-04-05 09:00

📁 read (security)
  └─ T1: AWS OpenClaw 安全文章 [碼農1號]
  └─ T2: Session log 存檔 [樂樂]

📊 統計：2 個待處理

回覆「確認」建立 tasks
```

**確認後通知**：
```
✅ Tasks 已建立

📁 read/
  ├─ T001 → 碼農1號 (spawned)
  └─ T002 → 樂樂 (spawned)

🔄 執行中...
```

**完成通知**：
```
🎉 read 專案完成

✅ T001 AWS 安全文章 → howto/aws-security.md
✅ T002 Session log → howto/session-logging.md

📊 用時：12 分鐘
```

## 檔案結構

```
/Users/claw/.qclaw/workspace/skills/ideas2tasks/
├── scripts/
│   ├── lifecycle.py      # 掃描 + 通知
│   ├── executor.py       # 建立 tasks + spawn agents
│   ├── classify.py       # 分類邏輯（現有）
│   └── scan.py           # 掃描邏輯（現有）
└── lifecycle_status.json  # 狀態暫存
```

## 技術細節

### assignee → agentId 映射

| assignee | agentId |
|----------|---------|
| 寶寶 / 豪 | main |
| 碼農1號 | agent-f937014d |
| 碼農2號 | agent-coder2 |
| 安安 | agent-ann |
| 樂樂 | agent-lele |

### Telegram 格式規範
- **標題**：Emoji + 粗體
- **列表**：使用 `└─` / `├─` 樹狀結構
- **統計**：`📊` 前綴
- **狀態**：✅ / 🔄 / ❌
- **避免**：Markdown 表格（Telegram 顯示差）

---

_設計日期: 2026-04-05_
