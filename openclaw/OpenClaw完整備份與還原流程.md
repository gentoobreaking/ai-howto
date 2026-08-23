# OpenClaw 完整備份與還原流程

> 建立：2026-04-04｜更新：2026-04-04

## 📋 備份全景圖

```
~/.qclaw/                    ← 打包成 tar.gz（最主要！）
├── cron/jobs.json          ← 定時任務設定
├── workspace/scripts/       ← 自訂腳本（sync_all.sh 等）
├── gold_monitor_*.json     ← 黃金監控配置與歷史
├── memory-tdai/            ← 對話記憶、場景塊、向量數據
├── memory/                  ← LCM 長期記憶
├── openclaw.json           ← OpenClaw 主配置
├── identity/               ← 設備身份（更換機器必備）
└── workspace/skills/        ← 純 Skill 本體（不含 node_modules/.git）

排除（可重建）：
├── */node_modules/         ← skillhub 重裝時自動安裝
├── */.git/                 ← Git 歷史從 ClawHub 下載
├── */compile-cache/        ← 每次運行自動重建
└── */browser/              ← Chromium 緩存

~/howto/                    ← 備份到 GitHub (openclaw-howto repo)

ClawHub 已發布 Skills       ← 從 ClawHub 重新下載 zip
```

**壓縮後備份大小：約 31 MB**（原 892 MB，排除 node_modules/.git/compile-cache/browser 後）

---

## ⏰ 自動備份設定

- **頻率**：每 2 小時（cron job ID：`edaa5e37-0a1d-4e33-877d-7ea01d172967`）
- **觸發器**：OpenClaw cron（isolated session）
- **Delivery**：純 announce（webchat），失敗才發 Telegram

### 通知邏輯

| 結果 | webchat | Telegram |
|------|---------|----------|
| ✅ 成功 | 報告 | 安靜 |
| ⚠️ 失敗 | 報告 + 錯誤片段 | 直接 curl 發送 |

---

## 🖥️ 還原情境 A：繼續使用 QClaw

> 新機器同樣使用 QClaw 運行 OpenClaw 的情境。

### 步驟

**Step 1：恢復數據目錄**

```bash
# 在新機器上下載最新備份（從 GitHub private repo 或直接拷貝）
# 假設備份檔名為 qclaw-full-20260404_1200.tar.gz

tar -xzf qclaw-full-20260404_1200.tar.gz -C ~/
```

這會還原：
- `~/.qclaw/` 全部配置（含 cron 任務，無需重建）
- `~/howto/` 文件

**Step 2：確認路徑正確**

```bash
ls ~/.qclaw/workspace/scripts/sync_all.sh   # 腳本是否存在
ls ~/.qclaw/cron/jobs.json                  # cron 任務是否存在
```

**Step 3：重啟 OpenClaw Gateway**

```bash
# 在 QClaw 設定中重啟，或：
openclaw gateway restart
```

**Step 4：驗證**

```bash
# 手動觸發一次備份確認正常
bash ~/.qclaw/workspace/scripts/sync_all.sh
```

**⚠️ 注意事項**
- 設備身份（`~/.qclaw/identity/`）如果與新機器衝突，刪除後重配
- ClawHub Skills 從平台重新下載，不依賴本地備份

---

## 🖥️ 還原情境 B：換成標準 OpenClaw（非 QClaw）

> 新機器使用標準 OpenClaw（非 QClaw 封裝），數據目錄結構不同的情境。

### OpenClaw 數據存放位置對照

| 數據類型 | QClaw 路徑 | 標準 OpenClaw 路徑 |
|---------|-----------|-----------------|
| 主配置 | `~/.qclaw/openclaw.json` | `~/.openclaw/openclaw.json` |
| cron 任務 | `~/.qclaw/cron/jobs.json` | `~/.openclaw/cron/jobs.json` |
| 設備身份 | `~/.qclaw/identity/` | `~/.openclaw/identity/` |
| 記憶 | `~/.qclaw/memory-tdai/` | `~/.openclaw/memory-tdai/` |
| 自訂腳本 | `~/.qclaw/workspace/scripts/` | `~/.openclaw/workspace/scripts/` |

> **核心差異**：QClaw 用 `~/.qclaw/`，標準 OpenClaw 用 `~/.openclaw/`

### 步驟

**Step 1：安裝標準 OpenClaw**

```bash
# 参考 openclaw.com 官方安裝方式
# 安裝完成後確認版本
openclaw --version
```

**Step 2：解壓縮備份，並手動對應路徑**

```bash
# 解壓
tar -xzf qclaw-full-20260404_1200.tar.gz -C /tmp/restore/

# 對應拷貝（QClaw → 標準 OpenClaw 路径）
cp -r /tmp/restore/.qclaw/openclaw.json  ~/.openclaw/openclaw.json
cp -r /tmp/restore/.qclaw/identity/     ~/.openclaw/identity/
cp -r /tmp/restore/.qclaw/cron/           ~/.openclaw/cron/
cp -r /tmp/restore/.qclaw/memory-tdai/   ~/.openclaw/memory-tdai/
cp -r /tmp/restore/.qclaw/workspace/      ~/.openclaw/workspace/

# howto 文件
cp -r /tmp/restore/howto/                ~/howto/
```

**Step 3：重建 cron 任務**

QClaw 的 cron 任務 ID 會完整保留在 `~/.openclaw/cron/jobs.json` 中，
重啟 OpenClaw 後自動生效。

**Step 4：驗證**

```bash
# 檢查 cron 任務是否正確加載
openclaw cron list

# 手動觸發一次
bash ~/.openclaw/workspace/scripts/sync_all.sh
```

**⚠️ 注意事項**
- 標準 OpenClaw 不包含 QClaw 特有的 GUI，啟動方式為 `openclaw gateway start`
- 如果新機器的 macOS 用戶名不同，路徑中的 `~` 需替換為實際路徑

---

## 📁 備份文件說明

| 檔案 | 內容 | 是否含在 tar.gz |
|------|------|----------------|
| `sync_all.sh` | 統一備份入口腳本 | ✅ 完整收錄 |
| `sync_skills.sh` | ClawHub Skills 下載腳本 | ✅ 完整收錄 |
| `sync_howto.sh` | howto → GitHub 同步腳本 | ✅ 完整收錄 |
| `gold_monitor.py` | 黃金價格監控腳本 | ✅ 完整收錄 |
| `jobs.json` | cron 定時任務配置 | ✅ 完整收錄 |
| `memory-tdai/` | 對話記憶與場景塊 | ✅ 完整收錄 |

---

## 🔑 設備身份與隱私

- 設備身份文件（`identity/device.json`）只能用於設備配對，不可外流
- tar.gz 包含設備身份，上傳到 GitHub private repo 或本地保存時請確認空間可信
