# pi agent × Agent Reach ＋ BrowserAct 安裝筆記

> 建立日期：2026-08-25
> 上游專案：
> - Agent Reach：https://github.com/Panniantong/agent-reach
> - BrowserAct Skills：https://github.com/browser-act/skills

---

## 一、這兩個工具是什麼、差在哪

| | Agent Reach | BrowserAct |
|---|---|---|
| 定位 | Agent 的「上網能力安裝器／路由器」 | 商用反偵測瀏覽器自動化（CLI + Skill） |
| 解決 | 一鍵裝好各平台讀取工具（Twitter/YouTube/雪球/B站/小紅書…），上游被封它負責換路徑 | 過反爬牆、解 CAPTCHA、stealth 指紋、多帳號隔離 |
| 費用 | 免費（上游全開源） | Freemium：Chrome 自動化免費；stealth 瀏覽器/解驗證碼/雲代理要 API Key，規模化付費 |
| 安裝位置 | pipx → `~/.local/bin/agent-reach` | uv tool → `~/.local/share/uv/tools/` |

與既有 camofox 的關係：BrowserAct 功能與 camofox 重疊度高，camofox 解決不了的場景才用它。

---

## 二、事前設定：pi-sandbox 權限

pi 若裝了 `npm:pi-sandbox` 套件（`~/.pi/agent/settings.json` 的 `packages`），
agent 的 bash 會被沙箱限制，預設只能寫工作目錄和 `/tmp`。

**正解不是移除套件，而是改 `~/.pi/agent/sandbox.json` 開權限**（保留沙箱安全性）：

```jsonc
// ~/.pi/agent/sandbox.json → filesystem.allowWrite 加入：
"/Users/david/Library/Application Support/browseract/",  // browser-act 寫 log/daemon 狀態
"/Users/david/.pi/agent/skills/"                          // 安裝/更新 skill 檔案
```

實測加入後 browser-act 即可在 pi 內正常運行；若 agent-reach 相關指令也被擋，
比照加入對應目錄（如 `~/.agent-reach/`）即可。

---

## 三、Agent Reach 安裝

### 1. 本體（pipx 全域安裝）

```bash
brew install pipx
pipx ensurepath            # 重開終端機讓 PATH 生效
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
```

### 2. 環境檢查 → 授權安裝

```bash
agent-reach install --env=auto              # 唯讀體檢（預設安全行為）
agent-reach install --env=auto --system     # 確認後才授權：裝上游工具 + 寫 SKILL.md
agent-reach doctor                          # 各渠道狀態總表
```

`--system` 會認得 Claude Code/OpenClaw 等，**不一定偵測到 pi**。
實測結果：SKILL.md 被放在 `~/.agents/skills/agent-reach/`（不是 `~/.openclaw/`）。

### 3. 手動把 skill 掛進 pi（實際可用的指令）

```bash
cp -rp /Users/david/.agents/skills/agent-reach ~/.pi/agent/skills/
```

### 4. 日後更新

```
幫我更新 Agent Reach：https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```
（貼給 agent 即可）

---

## 四、BrowserAct 安裝

### 1. CLI（uv tool，自帶 Python 3.12）

```bash
uv tool install browser-act-cli --python 3.12
browser-act --version
```

### 2. Skill 掛進 pi（含 Skill Forge，用 mv）

```bash
git clone --depth 1 https://github.com/browser-act/skills /tmp/ba-skills
mv /tmp/ba-skills/browser-act ~/.pi/agent/skills/
mv /tmp/ba-skills/browser-act-skill-forge ~/.pi/agent/skills/
rm -rf /tmp/ba-skills
```

### 3. Skill 版本握手（重要，首次必做）

CLI 有版本握手機制：Skill 檔與 CLI 版本不符時，**所有指令都會被 BLOCKING 擋下**。
實測從 GitHub main 抓的 SKILL.md（v2.0.2）會被 CLI 1.4.0 判定 stale。修法：

```bash
# 用 get-skills 取得與 CLI 版本相符的內容，整個覆蓋 SKILL.md
browser-act get-skills core --skill-version 2.0.2 \
  > ~/.pi/agent/skills/browser-act/SKILL.md

# 確認版本已更新
grep -m1 "version" ~/.pi/agent/skills/browser-act/SKILL.md
# 實測輸出：version: v1.4.0
```

不先做這步，`auth login` 等所有指令都會回報
「[BLOCKING] Skill version incompatible」。日後 CLI 升級若再被擋，同樣跑一次即可。

### 4. 認證（可選）

只有 stealth 瀏覽器、`stealth-extract`、`solve-captcha`、雲端代理需要 API Key；
基本 Chrome 自動化（`chrome` / `chrome-direct` 模式）免費免 Key。

```bash
browser-act auth login
# 印出註冊連結（60 分鐘內有效），例如：
#   https://www.browseract.com/quick-register?session=...
# 到瀏覽器完成註冊後：
browser-act auth poll
# status=completed
# message="Registration completed. API key has been saved."
```

備案：若想跳過註冊流程，可手動到 https://www.browseract.com 註冊，
從後台複製 API Key 後直接 `browser-act auth set <key>`。

### 5. 升級

```bash
uv tool upgrade browser-act-cli
```

升級後若指令被 BLOCKING 擋下，重跑一次第三節的握手流程。

---

## 五、驗證（重開 pi session 後）

pi 會自動掃描 `~/.pi/agent/skills/` 下含 `SKILL.md` 的目錄，無需改 settings。
叫 agent 執行：

```
用 agent-reach doctor 檢查各渠道狀態
用 browser-act stealth-extract 抓 https://example.com 測試
```

## 六、日常調用對照

| 需求 | 指令 |
|---|---|
| 讀任意網頁 | `curl -s "https://r.jina.ai/<URL>"` |
| YouTube 字幕 | `yt-dlp --skip-download --write-auto-sub <URL>` |
| B站搜尋 | `bili search "query" --type video` |
| GitHub 搜尋 | `gh search repos "query"` |
| Exa 語意搜尋 | `mcporter call exa.web_search_exa query="..." numResults=5` |
| 反偵測抓頁面 | `browser-act stealth-extract <URL>` |
| 完整瀏覽器操作 | `browser-act --session <name> browser open <id> <URL>` → `state` → `click <n>` |

需要登入態的渠道（Twitter/雪球/小紅書/Reddit…）：告訴 agent「幫我配 XXX」，
Cookie 用 [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
Export → Header String 交給 agent。建議用次要帳號，降低封號與 Cookie 外洩風險。

---

## 七、踩坑紀錄

| 問題 | 原因 | 解法 |
|---|---|---|
| agent bash 寫 `~/...` 報 Operation not permitted | pi 裝了 `pi-sandbox` 套件 | 在 `~/.pi/agent/sandbox.json` 的 `filesystem.allowWrite` 加入需要的目錄（保留沙箱，勿移除套件） |
| Agent Reach `--system` 後 pi 沒有 skill | 它不認得 pi，skill 落在 `~/.agents/skills/` | 手動 `cp -rp ~/.agents/skills/agent-reach ~/.pi/agent/skills/` |
`browser-act auth login` 沒反應 | Skill 版本握手未過（BLOCKING），或 CLI log 目錄不可寫 | 先跑 `get-skills core --skill-version 2.0.2 > .../SKILL.md` 完成握手；沙箱環境下需在本機終端機執行 |
| CLI 全部指令報 Operation not permitted（log 寫不進 `~/Library/Application Support/browseract/`） | pi 的 bash 沙箱限制 | `sandbox.json` → `allowWrite` 加入 `/Users/david/Library/Application Support/browseract/`，已驗證可解 |
