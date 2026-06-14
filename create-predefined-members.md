# T023 - 如何不啟動 OpenClaw 也能建立預定義成員

## 任務
在 **不啟動 OpenClaw GUI/daemon** 的情況下，純靠檔案配置建立一個完整的 sub-agent 預定義成員。

---

## 核心原理

OpenClaw 的 sub-agent 透過三層配置驅動：

| 層 | 檔案 | 用途 |
|----|------|------|
| **身份層** | `workspace/IDENTITY.md` 等 | 定義人格、名字、emoji |
| **註冊層** | `openclaw.json` | 向 Gateway 宣告 agent 存在 |
| **模型層** | `agents/<id>/agent/models.json` | 模型供應商設定 |

OpenClaw 啟動時讀取 workspace 的 markdown 檔案 (`IDENTITY.md` / `SOUL.md` / `USER.md` 等)，注入到 session 的 Project Context。**這些檔案不需要 OpenClaw 在線，純文字即可。**

---

## 完整流程（7 步）

### Step 1：建立 Workspace 目錄

```bash
AGENT_ID="agent-mybot"
WORKSPACE_DIR="$HOME/.qclaw/workspace-${AGENT_ID#agent-}"

mkdir -p "$WORKSPACE_DIR"
```

### Step 2：建立身份檔案（IDENTITY.md）

```bash
cat > "$WORKSPACE_DIR/IDENTITY.md" << 'EOF'
# Who Am I?

- **Name:** 我的機器人
- **Creature:** AI Assistant
- **Vibe:** 嚴謹務實、注重細節
- **Emoji:** 🤖
EOF
```

**為什麼需要**：這是 OpenClaw 啟動時第一個讀取的檔案，定義 Agent 的基本身份。

### Step 3：建立人格檔案（SOUL.md）

```bash
cat > "$WORKSPACE_DIR/SOUL.md" << 'EOF'
# SOUL.md

## 經歷
[描述該成員的背景和經驗]

## 風格
- 簡潔直接，不說廢話
- 有深度但不故弄玄虛
- 遇到問題直接說，不繞彎

## 協作方式
- 服從 Planner（豪）的任務指派
- 遇到阻塞主動上報
- 完成後主動確認
EOF
```

### Step 4：建立用戶檔案（USER.md）

```bash
cat > "$WORKSPACE_DIR/USER.md" << 'EOF'
# USER.md - About Your Human

- **Name:** 豪
- **What to call them:** 豪
- **Pronouns:** they/them
- **Timezone:** Asia/Taipei (GMT+8)

## 核心偏好
- 實踐導向：有案例、有步驟、可執行
- 技術有深度，表達要易懂
- 數據必須真實，絕不編造
EOF
```

### Step 5：建立其餘標配檔案

```bash
# AGENTS.md - 工作區規範
cat > "$WORKSPACE_DIR/AGENTS.md" << 'EOF'
# AGENTS.md

## 第一次執行
如果 `BOOTSTRAP.md` 存在，跟隨它初始化。

## 啟動時
1. 讀取 `SOUL.md` — 這是你是誰
2. 讀取 `USER.md` — 這是誰在幫助
3. 讀取 `memory/YYYY-MM-DD.md` 獲取近期上下文
EOF

# HEARTBEAT.md
cat > "$WORKSPACE_DIR/HEARTBEAT.md" << 'EOF'
# HEARTBEAT.md

讀取 HEARTBEAT.md 如果存在，嚴格跟隨它。
不要從先前對話中推斷或重複舊任務。
如果無需關注，回覆 HEARTBEAT_OK。
EOF

# TOOLS.md
cat > "$WORKSPACE_DIR/TOOLS.md" << 'EOF'
# TOOLS.md

## 本地工具備忘錄

[記錄該成員特有的工具、SSH 設定等]
EOF

# MEMORY.md
cat > "$WORKSPACE_DIR/MEMORY.md" << 'EOF'
# MEMORY.md

[長期記憶，初期為空，逐步累積重要資訊]
EOF

# BOOTSTRAP.md（可選，首次啟動用）
cat > "$WORKSPACE_DIR/BOOTSTRAP.md" << 'EOF'
# BOOTSTRAP.md

初次啟動，請建立以下基本配置：
1. 讀取 USER.md 了解服務對象
2. 建立 memory/ 目錄
3. 刪除 BOOTSTRAP.md（已完成初始化）
EOF

mkdir -p "$WORKSPACE_DIR/memory"
```

### Step 6：向 openclaw.json 註冊 Agent

```bash
CONFIG="$HOME/.qclaw/openclaw.json"
AGENT_ID="agent-mybot"
WORKSPACE_DIR="$HOME/.qclaw/workspace-${AGENT_ID#agent-}"
AGENT_DIR="$HOME/.qclaw/agents/${AGENT_ID}/agent"

# 建立 agentDir 目錄
mkdir -p "$AGENT_DIR"

# 複製 auth-profiles.json（從 main 複製以繼承 API keys）
MAIN_AUTH="$HOME/.qclaw/agents/main/agent/auth-profiles.json"
if [ -f "$MAIN_AUTH" ]; then
    cp "$MAIN_AUTH" "$AGENT_DIR/auth-profiles.json"
fi

# 複製 models.json
MAIN_MODELS="$HOME/.qclaw/agents/main/agent/models.json"
if [ -f "$MAIN_MODELS" ]; then
    cp "$MAIN_MODELS" "$AGENT_DIR/models.json"
fi
```

然後使用 `gateway config.patch` 加入 agent 條目：

```bash
# 假設新 agent 條目：
# {
#   "id": "agent-mybot",
#   "name": "我的機器人",
#   "workspace": "/Users/claw/.qclaw/workspace-mybot",
#   "agentDir": "/Users/claw/.qclaw/agents/agent-mybot/agent",
#   "model": {
#     "primary": "qclaw/modelroute",
#     "fallbacks": [
#       "openrouter/openai/gpt-oss-120b:free",
#       "openrouter/meta-llama/llama-3.3-70b-instruct:free"
#     ]
#   }
# }
```

### Step 7：重啟 Gateway

```bash
# 方式一：CLI
openclaw gateway restart

# 方式二：QClaw UI → 設定 → Gateway → 重啟

# 方式三：發送 SIGUSR1
kill -USR1 $(pgrep -f "openclaw" | head -1)
```

---

## Workspace 檔案清單

完整 workspace 需要以下檔案：

```
workspace-{id}/
├── IDENTITY.md      ← 名字 / emoji / 定位（必填，Gateway 讀取）
├── SOUL.md          ← 性格 / 風格 / 協作方式（必填）
├── USER.md          ← 服務對象 + 核心偏好（必填）
├── AGENTS.md        ← 工作區規範（必填）
├── TOOLS.md         ← 本地工具備忘錄（建議填寫）
├── HEARTBEAT.md     ← 心跳任務配置（可選）
├── MEMORY.md        ← 長期記憶（初期空即可）
├── BOOTSTRAP.md     ← 首次初始化腳本（可選，用後刪除）
└── memory/
    └── YYYY-MM-DD.md ← 每日日誌（由 agent 自動建立）
```

### 各檔案何時被讀取

| 檔案 | 讀取時機 |
|------|----------|
| `IDENTITY.md` | 每次啟動新 session 時，從 workspace 載入作為 Project Context |
| `SOUL.md` | 同上，注入到 system prompt |
| `USER.md` | 同上，注入到 Project Context |
| `AGENTS.md` | 同上 |
| `TOOLS.md` | 工具備忘錄，手動查閱 |
| `HEARTBEAT.md` | 每次 heartbeat 時 |
| `BOOTSTRAP.md` | 首次啟動後自動刪除 |
| `memory/YYYY-MM-DD.md` | 每次 session 啟動時讀取 |

---

## 免重啟驗證法（開發期）

如果不想每次改完都重啟 Gateway，可以用這個流程：

```
1. 建立 workspace + 所有 md 檔案（已完成）
2. 用 gateway config.patch 註冊 agent
3. 不重啟，直接在 UI 新開一個與該 agent 的 DM
   → OpenClaw 會即時讀取 workspace 檔案，驗證配置正確
4. 確認無誤後再重啟 Gateway
```

---

## 與 ScenarioWizard 的關係

OpenClaw Admin 的 ScenarioWizard 元件（`ScenarioWizard.vue`）其實就是在做同樣的事，但透過 WebSocket RPC 自動化：

1. AI 生成 `agentsMd`、`soulMd`、`userMd`、`identityMd`
2. 透過 `wsStore.rpc.setAgentFile()` 寫入 workspace
3. 透過 `configStore.setConfig()` 更新 `openclaw.json`
4. 重啟 Gateway

**純配置方式**跳過了 RPC 這層，直接寫檔案，原理完全相同。

---

## 常見坑

1. **IDENTITY.md 沒寫**：Agent 會沒有名字和 emoji，列表只顯示 ID
2. **workspace 路徑錯誤**：路徑必須與 `openclaw.json` 中一致
3. **models.json 缺少 provider**：導致無法呼叫 LLM
4. **忘記重啟 Gateway**：`openclaw.json` 改了但 Gateway 還在用舊配置
5. **BOOTSTRAP.md 沒刪除**：每次啟動都重複初始化邏輯

---

## 快速複製範本（懶人法）

如果已有一個完整的 agent workspace（如 `workspace-ann`），可以直接複製：

```bash
# 複製整個 workspace
cp -r ~/.qclaw/workspace-ann ~/.qclaw/workspace-newbot

# 修改 IDENTITY.md（最重要）
# 修改 SOUL.md
# 修改 USER.md

# 複製 agentDir
mkdir -p ~/.qclaw/agents/agent-newbot/agent
cp ~/.qclaw/agents/ann-agent/agent/models.json ~/.qclaw/agents/agent-newbot/agent/
cp ~/.qclaw/agents/ann-agent/agent/auth-profiles.json ~/.qclaw/agents/agent-newbot/agent/

# 用 gateway config.patch 註冊新 agent
# 重啟 Gateway
```

---

*T023 產出：碼農 1 號，2026-04-08*
