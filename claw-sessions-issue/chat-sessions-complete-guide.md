# OpenClaw Chat Sessions 完整說明指南

## 目錄
1. [Sessions 機制說明](#sessions-機制說明)
2. [實務常見問題與避坑](#實務常見問題與避坑)
3. [Scrum Project 中的影響與解決方案](#scrum-project-中的影響與解決方案)
4. [最佳實踐建議](#最佳實踐建議)

---

## Sessions 機制說明

### 什麼是 Session？

Session 是 OpenClaw 中**對話上下文的生命週期單元**，負責管理 AI agent 與使用者之間的連續互動。每個 session 包含：

- **對話歷史**：messages、tool calls、responses
- **Agent 狀態**：當前 model、配置、context window
- **路由資訊**：channel（webchat/Discord/Slack）、threadId、delivery 配置
- **元數據**：建立時間、最後活躍時間、session kind（main/subagent/cron/heartbeat）

### Session 的核心概念

#### 1. Session Key 格式
```
agent:<agent-name>:<session-kind>:<uuid>
```

範例：
- `agent:main:cron:1365c343-b2ee-4511-b034-914e71894c8f` - cron 定時任務 session
- `agent:agent-ann:subagent:d90519e3-41d3-4bb3-9876-03c6edc1f513` - subagent session
- `agent:main:webchat:abc123...` - 直接對話 session

#### 2. Session 與 Conversation 的關聯

| 概念 | 說明 | 生命週期 |
|------|------|----------|
| **Conversation** | 使用者的一個「對話頻道」或「聊天室」 | 持續存在，直到手動刪除 |
| **Session** | Conversation 下的**一次完整互動週期** | 有明確的開始與結束 |
| **Context** | Session 內的對話歷史與狀態 | 隨 session 而存在，可能被 compact 壓縮 |

**關鍵差異**：
- 一個 Conversation 可以包含多個 Sessions（例如：跨裝置、跨時間的對話）
- Session 是 OpenClaw 內部的**執行單元**，Conversation 是**使用者視角的對話容器**
- Session 可以被 reset、compact、archive，但不會刪除 Conversation

#### 3. Session 的生命週期狀態

```
[建立] → [Active] → [Idle] → [Compacted] → [Archived] → [Deleted]
         ↓           ↓
      [Processing] [Sleeping]
```

- **Active**：正在處理訊息
- **Idle**：等待新訊息
- **Sleeping**：長時間未使用，可能被清理
- **Compacted**：context 被壓縮（移除舊訊息）
- **Archived**：已歸檔，context 可能已釋放

### Session 的核心工具

OpenClaw 提供以下 session 相關工具：

#### sessions_spawn
建立新的 session（通常用於 subagent）：
```typescript
sessions_spawn({
  agentId: "agent-ann",
  task: "撰寫技術文檔",
  context: { projectInfo: "..." }
})
```

#### sessions_send
向現有 session 發送訊息：
```typescript
sessions_send({
  sessionKey: "agent:main:cron:...",
  message: "任務完成通知"
})
```

#### sessions_list
列出所有 sessions：
```typescript
sessions_list({ agentId: "main" })
```

#### sessions_history
讀取 session 歷史：
```typescript
sessions_history({
  sessionKey: "agent:main:cron:...",
  limit: 100
})
```

#### sessions_compact
壓縮 session context（移除舊訊息以釋放 context window）：
```typescript
sessions_compact({
  sessionKey: "agent:main:cron:..."
})
```

---

## 實務常見問題與避坑

### 問題 1：Session Context 遺失

**症狀**：
- Agent 忘記之前說過的話
- 重複詢問已確認的資訊
- Tool call 結果未被記住

**原因**：
1. **Context Window 達到上限** → OpenClaw 自動 compact 舊訊息
2. **Session 被重置或歸檔** → context 被清空
3. **Subagent session 未正確繼承 context** → 子任務看不到父任務資訊

**解決方案**：
```typescript
// ❌ 錯誤：假設 context 永遠存在
if (userAskedBefore) {
  return previousAnswer; // 可能已被 compact
}

// ✅ 正確：重要資訊持久化到外部檔案
// 將關鍵決策寫入 MEMORY.md 或專案檔案
write_file("MEMORY.md", "用戶偏好: 使用繁體中文");
```

**避坑要點**：
- **關鍵資訊必須寫檔**，不要只放在 session context 中
- 使用 `MEMORY.md` 或專案文檔保存重要決策
- 定期檢查 `sessions_history` 確認 context 是否完整

---

### 問題 2：Cron Session Model 快取汙染

**症狀**（來自 GitHub Issue #61573）：
- Cron job 永久使用 fallback model，即使主要 model 已恢復
- `sessions.json` 中的 `model` 欄位被 fallback model 覆蓋

**原因**：
```json
// sessions.json
{
  "agent:main:cron:xxx": {
    "model": "gpt-5.4-mini"  // ❌ 被 fallback model 永久覆蓋
  }
}
```

當主要 model（如 `anthropic/claude-sonnet-4-6`）暫時不可用時，OpenClaw 會 fallback 到備用 model。但這個 fallback model 會被永久寫入 `sessions.json`，導致後續所有執行都使用錯誤的 model。

**影響**：
- Job 在錯誤的 model 上執行（可能消耗付費 API 額度）
- 問題隨時間累積（每次 outage 感染更多 session keys）
- 無自動修復機制

**解決方案**：
```bash
# 定期清理 cron session 的 model 快取
for key, val in sessions_data.items():
    if ':cron:' in key and 'model' in val:
        del val['model']

# 或使用 openclaw CLI
openclaw sessions clear-model --filter ":cron:"
```

**避坑要點**：
- 監控 cron job 實際使用的 model
- 定期檢查 `sessions.json` 中的 model 欄位
- 考慮在 cron payload 中強制指定 model，不依賴快取

---

### 問題 3：Session 斷裂與重複執行

**症狀**：
- 同一任務被執行多次
- Agent 之間溝通斷層
- Subagent 結果未回傳給 parent

**原因**：
1. **Session A2A (Agent-to-Agent) Ping-Pong**（Issue #62872, #62814）
   - `sessions_send` 在 persistent sessions 中造成重複訊息
   - A2A flow 的 ping-pong 效應導致訊息循環

2. **Thread Routing 遺失**（Issue #49750, #47549）
   - Slack thread ID 未正確保存
   - 導致回覆跑到錯誤的 thread

**解決方案**：
```typescript
// ✅ 正確：使用 private delivery 避免重複
sessions_send({
  sessionKey: targetSession,
  message: "任務完成",
  delivery: { private: true }  // 避免廣播到原 channel
})

// ✅ 正確：保存 threadId
sessions_send({
  sessionKey: targetSession,
  message: "結果回報",
  threadId: originalThreadId  // 確保回覆到正確 thread
})
```

**避坑要點**：
- 使用 `private: true` 避免 A2A 訊息外洩
- 保存並傳遞 threadId 確保正確路由
- 監控 sessions 數量，避免 orphaned sessions 累積

---

### 問題 4：Heartbeat Session 的 Null SessionId

**症狀**（來自 Issue #51066）：
- `sessions.json` 中 heartbeat-origin sessions 的 `sessionId`/`sessionFile` 為 null
- 導致無法正確追蹤 heartbeat sessions

**原因**：
Heartbeat sessions 的初始化流程與一般 sessions 不同，可能在完全建立前就被使用。

**解決方案**：
- 確保 heartbeat sessions 有完整的初始化流程
- 檢查 `sessions.json` 中的 null 值並修復

---

### 問題 5：Session Compact 導致資料遺失

**症狀**：
- 使用 `sessions_compact` 後重要資訊消失
- 無法恢復被 compact 的訊息

**原因**（來自 Issue #57706）：
- `sessions.compact` 的命名容易誤導使用者
- 實際上是 **刪除** 舊訊息，而非只是「壓縮」

**解決方案**：
```typescript
// ❌ 危險：直接 compact 可能遺失重要資訊
sessions_compact({ sessionKey: "..." })

// ✅ 安全：先匯出歷史再 compact
const history = await sessions_history({ sessionKey: "..." });
await write_file("session-backup.json", JSON.stringify(history));
await sessions_compact({ sessionKey: "..." });
```

**避坑要點**：
- Compact 前先備份重要歷史
- 使用 `sessions_export` 功能（Issue #63568 提案中）
- 將關鍵決策寫入外部檔案，不依賴 session context

---

## Scrum Project 中的影響與解決方案

### Session 機制對多 Agent 協作的挑戰

在 Scrum Project 等多 agent 協作專案中，session 機制會造成以下問題：

#### 1. 任務中斷問題

**情境**：
```
Sprint Planning → 建立 task sessions
↓
開發過程中 session 被重置/compact
↓
Agent 忘記任務細節，需要重新說明
```

**影響**：
- Sprint 週期內 agent 上下文遺失
- 估算與實際執行不一致
- 需要頻繁重新 onboarding agent

**解決方案**：
```markdown
# 建立 Sprint 記憶機制

## 1. 使用 MEMORY.md 保存 Sprint Context
# SPRINT_MEMORY.md
- Sprint 目標: 完成用戶認證模組
- 團隊成員: 安安(DocWriter), 小明(Dev)
- 當前進度: T001 完成, T002 進行中
- Blockers: 等待 API 文檔

## 2. 每個 Task 建立獨立檔案
/tasks/T001.md
/tasks/T002.md

## 3. Session 重啟時自動載入
Read SPRINT_MEMORY.md
Read /tasks/T001.md
```

#### 2. Agent 間狀態不同步

**情境**：
```
Agent A (Planner) 建立任務 → 寫入 session context
↓
Agent B (Doer) 執行任務 → 看不到 Agent A 的決策
↓
執行方向與規劃不一致
```

**影響**：
- Planner 與 Doer 認知偏差
- Task 狀態更新不及時
- 重複討論相同議題

**解決方案**：
```markdown
# 建立 Agent 溝通協議

## 1. 使用共享檔案作為訊息佇列
# /comm/agent-messages.md
## Agent A → Agent B
- [2026-04-12 08:00] T001 已建立, 請開始執行
- [2026-04-12 08:05] 收到, 預計 2 小時完成

## 2. 定期 Heartbeat 同步
# HEARTBEAT.md
- [ ] 檢查其他 agent 的訊息
- [ ] 更新自己負責的 task 狀態
- [ ] 同步最新決策到 MEMORY.md

## 3. 使用 sessions_send 進行即時通知
sessions_send({
  sessionKey: "agent:agent-b:main:...",
  message: "T001 需求已更新，請查看"
})
```

#### 3. Context Window 限制與知識碎片化

**情境**：
```
Sprint 進行中 → 大量對話歷史
↓
Session 被自動 compact
↓
早期決策被移除
↓
後期對話缺乏背景資訊
```

**影響**：
- 早期 architectural decisions 遺失
- 新加入的 agent 缺乏上下文
- 需要重新解釋相同概念

**解決方案**：
```markdown
# 知識管理策略

## 1. 決策文檔化（ADR - Architecture Decision Records）
# /docs/adr/
ADR-001-選擇-PostgreSQL-作為主資料庫.md
ADR-002-使用-JWT-進行認證.md

## 2. Context 分層管理
# Layer 1: 專案背景（永久保存）
MEMORY.md, README.md

# Layer 2: Sprint 記憶（Sprint 週期）
SPRINT_MEMORY.md, tasks/*.md

# Layer 3: Session Context（臨時）
messages, tool calls

## 3. 定期 Compaction 檢查
# HEARTBEAT.md
- [ ] 檢查 session context 長度
- [ ] 將重要決策移至 MEMORY.md
- [ ] 觸發 compact 釋放空間
```

---

### 實際案例：Scrum Project Session 避坑指南

#### 案例 1：Sprint Planning Session 管理

**錯誤做法**：
```typescript
// ❌ Sprint Planning 討論全部放在一個 session
sessions_spawn({
  agentId: "planner",
  task: "Sprint Planning 會議"
})
// 所有討論、決策、估算都在這個 session
// → Session 超載，後續查詢困難
```

**正確做法**：
```markdown
# Sprint Planning 拆分為多個單元

## Session 1: Backlog Review
- 檢視 Product Backlog
- 產出: BACKLOG_REVIEW.md

## Session 2: Capacity Planning
- 團隊容量估算
- 產出: CAPACITY.md

## Session 3: Sprint Goal Setting
- 決定 Sprint Goal
- 產出: SPRINT_GOAL.md

## Session 4: Task Breakdown
- 將 Stories 拆成 Tasks
- 產出: tasks/T001.md, T002.md...

每個 Session 有明確產出，寫入檔案而非 session context
```

#### 案例 2：Daily Standup 自動化

**問題**：
- Cron job 觸發 standup 詢問
- Agent 需記住昨天做了什麼
- Session context 可能已 compact

**解決方案**：
```markdown
# HEARTBEAT.md（每日更新）

## 今日狀態
- 昨天完成: T001, T002
- 今天計畫: T003, T004
- Blockers: 無

## Cron Job 腳本
1. Read HEARTBEAT.md
2. 檢查 task 狀態
3. 發送 standup 報告到 Slack
4. 更新 HEARTBEAT.md
```

#### 案例 3：跨 Agent 任務移交

**問題**：
```
Agent A (Planner) 完成規劃 → 建立 tasks
↓
Agent B (Doer) 接手 → 不知道從何開始
```

**解決方案**：
```markdown
# /tasks/T001.md（標準模板）

# T001 - 實作用戶認證 API

## 基本資訊
- **Type**: feature
- **Assignee**: 安安
- **Priority**: high
- **Status**: ready-to-start

## 描述
實作 POST /api/auth/login 端點...

## 實作要點（由 Planner 提供）
- 使用 JWT token
- 密碼使用 bcrypt 加密
- 需處理 rate limiting

## 驗收標準
- [ ] 可正確驗證用戶
- [ ] 錯誤處理完整
- [ ] 單元測試覆蓋率 > 80%

## 技術決策（參考 ADR-002）

## 相關資源
- [API 文檔](link)
- [設計稿](link)

---
_建立日期: 2026-04-12_
_建立者: Agent A (Planner)_
```

---

## 最佳實踐建議

### 1. Session 生命週期管理

```markdown
## 建立 Session
✅ 使用有意義的 label/sessionKey
✅ 初始化時載入必要的 context（從檔案）
✅ 記錄 session 建立原因

## 使用 Session
✅ 重要決策立即寫檔，不依賴 context
✅ 定期檢查 context 長度
✅ 使用 heartbeat 保持 session 活躍

## 結束 Session
✅ 產出結果寫入檔案
✅ 更新相關 task 狀態
✅ 通知相關 agents
```

### 2. 多 Agent 協作協議

```markdown
## 溝通方式優先級
1. **檔案交換**（最可靠）
   - MEMORY.md, tasks/*.md, comm/*.md
   
2. **sessions_send**（即時通知）
   - 用於提醒、狀態更新
   - 不應包含完整 context

3. **Session context**（最脆弱）
   - 只用於臨時對話
   - 可能被 compact

## 狀態同步機制
- 每 6 小時 heartbeat 檢查
- 每日更新 MEMORY.md
- 每個 task 狀態變更立即寫檔
```

### 3. Context Window 優化

```markdown
## 減少 Context 消耗
✅ 使用 compact 工具定期清理
✅ 避免重複載入相同資訊
✅ 將大型檔案分段讀取（offset/limit）

## Context 分層
Layer 0: 系統指令（不可變）
Layer 1: 專案記憶（MEMORY.md，長期）
Layer 2: 當前任務（task 檔案，中期）
Layer 3: 對話歷史（session context，短期）

## Compaction 策略
- 重要決策 → 立即寫檔
- 臨時討論 → 可被 compact
- 定期備份 session history
```

### 4. 監控與除錯

```markdown
## 定期檢查項目
- [ ] sessions.json 中的 model 欄位（避免 fallback 汙染）
- [ ] Orphaned sessions 數量（Dashboard → Sessions）
- [ ] Session context 長度（避免超載）
- [ ] Thread routing 正確性（Slack/Discord）

## 除錯工具
```bash
# 列出所有 sessions
openclaw sessions list

# 檢查 session 歷史
openclaw sessions history <sessionKey>

# 清理 stale sessions
openclaw sessions prune

# 匯出 session（未來功能）
openclaw sessions export <sessionKey> --output backup.json
```
```

---

## 總結

OpenClaw 的 session 機制是強大的對話管理工具，但在實務上需要注意：

1. **Session Context 是臨時的** → 重要資訊必須持久化到檔案
2. **Model 快取可能汙染** → 定期檢查 sessions.json
3. **Multi-agent 需要同步機制** → 使用檔案交換 + sessions_send 通知
4. **Context Window 有上限** → 分層管理 + 定期 compact

**核心原則**：
> **檔案 > Session Context**
> 
> 重要決策、長期記憶、agent 間通訊都應該依賴檔案系統，而非 session context。

---

## 參考資源

- [OpenClaw GitHub Issues - sessions](https://github.com/openclaw/openclaw/issues?q=sessions)
- Issue #61573: Cron sessions permanently cache fallback model
- Issue #62872, #62814: sessions_send A2A ping-pong duplicate messages
- Issue #57706: Rename sessions.compact to prevent confusion
- Issue #51066: sessionId null for heartbeat-origin sessions
- OpenClaw Documentation: Agent Runtime and Tooling

---

_文檔版本: 1.0_  
_建立日期: 2026-04-12_  
_作者: 安安 (DocWriter)_
