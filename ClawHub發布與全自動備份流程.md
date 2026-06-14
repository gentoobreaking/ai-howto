# ClawHub 發布 → 全自動備份流程

> 建立時間：2026-04-04｜更新：2026-04-05

## 📋 流程全景

```
發布 Skill 到 ClawHub
    ↓
全自動定期備份（每 2 小時）
    ├── 備份已發布的 Skills（sync_skills.sh → GitHub）
    ├── 備份本地 howto 文件（sync_howto.sh → GitHub）
    ├── 備份 Tasks 任務追蹤（sync_tasks.sh → GitHub）
    └── 失敗時發 Telegram 通知（sync_all.sh 統一觸發）
```

## 🔧 核心腳本

### 1. sync_all.sh — 統一入口
路徑：`~/.qclaw/workspace/scripts/sync_all.sh`

調用三個子腳本，整合成功/失敗邏輯：
- 成功 → 安靜，僅寫本地日誌
- 失敗 → 發 Telegram 通知 + webchat 報告

### 2. sync_skills.sh — Skills 備份
路徑：`~/.qclaw/workspace/scripts/sync_skills.sh`

下載用戶在 ClawHub 發布過的所有版本的壓縮包：
- 已發布 Skill：yuhao-voice-reply、free-gold-monitor
- 存放到：`~/.qclaw/workspace/clawhub-backup/`

### 3. sync_howto.sh — howto 文件同步
路徑：`~/.qclaw/workspace/scripts/sync_howto.sh`

同步 `/Users/claw/howto/` 到 GitHub（openclaw-howto repo）。

### 4. sync_tasks.sh — Tasks 同步
路徑：`~/.qclaw/workspace/scripts/sync_tasks.sh`

同步 `/Users/claw/Tasks/` 到 GitHub（openclaw-tasks repo）。

## ⏰ 定時任務

- **頻率**：每 2 小時自動執行
- **觸發器**：OpenClaw cron（isolated session）
- **Delivery**：成功 → webchat 安靜報告，失敗 → webchat + Telegram

## 🔔 通知邏輯

| 結果 | webchat | Telegram |
|------|---------|----------|
| ✅ 成功 | 報告 | 安靜 |
| ⚠️ 失敗 | 報告 + 錯誤片段 | 直接 curl 發送 |

失敗時 Telegram 訊息由 sync_all.sh 透過 curl 直接呼叫 Telegram Bot API，繞過 OpenClaw 的 delivery 設定，確保精準控制。

## 📁 相關文件

| 檔案 | 用途 |
|------|------|
| `~/.qclaw/workspace/scripts/sync_all.sh` | 統一入口腳本 |
| `~/.qclaw/workspace/scripts/sync_skills.sh` | ClawHub Skills 下載 |
| `~/.qclaw/workspace/scripts/sync_howto.sh` | howto → GitHub 同步 |
| `~/.qclaw/workspace/scripts/sync_tasks.sh` | Tasks → GitHub 同步 |
| `/Users/claw/howto/` | 本地 howto 文件存放 |
| `/Users/claw/Tasks/` | 任務追蹤目錄 |
| `~/.openclaw/logs/sync_all.log` | 執行日誌 |

## 🧩 為什麼需要這套流程

發布 Skill 到 ClawHub 後，數據散落在兩處：
1. **ClawHub 平台**（在線）
2. **本地磁盤**（openclaw 配置）

這套流程將所有數據同步到 GitHub private repo，確保任何單點故障都能從備份恢復。
