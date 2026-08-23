# Alpaca Paper Trading API 註冊與配置指南

> 建立日期：2026-04-22
> 用途：gold-analysis T004 實盤交易對接 - Alpaca 交易所接入

---

## 註冊流程

### Step 1：註冊 Paper Trading 帳號

1. 訪問：https://app.alpaca.markets/signup
2. 填寫 Email 和密碼
3. 選擇國家（台灣可用，但只能用 Paper Trading）
4. 完成 Email 驗證

> **注意**：如果台灣不在國家列表中，只能使用 Paper Trading（模擬交易），無法進行實盤交易。對於 gold-analysis 的實驗性質，Paper Trading 已足夠。

---

### Step 2：獲取 API Key 和 Secret Key

> ⚠️ **重要提醒**：API Keys 入口不在 Home 頁面！正確路徑如下：
>
> **Setting（左下小齒輪）→ Profile Settings → Manage Accounts → Paper Accounts → API Keys → Generate New Key**

1. 登入後，點擊左下角的 **⚙️ 小齒輪**（Setting）
2. 進入 **Profile Settings**
3. 選擇 **Manage Accounts**
4. 點擊 **Paper Accounts**
5. 進入 **API Keys** 區塊
6. 點擊 **Generate New Key**
7. **立即複製並保存 Secret Key**（只顯示一次！）

**安全提示**：
- ❌ 不要將 API Key 和 Secret Key 提交到 Git
- ✅ 使用環境變數或 `.env` 檔案存儲
- ✅ 將 `.env` 加入 `.gitignore`

---

### Step 3：環境變數配置

在 gold-analysis 專案根目錄建立 `.env` 檔案：

```bash
# gold-analysis/.env
ALPACA_API_KEY=你的API_KEY
ALPACA_SECRET_KEY=你的SECRET_KEY
ALPACA_PAPER=true
```

加入 `.gitignore`：

```gitignore
# gold-analysis/.gitignore
.env
```

---

## Python SDK 安裝

### 官方 SDK：alpaca-py

```bash
pip install alpaca-py
```

### 初始化 Trading Client

```python
import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient

# 載入環境變數
load_dotenv()

# 初始化 Paper Trading Client
trade_client = TradingClient(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_SECRET_KEY"),
    paper=True  # Paper Trading 模式
)

# 驗證連線
account = trade_client.get_account()
print(f"帳號狀態: {account.status}")
print(f"可用資金: {account.buying_power}")
```

---

## 黃金交易支持

### 可交易的黃金相關標的

| 標的 | 類型 | 說明 |
|------|------|------|
| **GLD** | ETF | SPDR Gold Shares，追蹤黃金現貨價格 |
| **IAU** | ETF | iShares Gold Trust，較低管理費 |
| **GDX** | ETF | 黃金礦業指數 ETF |
| **XAU/USDT** | Crypto | 黃金對 USDT 永續合約（加密貨幣） |

### 獲取黃金報價

```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

# 初始化數據客戶端
data_client = StockHistoricalDataClient(
    api_key=os.environ.get("ALPACA_API_KEY"),
    secret_key=os.environ.get("ALPACA_SECRET_KEY")
)

# 獲取 GLD 最新報價
request = StockLatestQuoteRequest(symbol_or_symbols="GLD")
quote = data_client.get_stock_latest_quote(request)
print(f"GLD 買價: {quote['GLD'].ask_price}")
print(f"GLD 賣價: {quote['GLD'].bid_price}")
```

---

## 下單示例

### 買入 GLD

```python
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# 市價買入 1 股 GLD
order = trade_client.submit_order(
    MarketOrderRequest(
        symbol="GLD",
        qty=1,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY
    )
)
print(f"訂單 ID: {order.id}")
print(f"訂單狀態: {order.status}")
```

---

## 相關連結

- **Alpaca 官方文檔**：https://docs.alpaca.markets/
- **alpaca-py GitHub**：https://github.com/alpacahq/alpaca-py
- **API 參考文檔**：https://docs.alpaca.markets/reference/
- **Gold-analysis 專案**：`/Users/claw/Projects/gold-analysis`
- **交易所接口設計**：`/Users/claw/Projects/gold-analysis/backend/app/trading/exchange_interface.py`

---

## 下一步

1. 完成註冊並獲取 API Key
2. 在 gold-analysis 專案中建立 `.env` 檔案
3. 實作 `AlpacaExchange` 適配器（繼承 `ExchangeInterface`）
4. 整合測試
