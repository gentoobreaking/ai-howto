# HOWTO: 追蹤 Subagent 任務執行狀態的解決方案

## 問題描述

當 Planner（豪）在 QClaw App 下達任務給 subagent 時，QClaw App 的對話介面只能看到最終結果，**無法看到 subagent 的處理過程**（如：讀了哪些檔案、執行了哪些步驟、遇到了什麼問題）。

---

## 二、現有追蹤機制分析

### 2.1 為什麼 QClaw App 看不到處理過程

| 層面 | 說明 |
|------|------|
| **架構限制** | Subagent 在隔離 session 運行，主 agent 僅接收最終回報 |
| **UI 限制** | QClaw App 的對話串僅顯示最終文字回覆，不顯示 subagent 內部日誌 |
| **設計意圖** | QClaw 設計為「語義回覆介面」，而非「開發者除錯面板」|

### 2.2 目前可用的追蹤方式

| 方式 | 說明 | 對豪的可見性 |
|------|------|-------------|
| **對話回覆** | subagent 最後一條訊息 | ✅ 直接可見 |
| **`openclaw-chats/`** | 聊天記錄檔案 | ⚠️ 需主動查閱 |
| **`openclaw-reports/`** | 每日報告 | ⚠️ 需主動查閱 |
| **`openclaw-tasks/`** | 任務卡（最終狀態） | ⚠️ 需主動查閱 |
| **OpenClaw CLI** | `openclaw session list` | ⚠️ 需 SSH 到主機 |

---

## 三、解決方案（共 4 種，按實作難度排序）

### 方案 1：【最簡單 — 要求 subagent 主動匯報里程碑】（✅ 立即可行）

#### 思路
在豪下達任務時，要求 subagent 每完成一個步驟就向豪的主 session 發送一條簡短進度訊息。

#### 實作方式

豪可以在任務描述中加入以下指示：
```
「每完成一個步驟，請發一條訊息回來，格式如：[T016-1/5] 已讀取設定檔」
```

#### 限制
- 需要豪願意接收大量訊息轟炸
- subagent 需具備 `message` 工具許可權
- 不適合高頻率的步驟追蹤

---

### 方案 2：【寫入聊天記錄檔（推薦）】（✅ 立即可行）

#### 思路
Subagent 每完成一個步驟，就寫入 `openclaw-chats/{project}/T{N}.md`。豪可在任何時候打開該檔案查看進度。

#### 實作方式

在 subagent 啟動時，豪指定產出路徑：
```
「請處理 T016，產出路徑：
- openclaw-tasks/openclaw-scrum/T016.md
- openclaw-howto/openclaw-scrum/T016.md
- openclaw-chats/openclaw-scrum/T016.md（請在裡面即時更新步驟進度）」
```

#### 檔案結構建議

```markdown
# T016 聊天記錄

## 基本資訊
- **狀態：** 🔄 處理中
- **進度：** 2/5 步驟完成

## 執行步驟

- [x] Step 1：讀取 openclaw-tasks/ 任務卡 ✅
- [x] Step 2：研究 Cron Job 機制 ✅
- [ ] Step 3：評估三種實作方案 ⏳（當前）
- [ ] Step 4：撰寫 HOWTO 文件
- [ ] Step 5：更新每日報告

## 當前狀態
正在評估方案 A（Cron 掃描）的實作可行性...
```

#### 優勢
- **零額外設定**：直接利用現有架構
- **豪何時想看都可以**：打開檔案即見進度
- **可離線查閱**：不需要即時網路連線

#### 劣勢
- 需要豪主動打開檔案查看（不是主動推送）

---

### 方案 3：【建立每日報告自動推送】（需設定 cron）

#### 思路
建立一個每日 cron job，自動彙整所有任務的當前進度，並推送給豪。

#### 實作步驟

**Step 1：建立進度掃描 agent**

建立 `~/.openclaw/workspace/skills/scrum-progress/SKILL.md`（或用現有的 agent-ann 處理）。

**Step 2：設定每日 cron job**

```bash
openclaw cron add \
  --name "敏捷任務進度報告" \
  --every 24h \
  --session isolated \
  --agent main \
  --message "請讀取 openclaw-chats/ 和 openclaw-tasks/ 目錄，生成所有任務的當前進度摘要，並主動回報" \
  --announce --channel webchat
```

**Step 3：設定推送時間**

建議設在豪每天開始工作前（如 09:00 GMT+8），讓豪一早就能看到前一天的任務進度摘要。

#### 優勢
- 被動接收，不需要豪主動查看
- 自動彙整所有任務狀態

#### 劣勢
- 每日僅一次，缺乏即時性
- 需要豪願意每天收到進度報告

---

### 方案 4：【結合方案 2 + 訊息通知的混合模式】（⭐ 最佳實務）

#### 實作流程

```
豪下達任務
    ↓
subagent spawn → 立即寫入 openclaw-chats/{project}/T{N}.md
    標題：[🔄 進行中] T016 任務處理中
    ↓
每完成一個步驟 → 更新 openclaw-chats/{project}/T{N}.md
    ↓
任務完成 → 發送最終回覆給豪（主 session）
    並在 openclaw-reports/YYYY-MM-DD.md 新增一行產出摘要
```

#### 對豪來說的好處

| 需求 | 對應方式 |
|------|----------|
| 想即時看進度 | 打開 `openclaw-chats/openclaw-scrum/T016.md` |
| 想等完成後看總結 | 等 subagent 的最終回覆 |
| 想看團隊整體進度 | 看每日 `openclaw-reports/` 報告 |

---

## 四、實作建議

### 立即可行的做法（零設定）

豪在指派任務時，加入以下標準指令：

```
請執行以下任務，並即時將處理步驟寫入：
openclaw-chats/{project}/T{N}.md
每完成一步在「執行步驟」區塊打勾。
任務完成後在 openclaw-reports/YYYY-MM-DD.md 新增一行摘要。
```

### 標準化追蹤格式（建議模板）

在 `openclaw-chats/{project}/T{N}.md` 的最上方加入狀態列：

```markdown
<!--
狀態追蹤：🔄進行中 | ✅完成 | ⚠️問題 | ❌逾期
進度：X/Y 步驟
負責人：安安
開始時間：2026-04-10 14:00 GMT+8
-->
```

---

## 五、相關限制說明

| 限制 | 說明 | 目前是否可解決 |
|------|------|----------------|
| QClaw App 無 subagent 內部日誌 | 架構限制 | ❌ 無法直接解決 |
| 豪需要主動查看檔案 | 可透過方案 3 自動推送 | ✅ 可繞過 |
| subagent 執行中無即時反饋 | 預設設計 | ⚠️ 可透過方案 1/4 改善 |

---

## 六、後續建議

1. **豪**：建立一個 `~/.qclaw/workspace/openclaw-chats/` 的捷徑，方便快速查看所有任務進度
2. **豪**：在 QClaw App 建立一個「每日 standup」習慣，於 09:00 查閱 `openclaw-reports/` 報告
3. **技術層面**：若需要更即時的追蹤（如 subagent 正在處理哪個檔案），需要 OpenClaw 未來版本支援，目前無法達成
