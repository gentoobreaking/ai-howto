# OpenClaw 瀏覽器工具無法訪問 localhost 的解決方案

## 問題描述

當使用 OpenClaw 瀏覽器工具訪問本地服務（如 `http://localhost:8000/docs`）時，會遇到錯誤：

```
Blocked hostname or private/internal/special-use IP address
```

### 影響範圍

- ❌ 無法截圖本地運行的 API 文檔（Swagger/OpenAPI）
- ❌ 無法截圖本地前端應用
- ❌ 無法測試本地開發中的 Web 服務
- ❌ 驗收流程必須先部署到公網才能截圖

### 根本原因

這是 OpenClaw 的 **SSRF（Server-Side Request Forgery）防護機制**。

- **模組**：`openclaw/dist/plugin-sdk/ssrf-BC5-OCfy.js`
- **目的**：防止 AI Agent 訪問本地私有網絡資源
- **被封鎖的地址類型**：
  - `localhost` / `127.0.0.1`
  - `192.168.x.x`（私有 IP）
  - `10.x.x.x`（私有 IP）
  - 其他內網特殊用途地址

### 為什麼 ngrok 可以但瀏覽器不行？

| 方法 | 行為 |
|------|------|
| **ngrok** | 直接走系統網路，不經過 OpenClaw 安全檢查 ✅ |
| **瀏覽器工具** | 經過 OpenClaw SSRF 防護過濾 ❌ |

---

## 解決方案

### 步驟 1：修改配置

編輯 OpenClaw 配置文件：

```bash
# 配置文件位置
~/Library/Application\ Support/QClaw/openclaw/config/openclaw.json
```

找到 `browser` 區塊，修改 `ssrfPolicy.dangerouslyAllowPrivateNetwork` 為 `true`：

```json
"browser": {
  "enabled": true,
  "defaultProfile": "openclaw",
  "ssrfPolicy": {
    "dangerouslyAllowPrivateNetwork": true
  }
}
```

### 步驟 2：重啟 QClaw Electron

關閉並重新打開 QClaw 應用程式，使配置生效。

### 步驟 3：驗證

修改後，瀏覽器工具應該能正常訪問 localhost：

```
http://localhost:8000/docs
http://127.0.0.1:3000
```

---

## 回報給 OpenClaw 團隊

### 回報內容

```
問題：瀏覽器工具無法訪問 localhost，嚴重影響開發/驗證流程

詳細說明：
1. 當前行為：訪問 localhost/127.0.0.1/內網 IP 時，報錯
   "Blocked hostname or private/internal/special-use IP address"

2. 影響範圍：
   - 無法截圖本地運行的 API 文檔（Swagger/OpenAPI）
   - 無法截圖本地前端應用
   - 無法測試本地開發中的 Web 服務
   - 驗收流程必須先部署到公網才能截圖（本末倒置）

3. 現有 workaround（ngrok）的問題：
   - 需要額外安裝設定
   - 延遲驗證流程
   - 增加不必要的複雜度

4. 實務合理性：
   開發/驗收流程中，本地測試是標準作業。
   要求所有服務都先上線才能驗證，不符合軟體開發常態。

5. 建議改進：
   - 選項 A：預設允許 localhost 訪問（風險極低）
   - 選項 B：提供明確的配置文件開關（已在 config 中存在）
   - 選項 C：在錯誤訊息中提示用戶如何開通
```

### 回報方式

### 回報方式

**方式 1：GitHub Issues（推薦）**
- OpenClaw 官方倉庫：https://github.com/openclaw/openclaw
- 前往 Issues 頁面新建 Issue：https://github.com/openclaw/openclaw/issues/new

**方式 2：Discord（官方社群）**
- Discord 邀請連結：https://discord.gg/clawd
- 在 #bug-reports 或 #feedback 頻道回報

**方式 3：QClaw 內建回饋**
- 通過 QClaw 應用程式的「幫助與反饋」功能

---

## 延伸閱讀

- [OpenClaw SSRF 防護模組](../openclaw-security-check.md)
- [OpenClaw Plugins vs Skills 區別](./OpenClaw%20Plugins%20vs%20Skills%20區別.md)

---

## 更新記錄

| 日期 | 內容 |
|------|------|
| 2026-04-11 | 初次建立 |

---

*本文由 寶寶 整理*
