# OpenClaw Chat Sessions 說明與實務指南

> 如何正確理解並使用 OpenClaw 的 Sessions 機制，避開常見坑洞
> 
> 最後更新：2026-04-11

---

## 一、什麼是 Session？

### 1.1 概念定義

**Session = 一次對話實例**

Session 是 OpenClaw 中記錄「誰在什麼時候、說了什麼、做了什麼」的基本單位。每一個 Session 都有：

| 屬性 | 說明 | 範例 |
|------|------|------|
| `sessionKey` | 唯一識別碼 | `agent:main:telegram:direct:6748222184` |
| `agentId` | 所屬 Agent | `main`、`agent-coder1` |
| `channel` | 通訊渠道 | `telegram`、`webchat`、`discord` |
| `model` | 使用的模型 | `modelroute`、`claude-sonnet-4-20250514` |
| `contextTokens` | 上下文 Token 上限 | `200000` |
| `totalTokens` | 已使用 Token | `58496` |

### 1.2 Session 的層級結構

```
Depth 0: agent:<agentId>:main           ← 主 Agent（龍蝦場主）
            │
            │ sessions_spawn()
            ▼
Depth 1: agent:<agentId>:subagent:<uuid> ← 子 Agent（專業 Worker）
            │
            │ 若啟用 Orchestrator 且 maxSpawnDepth ≥ 2
            ▼
Depth 2: agent:<agentId>:subagent:<uuid>:subagent:<uuid> ← 子子 Agent
```

**關鍵特性：**
- Depth 0 是主 Agent，永遠存在
- Depth 1+ 是 Subagent，由主 Agent 動態派生
- 預設 `maxSpawnDepth = 1`，只允許一層 Subagent
- 子 Session 獨立執行，完成後自動回傳結果

---

## 二、核心 API 一覽

### 2.1 sessions_list — 查看所有 Session

```python
sessions_list(limit=10)
```

**用途：** 查看目前運行中的所有 Session

**輸出範例：**
```json
{
  "count": 1,
  "sessions": [
    {
      "key": "agent:main:telegram:direct:6748222184",
      "kind": "other",
      "channel": "telegram",
      "updatedAt": 1775791677608,
      "model": "modelroute",
      "contextTokens": 200000,
      "totalTokens": 47157
    }
  ]
}
```

### 2.2 sessions_spawn — 啟動子 Agent

```python
sessions_spawn(
    agentId="agent-coder1",        # 目標 Agent ID
    key="agent:main:subagent:xxx", # 自訂 Session Key
    task="執行 T001 任務...",      # 任務描述
    model="modelroute",            # 指定模型（可選）
    timeoutSeconds=3600,           # 超時時間（秒）
    runtime="subagent"             # 運行時環境
)
```

**用途：** 派工給子 Agent，建立獨立的 Sub-session

**重要參數：**
| 參數 | 必填 | 說明 |
|------|------|------|
| `agentId` | 是 | 目標 Agent 的 ID（需在 allowlist 中） |
| `task` | 是 | 要執行的任務描述 |
| `key` | 否 | 自訂 Session Key（不填則自動生成） |
| `model` | 否 | 指定模型（不填則使用 Agent 預設） |
| `timeoutSeconds` | 否 | 超時秒數（預設 300） |

### 2.3 sessions_send — 跨 Session 通訊

```python
sessions_send(
    sessionKey="agent:agent-coder1:subagent:xxx",
    message="進度如何？"
)
```

**用途：** 向指定的 Session 發送訊息（詢問進度、追加指令）

### 2.4 sessions_yield — 結束當前回合

```python
sessions_yield(message="等待子 Agent 完成...")
```

**用途：** 當主 Agent 派發多個 Subagent 時，用 yield 暫停主回合，等待子 Agent 回報結果

---

## 三、Session 與 Agent 的關係

### 3.1 三角關係圖

```
┌─────────────────────────────────────────────────────┐
│                    Agent（角色定義）                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  id: "main"                                   │  │
│  │  tools: [exec, read, write, ...]              │  │
│  │  model: "modelroute"                         │  │
│  │  system: "你是寶寶寶，溫暖活潑..."               │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         │ 派生
                         ▼
┌─────────────────────────────────────────────────────┐
│                  Session（對話實例）                  │
│  ┌──────────────────────────────────────────────┐  │
│  │  sessionKey: "agent:main:telegram:xxx"       │  │
│  │  messages: [                                  │  │
│  │    {"role": "user", "content": "..."},       │  │
│  │    {"role": "assistant", "content": "..."}  │  │
│  │  ]                                            │  │
│  │  contextTokens: 200000                       │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                         │
                         │ spawn
                         ▼
┌─────────────────────────────────────────────────────┐
│              Subagent Session（子對話）               │
│  ┌──────────────────────────────────────────────┐  │
│  │  sessionKey: "agent:main:subagent:uuid"       │  │
│  │  agentId: "agent-coder1"                     │  │
│  │  messages: [...]                             │  │
│  │  完成後 → 結果回傳主 Session                  │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 3.2 Agent ≠ Session

| Agent | Session |
|-------|---------|
| 靜態定義（角色、工具、模型） | 動態實例（對話、記憶） |
| 配置檔 `openclaw.json` | 執行時 `.jsonl` 檔案 |
| 不在「運行」，只是存在 | 正在「運行」，消耗資源 |
| 一個 Agent 可對應多個 Session | 一個 Session 只屬於一個 Agent |

---

## 四、何時使用 Subagent？

### 4.1 適用場景

| 場景 | 說明 |
|------|------|
| **並行任務** | 同時處理多個獨立任務（如：同時分析多支股票） |
| **不同工具集** | 某些任務需要特殊工具權限（如：僅給數據分析 Agent 資料庫存取） |
| **不同模型** | 簡單任務用便宜模型，複雜決策用昂貴模型 |
| **專業分工** | 碼農寫程式、樂樂做測試、安安寫文檔 |
| **風險隔離** | 不信任的任務在隔離 Session 執行 |

### 4.2 不適用場景

| 場景 | 建議 |
|------|------|
| 簡單單一任務 | 直接在主 Session 執行即可 |
| 需要頻繁同步 | Subagent 是獨立的，通訊成本高 |
| 任務間高度依賴 | 用 Pipeline 而非並行 Subagent |
| 任務秒級完成 | Spawn 開銷 > 執行時間，不划算 |

---

## 五、實務流程範例

### 5.1 派工給多個 Subagent（並行執行）

```python
# Step 1: 主 Agent 同時派發 3 個任務
task1 = sessions_spawn(agentId="agent-coder1", task="開發後端 API", key="task1")
task2 = sessions_spawn(agentId="agent-coder2", task="訓練 ML 模型", key="task2")
task3 = sessions_spawn(agentId="agent-ann", task="撰寫文檔", key="task3")

# Step 2: 主 Agent yield，等待結果
sessions_yield(message="已派發 3 個任務，等待完成...")

# Step 3: 下回合會收到子 Agent 的結果
# OpenClaw 會把結果注入到下一則訊息中
```

### 5.2 跨 Session 通訊（詢問進度）

```python
# 主 Agent 向子 Session 發送訊息
sessions_send(
    sessionKey="agent:agent-coder1:subagent:xxx",
    message="進度如何？預計多久完成？"
)

# 子 Session 會收到訊息並回應
# 回應會出現在主 Session 的下一回合
```

### 5.3 查看所有運行中的 Session

```python
# 列出所有 Session
sessions_list(limit=20)

# 輸出：
# agent:main:telegram:direct:6748222184     ← 主 Session
# agent:agent-coder1:subagent:task1        ← 子 Session（運行中）
# agent:agent-coder2:subagent:task2        ← 子 Session（運行中）
# agent:agent-ann:subagent:task3           ← 子 Session（運行中）
```

---

## 六、常見問題與避坑指南

### 6.1 權限拒絕：`agentId is not allowed for sessions_spawn`

**錯誤訊息：**
```
agentId is not allowed for sessions_spawn (allowed: none)
```

**原因：** 主 Agent 沒有權限 spawn 子 Agent

**解法：** 在 `openclaw.json` 的 Agent 配置中加入 `allowedAgents`

```json
{
  "agents": {
    "entries": [
      {
        "id": "main",
        "allowedAgents": {
          "allowAny": false,
          "agents": ["agent-coder1", "agent-coder2", "agent-ann"]
        }
      }
    ]
  }
}
```

### 6.2 子 Agent 工具失靈（如搜尋功能）

**現象：** 子 Agent 啟動成功，但無法使用某些工具（如 web_search）

**原因：** 子 Agent 的工具權限與主 Agent 不同

**解法：** 檢查子 Agent 的 `tools` 配置

```json
{
  "agents": {
    "entries": [
      {
        "id": "agent-coder1",
        "tools": {
          "allowAny": false,
          "tools": ["exec", "read", "write", "web_search", "web_fetch"]
        }
      }
    ]
  }
}
```

### 6.3 Subagent 超時

**現象：** 子 Agent 執行超過預設時間（預設 300 秒）後被終止

**解法：** 調整 `timeoutSeconds`

```python
sessions_spawn(
    agentId="agent-coder1",
    task="大型任務...",
    timeoutSeconds=3600  # 1 小時
)
```

### 6.4 忘記 Yield，主 Session 卡住

**現象：** 主 Agent 派發 Subagent 後，主 Session 沒有回應

**原因：** 主 Agent 需要 `sessions_yield()` 才能進入下一回合接收結果

**正確做法：**
```python
# 派發任務後
sessions_spawn(agentId="agent-coder1", task="...")

# 必須 yield 才會收到結果
sessions_yield(message="等待子 Agent 完成...")
```

### 6.5 太多 Subagent 導致資源耗盡

**現象：** 同時 spawn 過多 Subagent，系統變慢或崩潰

**建議：**
- 一般任務建議同時不超過 5-10 個 Subagent
- 大型任務用 Queue 排隊
- 監控 `sessions_list()` 確保沒有殭屍 Session

### 6.6 子 Agent 之間上下文不共享

**現象：** 子 Agent A 不知道子 Agent B 做了什麼

**原因：** Subagent Session 是完全獨立的

**解法：**
- 若需共享資訊，透過主 Agent 中轉
- 或寫入共享檔案（如 `/tmp/shared_context.json`）

---

## 七、最佳實踐

### 7.1 派工前檢查清單

| 檢查項 | 說明 |
|--------|------|
| ✅ Agent ID 是否在 allowlist | `allowedAgents.agents` 包含目標 ID |
| ✅ 工具權限是否足夠 | 子 Agent 有執行任務所需工具 |
| ✅ 任務是否可獨立執行 | 子 Agent 不依賴主 Session 上下文 |
| ✅ 超時時間是否合理 | 大任務調大 `timeoutSeconds` |

### 7.2 命名慣例

```python
# Session Key 建議格式
key = f"agent:{agent_id}:subagent:{task_id}"
# 例：agent:agent-coder1:subagent:T001

# 或用 UUID
import uuid
key = f"agent:{agent_id}:subagent:{uuid.uuid4()}"
```

### 7.3 錯誤處理

```python
try:
    result = sessions_spawn(agentId="agent-coder1", task="...")
except Exception as e:
    # 記錄錯誤，回報用戶
    print(f"Subagent spawn 失敗: {e}")
```

---

## 八、除錯工具

### 8.1 openclaw doctor

```bash
openclaw doctor           # 執行診斷
openclaw doctor --fix     # 嘗試自動修復
```

可檢測：
- 配置缺失
- 端口衝突
- 認證失效
- Agent 權限問題

### 8.2 查看 Session Log

```bash
# Session 記錄位置
~/.qclaw/agents/<agent_id>/sessions/<session_id>.jsonl

# 例
cat ~/.qclaw/agents/main/sessions/ebc843cd-...-...-.jsonl | tail -100
```

### 8.3 即時監控

```python
# 定期檢查 Session 狀態
while True:
    sessions_list(limit=20)
    time.sleep(60)
```

---

## 九、進階主題

### 9.1 Orchestrator 模式

啟用後，Subagent 可以再 spawn 子 Subagent（Depth ≥ 2）

```json
{
  "agents": {
    "orchestrator": {
      "maxSpawnDepth": 2
    }
  }
}
```

### 9.2 Subagent + Cron 結合

讓 Cron 任務 spawn Subagent 處理：

```python
# 在 cron handler 中
sessions_spawn(
    agentId="agent-coder1",
    task="每日資料清理",
    timeoutSeconds=1800
)
```

### 9.3 多 Agent 協作框架

```
         ┌─→ agent-coder1（後端）
         │
main ────┼─→ agent-coder2（ML）
         │
         └─→ agent-ann（全端）────→ agent-lele（測試）
```

---

## 十、總結

| 主題 | 要點 |
|------|------|
| **概念** | Session = 對話實例，Agent = 角色定義 |
| **API** | `sessions_list`、`sessions_spawn`、`sessions_send`、`sessions_yield` |
| **何時用** | 並行任務、不同工具集、不同模型、專業分工 |
| **何時不用** | 簡單任務、高度依賴、秒級完成 |
| **常見坑** | 權限拒絕、工具失靈、超時、忘記 yield、資源耗盡 |
| **除錯** | `openclaw doctor`、查看 `.jsonl` log |

---

## 參考資料

- [OpenClaw 官方文檔](https://docs.openclaw.ai/)
- [OpenClaw 多會話管理與子代理](https://blog.csdn.net/alspd_zhangpan/article/details/158698256)
- [Subagent 與會話管理](https://blog.csdn.net/zhaoyang4298/article/details/159711815)
- [OpenClaw 多 Agent 協作踩坑實錄](https://blog.csdn.net/tommychian/article/details/159348509)
- [OpenClaw 錯誤信息與故障排除](https://blog.csdn.net/zhwx0537/article/details/159318966)

---

*本文檔基於 OpenClay 2026-04 版本，API 可能隨版本更新而變化*
