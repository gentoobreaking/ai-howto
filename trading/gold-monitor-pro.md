# Gold Monitor Pro 使用手冊

## 系統架構

Gold Monitor Pro 是台灣銀行黃金存摺價格監控系統，包含以下組件：

| 組件 | 路徑 | 功能 |
|------|------|------|
| 主監控腳本 | `~/.qclaw/workspace/skills/clw-gold-monitor-pro/gold_monitor_pro.py` | 即時價格抓取與通知 |
| 歷史同步腳本 | `~/scripts/gold_bot_history.py` | 台灣銀行一年歷史資料同步 |
| 資料庫 | `~/.qclaw/gold_monitor_pro.db` | SQLite 價格歷史儲存（動態路徑，依使用者 home 目錄） |

## 台灣銀行 URL Pattern

| URL Pattern | 用途 | `--flag` |
|-------------|------|---------|
| `https://rate.bot.com.tw/gold/chart/year/TWD` | 滾動一年（約 244 筆） | 預設 |
| `https://rate.bot.com.tw/gold/chart/YYYY-MM/TWD` | 指定月份 | `--month 2025-01` |
| `https://rate.bot.com.tw/gold/chart/day/TWD` | 最近一個營業日（intra-day 多筆） | `--day` |

## gold_bot_history.py 歷史同步腳本

### 同步邏輯

- **資料來源**：台灣銀行官網 `https://rate.bot.com.tw/gold/chart/year/TWD`
- **資料範圍**：滾動一年（約 244 個營業日）
- **資料內涵**：前一天收盤牌告價（網站顯示的是昨日 close）
- **Gap-filling**：只補「DB 沒有的日期」，不覆蓋已有資料

### 命令列介面

```bash
# 基本同步（滾動一年）
python3 ~/scripts/gold_bot_history.py

# 抓取指定月份的歷史資料（例：2025-01）
python3 ~/scripts/gold_bot_history.py --month 2025-01

# 抓取最近一個營業日
python3 ~/scripts/gold_bot_history.py --day

# 預覽模式（搭配 --month / --day 使用）
python3 ~/scripts/gold_bot_history.py --month 2025-01 --dry-run
python3 ~/scripts/gold_bot_history.py --day --dry-run

# 查看資料庫現況
python3 ~/scripts/gold_bot_history.py --stats

# 強制覆蓋已存在的日期
python3 ~/scripts/gold_bot_history.py --force

# 強制重建（清除 gold data 後重新匯入）
python3 ~/scripts/gold_bot_history.py --init
```

### 自動建表機制

第一次執行時，腳本會自動：
1. 建立 `~/.qclaw/` 目錄（如果不存在）
2. 建立 `gold_monitor_pro.db` SQLite 資料庫
3. 建立 `price_history` table + index

無需手動執行任何 SQL。

**資料庫路徑說明**：
- 程式碼中使用 `pathlib.Path.home() / ".qclaw" / "gold_monitor_pro.db"`
- 這是**動態路徑**，會根據執行使用者的 home 目錄自動調整
- 例如：使用者 `claw` → `/Users/claw/.qclaw/gold_monitor_pro.db`
- 非寫死路徑，可在任何使用者環境中正確執行

### Cron 建議

```bash
# 每日檢查是否有新歷史資料（台灣銀行每營業日 12:00 公布）
0 13 * * 1-5 python3 /Users/claw/scripts/gold_bot_history.py
```

## 資料庫 Schema

```sql
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metal TEXT NOT NULL,              -- 'gold', 'silver', 'platinum'
    local_sell REAL,                  -- 台銀賣出價（台幣/克）
    local_buy REAL,                   -- 台銀買入價（台幣/克）
    international_spot REAL,          -- 國際現貨參考價
    exchange_rate REAL,               -- 匯率（可選）
    timestamp TEXT NOT NULL,          -- ISO 8601 格式
    source_time TEXT,                 -- 原始時間字串
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_daily_close INTEGER DEFAULT 0  -- 是否為每日收盤價
);

CREATE INDEX idx_price_metal_time ON price_history(metal, timestamp);
```

## 與 gold_monitor_pro.py 的關係

| 腳本 | 更新頻率 | 資料來源 | 主要用途 |
|------|---------|---------|---------|
| `gold_monitor_pro.py` | 每 10 分鐘 | 台灣銀行即時報價 API | 即時監控與通知（只讀 SQLite） |
| `gold_bot_history.py` | 每日 22:00 | 台灣銀行歷史頁面 | 唯一寫入 SQLite 的地方 |

**gold_monitor_pro.py 架構（v2）**：
1. 啟動時清除 `/tmp/gold_monitor_pro_session.json`
2. 從 SQLite 取最近營業日收盤（db_baseline）
3. session（有值）或 DB 基準 → 比對閾值 → 發通知
4. 更新 tmp session（下次 cron 的「上次」）

**職責分離**：gold_monitor_pro.py 不寫 SQLite，SQLite 由 gold_bot_history.py 統一維護。

## 常見問題

### Q: 為什麼 --dry-run 顯示 DB 已有 0 筆？
A: 舊版腳本有 bug，請更新到最新版。

### Q: --init 會刪除 silver/platinum 資料嗎？
A: 不會，只會清除 `metal='gold'` 的資料。

### Q: 可以同步 silver/platinum 歷史嗎？
A: 目前台灣銀行官網只提供 gold 的歷史頁面。
