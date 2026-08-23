# 提供免費 Demo/Paper Trading API 的交易所

> 建立日期：2026-04-22
> 用途：gold-analysis T004 實盤交易對接研究

---

## 1. Alpaca Markets ⭐ 推薦（最適合黃金交易實驗）

**官網**：https://alpaca.markets/

**特點**：
- ✅ **免費 Paper Trading 帳號** — 註冊即送虛擬資金
- ✅ **完整 REST API** — Python SDK (`alpaca-trade-api-python`)
- ✅ **支持股票、期權、加密貨幣**
- ✅ **即時市場數據** — 免費獲取
- ✅ **無需真實資金** — 測試環境完全獨立
- ⚠️ **黃金支持** — 有黃金相關 ETF（如 GLD、IAU）和 XAU/USDT 永續合約

**API 申請流程**：
1. 註冊免費帳號 → https://alpaca.markets/
2. 選擇 Paper Trading 模式
3. 獲取 API Key 和 Secret Key
4. Python SDK：`pip install alpaca-trade-api`

**適合 gold-analysis 的理由**：
- 可交易黃金 ETF（GLD、IAU）
- API 簡潔，文檔完善
- 完全免費，無需真實資金

---

## 2. Binance Testnet ⭐ 適合加密貨幣

**Testnet URL**：https://testnet.binance.vision/

**特點**：
- ✅ **免費 Testnet API** — 完整模擬環境
- ✅ **支持現貨、期貨、合約**
- ✅ **XAU/USDT 永續合約** — 直接交易黃金對
- ✅ **無需真實資金** — 註冊即送測試 USDT
- ⚠️ **僅限加密貨幣** — 無股票、外匯

**API 申請流程**：
1. 訪問 Testnet → https://testnet.binancefuture.com/
2. 用 GitHub 帳號登入
3. 獲取 API Key（自動給測試 USDT）
4. Python SDK：`pip install python-binance`

**適合 gold-analysis 的理由**：
- 直接支持 XAU/USDT（黃金對 USDT）
- 24/7 交易，無時段限制
- 完整的期貨/合約功能

---

## 3. Interactive Brokers (IBKR) ⭐ 專業級（需要門檻）

**官網**：https://www.interactivebrokers.com/

**特點**：
- ✅ **Paper Trading 帳號** — 完整模擬
- ✅ **全球市場** — 股票、期貨、外匯、黃金
- ✅ **TWS API** — Python/Java/C# SDK
- ⚠️ **需要開戶** — 需提交身份證明
- ⚠️ **最低入金** — 帳戶有最低要求
- ⚠️ **API 複雜** — 學習曲線較陡

**適合 gold-analysis 的理由**：
- 可交易真實的黃金期貨（GC.CMDTY）
- 全球市場，數據最完整
- 但需要開戶流程

---

## 4. OANDA Practice Account

**官網**：https://www.oanda.com/

**特點**：
- ✅ **Practice Account** — 模擬帳號
- ✅ **支持外匯、黃金（XAU_USD）**
- ✅ **REST API** — 完整文檔
- ⚠️ **需要註冊** — 但無需真實資金
- ⚠️ **API 需申請** — 部分功能需審核

**API 申請流程**：
1. 註冊 Practice Account
2. 申請 API Token
3. Python SDK：`pip install oandapyV20`

---

## 📊 對比總結

| 交易所 | 黃金支持 | 免費 API | 開戶門檻 | API 難度 | 適合程度 |
|--------|---------|---------|---------|---------|---------|
| **Alpaca** | GLD/IAU ETF | ✅ 完全免費 | 無 | 簡單 | ⭐⭐⭐⭐⭐ |
| **Binance Testnet** | XAU/USDT | ✅ 完全免費 | 無 | 簡單 | ⭐⭐⭐⭐ |
| **IBKR** | 黃金期貨 | ✅ Paper Trading | 需開戶 | 複雜 | ⭐⭐⭐ |
| **OANDA** | XAU_USD | ✅ Practice | 需註冊 | 中等 | ⭐⭐⭐ |

---

## 🎯 建議

**如果 gold-analysis 是實驗性質**，推薦：

1. **首選：Alpaca**
   - 最簡單，API 最乾淨
   - 可交易 GLD（黃金 ETF）
   - 完全免費，無需開戶

2. **次選：Binance Testnet**
   - 直接交易 XAU/USDT（黃金對 USDT）
   - 24/7 交易，數據豐富
   - 加密貨幣性質，風險較高

**如果要走向 Production**，則需要：
- IBKR（真實黃金期貨）
- OANDA（外匯/黃金專業平台）

---

## 相關連結

- gold-analysis 專案：`/Users/claw/Projects/gold-analysis`
- T004 任務：`/Users/claw/Tasks/gold-analysis-advanced/tasks/T004.md`
- 交易所接口設計：`/Users/claw/Projects/gold-analysis/backend/app/trading/exchange_interface.py`
