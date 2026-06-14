# HOWTO: OpenClaw 敏捷任務自動化實作方案

## 目標
在不依赖外部服務的前提下，於本地環境實現 OpenClaw 的敏捷任務自動化流程，涵蓋任務創建、分派、追蹤與成效評估。

---

## 一、現有能力盤點

### 1.1 OpenClaw 內建自動化機制

| 機制 | 說明 | 適用場景 |
|------|------|----------|
| **Cron Jobs** | 定時自動觸發 agent 任務 | 每日standup提醒、週報生成、定期健康檢查 |
| **Subagent Spawn** | 主 agent 派生子 agent 處理子任務 | 任務分解、並行處理、專業分工 |
| **Heartbeat** | 定期背景檢查（郵件/日曆/天氣等） | 被動監控、被動通知 |
| **openclaw cron CLI** | 命令列管理定時任務 | 任務的增刪改查 |
| **Message Tool** | agent 間或對外主動發送訊息 | 任務完成通知、進度回報 |

### 1.2 現有資料架構

```
~/.qclaw/workspace/
├── openclaw-tasks/     # 任務卡片存放
├── openclaw-howto/     # 實作指南存放
├── openclaw-chats/     # 聊天記錄存放
├── openclaw-reports/   # 每日報告存放
└── workspace-ann/      # 安安個人工作區
    ├── memory/          # 每日記憶檔
    └── HEARTBEAT.md     # 心跳任務清單
```

---

## 二、敏捷自動化實作方案

### 方案 A：【基於檔案系統 + Cron 的輕量級方案】（推薦）

#### 核心思路
以 Markdown 檔案（`openclaw-tasks/`）作為任務事實來源，利用 cron job 定期掃描並自動執行對應行動。

#### 工作流程

```
[任務建立]
  planner@豪 建立 .md 任務卡 → 寫入 openclaw-tasks/{project}/T{N}.md
       ↓
[定時掃描]  cron job (每小時或每30分鐘)
  agent 讀取 openclaw-tasks/ 所有未完成的任務卡
       ↓
[自動分派]
  根據 task.metadata.assignee 路由至對應 subagent
  或寫入 openclaw-chats/{project}/T{N}.md 供 planner 後續分派
       ↓
[狀態更新]
  subagent 完成後寫入 openclaw-chats/{project}/T{N}.md 聊天記錄
  並更新 openclaw-reports/ 每日報告
       ↓
[成效追蹤]
  每日報告包含：完成任務數、平均處理時間、逾期任務數
```

#### 實作步驟

**Step 1：建立任務卡範本**

在 `openclaw-tasks/` 下建立統一格式：

```markdown
# T{N} 任務單

## 基本資訊
- **專案：** {project}
- **任務編號：** T{N}
- **建立日期：** {date}
- **負責人：** {assignee}
- **狀態：** 待分派 | 已分派 | 進行中 | 已完成 | 逾期

## 原始需求
{description}

## 評估
- **預估工時：** {estimated_hours}h
- **優先級：** P0/P1/P2/P3
- **標籤：** {tags}

## 實作產出
- Howto 文件：`../openclaw-howto/{project}/T{N}.md`
- 聊天記錄：`../openclaw-chats/{project}/T{N}.md`

## 執行紀錄
<!-- 由 agent 填寫 -->
- **實際開始：** {start_time}
- **實際結束：** {end_time}
- **實際工時：** {actual_hours}h
- **問題/筆記：** {notes}
```

**Step 2：建立每日報告範本**

在 `openclaw-reports/` 下建立每日報告：

```markdown
# 每日報告 {YYYY-MM-DD}

## 今日產出
| 任務 | 負責人 | 狀態 | 備註 |
|------|--------|------|------|
| T016 | 安安 | ✅ 完成 | HOWTO文件已寫入 |

## 明日待辨
| 任務 | 優先級 | 備註 |
|------|--------|------|
| T017 | P1 |  |

## 成效指標
- **任務完成率：** X/Y (Z%)
- **平均處理時間：** N 小時
- **逾期任務：** 0 筆
```

**Step 3：建立自動掃描 Cron Job**

```bash
openclaw cron add \
  --name "敏捷任務掃描" \
  --every 30m \
  --session isolated \
  --agent main \
  --message "請讀取 openclaw-tasks/ 目錄，檢查未完成任務並更新每日報告" \
  --announce --channel webchat
```

> ⚠️ 此 cron job 為概念驗證，需視實際需求調整掃描邏輯與觸發頻率。

---

### 方案 B：【基於 Subagent + 訊息驅動的方案】

#### 核心思路
Planner 在 QClaw App 直接下達任務指令，主 agent 即時 spawn subagent 處理，結果自動寫入對應檔案。

#### 工作流程

```
豪：「幫我執行 T016」
    ↓
主 agent spawn  subagent:ann → 處理 T016
    ↓
subagent 寫入 openclaw-howto/openclaw-scrum/T016.md
    ↓
subagent 寫入 openclaw-chats/openclaw-scrum/T016.md
    ↓
subagent 寫入 openclaw-reports/2026-04-10-agent-ann.md
    ↓
主 agent 回報豪：「T016 已完成，HOWTO文件已寫入」
```

#### 優勢
- 即時響應，無需等待 cron 觸發
- 適合緊急或一次性任務
- subagent 結果自動彙總

#### 劣勢
- 需要豪主動觸發，無法全自動

---

### 方案 C：【結合方案 A + B 的混合方案】（最終推薦）

```
日常流程  → 方案 B（豪主動下達指令，即時處理）
例行工作  → 方案 A（cron 自動掃描，被動執行）
每日報告  → 方案 A（自動彙整）
```

---

## 三、成效追蹤機制

### 3.1 關鍵指標（KPI）

| 指標 | 計算方式 | 目標值 |
|------|----------|--------|
| 任務完成率 | 已完成任務數 / 總任務數 | ≥ 80% |
| 平均處理時間 | 各任務實際工時總和 / 完成任務數 | ≤ 預估工時 |
| 逾期率 | 逾期任務數 / 總任務數 | ≤ 10% |
| HOWTO 文件產出率 | 有 HOWTO 的任務數 / 總任務數 | 100% |

### 3.2 追蹤方式

- **每日報告**：`openclaw-reports/YYYY-MM-DD.md` 自動彙整
- **Heartbeat 摘要**：每 8 小時主動彙報一次進度
- **任務卡狀態欄**：每個任務卡的 `狀態` 欄位即時更新

---

## 四、後續建議

1. **立即可行**：豪在 QClaw App 下達任務時，指定 `openclaw-howto/` 與 `openclaw-chats/` 產出路徑，subagent 會自動寫入
2. **短期（1週內）**：建立統一的任務卡範本與每日報告範本，並建立每日 09:00 的 standup cron job
3. **中期（1個月內）**：評估是否需要引入 `ideas2tasks` skill 將想法自動轉為任務卡片
4. **長期**：若有更多 agent 加入，可考慮建立統一的 `AGENTS.md` 設定檔，規範各 agent 的職責範圍

---

## 五、相關資源

- Cron Job 管理：參考 `openclaw cron --help`
- Subagent 機制：參考 `openclaw help` 中的 subagent 說明
- 備份還原：參考 `HOWTO: OpenClaw Cron Tasks 備份與還原`（T036）
