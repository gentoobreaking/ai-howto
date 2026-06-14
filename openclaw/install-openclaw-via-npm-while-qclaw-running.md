# HOWTO: 在 MacBook 上用 npm 安裝 OpenClaw（QClaw 運行中）

## ⚠️ 前置說明

本文件假設：
- 你目前正在使用 **QClaw App**（即 QClaw 正在運行中）
- 你希望透過 `npm` 安裝獨立的 **OpenClaw CLI** 或另一份 OpenClaw
- 你的作業系統：**macOS**（Darwin）
- 你的晶片：**Apple Silicon（M1/M2/M3）** 或 Intel

---

## 一、基本概念

| 術語 | 說明 |
|------|------|
| **QClaw** |  macOS/iOS 的圖形化 App，內建 OpenClaw 功能 |
| **OpenClaw** |  Core AI Agent 引擎，QClaw 的底層技術 |
| **openclaw CLI** |  命令列工具，可獨立安裝使用 |
| **npm openclaw** |  Node.js 生態中的 openclaw 套件 |

> 📌 **重要**：QClaw App 本身就是一個封裝好的 OpenClaw GUI。用 npm 安裝的 `openclaw` CLI 是底層工具，兩者**可以同時運行**，不會衝突。

---

## 二、安裝步驟

### Step 1：確認環境

```bash
# 確認 Node.js 版本（建議 v18+）
node --version

# 確認 npm 版本
npm --version

# 確認作業系統
uname -a
```

**預期輸出（Apple Silicon 示例）：**
```
v22.21.1          # Node.js
10.2.4            # npm
Darwin 25.3.0 arm64  # macOS Sonoma + Apple Silicon
```

### Step 2：全域安裝 openclaw CLI

```bash
npm install -g openclaw
```

**或使用 npx 免安裝直接運行：**
```bash
npx openclaw --version
```

### Step 3：確認安裝成功

```bash
openclaw --version
```

**或查看完整指令：**
```bash
openclaw --help
```

---

## 三、讓 npm 安裝的 openclaw 與 QClaw 共存的關鍵

### 3.1 為什麼兩者可以同時運行？

| 層面 | QClaw App | npm 安裝的 openclaw CLI |
|------|-----------|-------------------------|
| 運行位置 | App Bundle 內 | 全域 `node_modules/openclaw` |
| 設定檔位置 | `~/Library/Application Support/QClaw/` | `~/.openclaw/` |
| 默認 Gateway 端口 | 自動管理 | 需手動指定或使用不同端口 |
| 使用者 | GUI 操作 | 終端機指令 |

### 3.2 避免端口衝突

QClaw App 預設使用 Gateway 端口。如果你想同時用 npm openclaw CLI：

```bash
# 查看 QClaw App 目前使用的端口
openclaw gateway status

# 如果需要，可以指定不同端口
openclaw gateway start --port 18792
```

---

## 四、常見問題與解決方式

### Q1：安裝失敗，報 `EACCES` 權限錯誤

**錯誤訊息：**
```
npm ERR! Error: EACCES: permission denied
```

**解決方式：**
```bash
# 方式 1：使用 sudo（不推薦，但最簡單）
sudo npm install -g openclaw

# 方式 2（推薦）：建立 npm 全域目錄的軟連結
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:'"$PATH" >> ~/.zshrc
source ~/.zshrc
npm install -g openclaw
```

---

### Q2：`openclaw: command not found`

**解決方式：**
```bash
# 確認安裝位置
npm root -g

# 將全域 bin 加入 PATH
export PATH="$(npm root -g):$PATH"

# 測試
openclaw --version
```

如果仍找不到，檢查是否安裝在 `node_modules/.bin/openclaw`：
```bash
ls $(npm root -g)/.bin/openclaw
```

---

### Q3：版本與 QClaw App 不相容

**症狀：** 安裝成功但無法正常運作，或提示 API 版本不相容。

**解決方式：**
```bash
# 查看 QClaw App 內建的 openclaw 版本
# （在 QClaw App → 設定 → About 中查看）

# 安裝相同版本
npm install -g openclaw@x.x.x
```

> 📌 QClaw App 通常綁定特定版本的 OpenClaw。用 npm 安裝的版本可能會落後或領先，實測確認相容性後再使用。

---

### Q4：npm 安裝的 openclaw 無法連接 QClaw Gateway

**原因：** QClaw App 運行時，它的 Gateway 是獨立的實例。

**解決方式：**

如果你想用 npm openclaw CLI **控制同一個 QClaw Gateway**：

1. 查看 QClaw App 的 Gateway URL：
   ```
   在 QClaw App → 設定 → Advanced → Gateway URL
   ```

2. 在 CLI 中指定 Gateway URL：
   ```bash
   openclaw gateway status --gateway-url http://localhost:18789
   ```

3. 或將 QClaw App 的 Gateway URL 寫入環境變數：
   ```bash
   export OPENCLAW_GATEWAY_URL=http://localhost:18789
   openclaw gateway status
   ```

---

### Q5：Apple Silicon（M1/M2/M3）上的原生相容性問題

**症狀：** 安裝成功但執行時崩潰或警告架構不符。

**解決方式：**
```bash
# 確認是否使用 Rosetta 轉譯
arch

# 若需要，安裝 x64 版本的 Node.js
# 或使用 nvm 安裝原生 ARM64 版本：
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 22
nvm use 22
npm install -g openclaw
```

---

### Q6：同時運行兩個不同版本的 openclaw

**需求：** 你想在測試新版 openclaw 的同時，保持 QClaw App（舊版）的穩定。

**解決方式：**
```bash
# 安裝 nvm（Node Version Manager）
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.zshrc

# 為 QClaw 安裝一個版本
nvm install 20
nvm use 20
npm install -g openclaw@1.x.x

# 為測試安裝另一個版本
nvm install 22
nvm use 22
npm install -g openclaw@latest
```

---

## 五、使用情境建議

### 情境 A：用 CLI 管理 QClaw App 的設定

```bash
# 查看目前 Gateway 狀態
openclaw gateway status

# 查看已安裝的 skills
openclaw skills list

# 查看 cron jobs
openclaw cron list
```

### 情境 B：用 npm 版本開發/測試新的自動化腳本

```bash
# 在獨立目錄初始化專案
mkdir ~/my-openclaw-scripts
cd ~/my-openclaw-scripts
npm init -y
npm install openclaw

# 撰寫腳本...
```

### 情境 C：將 npm openclaw CLI 作為 QClaw App 的功能擴展

> ⚠️ 這是高階用法，需確認 npm 版本與 QClaw App 版本相容。

---

## 六、快速檢查清單

- [ ] Node.js 版本 ≥ 18（`node --version`）
- [ ] npm 可正常運行（`npm --version`）
- [ ] 全域 bin 目錄已加入 PATH
- [ ] `openclaw --version` 可正確輸出
- [ ] 確認與 QClaw App 的 Gateway 端口不衝突
- [ ] 確認使用情境（A/B/C）

---

## 七、相關參考

- OpenClaw CLI：`openclaw --help`
- Cron Job 管理：`openclaw cron --help`
- Gateway 管理：`openclaw gateway --help`
- Skill 安裝：參考 `HOWTO: 如何安裝 OpenClaw Plugins`（T034）
