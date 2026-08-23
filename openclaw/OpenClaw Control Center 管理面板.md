# OpenClaw Control Center 管理面板

## 功能說明

OpenClaw Control Center（任務控制中心）是一套專為 OpenClaw 設計的任務管理與監控介面，提供：

- 任務心臟：自動檢查 backlog 任務、執行排程
- 時間線日誌：追蹤所有操作事件與時間軸
- Observability：Gateway 連線狀態、Sessions / Cron / Approvals 即時監控
- 專案面板：Project / Task / Budget 管理
- Hall 協作空間：多人協作式 AI 討論與任務分配

## 安裝流程（2026-04-03）

### 前置需求
- Node.js >= 18.0.0
- npm >= 9.0.0
- OpenClaw Gateway 正常運行

### Step 1：Clone 專案
```bash
cd ~/.qclaw/workspace/skills
git clone https://github.com/TianyiDataScience/openclaw-control-center.git
```

### Step 2：安裝依賴
```bash
cd openclaw-control-center
npm install
```

### Step 3：設定環境變量
```bash
cp .env.example .env
```

編輯 `.env`，**務必設定以下關鍵內容**：

```env
# 必須：Gateway URL
GATEWAY_URL=ws://127.0.0.1:28789

# 必須：本地 Token
LOCAL_API_TOKEN=<生成隨機Token>

# 必須：OpenClaw 數據路徑（本機數據在 ~/.qclaw/，非預設的 ~/.openclaw/）
OPENCLAW_HOME=/Users/claw/.qclaw
OPENCLAW_WORKSPACE_ROOT=/Users/claw/.qclaw/workspace

# UI 模式
UI_MODE=true
UI_PORT=4310

# 安全設定（預設）
READONLY_MODE=true
APPROVAL_ACTIONS_ENABLED=false
```

### Step 4：驗證安裝
```bash
npm run build       # TypeScript 編譯
npm run smoke:ui    # UI 冒煙測試
```

### Step 5：啟動服務
```bash
bash /Users/claw/start-control-center.sh
```

## 啟動腳本（已設定）
路徑：`/Users/claw/start-control-center.sh`

```bash
#!/bin/bash
cd /Users/claw/openclaw-control-center
export PATH="$PWD/node_modules/.bin:/usr/local/bin:/opt/homebrew/bin:$PATH"
export OPENCLAW_HOME=/Users/claw/.qclaw
export OPENCLAW_WORKSPACE_ROOT=/Users/claw/.qclaw/workspace
export UI_MODE=true
exec node dist/index.js
```

## 設定開機自動啟動
```bash
launchctl submit -l com.openclaw-control-center -- /bin/bash /Users/claw/start-control-center.sh
```

## 安全設定（預設已開啟）
- READONLY_MODE=true（只讀模式）
- APPROVAL_ACTIONS_ENABLED=false（禁用審批寫入）
- IMPORT_MUTATION_ENABLED=false（禁用 Import 寫入）
- LOCAL_TOKEN_AUTH_REQUIRED=true（寫操作需 Token 驗證）

## 常見問題

Q：介面資訊都是空的？
A：確認 .env 中有設定 OPENCLAW_HOME=/Users/claw/.qclaw，否則 Control Center 會去 ~/.openclaw/ 找資料（找不到）。

Q：smoke:ui 測試失敗？
A：確認 Gateway 已啟動，curl http://localhost:28789/health 返回 200。

Q：UI 頁面空白？
A：確認使用 bash start-control-center.sh（有設定 UI_MODE=true），不是 npm run dev。

Q：如何停止服務？
```bash
pkill -f "openclaw-control-center"
```

## 訪問地址
- 本機：http://localhost:4310

## 首次開啟推薦頁面
1. /timeline - 時間線日誌
2. /sessions - 監控對話狀態
3. /cron - 查看定時任務

## 降級面板（無數據源）
- Subscription / Usage（無 Codex 訂閱數據）
- Budget（無預算配置）
- Projects / Tasks（無任務數據）

---

## ⚠️ 2026-04-04 修正記錄

**問題**：系統重啟後 Control Center 未自動啟動，且顯示資料為空。

**根本原因**：
1. `.env` 中 `GATEWAY_URL` 被錯誤設為 `ws://127.0.0.1:18789`（少打了 2）→ 已修正為 `28789`
2. `OPENCLAW_HOME` 和 `OPENCLAW_WORKSPACE_ROOT` 未設定（被註解）→ 已啟用並指向 `~/.qclaw/`
3. 啟動腳本 `start-control-center.sh` 缺少 `UI_MODE=true` 環境變量 → 已修正

**修正後狀態**：✅ 全部正常（port 4310, HTTP 200）

---

*最後更新：2026-04-04*
