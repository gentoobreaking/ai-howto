# pi agent × camofox-browser 反偵測瀏覽整合筆記

> 建立日期：2026-08-24
> Extension 位置：`~/.pi/agent/extensions/camofox.ts`
> 上游專案：https://github.com/jo-inc/camofox-browser （Camoufox 引擎的 REST API 包裝）

---

## 一、這是什麼

讓 pi coding agent 具備**反偵測**的網頁瀏覽／搜尋／截圖能力：

| 能力 | 對應 pi 工具 | 底層 camofox API |
|---|---|---|
| 搜尋 | `camofox_search` | navigate + `@google_search` 等巨集 |
| 瀏覽 | `camofox_browse` | POST /tabs + GET /tabs/:id/snapshot |
| 頁面互動 | `camofox_act` | /click /type /press /scroll /back /forward |
| 截圖 | `camofox_screenshot` | snapshot?includeScreenshot=true（退回 /screenshot） |
| 分頁管理 | `camofox_close_tab` | DELETE /tabs/:id |

為什麼需要它：Playwright/headless Chrome 會被指紋辨識封鎖；Camoufox 在 **C++ 層級**偽造
`navigator.hardwareConcurrency`、WebGL、AudioContext、螢幕解析度、WebRTC 等指紋，
可通過 Cloudflare 與多數 bot 偵測。snapshot 用 accessibility tree，比原始 HTML 小約 90%。

## 二、架構

```
pi agent ─工具呼叫→ ~/.pi/agent/extensions/camofox.ts ─HTTP(fetch)→ camofox-browser server
                                                                    http://localhost:9377
                                                                    └─ Camoufox (Firefox fork)
```

- camofox-browser 是獨立 REST 服務；pi 的 extension 只是用 fetch 包 API 的薄層
- 分頁以 `userId` 隔離 session（同 userId 共享 cookies/storage → 可維持登入狀態）
- 元素以穩定的 `e1`/`e2`/`e3` ref 標記，agent 拿 ref 做 click/type

## 三、安裝與自動啟動

### 自動啟動行為（重點）

每個 camofox 工具執行前都會先打 `/health`：

1. 服務已在跑 → 直接用
2. **沒起來 → 自動啟動**：`npx -y @askjo/camofox-browser` 以 detached 背景常駐，
   stdout/stderr 導到 log 檔，然後輪詢 `/health` 直到就緒（逾時 120 秒）
3. 首次啟動會下載 Camoufox binary（約 300MB），需耐心等待；之後啟動很快
4. 併發保護：同時多個工具呼叫共用同一個「啟動中」promise，不會重複拉起服務

- Log 檔：`~/.pi/agent/logs/camofox-browser.log`
- 手動啟動（除錯用）：`npx -y @askjo/camofox-browser`
- pi 內強制重啟：`/camofox-restart` 指令

### 環境變數

| 變數 | 預設 | 說明 |
|---|---|---|
| `CAMOFOX_BASE_URL` | `http://localhost:9377` | 服務位址 |
| `CAMOFOX_CRASH_REPORT_ENABLED` | true | 匿名錯誤回報，可設 false 關閉 |

## 四、工具使用說明

### camofox_search — 搜尋
```
query: "台積電 最新財報"
engine: "@google_search"（預設；另有 @duckduckgo_search 等）
```

### camofox_browse — 開網頁
```
url: "https://mops.twse.com.tw/mops/web/t163sb04"
userId: 可省略（預設 default；同 userId 的下次呼叫共享登入狀態）
```
回傳精簡 snapshot + tabId；snapshot 內元素有 `e1/e2/e3` ref。

### camofox_act — 頁面互動
```
action: click    → 配 ref: "e3"（或 CSS selector）
action: type     → 配 ref: "e5", text: "...", 再 action: press, key: "Enter"
action: scroll   → 配 direction: "down"
action: back / forward
```
互動後自動回傳新 snapshot，方便連續操作。

### camofox_screenshot — 截圖
```
fullPage: true/false
```
PNG 存 `/tmp/camofox_<時間戳>.png`，回傳路徑後可用 pi 的 read 工具看圖。

### /camofox-restart — 指令
服務異常時強制重啟（先 POST /stop 再自動拉起）。

## 五、實際用法範例（對 agent 說的話）

- 「用 camofox 搜尋『0050 成分股 最新』」
- 「打開 https://mops.twse.com.tw/... 幫我找 XX 欄位」（ref 交互：browse → act:click/type）
- 「把這個頁面截圖給我看」

典型流程：`camofox_search` → 從結果挑連結 → `camofox_browse` → 看 snapshot 找 ref →
`camofox_act` 點擊/輸入 → 需要畫面證據時 `camofox_screenshot`。

## 六、維運與排解

| 症狀 | 處理 |
|---|---|
| 工具回報「120s 內未能就緒」 | 看 `~/.pi/agent/logs/camofox-browser.log`；首次下載 binary 可能超過逾時，手動跑一次 `npx -y @askjo/camofox-browser` 讓它抓完 |
| 回應被截斷 | snapshot 過大，camofox 有 offset 分頁機制；可在 browse 後針對性 act |
| 登入狀態消失 | 同一 `userId` 才會共享 session；跨重啟要持久化請改用 cookie 匯入（POST /sessions/:userId/cookies） |
| 佔用資源 | camofox 有 idle shutdown（閒置自動關瀏覽器引擎，記憶體約 40MB）；也可 `/camofox-restart` 或手動 POST /stop |
| npx 每次重新解析版本慢 | 改成 git clone 後 `npm install && npm start` 常駐，或全域 `npm i -g @askjo/camofox-browser` |

## 七、與本機其他爬蟲方案的關係

| 方案 | 適用 | 反偵測 |
|---|---|---|
| 證交所 OpenAPI / FinMind（requests） | 結構化行情/財報資料，首選 | 不需要 |
| collectors/mops_scraper.py（T028，camoufox/httpx） | MOPS 財報歷史缺口的批次爬蟲 | ✅（程式化，最低優先級備援） |
| **本 extension（pi agent 互動式）** | agent 對話中即時查網頁、搜尋、截圖 | ✅（人機協作、單次任務） |

原則：能用 API 就用 API；網頁互動留給 camofox；高頻批次爬蟲注意速率（1–2 req/s）與法律合規。

## 八、待辦 / 已知限制

- [ ] camofox-browser 尚未驗證首次 300MB 下載在本機代理環境是否順利（log 會顯示進度）
- [ ] screenshot endpoint 的回傳欄位名稱以實際 /openapi.json 為準（extension 已做多欄位 fallback）
- [ ] 若要常駐，建議寫 launchd plist 或 docker compose 服務，避免依賴 npx 快取
- [ ] 相關任務：T028-camofox-browser-scraper（MOPS 批次爬蟲，已 done）
