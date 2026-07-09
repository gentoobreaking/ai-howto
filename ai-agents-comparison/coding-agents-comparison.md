# AI Coding Agent 差異性分析

> 比較 OpenCode、Pi.dev、OpenClaw、Hermes Agent 四個開源專案

---

## 一、基本資料

| | OpenCode | Pi.dev | OpenClaw | Hermes Agent |
|---|---|---|---|---|
| **開發團隊** | anomalyco（SST） | Earendil Inc. | Peter Steinberger 社群 | Nous Research |
| **GitHub Stars** | 184K | 69K | 382K | 212K |
| **語言** | TypeScript + Go (CLI) | TypeScript (Node.js) | TypeScript (Node.js) | Python |
| **授權** | MIT | MIT | MIT | MIT |
| **定位** | Terminal coding agent | Minimal agent harness | 個人 AI 助理（多頻道） | 自我進化 AI 代理 |
| **首次發布** | 2024 | 2025 | 2024 | 2025 |
| **Package** | `opencode-ai` | `@earendil-works/pi-coding-agent` | `openclaw` | `hermes-agent` |

---

## 二、核心技術架構

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **Runtime** | Effect-TS（TypeScript） | 原生 TypeScript | Pi SDK（TypeScript） | 原生 Python + asyncio |
| **Agent Loop** | Effect-TS 自幹 | `@pi-agent-core` 獨立 package | 基於 Pi SDK | 自幹（conversation_loop） |
| **LLM SDK** | `@ai-sdk/*` | `@pi-ai`（34+ providers） | Pi SDK | OpenAI SDK（通用傳輸層） |
| **Session 儲存** | SQLite（Drizzle ORM） | JSONL 樹狀結構 | JSONL（繼承 Pi） | SQLite（FTS5 全文搜尋） |
| **CLI 語言** | Go | TypeScript（Node） | TypeScript（Node） | Python |
| **TUI** | 自家 TUI | `@pi-tui` | 自家 TUI | prompt_toolkit + curses |
| **Desktop** | Electron / Tauri | 無 | macOS/iOS/Android/Windows | Electron（TypeScript） |

---

## 三、Tool System 比較

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **內建工具數** | 17 | 7 | ~20 | 50+ |
| **檔案操作** | read / write / edit / grep / glob | read / write / edit / grep / find / ls | read / write / edit / bash | read_file / write_file / patch / search_files |
| **Shell** | bash | bash | bash / process | terminal / process / read_terminal |
| **瀏覽器** | 無 | 無 | browser 自動化 | browser 12+ 動作 |
| **子代理** | task tool（原生） | 無（可 extension 實作） | 無（可 extension） | delegate_task |
| **網路** | websearch / webfetch | 無（無內建） | web_search / web_fetch | web_search / web_extract |
| **MCP** | 內建 MCP client | 無（extension 可加） | MCP client | MCP client |
| **LSP** | 內建 LSP client | 無 | 無 | LSP 支援 |
| **排程** | 無 | 無 | cron | cronjob + kanban |
| **Skill** | skill tool | skill 系統 | skill 系統 | skill 系統 + curator |
| **其他** | plan / todo / question / code-mode / apply_patch / lsp | ls（無其他） | canvas / nodes / sessions / discord/slack actions | vision / image_gen / video_gen / tts / computer_use / kanban / home_assistant / clarify |

---

## 四、LLM Provider 支援

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **Provider 數量** | 通用 `@ai-sdk/*` 生態 | 34+ 內建 | 繼承 Pi 生態 | 30+ plugin |
| **Anthropic** | ✓ | ✓ | ✓ | ✓ |
| **OpenAI** | ✓ | ✓ | ✓ | ✓ |
| **Google Gemini** | ✓ | ✓ | ✓ | ✓ |
| **AWS Bedrock** | ✓ | ✓ | ✓ | ✓ |
| **OpenRouter** | ✓ | ✓ | ✓ | ✓ |
| **GitHub Copilot** | ✓ | ✓ | ✓ | ✓ |
| **Ollama** | ✓ | ✓（自訂） | ✓ | ✓ |
| **DeepSeek** | ✓ | ✓ | ✓ | ✓ |
| **自訂 Provider** | ✓ | ✓（models.json） | ✓ | ✓（plugin） |

---

## 五、擴充性

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **Extension/Plugin** | 無（改原始碼） | TypeScript extension（30+ events） | Plugin SDK | Plugin 系統（20+ 種類） |
| **Skill** | skill 目錄 | skill 目錄 | skill 目錄 + ClawHub | skill 目錄 + curator 自動進化 |
| **MCP** | 內建 | 可 extension 實作 | 內建 | 內建 |
| **Hook 事件** | 無 | 30+ 事件 | 透過 Pi SDK | pre/post LLM call, session lifecycle |
| **自訂工具** | 無（改原始碼） | registerTool() | 透過 Pi SDK | registry.register() |
| **自訂 Provider** | config | models.json | config | plugin |

---

## 六、平台支援

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **Terminal CLI** | ✓ | ✓ | ✓ | ✓ |
| **TUI** | ✓ | ✓ | ✓ | ✓ |
| **Desktop** | macOS/Win/Linux | 無 | macOS/Win/Linux + iOS/Android | Desktop（Electron） |
| **Messaging** | 無 | 無 | 20+ 頻道（WhatsApp, Telegram, Discord 等） | 15+ 頻道（Telegram, Discord, Slack, WhatsApp 等） |
| **Voice** | 無 | 無 | macOS/iOS voice wake, Android Talk | 無 |
| **API Server** | ✓（opencode serve） | 無 | ✓（Gateway） | ✓（Gateway REST API） |

---

## 七、特色功能對照

| | OpenCode | Pi | OpenClaw | Hermes |
|---|---|---|---|---|
| **Sub-agent** | task tool 原生支援 | extension 實作 | 無 | delegate_task |
| **Multi-agent** | task tool 遞迴 | 無 | 無 | MoA（Mixture of Agents） |
| **Plan mode** | 內建 plan agent | extension 可實作 | 無 | kanban 規劃 |
| **Compaction** | 自動/手動 | 自動/手動 | 繼承 Pi | 自動/手動 |
| **Project trust** | ✓ | ✓ | ✓ | 無 |
| **Sandbox** | 無 | 建議 container | Docker/SSH/OpenShell | 無 |
| **Session 分支** | 無 | 樹狀分支（單檔多分支） | 繼承 Pi | session chaining |
| **Session 分享** | share link | HTML export + gist | 無 | 無 |
| **記憶系統** | 無 | 無 | memory system | MEMORY.md + USER.md + 外部 providers |
| **自律進化** | 無 | 無 | 無 | 技能 curator 自動改進 |
| **Live Canvas** | 無 | 無 | ✓（A2UI） | 無 |
| **頻道閘道器** | 無 | 無 | ✓（20+ channels） | ✓（15+ channels） |
| **Cron** | 無 | 無 | ✓ | ✓ |
| **Computer Use** | 無 | 無 | 無 | ✓ |
| **Kanban** | 無 | 無 | 無 | ✓ |
| **Web search** | ✓ | 無（可 extension） | ✓ | ✓ |
| **LSP** | ✓ | 無 | 無 | ✓ |

---

## 八、優劣分析

### OpenCode

**優勢：**
- Sub-agent 原生支援（task tool），可遞迴多層
- LSP 整合，程式碼語意理解強
- Plan/Build 雙 agent 模式
- 前後端分離架構（CLI Go + Agent TypeScript）
- Provider 生態通用（`@ai-sdk/*`）
- Session share link 功能
- Go CLI 啟動速度快、無 Node.js 依賴

**劣勢：**
- 無 Extension/Plugin 系統，擴充需改原始碼
- 僅 terminal-first，無多頻道、無語音
- 無分支 session
- 無記憶系統

### Pi.dev

**優勢：**
- Extension 系統成熟（30+ 事件 hook、registerTool/Command/Shortcut/Provider）
- 34+ provider 內建，生態最廣
- 樹狀分支 session（單檔多分支）
- 極簡核心，全用 extension 擴充
- 可程式化使用（SDK / RPC / Print mode）
- Session 可 export HTML / share gist

**劣勢：**
- 僅 7 個內建工具，無瀏覽器、無網路搜尋
- 無 sub-agent（需 extension 實作）
- 無 MCP、無 LSP
- 僅 terminal，無 Desktop 或 messaging
- Node.js 依賴

### OpenClaw

**優勢：**
- **頻道生態最強** — 20+ messaging platform，真正 anywhere access
- **多平台裝置** — macOS/iOS/Android/Windows companion apps
- Live Canvas（A2UI） — agent 驅動視覺介面
- Voice 支援（語音喚醒、TTS、Talk Mode）
- Plugin SDK — 第三方可開發 channel/tool/provider
- Sandbox — Docker/SSH/OpenShell
- 382K stars，社群最大

**劣勢：**
- Agent runtime 依賴 Pi SDK（非自製）
- 非 coding agent 定位（更偏向 general assistant）
- 無 sub-agent、無 plan mode
- 設定複雜（需架設 Gateway）
- TypeScript Node.js 環境

### Hermes Agent

**優勢：**
- **自我進化技能** — 唯一能自動創造/改善技能的 agent
- **工具生態最豐富** — 50+ 工具含 browser、vision、media、kanban、computer use
- **Plugin 系統最完整** — 20+ 種類 plugin，30+ providers
- **MoA（Mixture of Agents）** — 多 agent 協作推論
- **Gateway** — 15+ 頻道 + cron 排程
- 持久記憶系統 + FTS5 全文搜尋
- Credential pool（多 API key 自動 failover）
- Python 生態，科學計算/ML 整合容易

**劣勢：**
- Python 效能開銷大（137 萬行）
- Desktop 平台支援較弱
- Agent loop 最大 90 輪，複雜任務 token 消耗大
- 沒有 LSP 整合
- 設定複雜度高
- 無 sandbox

---

## 九、適用場景建議

| 場景 | 推薦 | 原因 |
|---|---|---|
| **寫程式、terminal coding** | OpenCode | Sub-agent、LSP、plan mode 最強 |
| **需要高度自訂 agent 行為** | Pi.dev | Extension 系統最靈活 |
| **多平台、多頻道個人助理** | OpenClaw | 20+ channels + desktop/mobile apps |
| **需要自我進化、長時間運行** | Hermes Agent | 技能 curator + cron + memory |
| **本地小模型、輕量使用** | OpenCode | Go CLI 輕量，無 Node 依賴 |
| **需要多頻道 + 語音助理** | OpenClaw | Voice + 裝置 node |
| **需要 browser automation** | Hermes Agent | 12+ browser 動作 |
| **需要 schedule 排程任務** | Hermes / OpenClaw | 兩者都有 cron |
| **研究用、快速 prototype** | Pi.dev | SDK/RPC mode，極簡核心 |
| **企業級私有部署** | OpenClaw | Sandbox + Plugin SDK + security policy |

---

> 最後更新：2026-07-09
