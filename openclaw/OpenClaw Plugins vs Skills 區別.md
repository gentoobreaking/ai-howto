# OpenClaw Plugins vs Skills 區別

> ClawHub 上 Plugins 與 Skills 的功能定位差異

## 配置時間
2026-04-04

## 背景
用戶在 ClawHub 浏览時發現 Plugins 與 Skills 兩種擴展類型，想了解區別以便後續選用。

## Plugins vs Skills 區別

| 維度 | Skills | Plugins |
|------|--------|---------|
| **定位** | 任務能力封裝（Task-oriented） | 系統層級擴展（System-level） |
| **用途** | 賦予 AI 特定技能/工具 | 擴展 OpenClaw 平台本身功能 |
| **粒度** | 較細緻，圍繞單一任務 | 較粗，影響整個系統 |
| **載入方式** | `skills.load.extraDirs` 指定目錄 | `plugins.allow` 白名單 + 加載路徑 |

## 簡單比喻

- **Plugin** = 買了一輛車，新增的底盤系統（輪胎、懸吊、動力系統）
- **Skill** = 給司機學會了某個技能（比如：會看地圖、會倒車雷達）

## ClawHub Plugins 類型

從 https://clawhub.ai/plugins 看到的 Plugin 類型：

| 類型 | 範例 |
|------|------|
| **記憶系統** | Finch Smart Memory、Memrok、DeepLake |
| **頻道整合** | Google Chat Pub/Sub、Zulip |
| **垂直功能** | Financialclaw（理財）、ArbiLink（區塊鏈）、Hedra（影片生成） |
| **安全控制** | Fine Grained Tool Access Control |

## 擴充時機

- 要擴充 AI 能力 → 用 **Skill**
- 要擴充平台功能 → 用 **Plugin**

## 參考文獻
- ClawHub Plugins：https://clawhub.ai/plugins
- ClawHub Skills：https://clawhub.ai/skills
- ClawHub About（安全政策）：https://clawhub.ai/about
