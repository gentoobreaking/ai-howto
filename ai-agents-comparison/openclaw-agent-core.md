# OpenClaw 核心架構分析

> 個人 AI 助理，多頻道閘道器。TypeScript（Node.js），MIT 授權。
>
> 原始碼：https://github.com/OpenClaw/OpenClaw
> 官網：https://openclaw.ai | Stars: 382K

---

## 一、概述

OpenClaw 定位為**個人 AI 助理**，核心是一個**多頻道閘道器（Gateway）**，讓使用者透過 WhatsApp、Telegram、Discord、Signal、iMessage 等 20+ 頻道與 AI 互動。它使用 Pi 的 SDK 作為 agent runtime（`@earendil-works/pi-coding-agent` 的 SDK 模式）。

**語言：** TypeScript（99%），Node.js 24+
**Package：** `openclaw`（npm）
**授權：** MIT
**贊助：** OpenAI, GitHub, NVIDIA, Vercel, Convex

---

## 二、核心架構

```
                    ┌─────────────────────────────────────────┐
                    │             使用者頻道                    │
                    │  WhatsApp │ Telegram │ Discord │ Signal  │
                    │  Slack │ iMessage │ LINE │ WeChat │ ...  │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │           Gateway (閘道器)               │
                    │  頻道配接器 │ Session 管理 │ 路由       │
                    │  訊息佇列 │ 串流派發 │ 安全政策         │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │            Agent Runtime                 │
                    │  （基於 Pi SDK）                          │
                    │  Session │ Tool │ LLM Provider           │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │          整合層                           │
                    │  Tools │ Skills │ MCP │ Cron │ Memory    │
                    │  Sandbox │ Plugin SDK │ Canvas           │
                    └─────────────────────────────────────────┘
```

---

## 三、主要元件

| 模組 | 路徑 | 職責 |
|---|---|---|
| Gateway | `src/gateway/` | 多頻道閘道器核心 — 頻道配接、session 管理、訊息路由 |
| Agent | `src/agents/` | Agent 生命週期（基於 Pi SDK） |
| LLM | `src/llm/` | LLM provider 統一介面 |
| Tools | `src/tools/` | 工具實作（bash, read, write, browser, canvas 等） |
| Sessions | `src/sessions/` | Session 管理與持久化 |
| Skills | `src/skills/` | Skill 載入與管理 |
| MCP | `src/mcp/` | MCP client 管理 |
| Cron | `src/cron/` | 排程任務 |
| Memory | `src/memory/` | 記憶系統 |
| Plugin SDK | `src/plugin-sdk/` | 第三方 plugin 開發 SDK |
| Channels | `src/channels/` | 各頻道配接器實作 |
| Config | `src/config/` | 設定管理 |
| Security | `src/security/` | 安全政策（sandbox，DM policy） |
| TUI | `src/tui/` | 終端機介面 |
| CLI | `src/cli/` | 命令列介面 |

---

## 四、Tool System

| 工具 | 功能 |
|---|---|
| bash | Shell 命令執行 |
| read | 讀取檔案 |
| write | 寫入檔案 |
| edit | 編輯檔案 |
| browser | 瀏覽器自動化 |
| canvas | 視覺畫布（Live Canvas + A2UI） |
| cron | 排程任務管理 |
| sessions_list / sessions_history / sessions_send | Session 操作 |
| discord / slack | 頻道動作 |
| gateway | 閘道器控制 |
| nodes | 節點管理（iOS/Android companion） |
| skills | Skill 管理 |
| web_search / web_fetch | 網路搜尋 |
| process | 程序管理 |

---

## 五、支援頻道（20+）

WhatsApp, Telegram, Slack, Discord, Google Chat, Signal, iMessage, IRC, Microsoft Teams, Matrix, Feishu, LINE, Mattermost, Nextcloud Talk, Nostr, Synology Chat, Tlon, Twitch, Zalo, Zalo Personal, WeChat, QQ, WebChat

---

## 六、通訊平台支援

- **macOS**: Menu bar app, Voice Wake, push-to-talk, Canvas
- **iOS**: Node 配對, Voice trigger, Canvas
- **Android**: Node 配對, Connect/Chat/Voice/Camera/Screen
- **Windows**: Hub 桌面應用

---

## 七、差異化特色

| 特色 | 說明 |
|---|---|
| **Channel-first** | 不是 terminal-first，而是你已有的通訊軟體 |
| **Live Canvas** | Agent 驅動的視覺畫布，支援 A2UI |
| **Voice** | macOS/iOS 語音喚醒 + Android Talk Mode |
| **Node 架構** | 手機/電腦作為節點配對到 Gateway |
| **Plugin SDK** | 第三方可開發 channel/tool/provider plugin |
| **Sandbox** | Docker/SSH/OpenShell 沙箱執行 |
| **ClawHub** | Skill 市集 |
| **Onboard Wizard** | 互動式首次設定 |

---

> 基於 Pi SDK 作為 agent runtime，但 Gateway、多頻道架構、Canvas、Nodes 為自建。
