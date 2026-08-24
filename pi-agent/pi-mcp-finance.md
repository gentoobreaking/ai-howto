# pi agent × 金融 MCP（yfinance-mcp ＋ FinMind-MCP）安裝筆記

> 建立日期：2026-08-25
> 上游專案：
> - yfinance-mcp：https://github.com/narumiruna/yfinance-mcp（PyPI 套件名 `yfmcp`）
> - FinMind-MCP：https://github.com/FinMind/FinMind-MCP
>
> 用途：讓 pi 在開發對話中即時查詢台股／美股數據，交叉驗證 tw-quant 管線輸出。
> **定位是開發除錯工具**——自動化管線直接呼叫函式庫／REST，不經過 MCP。

---

## 一、pi 沒有內建 MCP，怎麼接？

pi 官方設計不含 MCP runtime（見 pi docs usage.md）。本機既定慣例是用
**mcporter**（已裝 `/opt/homebrew/bin/mcporter`）當通用 MCP client，
pi 的 bash 直接 `mcporter call ...` 呼叫。

```
pi agent ──bash──> mcporter ──stdio──> yfmcp / finmind-mcp 子程序
```

## 二、事前需求

| 工具 | 檢查 | 未裝的話 |
|---|---|---|
| uv | `which uvx` | brew install uv |
| mcporter | `mcporter --version` | npm i -g mcporter |
| FinMind token | https://finmindtrade.com/analysis/#/account/user 註冊取得 | 免費會員即可 |

## 三、安裝

### 1. yfinance-mcp

無需預先安裝，`uvx yfmcp@latest` 會即時拉起。直接註冊到 mcporter：

```jsonc
// ~/.mcporter/mcporter.json — 加入 mcpServers 區塊
{
  "mcpServers": {
    "exa": { "baseUrl": "https://mcp.exa.ai/mcp" },
    "yfinance": {
      "command": "uvx",
      "args": ["yfmcp@latest"]
    }
  }
}
```

> Docker 替代：`"command": "docker", "args": ["run", "-i", "--rm", "narumi/yfinance-mcp"]`

### 2. FinMind-MCP

```bash
# 先驗證能跑（會印 MCP handshake JSON 即正常）
FINMIND_TOKEN=你的token uvx finmind-mcp@latest
# Ctrl+C 離開
```

註冊（token 用 env 帶入，不要寫進 config 以免外洩）：

```jsonc
// ~/.mcporter/mcporter.json — mcpServers 再加一筆
    "finmind": {
      "command": "uvx",
      "args": ["finmind-mcp@latest"],
      "env": {
        "FINMIND_TOKEN": "你的token"
      }
    }
```

> 若不想把 token 放設定檔：改用 wrapper script——
> `~/.local/bin/finmind-mcp-wrapper.sh` 內容 `exec env FINMIND_TOKEN=xxx uvx finmind-mcp@latest`
> （chmod +x），config 的 command 指向該 script。

### 3. 驗證

```bash
mcporter list                      # 兩個 server 都應顯示 healthy
mcporter call yfinance.yfinance_get_analyst_estimates symbol=2330.TW \
  sections='["eps_trend","eps_revisions"]'
mcporter call finmind.<tool名> ... # tool 清單見下方
```

## 四、兩個 MCP 能做什麼、限制在哪

### yfinance-mcp（Yahoo Finance）

| 重點工具 | 對應 tw-quant 因子 |
|---|---|
| `yfinance_get_analyst_estimates`（earnings_estimate / eps_trend / eps_revisions / growth_estimates） | **因子② EPS 上修**（唯一免費來源）|
| `yfinance_get_analyst_price_targets` | 輸出欄位「1個月目標價」參考 |
| `yfinance_get_price_history` / chart | K 線、均線驗算 |

**限制：**
- Yahoo 無 SLA、IP 限流嚴格（實測沙箱代理 IP 直接 429）；連續查詢要間隔
- 台股分析師覆蓋稀：權值股 20~40 位、小型股可能 <5 位甚至無資料
- 只有「共識彙總」，看不到個別券商報告原文
- ⚠️ 它與管線同源（都是 yfinance）→ **當備援沒有意義**，只當對話查詢工具

### FinMind-MCP（台股本土資料庫，75+ 資料集）

| 重點資料集 | 對應 tw-quant 因子 |
|---|---|
| InstitutionalInvestorsBuySell（三大法人買賣超） | 因子③ 籌碼（備援 TWSE fund/T86）|
| TaiwanStockMonthRevenue / FinancialStatements | 因子① 營收 YoY、財報（備援 TWSE API）|
| TaiwanStockPrice（日線 OHLCV） | 因子④⑤ 價量（備援 yfinance）|
| TaiwanStockPriceTick / IntradayTick | 盤中 tick（管線暫不用）|

**限制：**
- 免費會員約 **600 requests/hr**（未登記更少），批次抓取必須節流
- 資料皆為**日結更新**（法人/營收盤後才有），無盤中即時性
- ❌ **沒有券商 EPS 預估共識**——因子②無法用它備援，這點無解
- token 有效期限與配額以官網帳戶頁為準

## 五、在 tw-quant 架構中的分工

```
pipeline_screener.py（自動化）
  ├─ 主路徑：yfinance 函式庫 + TWSE API + TDCC
  └─ 備援：FinMind REST API（common/rate_limit.py 加 "finmind" 通道）

pi 開發對話（手動）
  └─ mcporter call yfinance.* / finmind.*
     用途：驗證管線輸出、臨時交叉比對、除錯時快速看數據
```

## 六、常見問題

| 症狀 | 原因 | 解法 |
|---|---|---|
| `mcporter list` 顯示 offline | uvx 第一次下載套件逾時（預設 timeout 30s）| 先手動 `uvx yfmcp@latest` 跑一次暖機；或調大 per-server timeout |
| Yahoo 查詢回 429/401 | IP 限流或缺 crumb | 等 60s 再試；管線內走 yfinance 函式庫（有內建處理）|
| FinMind 回 400/429 | token 失效或超過 600/hr | 換 token；批次作業加 delay |
| 沙箱環境抓不到 ~/Library/Caches | macOS TCC 保護 | 無影響——MCP server 不需要瀏覽器 |

---
*相關文件：pi-task-split.md（任務拆解）、pi-run-project.md（專案執行）、tw-quant 任務書 T003*
