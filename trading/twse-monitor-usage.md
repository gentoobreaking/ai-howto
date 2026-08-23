# TWSE Monitor 使用說明

## 概覽

TWSE Monitor 透過[臺灣證券交易所 OpenAPI](https://openapi.twse.com.tw/v1/swagger.json)監控豪關注的個股與市場動態，主動推播至 Telegram（含 iPhone / Apple Watch）。

**無需 API Key，完全免費。**

---

## 基本用法

### 單一模組執行
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-messages
```

### 多模組同時執行
```bash
# 同時跑重大訊息 + 大盤統計
python3 /Users/claw/scripts/twse_monitor.py --check-messages --check-market

# 個股行情 + 閾值監控一起跑
python3 /Users/claw/scripts/twse_monitor.py --check-price --check-threshold
```

### 每日完整總檢查
```bash
python3 /Users/claw/scripts/twse_monitor.py --daily
```
> 一次跑：重大訊息 + 除權除息 + 殖利率 + 注意/處置股票 + 董監事持股 + 月營收/EPS + 公司治理 + 大盤統計
> （`--check-price` 與 `--check-threshold` 不含在 `--daily` 中，需單獨掛 cron）

### Debug 模式
```bash
python3 /Users/claw/scripts/twse_monitor.py --debug --check-threshold
```
開啟後所有 API 請求、判斷過程、計算結果寫入 `/tmp/twse_monitor.log`。

### 查閱完整說明
```bash
python3 /Users/claw/scripts/twse_monitor.py --help
```

---

## 可用模組

| 參數 | 說明 | 頻率建議 | 觸發條件 |
|------|------|----------|----------|
| `--check-messages` | 個股重大訊息 | 每日 1-2 次 | 有新訊息才推 |
| `--check-dividend` | 除權除息預告 | 每日 | 有新預告才推 |
| `--check-valuation` | 殖利率 / 本益比 / 股價淨值比 | 每日 | 有變動才推 |
| `--check-price` | 個股日成交行情 | 每日收盤後 | 每日首次推，之後跳過 |
| `--check-threshold` | 股價閾值監控 | 每日收盤後 | 漲跌停/價格/百分比觸發 |
| `--check-alert` | 注意/處置/變更交易/暫停交易 | 每小時 | 關注股入列才推 |
| `--check-insider` | 董監事持股轉讓 + 持股明細 | 每日 | 有新申報/變動才推 |
| `--check-revenue` | 月營收 + EPS + 財測差異 | 每週/月營收高峰期 | 有新資料才推 |
| `--check-governance` | 裁罰/違規/經營權異動/ESG | 每日 | 有新事件才推 |
| `--check-market` | 大盤指數 + 台灣50 + 加權走勢 | 每日收盤後 | **每次都推** |

> `--check-market` 是唯一每次執行都推播的模組，其餘皆「有料才推」。

---

## 各模組使用範例

### `--check-messages` 重大訊息
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-messages
```
輸出範例：
```
📢 台積電(2330)
   2026/05/05 · 本公司代子公司 TSMC Global Ltd. 公告取得固定收益證券
```

### `--check-dividend` 除權除息預告
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-dividend
```
輸出範例：
```
💰 台積電(2330)
   除權息日: 115/06/15 · 現金股利: 5.0 · 股票股利: -
```

### `--check-valuation` 殖利率/本益比
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-valuation
```
輸出範例：
```
📊 台積電(2330)
   本益比: 33.97 · 殖利率: 0.98% · 淨值比: 10.77
   (已變動)
```

### `--check-price` 個股日成交
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-price
```
輸出範例：
```
📈 台積電(2330)
   收盤: 2250.00 (-25.00) · 成交量: 41,519,169
```

### `--check-threshold` 股價閾值監控
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-threshold
```
輸出範例（觸發時）：
```
🚨 【股價警報】
🔴 跌停！台積電(2330)
   收盤: 2047.50  (-10.0%)
🟡 台積電(2330) 跌破絕對低點
   收盤: 2047.50 ≤ 閾值 2240.00
🔵 台積電(2330) 單日大跌
   -10.0%  閾值: ≥5%
```

### `--check-alert` 注意/處置/變更交易/暫停交易
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-alert
```
4 種警示分級：
| emoji | 類型 | 端點 |
|-------|------|------|
| ⚠️ | 注意股票 | `/announcement/notice` |
| 🔴 | 處置股票 | `/announcement/punish` |
| 🟠 | 變更交易 | `/exchangeReport/TWT85U` |
| ⛔ | 暫停交易 | `/exchangeReport/TWTAWU` |

### `--check-insider` 董監事持股
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-insider
```
輸出範例：
```
📋 台積電(2330) 董事長本人 魏哲家
   選任時: 6,392,834 → 目前: 7,452,349 · 設質: 1600000 (21.46%)
```
涵蓋兩個端點：
- 持股轉讓申報（`t187ap12_L`）：預定轉讓的董監事
- 董監事持股餘額（`t187ap11_L`）：全體董監事持股與設質

### `--check-revenue` 月營收/EPS
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-revenue
```
輸出範例：
```
📊 台積電(2330) 半導體業 · 2026/03
   當月營收: 415,191,699
   月增: 30.70%  年增: 45.19%
   累計: 1,134,103,440  年增: 35.13%
```
涵蓋三個端點：
- 月營收（`t187ap05_L`）：當月/累計/月增/年增
- EPS 產業統計（`t187ap14_L`）：按產業統計
- 財測差異 10%+（`t187ap16_L`）：實際與預測差距

### `--check-governance` 公司治理/ESG
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-governance
```
6 個端點分三級：

| 等級 | 類型 | emoji | 端點 |
|------|------|-------|------|
| 🔴 緊急 | 裁罰案件 | 🔴 | `t187ap22_L` |
| 🔴 緊急 | 經營權異動+變更交易 | 🔴 | `t187ap27_L` |
| 🟡 警告 | 違反資訊申報 | 🟡 | `t187ap23_L` |
| 🟠 警告 | 經營權異動 | 🟠 | `t187ap24_L` |
| 🔵 參考 | ESG 資訊安全 | 🔵 | `t187ap46_L_16` |
| 🔵 參考 | ESG 職業安全衛生 | 🔵 | `t187ap46_L_21` |

### `--check-market` 大盤統計
```bash
python3 /Users/claw/scripts/twse_monitor.py --check-market
```
輸出範例：
```
【大盤收盤】

🔺 寶島股價指數
   收盤: 45683.96 +145.84 (0.32%)

📊 臺灣50指數
   2026/05/05 · 價格: 37805.31 · 報酬: 86563.25

📈 加權指數走勢
   2026/05/05 · 開: 40708.40 · 高: ... · 低: ... · 收: 40769.29
```
涵蓋三個端點：
- 大盤統計（`MI_INDEX`）：漲跌+百分比
- 台灣50（`TAI50I`）：價格指數+報酬指數
- 加權歷史（`MI_5MINS_HIST`）：開高低收

---

## 管理指令

### 設定持有成本
```bash
python3 /Users/claw/scripts/twse_monitor.py --cost 2330 2150
python3 /Users/claw/scripts/twse_monitor.py --cost 0050 88.5
```
輸出範例：
```
✅ 持有成本已更新
   股票：2330 台積電
   成本：2,150.00
   現價：2,250.00（close_today）
   未實現損益：📈 +100.00（+4.65%）
```

### 查詢 DB
```bash
python3 /Users/claw/scripts/twse_monitor.py --show-db                # 全部表
python3 /Users/claw/scripts/twse_monitor.py --show-db --table stocks  # 只看 stocks
```

### 查詢設定檔
```bash
python3 /Users/claw/scripts/twse_monitor.py --show-config
```

---

## 資料庫

**位置**：`~/.twse_monitor.db`（SQLite）

### 資料表：stocks

| 欄位 | 說明 | 範例 |
|------|------|------|
| `code` | 股票代碼（主鍵） | `2330` |
| `name` | 股票名稱 | `台積電` |
| `cost` | **持有成本**（豪自行填入） | `2150.0` |
| `close_today` | 今日收盤價（每日更新） | `2250.0` |
| `close_prev` | 昨日收盤價（每日更新） | `2275.0` |
| `updated_ts` | 最後更新時間 | `2026-05-06T14:16:56` |

> `cost` 欄位由豪自行維護，使用 `--cost CODE VALUE` 設定。

### 資料表：seen_items

記錄已通知過的項目，防止重複推播。

| 欄位 | 說明 | 範例 |
|------|------|------|
| `category` | 訊息類別 | `major_news`、`insider_holding`、`revenue`、`gov_penalty` 等 |
| `item_key` | 訊息唯一識別鍵 | `revenue_2330_11503`、`holding_11503_2330_魏哲家` |
| `message` | 訊息內容摘要 | `415191699|45.19%` |
| `ts` | 寫入時間 | `2026-05-06T14:16:40` |

### 手動查詢範例

```bash
sqlite3 ~/.twse_monitor.db "SELECT * FROM stocks;"
sqlite3 ~/.twse_monitor.db "SELECT category, item_key, ts FROM seen_items ORDER BY ts DESC LIMIT 10;"
```

---

## 設定檔

**位置**：`~/.twse_monitor_config.json`

```json
{
  "watchlist": ["0050", "2330", "00981A"],
  "thresholds": {
    "2330": {
      "max_price":    "+10",
      "min_price":    "-10",
      "max_pct_up":    5,
      "max_pct_down":  5,
      "circuit_up":    true,
      "circuit_down":  true,
      "circuit_pct":   10
    }
  },
  "telegram_bot_token": "...",
  "telegram_chat_id": "..."
}
```

---

## 閾值設定完整說明（以 2330 為例）

| 欄位 | 預設值 | 說明 |
|------|--------|------|
| `max_price` | `close + 10`（未填時） | 漲破此價位 → 🟡 警告 |
| `min_price` | `close - 10`（未填時） | 跌破此價位 → 🟡 警告 |
| `max_pct_up` | `5` | 單日漲幅 > 此值 → 🔵 參考 |
| `max_pct_down` | `5` | 單日跌幅 > 此值 → 🔵 參考 |
| `circuit_up` | `true` | 漲停通知（±10%）|
| `circuit_down` | `true` | 跌停通知 |
| `circuit_pct` | `10` | 漲跌停幅度（%）|

### 支援的閾值格式

| 設定值 | 意義 | 範例情境（2330 close=2250） |
|--------|------|------|
| `2400` | 絕對價格 | 漲破 2400 才通知 |
| `"+10"` | close + 10 | close ≥ 2260 通知 |
| `"-10"` | close - 10 | close ≤ 2240 通知 |
| `"+5%"` | close × 1.05 | close ≥ 2362.5 通知 |
| `"-5%"` | close × 0.95 | close ≤ 2137.5 通知 |
| `"90%"` | close × 0.90 | close ≤ 2025 通知 |

### 實務範例

```json
{
  "2330": {
    "max_price": 2400,
    "min_price": "-10",
    "max_pct_up": 5,
    "max_pct_down": 5,
    "circuit_up": true,
    "circuit_down": true,
    "circuit_pct": 10
  },
  "0050": {
    "max_price": "+5%",
    "min_price": "-5%",
    "circuit_up": true,
    "circuit_down": true
  }
}
```

---

## 通知分級

| 等級 | 觸發條件 | iPhone / Apple Watch |
|------|----------|----------------------|
| 🔴 緊急 | 漲停 / 跌停 / 裁罰 / 經營權+變更交易 | 響鈴 + 抬手 |
| 🟡 警告 | 突破價格閾值 / 違反申報 / 經營權異動 | 響鈴 |
| 🟠 警告 | 變更交易 | 響鈴 |
| 🔵 參考 | 百分比警告 / ESG 揭露 | 一般推播 |
| ⚠️ | 注意股票 | 一般推播 |

---

## 快速參考

```bash
# ── 監控 ──
python3 /Users/claw/scripts/twse_monitor.py --daily                         # 每日總檢查
python3 /Users/claw/scripts/twse_monitor.py --check-price --check-threshold  # 收盤後
python3 /Users/claw/scripts/twse_monitor.py --check-alert                   # 即時警示
python3 /Users/claw/scripts/twse_monitor.py --check-insider                 # 董監事
python3 /Users/claw/scripts/twse_monitor.py --check-revenue                 # 月營收
python3 /Users/claw/scripts/twse_monitor.py --check-governance              # 公司治理
python3 /Users/claw/scripts/twse_monitor.py --check-market                  # 大盤

# ── 管理 ──
python3 /Users/claw/scripts/twse_monitor.py --cost 2330 2150                # 持有成本
python3 /Users/claw/scripts/twse_monitor.py --show-db                       # 查 DB
python3 /Users/claw/scripts/twse_monitor.py --show-config                   # 查設定

# ── 除錯 ──
python3 /Users/claw/scripts/twse_monitor.py --debug --check-threshold       # Debug
python3 /Users/claw/scripts/twse_monitor.py --help                          # 說明
```

---

## 常見問題

**Q: `--check-price` 執行兩次會重複通知嗎？**
A: 不會。每日首次執行寫入 SQLite 後，之後執行會自動略過。

**Q: 哪些 API 可用於 ETF（如 0050）？**
A: `STOCK_DAY_ALL`、`BWIBBU_ALL`、`TWT48U_ALL` 均支援 ETF。月營收（`t187ap05_L`）僅限上市公司。

**Q: `stocks.cost`（持有成本）怎麼填？**
A: `python3 twse_monitor.py --cost 2330 2150`

**Q: Debug log 在哪裡？**
A: `/tmp/twse_monitor.log`，每次加 `--debug` 執行時覆蓋。

**Q: iPhone 收到但 Apple Watch 沒響？**
A: 檢查 Telegram App 設定 → 通知 → Apple Watch 同步是否開啟。

**Q: `--daily` 包含哪些模組？**
A: 重大訊息 + 除權除息 + 殖利率 + 注意股票 + 董監事 + 月營收 + 公司治理 + 大盤。不含 `--check-price` 和 `--check-threshold`（需單獨掛 cron）。
