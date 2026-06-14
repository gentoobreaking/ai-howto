# OpenClaw Cron 備份與還原

## 一、備份 Cron 任務

### 查看所有 Cron 任務

```bash
# 在 OpenClaw Control UI > Schedule 查看，或透過 API：
curl -s -H "Authorization: Bearer <token>" \
  http://localhost:28789/api/cron/list
```

### 匯出 Cron 任務配置

```bash
SKILL_DIR="~/Library/Application Support/QClaw/openclaw/config/skills/qclaw-openclaw"
BACKUP_DIR="$HOME/.qclaw/backups"
mkdir -p "$BACKUP_DIR"

bash "$SKILL_DIR/scripts/openclaw-mac.sh" cron list
```

### 自動排程備份（每小時）

透過 OpenClaw cron 工具建立一次性或週期性備份任務。

---

## 二、還原 Cron 任務

### 從 JSON 還原

若備份了完整 cron job 配置，可透過 `cron add` 逐個重建。

### 手動重建常用任務

```bash
# 黃金監控（每10分鐘，營業日）
# 使用 cron 工具，schedule: {"kind":"cron","expr":"*/10 9-15 * * 1-5","tz":"Asia/Taipei"}

# 每日收盤報告（15:30）
# schedule: {"kind":"cron","expr":"30 15 * * 1-5","tz":"Asia/Taipei"}

# Ideas 每日掃描（09:00）
# schedule: {"kind":"cron","expr":"0 9 * * *","tz":"Asia/Taipei"}
```

---

## 三、驗證還原結果

查詢 cron list 確認任務數量與下次執行時間正確。

---

_最後更新：2026-04-06_
