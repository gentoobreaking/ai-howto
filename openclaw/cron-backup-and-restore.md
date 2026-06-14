# HOWTO: OpenClaw Cron Tasks 備份與還原

## ⚠️ 前置說明

本文件涵蓋：
- 如何備份現有的 Cron Jobs 設定
- 如何匯出為可讀格式
- 如何在另一台機器或重新安裝後還原
- 如何定期自動化備份

---

## 一、認識 Cron Jobs 的儲存位置

### 1.1 設定檔位置

OpenClaw 的 Cron Jobs 資料通常儲存在以下位置之一：

| 位置 | 說明 |
|------|------|
| `~/.openclaw/cron-jobs.json` | 主要的 Cron Jobs 資料庫 |
| `~/.openclaw/jobs/` | 個別任務檔案目錄 |
| `~/Library/Application Support/QClaw/openclaw/` | QClaw App 的資料區 |

> 📌 具體路徑取決於你的 OpenClaw 安裝方式（CLI 或 QClaw App）。

### 1.2 查看 Cron Jobs 現況

**使用 CLI 查看：**
```bash
openclaw cron list
```

**預期輸出格式：**
```
ID         Name          Schedule      Next Run          Agent    Status
---------- ------------- ------------- ----------------- -------- -------
abc123defg Standup       every 24h     2026-04-11 09:00  main     active
hij456klmn Weekly Report every 7d      2026-04-17 00:00  main     active
```

---

## 二、手動備份 Cron Jobs

### 2.1 匯出為 JSON 格式（完整備份）

```bash
# 方式 1：直接複製設定檔（最簡單）
cp ~/.openclaw/cron-jobs.json ~/Documents/openclaw-cron-backup-$(date +%Y%m%d).json

# 方式 2：如果有 jobs 目錄，一併備份
cp -r ~/.openclaw/jobs/ ~/Documents/openclaw-jobs-backup-$(date +%Y%m%d)/
```

### 2.2 匯出為可讀文字格式（方便人工檢視）

```bash
# 建立備份目錄
mkdir -p ~/Documents/openclaw-backup-$(date +%Y%m%d)

# 匯出 Cron Jobs 清單
openclaw cron list > ~/Documents/openclaw-backup-$(date +%Y%m%d)/cron-jobs-list.txt

# 匯出詳細設定
openclaw cron list --format json > ~/Documents/openclaw-backup-$(date +%Y%m%d)/cron-jobs-full.json
```

### 2.3 建立人類可讀的備份報告

```bash
# 建立包含時間戳的備份檔
cat > ~/Documents/openclaw-backup-$(date +%Y%m%d)/README.md << 'EOF'
# OpenClaw Cron Jobs 備份報告

## 備份時間
`date`

## Cron Jobs 清單

<!-- 請在此貼上 openclaw cron list 的輸出 -->

## 重要說明

1. 此備份包含所有定時任務的名稱、執行頻率、下次執行時間
2. 若需完整還原，需同時還原 cron-jobs.json 檔案
3. 若僅需重建任務，可使用下方的重建腳本

EOF
```

---

## 三、從備份還原 Cron Jobs

### 3.1 完整還原（直接覆蓋）

> ⚠️ 這會**覆蓋**現有的 Cron Jobs。

```bash
# 停止 Gateway（避免寫入衝突）
openclaw gateway stop

# 還原 JSON 檔案
cp ~/Documents/openclaw-cron-backup-YYYYMMDD.json ~/.openclaw/cron-jobs.json

# 重啟 Gateway
openclaw gateway start
```

### 3.2 重建還原（逐一重建，保留現有任務）

如果你不確定覆蓋是否安全，使用重建方式：

#### Step 1：取得備份檔中的任務清單

```bash
# 讀取備份的 JSON 檔案
cat ~/Documents/openclaw-cron-backup-YYYYMMDD.json
```

#### Step 2：根據清單逐一重建

```bash
# 範例：重建一個每日 standup 任務
openclaw cron add \
  --name "每日 Standup" \
  --every 24h \
  --session isolated \
  --agent main \
  --message "請生成每日 standup 摘要並回報" \
  --announce --channel webchat

# 範例：重建一個每小時健康檢查
openclaw cron add \
  --name "每小時健康檢查" \
  --every 1h \
  --session isolated \
  --agent main \
  --message "請執行健康檢查（磁碟、記憶體、Gateway 狀態）" \
  --announce --channel webchat
```

#### Step 3：確認還原結果

```bash
openclaw cron list
```

---

## 四、自動化定期備份

### 4.1 建立備份 Cron Job

建議每週自動備份一次：

```bash
openclaw cron add \
  --name "OpenClaw Cron Jobs 每週備份" \
  --every 7d \
  --session isolated \
  --agent main \
  --message "請執行以下備份：
1. cp ~/.openclaw/cron-jobs.json ~/Documents/openclaw-cron-backup-\$(date +%Y%m%d).json
2. openclaw cron list > ~/Documents/openclaw-backup-\$(date +%Y%m%d)/cron-jobs-list.txt
備份完成後回報結果。" \
  --announce --channel webchat
```

### 4.2 建立專用的備份腳本

建立 `/Users/claw/scripts/openclaw-backup.sh`：

```bash
#!/bin/bash
# openclaw-backup.sh
# 用途：備份 OpenClaw Cron Jobs

BACKUP_DIR="$HOME/Documents/openclaw-cron-backups"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# 備份 Cron Jobs 設定檔
cp ~/.openclaw/cron-jobs.json "$BACKUP_DIR/cron-jobs-$DATE.json" 2>/dev/null || echo "No cron-jobs.json found"

# 匯出 Cron Jobs 清單
openclaw cron list > "$BACKUP_DIR/cron-list-$DATE.txt" 2>/dev/null || echo "openclaw CLI not available"

# 保留最近 30 份備份，刪除舊的
cd "$BACKUP_DIR"
ls -t | tail -n +31 | xargs rm -f 2>/dev/null

echo "✅ Backup completed: $BACKUP_DIR"
echo "📁 Files: $(ls -1 $BACKUP_DIR | wc -l | tr -d ' ') backups"
```

執行：
```bash
chmod +x /Users/claw/scripts/openclaw-backup.sh
./scripts/openclaw-backup.sh
```

---

## 五、跨設備遷移 Cron Jobs

### 5.1 從 Mac A 遷移到 Mac B

**在 Mac A 上：**
```bash
# 匯出所有 Cron Jobs 為 JSON
openclaw cron list --format json > ~/Desktop/cron-export.json

# 列出所有工作階段與設定（可選）
openclaw session list > ~/Desktop/sessions.txt
```

**在 Mac B 上：**
```bash
# 安裝 openclaw CLI
npm install -g openclaw

# 還原 Cron Jobs
openclaw cron import --file ~/Desktop/cron-export.json

# 或手動重建
# （根據 Mac A 匯出的 sessions.txt 逐一重建）
```

### 5.2 匯出/匯入格式參考

**JSON 匯出格式（預估）：**
```json
[
  {
    "id": "abc123",
    "name": "每日 Standup",
    "schedule": "every 24h",
    "agent": "main",
    "message": "請生成每日 standup 摘要",
    "enabled": true,
    "createdAt": "2026-04-01T09:00:00+08:00"
  }
]
```

---

## 六、常見問題與解決方式

### Q1：備份檔是空的或不存在

**可能原因：**
- QClaw App 模式下，設定檔在 `~/Library/Application Support/QClaw/`
- OpenClaw CLI 模式下，設定檔在 `~/.openclaw/`

**解決方式：**
```bash
# 兩者都檢查
ls ~/.openclaw/cron-jobs.json 2>/dev/null || echo "Not in ~/.openclaw"
ls ~/Library/Application\ Support/QClaw/openclaw/cron-jobs.json 2>/dev/null || echo "Not in QClaw dir"
```

### Q2：還原後任務沒有出現

**可能原因：**
- JSON 格式不符
- 還原時 Gateway 未重啟

**解決方式：**
```bash
# 重啟 Gateway
openclaw gateway restart

# 重新檢視
openclaw cron list
```

### Q3：想保留舊任務，同時新增新任務

**解決方式：**
- 使用「重建還原」方式（不覆蓋，直接新建）
- 或手動比對現有清單與備份清單，只新增缺少的

---

## 七、備份策略建議

| 備份頻率 | 觸發方式 | 保留份數 | 適用場景 |
|---------|---------|---------|---------|
| 每日 | Cron Job | 7 份 | 重要任務 |
| 每週 | Cron Job | 12 份 | 一般使用 |
| 手動 | 按需求 | 永久 | 重大變更前 |

**建議做法：**
1. **每次修改 Cron Jobs 前**：手動備份一次
2. **每週日**：自動化備份到外部儲存
3. **每次升級 QClaw/App 前**：完整備份所有設定

---

## 八、相關參考

- Cron Job 管理：`openclaw cron --help`
- 備份 OpenClaw 全部資料：參考 `openclaw-backup` skill
- 還原流程：見上方「Step 3.2 重建還原」
