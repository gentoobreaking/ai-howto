# OpenClaw Admin 管理面板

## 功能說明

OpenClaw Admin 是一套完整的 Web 管理介面，透過瀏覽器管理 OpenClaw Gateway 的各項設定。

**主要功能：**
- 📊 儀表盤：系統一覽、Token 使用趨勢、會話活躍度統計
- 💬 線上對話：即時聊天互動、支援斜槓命令
- 📋 會話管理：會話列表、詳情查看、創建/重置/刪除
- 🧠 記憶管理：編輯 AGENTS、SOUL、IDENTITY、USER 等核心文件
- ⏰ 任務計劃：Cron 定時任務創建與管理
- 🤖 模型管理：多模型渠道配置、API Key 安全管理
- 📡 頻道管理：QQ、飛書、釘釘、企業微信、Telegram 等渠道配置
- 🛠️ 技能管理：技能插件列表、安裝與更新
- 🖥️ 系統監控：CPU、記憶體、磁碟使用率
- 🖱️ 遠程終端：SSE 協議遠程終端、多節點支援

---

## 安裝流程（2026-04-03）

### 前置需求
- Node.js >= 18.0.0
- npm >= 9.0.0

### Step 1：Clone 專案
```bash
cd ~/.qclaw/workspace/skills
git clone https://github.com/itq5/OpenClaw-Admin.git
```

### Step 2：安裝依賴
```bash
cd OpenClaw-Admin
npm install
```

### Step 3：設定環境變量

編輯 `~/.qclaw/workspace/skills/OpenClaw-Admin/.env`：

```env
OPENCLAW_WS_URL=ws://localhost:28789
OPENCLAW_AUTH_TOKEN=你的Gateway_Token
PORT=3000
DEV_PORT=3001
```

> 如何取得 Gateway Token？
> `cat ~/.qclaw/openclaw.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['gateway']['auth']['token'])"`

### Step 4：啟動服務
```bash
bash /Users/claw/start-admin.sh
```

**生產模式（Node.js 後端）：** 使用 `server/index.js`，同時提供前端靜態檔案 + API proxy。

> ⚠️ 不要用 `python3 -m http.server`，它不支援 /api proxy，會導致 JSON 請求返回 HTML。

---

## 啟動腳本（已設定）
路徑：`/Users/claw/start-admin.sh`

```bash
#!/bin/bash
cd /Users/claw/.qclaw/workspace/skills/OpenClaw-Admin
export NODE_PATH="$PWD/node_modules"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
exec node --env-file=.env server/index.js
```

## 設定開機自動啟動
```bash
launchctl submit -l com.openclaw-admin -- /bin/bash /Users/claw/start-admin.sh
```

## 設定登入密碼
編輯 `.env`：
```env
AUTH_USERNAME=你的用戶名
AUTH_PASSWORD=你的密碼
```

---

## 設定 Telegram 頻道

### 1. 申請 Telegram Bot Token
1. 在 Telegram 找 **@BotFather**
2. 發送 `/newbot`
3. 照步驟命名後取得 Token

### 2. 設定 Token

在 Admin 的 **頻道管理** 頁面設定，或直接修改 `~/.qclaw/openclaw.json`：

```json
"channels": {
  "telegram": {
    "enabled": true,
    "botToken": "你的Bot_Token",
    "dmPolicy": "open",
    "allowFrom": ["*"]
  }
}
```

### 3. dmPolicy 選項

| 模式 | 說明 |
|------|------|
| `pairing` | 需要配對審批 |
| `open` | 所有人直接可用（推薦） |

---

## 常見問題

### Q：Admin 無法連線到 Gateway？
A：確認 `.env` 中 `OPENCLAW_WS_URL` 連接埠正確（預設 `28789`），並確保 Gateway 已啟動。

### Q：登入後看不到任何數據？
A：檢查 `OPENCLAW_AUTH_TOKEN` 是否正確。

### Q：如何重啟 Admin 服務？
```bash
pkill -f "OpenClaw-Admin"
bash /Users/claw/start-admin.sh
```

---

## 訪問地址

| 服務 | 模式 | 地址 |
|------|------|------|
| Admin 生產模式 | 本機 | http://localhost:3000 |
| Admin 開發模式 | 本機 | http://localhost:3001 |

---

## ⚠️ 2026-04-04 修正記錄

**問題**：系統重啟後 Admin 未自動啟動。

**修正**：重新透過 `launchctl submit` 設定開機自啟，確認 HTTP 200 正常。

**狀態**：✅ 正常（port 3000, HTTP 200）

---

*最後更新：2026-04-04*
