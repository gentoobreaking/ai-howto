# ideas2tasks 自動化腳本系統 howto

> 建立時間：2026-04-21｜最後更新：2026-04-21
> 適用場景：ideas → tasks → GitHub Issues → Board 全鏈路自動化

---

## 📑 目錄

1. [系統概述](#1-系統概述)
2. [目錄結構](#2-目錄結構)
3. [三核心腳本對比](#3-三核心腳本對比)
4. [cron 排程一覽](#4-cron-排程一覽)
5. [資料流向架構圖](#5-資料流向架構圖)
6. [狀態檔案說明](#6-狀態檔案說明)
7. [各腳本詳解](#7-各腳本詳解)
   - [7.1 scan.py — 掃描 Ideas 目錄](#71-scanpy--掃描-ideas-目錄)
   - [7.2 classify.py — 解析 idea 為 tasks](#72-classifypy--解析-idea-為-tasks)
   - [7.3 state_sync.py — 狀態同步核心](#73-state_syncpy--狀態同步核心)
   - [7.4 lifecycle.py — 每日掃描匯報](#74-lifecyclepy--每日掃描匯報)
   - [7.5 executor.py — 建立 tasks + GitHub 同步](#75-executorpy--建立-tasks--github-同步)
   - [7.6 sync_issues_cron.py — GitHub Issue 狀態同步](#76-sync_issues_cronpy--github-issue-狀態同步)
8. [GitHub 同步機制](#8-gitHub-同步機制)
9. [使用範例](#9-使用範例)
10. [已知限制與改善方向](#10-已知限制與改善方向)

---

## 1. 系統概述

這套系統解決的核心問題：**從一個想法（idea）如何自動長成可追蹤的任務（task）並同步到 GitHub**。

核心流程：
```
 Ideas/*.txt（原始想法）
       ↓
 lifecycle.py（每日掃描 + 分類）
       ↓
 lifecycle_status.json（掃描結果快照）
       ↓
 executor.py（建立 T*.md + GitHub Issues + Board）
       ↓
 Tasks/（本地事實來源）
       ↓
 sync_issues_cron.py（每日 21:00，把本地 done 同步回 GitHub）
```

---

## 2. 目錄結構

```
/Users/claw/Ideas/                          ← 原始想法輸入
  ├── project-idea-1.txt                     ← 格式：task.1 / task.1 done
  ├── another-idea.txt
  └── _done/                                 ← 已完成 ideas 歸檔

/Users/claw/Tasks/                           ← 任務追蹤（事實來源）
  ├── gold-analysis/                         ← 專案目錄
  │   ├── README.md
  │   └── tasks/
  │       ├── T001.md
  │       └── T002.md
  └── another-project/
      ├── README.md
      └── tasks/

/Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/   ← 腳本本體
  ├── scan.py              # 讀 Ideas/
  ├── classify.py          # 解析 task.N 標記 → task 列表
  ├── state_sync.py        # 狀態同步核心（TASKS ↔ idea 檔）
  ├── lifecycle.py         # 每日掃描入口
  ├── executor.py          # 建立 tasks + GitHub 同步
  ├── migrate_readme.py   # T*.md → README.md 一次性遷移
  ├── task_audit.py       # 稽核 T*.md vs README.md 一致性
  ├── lifecycle_status.json   # lifecycle.py 輸出
  ├── executor_status.json    # executor.py 輸出
  └── processed_ideas.json   # 跳過已處理 ideas 的記錄

/scripts/                                 ← 其他排程腳本
  ├── sync_issues_cron.py   # GitHub Issue 雙向同步
  ├── gold_monitor_pro.py  # 黃金監控
  ├── sync_all.sh          # 全量同步（~2h一次）
  ├── push-private.sh      # 私有備份上傳
  ├── cleanup_sessions.py  # Sessions 清理
  └── daily-task-review.sh # 每日任務回顧
```

---

## 3. 三核心腳本對比

| | `lifecycle.py` | `executor.py` | `sync_issues_cron.py` |
|---|---|---|---|
| **輸入** | `/Users/claw/Ideas/*.txt` | `lifecycle_status.json` | `/Users/claw/Tasks/**/*.md` |
| **輸出** | `lifecycle_status.json` | `T*.md` + GitHub Issues | GitHub Issue 關閉 |
| **目標** | 發現新 ideas、歸檔已完成的 | 建立 task 檔、寫 GitHub | 同步本地 done → GitHub |
| **寫入** | ❌ 不寫 Tasks/ | ✅ 建立 `T*.md` | ❌ 只讀 Tasks/ |
| **碰 GitHub** | ❌ | ✅（`--github`） | ✅ 關閉 Issue |
| **被誰觸發** | 每小時 cron | 每小時 cron | 每日 21:00 cron |
| **依賴** | `scan.py`、`classify.py`、`state_sync.py` | `lifecycle_status.json` | `gh` CLI |

### 關鍵設計原則

- **Tasks/ 是唯一事實來源**。task 檔的 `Status: done` 為準，idea 檔的 `task.N done` 標記只是輔助。
- **Ideas → Tasks 單向建立**：lifecycle 只負責發現和分類，從不修改 Tasks/。
- **GitHub 同步是雙向的**：executor 寫入（新建 Issue），sync_issues_cron 讀取後關閉（done 的 Issue）。

---

## 4. cron 排程一覽

| cron 名稱 | 時間 | 腳本 | 功能 |
|---|---|---|---|
| `ideas2tasks-scan` | 每小時 | `lifecycle.py --telegram` | 掃 Ideas，發 Telegram 摘要 |
| `ideas2tasks 自動同步 GitHub` | 每小時 | `executor.py --github --no-spawn` | 建立 T*.md + GitHub Issues + Board |
| `sync_issues_cron.py` | 每日 21:00 | `sync_issues_cron.py` | 把本地 done 同步回 GitHub，關閉對應 Issue |
| `daily-task-review` | 每日 21:00 | `daily-task-review.sh` | 每日任務回顧通知 |
| `Private Backup` | 每 3 小時 | `push-private.sh` | 私有資料備份上傳 GitHub |
| `OpenClaw 每3小時自動備份` | 每 3 小時 | `sync_all.sh` | 全量資料同步 |
| `Sessions 清理` | 每 8 小時 | `cleanup_sessions.py` | Sessions 檔案清理 |
| `update_projects.py` | 每日 07:00 | `update_projects.py` | 更新 Projects 看板 |
| `update_daily.py` | 每日 07:00 | `update_daily.py` | 更新每日摘要 |
| `黃金存摺價格監控` | 每 10 分（9-21點）| `gold_monitor_pro.py --check` | 黃金價格監控 |
| `黃金存摺每日收盤` | 週一至五 09:05 | `gold_bot_history.py --daily` | 寫入每日收盤記錄 |

> 查看完整 cron 清單：`cron list`

---

## 5. 資料流向架構圖

```
┌─────────────────────────────────────────────────────────────┐
│                      Ideas/                                 │
│         *.txt（格式：task.1 / task.1 done）                │
└─────────────────────┬───────────────────────────────────────┘
                      │ scan.py（每小時）
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    classify.py                              │
│     task.N 標記解析 → 產出 task 列表（title/assignee/優先） │
│     支援的格式：task.N done、task.N、- [ ] task.N           │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  state_sync.py                               │
│   合併 Tasks/ 實際狀態（ground truth）                      │
│   → 過濾掉已 done 的 task（不重複建立）                     │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│  lifecycle.py ──→ lifecycle_status.json                     │
│  Telegram 摘要（待處理 tasks 數量）                         │
└──────────┬──────────────────────────────────────────────────┘
           │ 每小時
           ▼
┌─────────────────────────────────────────────────────────────┐
│  executor.py --github --no-spawn                             │
│   ├─ 建立 T*.md（防重複：精確→正規化→相似度 0.8）          │
│   ├─ 更新專案 README.md                                      │
│   ├─ 建立 GitHub Issue（含 body file 避免 shell 問題）      │
│   └─ 加入 GitHub Project Board（GraphQL）                  │
└──────────┬──────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│                   Tasks/（本地事實來源）                     │
│         T001.md（含 GitHub Issue URL）                      │
│         README.md（狀態追蹤）                               │
└──────────┬──────────────────────────────────────────────────┘
           │ 每日 21:00
           ▼
┌─────────────────────────────────────────────────────────────┐
│  sync_issues_cron.py                                         │
│   ├─ 正向同步：done/skip task（含 Issue URL）→ 關閉 Issue   │
│   └─ 反向同步（--reverse-sync）：標題比對 → 關閉無 URL 的  │
│       Issue（策略：精確 key → 正規化 match → 相似度 0.85）  │
└─────────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Issues + Project Board                   │
│         openclawchen8-lgtm / openclaw-tasks                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 狀態檔案說明

| 檔案 | 誰寫 | 誰讀 | 用途 |
|---|---|---|---|
| `lifecycle_status.json` | lifecycle.py | executor.py | 掃描快照，供 executor 建立 tasks |
| `executor_status.json` | executor.py | — | 執行結果記錄 |
| `processed_ideas.json` | lifecycle.py | lifecycle.py | 跳過已處理 ideas，避免重複通知 |
| `lifecycle_status.json` | lifecycle.py | — | 掃描快照 |
| `lifecycle_status.json` | lifecycle.py | — | 掃描快照 |

> ⚠️ 注意：`lifecycle_status.json` 同名存在於 `skills/ideas2tasks/scripts/` 和 `skills/ideas2tasks/` 兩處，確認使用腳本所在目錄的版本。

---

## 7. 各腳本詳解

### 7.1 scan.py — 掃描 Ideas 目錄

**職責**：讀取 `/Users/claw/Ideas/*.txt`，回傳候選 idea 列表。

**規則**：
- 排除 `_done/` 子目錄
- 只處理 `.txt` 檔案
- 跳過 0 bytes 空檔案
- 依修改時間倒序（最新優先）

**輸出**：
```python
[{"filename": "gold-analysis-idea.txt", "path": "...", "content": "...", "modified": "..."}]
```

---

### 7.2 classify.py — 解析 idea 為 tasks

**職責**：將 idea 文字解析成結構化 task 列表。

**支援的 task 標記格式**（任一即可）：
```
task.1 done        ← 已完成（executor 跳過）
task.1             ← 待建立
- [ ] task.1       ← 待建立（Markdown checkbox）
task.1 (码农1号)   ← 指定負責人
task.1 (中)        ← 中優先級（預設 Medium）
task.1 (高)        ← 高優先級
task.1: 實際標題    ← 自訂標題
```

**分類邏輯**（`parse_all_formats`）：
- 優先解析 `task.N done` → done list
- 再解析 `task.N` → pending list
- **重要 Bug（2026-04-20 已修復）**：`parse_all_formats` 最末行原本 `return best_pending, best_done`，swap 後順序顛倒，導致 done_count=0。現已改為 `return best_done, best_pending`。

---

### 7.3 state_sync.py — 狀態同步核心

**職責**：維持 Tasks/ 目錄（ground truth）和 idea 檔 task.N 標記之間的同步。

**重要函式**：

| 函式 | 用途 |
|---|---|
| `read_task_status()` | 讀 T*.md 的 Status，正規化輸出 |
| `write_task_status()` | 寫入統一格式（`- **Status**: pending`） |
| `get_tasks_dir_status()` | 掃專案 tasks/，回傳 `{T001: done, T002: pending}` |
| `should_skip_task()` | 三重去重：精確→正規化→相似度>0.8 |
| `merge_classify_with_tasks_status()` | classify 結果 + Tasks/ 實際狀態合併 |
| `sync_idea_to_task_done()` | Tasks/ done → 回寫 idea 檔 task.N done 標記 |
| `scan_tasks_dir()` | 掃描整個 Tasks/，產出待處理追蹤報告 |

**去重三層比對**：
1. **精確一致**：完全相同的標題
2. **正規化一致**：移除 T001 前綴、URL、日期、特殊符號後比對
3. **相似度 > 0.8**：序列相似度超過 80%

---

### 7.4 lifecycle.py — 每日掃描匯報

**職責**：每小時 cron 執行，掃 Ideas → 分類 → 發 Telegram 摘要 → 歸檔已完成的 ideas。

**流程**：
```
1. scan.py 掃 Ideas/（跳過 processed_ideas.json 記錄的檔）
2. classify.py 解析每個 idea
3. state_sync.merge_classify_with_tasks_status() 合併 Tasks/ 實際狀態
4. state_sync.sync_idea_to_task_done() 同步 done 標記
5. 歸檔全 done 的 idea → _done/
6. scan_tasks_dir() 掃描 Tasks/（待處理追蹤主要來源）
7. 寫入 lifecycle_status.json
8. --telegram：發送簡潔摘要
```

**關鍵設計原則（2026-04-20 修正）**：
- 「待處理」從 Tasks/ 目錄來（ground truth），不是 idea 檔
- idea 掃描只用於偵測新 ideas（待建 tasks）
- 歸檔條件：idea 檔所有 task.N 都 done → 歸到 `_done/`

**狀態檔**：寫入 `lifecycle_status.json`，含 `results`（各 idea 解析結果）和 `tasks_report`（Tasks/ 追蹤報告）。

---

### 7.5 executor.py — 建立 tasks + GitHub 同步

**職責**：讀取 `lifecycle_status.json`，為待處理 tasks 建立 `T*.md`，可選同步到 GitHub。

**流程**：
```
1. 讀 lifecycle_status.json
2. 對每個待處理 task：
   ├─ should_skip_task() 去重檢查
   ├─ 建立 T001.md（含 title/assignee/priority/description）
   └─ 更新專案 README.md
3. --github：
   ├─ gh issue create（body file 寫 /tmp/ 避免 shell 問題）
   ├─ gh api graphql 加入 Project Board
   └─ 把 GitHub URL 寫回 T*.md
4. 寫入 executor_status.json
```

**GitHub Issue 標題格式化**（`_humanize_issue_title`）：
- 移除 URL（URL 不該出現在 Issue 標題）
- 移除「請」「幫我」等祈使句開頭
- 在句號/逗號等自然斷句處截斷（不硬切）

**GitHub 設定**：
- Repo：`openclawchen8-lgtm/openclaw-tasks`
- Project Board ID：`PVT_kwHOD-tSg84BUX2a`

---

### 7.6 sync_issues_cron.py — GitHub Issue 狀態同步

**職責**：每日 21:00 執行，把本地已完成（done/skip）的 tasks 同步回 GitHub，自動關閉對應 Issue。

**兩種模式**：

#### 正向同步（預設）
- 條件：task done/skip **且** 含 GitHub Issue URL
- 流程：
  1. `_read_task_status()` 讀取本地狀態
  2. `_extract_issue_numbers()` 提取 URL 中的 issue 編號
  3. 確認 GitHub 上仍是 OPEN
  4. `gh issue close` 關閉，並留言「本地任務已完成，自動同步關閉」

#### 反向同步（`--reverse-sync`）
- 條件：GitHub OPEN Issue 但本地無對應 URL
- 比對策略（三層，由快到慢）：
  1. **Key 比對**：`[project] T00X` 格式 → 直接 key 匹配
  2. **正規化精確比對**：移除所有空白/特殊符號後比對
  3. **相似度 > 0.85**：序列相似度
- 適用場景：手動建立的 Issue 或 executor 漏掉的舊 Issue

**其他模式**：
- `--check-url-missing`：預警 done/skip 但無 GitHub URL 的 task

**Telegram 通知**：執行完發送摘要（關閉數量 + 失敗數量）。

---

## 8. GitHub 同步機制

### 三個同步點

```
┌─────────────┐      executor.py       ┌──────────────┐
│  建立 Issue │  ──── + Board ────→    │  GitHub       │
│  + 加入 Board│      --github          │  Issue OPEN  │
└─────────────┘                         └──────┬───────┘
                                                 │
                    sync_issues_cron.py          │ 每日 21:00
                    ── 關閉 done 的 ──→           │
                                                 ▼
┌─────────────┐                          ┌──────────────┐
│  Tasks/     │  ←────── 讀取 ──────    │  GitHub       │
│  T*.md      │                          │  Issue CLOSED│
└─────────────┘                          └──────────────┘
```

### GitHub 相關檔案位置

| 檔案 | 路徑 |
|---|---|
| Tasks 同步 Repo | `openclawchen8-lgtm/openclaw-tasks` |
| Project Board | `https://github.com/users/openclawchen8-lgtm/projects/1` |
| Issues URL 格式 | `https://github.com/openclawchen8-lgtm/openclaw-tasks/issues/{N}` |
| T*.md 內含 | `📂 GitHub: https://github.com/.../issues/N` |

---

## 9. 使用範例

### 手動執行（除錯/測試）

```bash
# 1. 掃描 ideas（Telegram 格式，忽略已處理）
python3 /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/lifecycle.py --telegram

# 2. 強制重新掃描所有 ideas
python3 /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/lifecycle.py --telegram --force-rescan

# 3. 只乾跑，看會建立什麼 tasks
python3 /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/executor.py --dry-run

# 4. 建立 tasks + GitHub Issues（不含 spawn）
python3 /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/executor.py --github --no-spawn

# 5. 查看 lifecycle_status.json
cat /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/lifecycle_status.json | python3 -m json.tool

# 6. GitHub Issue 同步（預覽）
python3 /Users/claw/scripts/sync_issues_cron.py --dry-run --verbose

# 7. GitHub 反向同步（預覽）
python3 /Users/claw/scripts/sync_issues_cron.py --reverse-sync --dry-run

# 8. 預警：done/skip 但缺 GitHub URL 的 task
python3 /Users/claw/scripts/sync_issues_cron.py --check-url-missing

# 9. 稽核 Tasks/ vs README.md 一致性
python3 /Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/task_audit.py
```

### cron 相關

```bash
# 立即觸發 lifecycle.py
cron run --jobId=<jobId>

# 查看所有 cron jobs（含停用的）
cron list --includeDisabled=true

# 停用/啟用
cron update --jobId=<jobId> --enabled=false
cron update --jobId=<jobId> --enabled=true
```

---

## 10. 已知限制與改善方向

### 已知限制

| 限制 | 說明 | 當前 workaround |
|---|---|---|
| executor 每小時執行 | lifecycle 每小時跑，executor 也每小時跑，但 ideas 通常幾天才新增一個 | 目前 `--no-spawn` 避免浪費，下次可考慮按需執行 |
| lifecycle_status.json 格式 | JSON 結構未版本化，欄位增減不易追蹤 | 目前靠 docstring 維護 |
| 雙向同步依賴 URL | sync_issues_cron 反向同步依賴標題比對，準確度有限 | `--reverse-sync` 標題相似度 0.85 |
| Telegram 通知只是摘要 | lifecycle --telegram 發的是摘要，沒有「確認」互動鈕 | 目前手動執行 executor |

### 改善建議

1. **減少 executor 執行頻率**：ideas2tasks-sync cron 目前每小時，executor 實際只需在 lifecycle 發現新 ideas 時才需要跑。可改為 lifecycle 發現新 tasks → 主動觸發 executor。
2. **統一路徑配置**：所有腳本的 `TASKS_DIR` / `IDEAS_DIR` 應該從一個共用的 `config.json` 讀取，避免散落在各檔案頂部。
3. **executor --github 加上 --dry-run 確認**：實際上線前應該先預覽，確認無誤再執行。
4. **lifecycle.py --telegram 互動升級**：加入 Inline Button「確認建立」或「略過」，讓豪在 Telegram 就能完成操作。
5. **任務超時保護**：executor spawn 的 sub-agent 沒有超時限制，長任務可能卡住。建議加 `--timeout` 或定期 checkpoint。

---

## 相關文件

- [tasks-executor-design.md](../howto/tasks-executor-design.md) — executor 設計原方案（較舊，部分細節已過時）
- `/Users/claw/Tasks/ideas2tasks/README.md` — 專案內部狀態追蹤
- `/Users/claw/.qclaw/workspace/skills/ideas2tasks/scripts/` — 腳本本體（含完整 docstring）
