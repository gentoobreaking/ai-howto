# QClaw Agent 配置管理指南

## 配置檔案層級

```
~/.qclaw/
├── openclaw.json              # 主配置（agents.list 定義所有 agent）
├── agents/
│   ├── main/agent/            # main agent 專屬配置
│   │   ├── auth-profiles.json # API keys
│   │   └── models.json        # 可用模型清單
│   ├── ann-agent/agent/       # 安安 agent 專屬配置
│   │   ├── auth-profiles.json
│   │   └── models.json
│   └── ...                    # 其他 sub-agents
└── workspace/                 # main agent workspace
    ├── auth-profiles.json     # (可能不存在，用 agents/main/agent/)
    └── models.json
```

## 配置職責分工

| 檔案 | 用途 | 修改方式 |
|------|------|----------|
| `openclaw.json` | Agent 註冊、模型指派、全局設定 | `gateway config.patch` |
| `auth-profiles.json` | API keys（敏感資訊） | 自動管理或手動複製 |
| `models.json` | 可用模型清單、provider 配置 | 自動生成或手動編輯 |

## 配置修改時機

### 1. 新增 Agent
```bash
# openclaw.json agents.list 新增條目
gateway config.patch
```
- 自動建立 `agents/<id>/agent/` 目錄
- 需手動配置 `auth-profiles.json`（複製 main 的）

### 2. 修改模型配置
```bash
# 方式一：修改 openclaw.json agents.list[].model
gateway config.patch

# 方式二：修改 agentDir/models.json（不推薦，可能被覆蓋）
```

### 3. 更新 API Key
```bash
# 手動編輯 auth-profiles.json
# 或透過 OpenClaw CLI: openclaw agents add <id>
```

## 最佳實踐

### ✅ 推薦做法

1. **集中管理 API keys**
   - main agent 的 `auth-profiles.json` 是唯一 source of truth
   - 新建 sub-agent 時從 main 複製

2. **使用 config.patch 修改 openclaw.json**
   - 避免手動編輯導致格式錯誤
   - 自動觸發 gateway reload

3. **model 配置使用物件格式**
   ```json
   {
     "primary": "openrouter/qwen/qwen3.6-plus:free",
     "fallbacks": ["openrouter/openai/gpt-oss-120b:free"]
   }
   ```
   - 比 `"model": "xxx"` 字串格式更好
   - 支援 fallback 機制

### ❌ 避免做法

1. **不要直接編輯 models.json**
   - QClaw/OpenClaw 可能覆蓋
   - 應透過 `openclaw.json` 的 `models.providers` 區段管理

2. **不要在多處存放 API keys**
   - 避免同步問題
   - 統一用 `auth-profiles.json`

## Sub-Agent 配置範本

新建 agent 時的最小配置：

```json
{
  "id": "agent-xxx",
  "name": "顯示名稱",
  "workspace": "/Users/claw/.qclaw/workspace-xxx",
  "agentDir": "/Users/claw/.qclaw/agents/xxx-agent/agent",
  "model": {
    "primary": "openrouter/qwen/qwen3.6-plus:free",
    "fallbacks": [
      "openrouter/openai/gpt-oss-120b:free",
      "openrouter/meta-llama/llama-3.3-70b-instruct:free"
    ]
  }
}
```

建立後執行：
```bash
# 複製 auth-profiles
cp ~/.qclaw/agents/main/agent/auth-profiles.json ~/.qclaw/agents/xxx-agent/agent/
```

---

*文檔建立：2026-04-05*
*相關 Task：T002*
