# GitHub Projects 任務看板建置指南

> 建立日期：2026-04-13  
> 用途：團隊任務視覺化管理

---

## 一、目前狀態

### ✅ 已完成
- [x] 任務掃描腳本：`/Users/claw/howto/import_tasks_to_github_projects.py`
- [x] 掃描結果：**142 個任務**（27 個專案）
  - Pending: 57
  - In Progress: 0
  - Done: 84
  - Skipped: 1

### ⏳ 待完成
- [ ] GitHub CLI 授權（需要 `read:project` scope）
- [ ] 建立 GitHub Project Board
- [ ] 匯入 142 個任務
- [ ] 設定 Telegram 通知

---

## 二、任務分布

| 專案 | 任務數 | 狀態 |
|------|--------|------|
| gold-analysis-core | 29 | 主要專案 |
| revenue-zero-cost | 11 | 營收相關 |
| agent-config | 9 | Agent 配置 |
| github-data-review | 8 | 資料審查 |
| openclaw-scrum | 7 | Scrum 流程 |
| ... | ... | 共 27 個專案 |

---

## 三、建置步驟

### Step 1: GitHub CLI 授權

```bash
# 在終端機執行
gh auth refresh -s read:project,project

# 會顯示授權碼，到 https://github.com/login/device 輸入
```

### Step 2: 建立 GitHub Project

```bash
# 建立 Project（Board view）
gh project create --owner openclawchen8-lgtm --title "任務看板" --format board

# 或使用網頁介面：
# https://github.com/users/openclawchen8-lgtm/projects
```

### Step 3: 設定 Board 欄位

建立 4 個欄位：
- **Pending** — 等待處理
- **In Progress** — 進行中
- **Done** — 已完成
- **Skipped** — 跳過

### Step 4: 匯入任務

```bash
# 預覽模式（不實際匯入）
python3 /Users/claw/howto/import_tasks_to_github_projects.py --dry-run

# 匯出 JSON（供手動匯入）
python3 /Users/claw/howto/import_tasks_to_github_projects.py --export tasks.json

# 實際匯入（需要 GraphQL API）
# 目前 GitHub CLI 對 Projects v2 支援有限，建議：
# 1. 使用 GitHub Projects 的 CSV 匯入功能
# 2. 或手動建立 Draft issues
```

### Step 5: 設定 Telegram 通知

#### 5.1 建立 Telegram Bot

1. 找 @BotFather，建立新 bot
2. 取得 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）
3. 取得 Chat ID：
   - 把 bot 加入群組
   - 發一條訊息
   - 訪問 `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - 找到 `chat.id`

#### 5.2 設定 GitHub Secrets

```bash
# 在 repo 根目錄
cd /Users/claw

gh secret set TELEGRAM_BOT_TOKEN --body "你的 bot token"
gh secret set TELEGRAM_CHAT_ID --body "你的 chat id"
```

#### 5.3 建立 GitHub Actions

建立 `.github/workflows/notify-telegram.yml`：

```yaml
name: Notify Telegram

on:
  issues:
    types: [opened, closed, reopened]
  project_card:
    types: [created, moved]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Send to Telegram
        uses: appleboy/telegram-action@master
        with:
          to: ${{ secrets.TELEGRAM_CHAT_ID }}
          token: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          message: |
            ${{ github.event_name == 'issues' && github.event.action == 'opened' && '📋 新任務' || github.event.action == 'closed' && '✅ 任務完成' || '🔄 任務更新' }}
            
            ${{ github.event.issue.title || github.event.project_card.note }}
            
            ${{ github.event.issue.html_url }}
```

---

## 四、使用方式

### 在 GitHub Projects 管理任務

1. **新增任務**：點「+」建立 Draft issue
2. **移動狀態**：拖曳卡片到不同欄位
3. **指派成員**：點卡片 → Assignees
4. **設定期限**：點卡片 → Due date

### 在 Telegram 接收通知

- 任務建立 → Telegram 通知
- 任務完成 → Telegram 通知
- 狀態變更 → Telegram 通知

### 與 OpenClaw 整合

```bash
# 在 OpenClaw 中查詢任務
gh issue list --project "任務看板"

# 建立新任務
gh issue create --title "新任務" --project "任務看板"
```

---

## 五、維護

### 定期同步

```bash
# 每週同步一次本地 Tasks/ 到 GitHub Projects
python3 /Users/claw/howto/import_tasks_to_github_projects.py --export tasks-$(date +%Y%m%d).json
```

### 備份

GitHub Projects 資料已包含在 repo 備份中（透過 GitHub API）。

---

## 六、參考資料

- [GitHub Projects 官方文檔](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [appleboy/telegram-action](https://github.com/appleboy/telegram-action)
- [GitHub Projects CSV 匯入](https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/adding-items-to-your-project#adding-multiple-issues-or-pull-requests-from-a-repository)

---

## 七、下一步行動

1. **立即**：執行 `gh auth refresh -s read:project,project` 完成授權
2. **今天**：建立 GitHub Project Board
3. **本週**：匯入 142 個任務
4. **本週**：設定 Telegram 通知
