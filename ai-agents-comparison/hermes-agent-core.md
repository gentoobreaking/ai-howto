# Hermes Agent 核心架構分析

> 自我進化的 AI 代理。由 Nous Research 開發，Python 為主。MIT 授權。
>
> 原始碼：https://github.com/NousResearch/hermes-agent
> 官網：https://hermes-agent.nousresearch.com | Stars: 212K

---

## 一、概述

Hermes Agent 是 **Nous Research** 開發的自我進化 AI 代理，標語為 "the agent that grows with you"。核心特色是**技能會從經驗中自我創造與改進**，具備跨 session 的持久記憶，支援 CLI、Telegram、Discord、Slack、WhatsApp、Signal 等 15+ 平台。

**語言：** Python 82.4%（核心）+ TypeScript 14.8%（TUI/Desktop）
**Runtime：** Python 3.11+，asyncio
**LLM SDK：** OpenAI Python SDK（作為通用傳輸層）
**授權：** MIT
**總行數：** ~137 萬行 Python，~2,926 檔案

---

## 二、核心架構

```
                    ┌─────────────────────────────────────────┐
                    │           使用者介面層                    │
                    │  CLI │ Gateway(TG/Discord/Signal/...)   │
                    │  TUI │ Desktop │ REST API               │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │           AIAgent (run_agent.py)         │
                    │                                        │
                    │  ┌────────────────────────────────┐     │
                    │  │    Conversation Loop           │     │
                    │  │    (tool-calling iteration)     │     │
                    │  │    • Turn prologue             │     │
                    │  │    • LLM API call + retry      │     │
                    │  │    • Tool execution            │     │
                    │  │    • Turn finalization         │     │
                    │  └────────────────────────────────┘     │
                    │                                        │
                    │  Tool Registry (50+ tools)              │
                    │  Memory Manager + Providers             │
                    │  Context Engine + Compressor            │
                    │  Credential Pool (multi-key failover)   │
                    │  Skill Curator (背景自我進化)           │
                    └──────────────────┬──────────────────────┘
                                       │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        │              │              │              │              │
   ┌────▼────┐  ┌──────▼──────┐ ┌────▼────┐  ┌────▼────┐  ┌──────▼──────┐
   │  LLM    │  │   Plugin    │ │   MCP   │  │  Cron   │  │   SQLite    │
   │Provider │  │   System    │ │ Servers │  │Scheduler│  │    State    │
   │(30+)    │  │(20+種類)    │ │         │  │         │  │(FTS5全文搜尋)│
   └─────────┘  └─────────────┘ └─────────┘  └─────────┘  └─────────────┘
```

---

## 三、核心元件

| 檔案 | 行數 | 職責 |
|---|---|---|
| `run_agent.py` | 6,043 | **AIAgent 類別** — 主要 agent 協調器，60+ 建構參數 |
| `agent/conversation_loop.py` | 5,315 | **Agent 主迴圈** — tool-calling 迭代核心 |
| `agent/agent_init.py` | 2,103 | AIAgent.__init__ — 初始化所有子系統 |
| `agent/chat_completion_helpers.py` | 3,114 | API 呼叫建構器 — kwargs 組合、fallback 啟動 |
| `agent/tool_executor.py` | 1,646 | 工具派發 — 順序/並行執行 |
| `agent/system_prompt.py` | 570 | System prompt 組裝 |
| `agent/credential_pool.py` | 2,384 | 多憑證 failover 管理 |
| `agent/memory_manager.py` | 1,135 | 記憶協調器 |
| `agent/curator.py` | 1,976 | 背景技能維護（自我進化） |
| `hermes_state.py` | 6,459 | SQLite 狀態儲存（FTS5） |
| `gateway/run.py` | 20,933 | 多頻道閘道器 daemon |
| `cli.py` | 16,272 | 互動式 TUI |

---

## 四、Conversation Loop 流程

```
使用者訊息
    │
    ▼
┌──────────────────────────────────────┐
│ Turn Prologue                        │
│ • sanitize message                   │
│ • build system prompt                │
│ • preflight context compression      │
│ • memory prefetch                    │
│ • plugin hooks (pre_llm_call)        │
│ • iteration budget check             │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│ Tool-Calling Loop (max 90 輪)        │
│                                      │
│ while (api_call_count < max_iter)    │
│   1. build api_messages              │
│   2. RETRY LOOP (with backoff)       │
│      • rate limit guard              │
│      • API call (stream/non-stream)  │
│      • error classification          │
│      • fallback activation           │
│   3. process tool_calls              │
│      • execute tools (seq/parallel)  │
│      • tool guardrails               │
│      • append results                │
│      • check should_compress()       │
│   4. ◄── LOOP ──────────────────     │
└──────────────┬───────────────────────┘
               ▼
┌──────────────────────────────────────┐
│ Turn Finalization                    │
│ • trajectory save                    │
│ • session persistence (SQLite)       │
│ • memory sync                        │
│ • skill nudge (自動創造新技能)       │
│ • background review (curator)        │
│ • plugin hooks (post_llm_call)       │
└──────────────────────────────────────┘
```

---

## 五、Tool System（50+ 工具）

| 分類 | 工具 |
|---|---|
| **Web** | `web_search`, `web_extract` |
| **Terminal** | `terminal`, `process`, `read_terminal`, `close_terminal` |
| **File** | `read_file`, `write_file`, `patch`, `search_files` |
| **Browser** | `browser_navigate`, `browser_click`, `browser_type`, `browser_scroll`, `browser_snapshot`, `browser_cdp`, `browser_vision` 等 12+ |
| **Vision** | `vision_analyze` |
| **Image/Video/Audio** | `image_generate`, `video_generate`, `text_to_speech`, `transcribe` |
| **Code** | `execute_code` |
| **Delegation** | `delegate_task`（子代理） |
| **Planning** | `todo`, `memory`, `session_search` |
| **Skills** | `skills_list`, `skill_view`, `skill_manage` |
| **Cron** | `cronjob` |
| **Kanban** | `kanban_show`, `kanban_create`, `kanban_complete`, `kanban_block` 等 10+ |
| **Communication** | `clarify`, `send_message`, `discord_send` |
| **Smart Home** | `ha_list_entities`, `ha_get_state`, `ha_call_service` |
| **Computer Use** | `computer_use` |
| **MCP** | 自動匯入任何 MCP server 工具 |
| **Social** | X/Twitter search 工具 |

---

## 六、LLM Provider 系統（30+）

| 類型 | Provider |
|---|---|
| **Aggregator** | OpenRouter（200+ models）, Nous Portal |
| **Cloud** | OpenAI, Anthropic, Google Gemini, AWS Bedrock, GCP Vertex, Azure AI Foundry |
| **AI Companies** | DeepSeek, xAI, MiniMax, Kimi/Moonshot, Z.AI/GLM, Xiaomi MiMo, NVIDIA NIM, Novita AI |
| **Chinese** | Alibaba (Qwen), Alibaba Coding Plan, StepFun |
| **Codex** | OpenAI Codex, GitHub Copilot, Copilot ACP |
| **Self-hosted** | Ollama, OpenCode Zen, GMI Cloud, OpenAI-compatible |
| **Custom** | 使用者自訂 provider |

**認證管理：** CredentialPool 支援多 API key 自動輪換、OAuth refresh、failover 鏈。

---

## 七、Plugin 系統（20+ 種類）

| Plugin 類型 | 目錄 |
|---|---|
| Model Providers | `plugins/model-providers/<name>/` |
| Memory | `plugins/memory/<name>/`（Honcho, Hindsight, Mem0 等） |
| Context Engines | `plugins/context_engine/<name>/` |
| Browser | `plugins/browser/<name>/` |
| Image/Video Gen | `plugins/image_gen/`, `plugins/video_gen/` |
| Web Search | `plugins/web/<name>/` |
| Platforms | `plugins/platforms/<name>/`（頻道配接器） |
| Cron Providers | `plugins/cron_providers/<name>/` |
| Observability | `plugins/observability/<name>/`（Langfuse 等） |

**Lifecycle hooks：** `pre_llm_call`, `post_llm_call`, `on_session_start`, `on_session_end`, `pre_api_request`, `on_memory_write`, `on_delegation`

---

## 八、差異化特色

| 特色 | 說明 |
|---|---|
| **自我進化技能** | Agent 從複雜任務自動創建技能，curator 背景維護 |
| **Mixture of Agents** | MoA loop — 多 agent 協作推論 |
| **持久記憶** | MEMORY.md + USER.md + 外部 memory provider |
| **Gateway（15+ 頻道）** | Telegram, Discord, Slack, WhatsApp, Signal, iMessage ... |
| **Cron 排程** | 使用自然語言創建 cronjob |
| **Kanban 管理** | 完整看板系統 |
| **Computer Use** | 桌面自動化（螢幕點擊） |
| **MCP 支援** | Stdio/HTTP/SSE transport |
| **Shell hooks** | 使用者自訂觸發腳本 |
| **Sub-agent delegation** | 子代理隔離執行，ThreadPoolExecutor |
| **Credential Pool** | 多 key failover、OAuth refresh |

---

> 核心哲學：Per-conversation prompt caching is sacred. Capability lives at the edges.
