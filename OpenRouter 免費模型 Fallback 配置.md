# OpenRouter 免費模型 Fallback 配置

> 當 QClaw 配額用完後，自動切換到 OpenRouter 免費模型

## 配置時間
2026-04-04

## 背景
QClaw 付費配額並非無限量供應。當額度用完時，需要自動切換到備援模型以確保服務不中斷。

## 配置內容

### 1. 新增 OpenRouter Provider
```json
"openrouter": {
  "baseUrl": "https://openrouter.ai/api/v1",
  "apiKey": "sk-or-v1-xxxxxxxxxxxx",
  "api": "openai-completions",
  "models": [
    { "id": "qwen/qwen3.6-plus:free", "name": "Qwen3.6 Plus (Free)" },
    { "id": "openai/gpt-oss-120b:free", "name": "GPT OSS 120B (Free)" },
    { "id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Llama 3.3 70B (Free)" }
  ]
}
```

### 2. 設定 Fallback 順序
```json
"agents": {
  "defaults": {
    "model": {
      "primary": "qclaw/modelroute",
      "fallbacks": [
        "openrouter/qwen/qwen3.6-plus:free",
        "openrouter/openai/gpt-oss-120b:free",
        "openrouter/meta-llama/llama-3.3-70b-instruct:free"
      ]
    }
  }
}
```

## Fallback 優先級

| 優先級 | 模型 | 理由 |
|--------|------|------|
| #1 | qwen/qwen3.6-plus:free | 1M context，中文能力最強，通用性最好 |
| #2 | openai/gpt-oss-120b:free | OpenAI 開源，工具調用能力不錯 |
| #3 | meta-llama/llama-3.3-70b-instruct:free | 穩定保底 |

## 運作原理

```
請求進來 
  → 先用 qclaw/modelroute 
  → 如果失敗（額度用完） 
    → 自動切換到 #1 qwen3.6-plus:free 
    → 再失敗 
      → 切換到 #2 gpt-oss-120b:free 
      → 再失敗 
        → 切換到 #3 llama-3.3-70b:free
```

## 相關命令

```bash
# 查看目前 fallback 列表
openclaw models fallbacks list

# 新增 fallback 模型
openclaw models fallbacks add openrouter/qwen/qwen3.6-plus:free

# 移除 fallback 模型
openclaw models fallbacks remove <model-id>
```

## 參考文獻
- OpenRouter 官網：https://openrouter.ai
- OpenRouter 免費模型列表：https://openrouter.ai/docs/free-models
- OpenRouter API Key 申請：https://openrouter.ai/settings/keys

## 備註
- 配置檔案位置：`~/.qclaw/openclaw.json`
- 需重新啟動 Gateway 生效（config.patch 會自動觸發）
- OpenRouter 免費模型可能因流量限制而出現暫時性不可用，多層 fallback 可提升可用性
