# sinotrade-scraper 架設手冊

## 環境需求

| 項目 | 需求 |
|------|------|
| Python | 3.9+ |
| Playwright | `pip3 install playwright` |
| 瀏覽器 | 系統已安裝 Google Chrome（`/Applications/Google Chrome.app`） |

## 安裝步驟

### 1. 安裝 Playwright
```bash
pip3 install playwright
```

### 2. 確認系統 Chrome 存在
```bash
ls /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome
```

### 3. 驗證 Playwright 可驅動系統 Chrome
```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        headless=True,
        args=['--no-sandbox']
    )
    page = browser.new_page()
    page.goto('https://example.com')
    print('✅ Chrome + Playwright 正常')
    browser.close()
"
```

## 抓取機制說明

**重點**：永豐投顧網站是 SPA（JavaScript 動態渲染），報告列表不是直接打 URL 就有的。

**正確方式**：
1. 開啟首頁 `https://scm.sinotrade.com.tw/`
2. Hover（懸停）「研究報告」連結 → 觸發 dropdown
3. Dropdown 內出現所有報告連結

**錯誤方式**：
- 直接打 `https://scm.sinotrade.com.tw/Research/StockReport` → 302 錯誤導向錯誤頁

## 腳本使用

```bash
# 基本執行（印出今日報告）
python3 /Users/claw/scripts/sinotrade_scraper.py

# 發送 Telegram 通知
python3 /Users/claw/scripts/sinotrade_scraper.py --telegram
```

## 輸出格式

```json
{
  "date": "20260422",
  "reports": [
    {
      "code": "2049",
      "name": "上銀",
      "title": "景氣初升，量價齊揚將推升獲利",
      "url": "https://scm.sinotrade.com.tw/Article/Inner/{uuid}",
      "date": "20260422"
    }
  ]
}
```

## Telegram 設定

腳本讀取 `~/.qclaw/gold_monitor_config.json`：
```json
{
  "telegram_bot_token": "...",
  "telegram_chat_id": "..."
}
```

## Cron 排程

- **Job ID**: `bbca5563-675d-40a1-8309-09cc814c5e00`
- **排程**: 每週一～五 08:30（Asia/Taipei）
- **Payload**: `python3 /Users/claw/scripts/sinotrade_scraper.py --telegram`

```bash
# 手動查詢 cron 狀態
openclaw cron list
```

## 維護

### 若報告抓不到
1. 檢查 hover 是否觸發 dropdown（網站可能改版）
2. 檢查 `STOCK_REPORT_PATTERN` 正規表達式是否仍匹配
3. 截圖 `/tmp/sinotrade-home.png` 看實際 DOM

### 更新正規表達式
編輯 `/Users/claw/scripts/sinotrade_scraper.py`，找到：
```python
STOCK_REPORT_PATTERN = re.compile(r"^(.+?)\s*\((\d{4,5})\s*TT\)｜(.+?)\s*(\d{8})$")
```

## 歷史記錄

- 位置: `~/.qclaw/sinotrade_history.json`
- 格式: `{ "reports": { "2026-04-22": [...], ... } }`

---

建立日期：2026-04-22
