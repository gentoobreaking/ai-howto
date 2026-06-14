# OpenRouter Model 快速切換指南

## 當前配置

| Agent | Primary Model | Fallbacks |
|-------|---------------|-----------|
| main | qclaw/modelroute | qwen3.6-plus → gpt-oss-120b → llama-3.3-70b |
| sub-agents | qwen/qwen3.6-plus:free | gpt-oss-120b → llama-3.3-70b |

## 切換方式

### 方式一：透過 gateway config.patch

```bash
# 修改單一 agent
gateway config.patch '{"agents":{"list":[{"id":"agent-ann","model":{"primary":"openrouter/meta-llama/llama-3.3-70b-instruct:free","fallbacks":["openrouter/qwen/qwen3.6-plus:free"]}}]}}'

# 修改所有 sub-agents（需完整列表）
gateway config.patch '{"agents":{"list":[...]}}'
```

### 方式二：修改 openclaw.json 後重啟

```bash
# 編輯配置
vim ~/.qclaw/openclaw.json

# 重啟 gateway
gateway restart
```

### 方式三：臨時切換（單次對話）

在對話開始時指定：
```
/use-model openrouter/meta-llama/llama-3.3-70b-instruct:free
```

## 推薦的 Fallback 順序

### 免費模型輪換（分散配額）
```json
{
  "primary": "openrouter/qwen/qwen3.6-plus:free",
  "fallbacks": [
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free"
  ]
}
```

### 高品質優先
```json
{
  "primary": "openrouter/meta-llama/llama-3.3-70b-instruct:free",
  "fallbacks": [
    "openrouter/qwen/qwen3.6-plus:free"
  ]
}
```

### 付費模型（如有 API key）
```json
{
  "primary": "openrouter/anthropic/claude-3.5-sonnet",
  "fallbacks": [
    "openrouter/qwen/qwen3.6-plus:free"
  ]
}
```

## 可用免費模型列表

| Model ID | Context | 特點 |
|----------|---------|------|
| qwen/qwen3.6-plus:free | 200K | 平衡型 |
| openai/gpt-oss-120b:free | 200K | GPT 系 |
| meta-llama/llama-3.3-70b-instruct:free | 200K | Llama 系 |

---

*文檔建立：2026-04-05*
*相關 Task：T003*
