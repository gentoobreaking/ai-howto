# QClaw 用量限制解決方案

## 問題描述

QClaw 使用 `http://127.0.0.1:19000/proxy/llm` 作為 LLM proxy，當用量達到限制時會返回：
```
当前访问繁忙或今日用量已达上限，请稍后重试或次日再试。
```

## 限制來源分析

| 層級 | 來源 | 說明 |
|------|------|------|
| QClaw Proxy | `127.0.0.1:19000` | QClaw 應用的 LLM 轉發服務 |
| 後端 Model | 騰訊雲/Qwen | 實際 LLM 提供者的配額 |

**關鍵發現**：這是 QClaw 應用層的限制，不是 OpenRouter 的限制。

## 已實施解決方案

### 多模型 Fallback 機制

```json
{
  "primary": "openrouter/qwen/qwen3.6-plus:free",
  "fallbacks": [
    "openrouter/openai/gpt-oss-120b:free",
    "openrouter/meta-llama/llama-3.3-70b-instruct:free"
  ]
}
```

**運作邏輯**：
1. 優先使用 QClaw proxy (`qclaw/modelroute`)
2. 當 main agent 遇到限制時，fallback 到 OpenRouter 免費模型
3. Sub-agents 直接使用 OpenRouter，繞過 QClaw proxy 限制

### 架構設計

```
┌─────────────────────────────────────────────────┐
│                   Main Agent                     │
│  primary: qclaw/modelroute (QClaw proxy)        │
│  fallbacks: OpenRouter free models              │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────┐   ┌───────────┐   ┌───────────┐
│  安安     │   │  樂樂     │   │  碼農2號  │
│ OpenRouter│   │ OpenRouter│   │ OpenRouter│
└───────────┘   └───────────┘   └───────────┘
```

**優點**：
- Main agent 享受 QClaw 整合功能
- Sub-agents 繞過 QClaw 限制，直接使用 OpenRouter
- 多個免費模型輪換，分散配額風險

## 其他解決方案（未採用）

### 方案 B：純 OpenRouter 架構
```json
{
  "primary": "openrouter/qwen/qwen3.6-plus:free",
  "fallbacks": [...]
}
```
- 優點：完全繞過 QClaw 限制
- 缺點：失去 QClaw 特有功能

### 方案 C：付費升級
- 升級 QClaw 會員或 OpenRouter 付費方案
- 適用於高頻使用場景

## 監控與告警

目前依賴錯誤訊息觸發 fallback。未來可考慮：
- 定期檢查 QClaw proxy 可用性
- 用量統計與預警

---

*文檔建立：2026-04-05*
*相關 Task：T007*
