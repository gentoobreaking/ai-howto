# kgi-monitor 架設手冊

## 環境需求

| 項目 | 需求 |
|------|------|
| Python | 3.9+ |
| yt-dlp | `pip3 install yt-dlp` |
| Playwright | `pip3 install playwright` |
| 瀏覽器 | 系統已安裝 Google Chrome |

## 安裝步驟

### 1. 安裝依賴
```bash
pip3 install yt-dlp playwright
playwright install chromium
```

### 2. 驗證 yt-dlp 可用
```bash
yt-dlp --version
```

### 3. 驗證 Playwright
```bash
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print('✅ Playwright 正常')
"
```

## 腳本使用

```bash
# 抓取近 1 天（預設）
python3 /Users/claw/scripts/kgi_monitor.py

# 抓取近 3 天
python3 /Users/claw/scripts/kgi_monitor.py --range 3d

# 抓取近 7 天
python3 /Users/claw/scripts/kgi_monitor.py --range 7d

# 指定日期（YYYYMMDD）
python3 /Users/claw/scripts/kgi_monitor.py --date 20260421

# 發送 Telegram 通知
python3 /Users/claw/scripts/kgi_monitor.py --telegram
```

## 目標頻道

- **頻道**: 凱基股股漲
- **YouTube ID**: `UCQ5URjmXbLhMI3dEAxpMWYA`
- **關鍵詞過濾**: `AI`、`AI供應鏈`、`AI伺服器`、`散熱`、`光通訊`、`機殼`、`電源`、`PCB`、`CCL`、`滑軌`

## 關鍵詞過濾邏輯

影片標題包含任一關鍵詞即列入報告。

## Telegram 設定

腳本讀取 `~/.qclaw/gold_monitor_config.json`：
```json
{
  "telegram_bot_token": "...",
  "telegram_chat_id": "..."
}
```

## Cron 排程

- **Job ID**: `67859e52-2562-42b8-a9c8-c0e9b8292265`
- **排程**: 每週一～五 17:00（Asia/Taipei）
- **Payload**: `python3 /Users/claw/scripts/kgi_monitor.py --telegram`

## 維護

### 若影片抓不到
1. 檢查頻道 ID 是否仍為 `UCQ5URjmXbLhMI3dEAxpMWYA`
2. 確認 yt-dlp 版本（`yt-dlp --version`）
3. 手動測試：`yt-dlp "https://www.youtube.com/@UCQ5URjmXbLhMI3dEAxpMWYA/videos"`

### 更新關鍵詞
編輯 `/Users/claw/scripts/kgi_monitor.py`，找到 `KEYWORDS` 列表。

## 歷史記錄

- 位置: `~/.qclaw/kgi_history.json`
- 格式: `{ "processed_ids": ["video_id1", "video_id2", ...] }`

---

建立日期：2026-04-22
