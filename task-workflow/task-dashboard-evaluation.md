# 任務面板追蹤工具評估報告

> 研究日期：2026-04-12  
> 研究員：研研  
> 背景：團隊 6 人，使用 OpenClaw + Telegram 協作，現以 `/Users/claw/Tasks/` + T*.md 追蹤任務

---

## 一、評估方案總覽

| 方案 | 費費 | Telegram 整合 | 中文支援 | 即時更新 | 部署難度 | 總評 |
|------|------|---------------|----------|----------|----------|------|
| **GitHub Projects** | 免費（公開 repo） | ⭐⭐⭐ 原生 webhook | ✅ 完整 | ✅ 即時 | ⭐ 無需部署 | **強烈推薦** |
| **騰訊文檔** | 免費（個人版） | ⭐⭐ 需自建 bot | ✅ 原生 | ✅ 即時 | ⭐ 無需部署 | 備選方案 |
| **Notion** | 免費（個人）／ $8/月（團隊） | ⭐⭐⭐ 有現成 bot | ✅ 完整 | ✅ 即時 | ⭐ 無需部署 | 可考慮 |
| **自建 Dashboard** | 免費（主機成本） | ⭐⭐⭐ 完全掌控 | ✅ 自行實現 | ⭐⭐ 需輪詢同步 | ⭐⭐⭐ 需開發 | 投入成本高 |
| **Planka（開源 Kanban）** | 免費（self-host） | ⭐ 需自建 | ⭐⭐ 社群翻譯 | ✅ 即時 | ⭐⭐ Docker 部署 | 技術門檻 |

---

## 二、各方案詳細評估

### 1. GitHub Projects（強烈推薦）

**優點：**
- **零成本**：公開 repo 免費，私有 repo 免費（GitHub Free for Teams）
- **原生整合**：Issues + Projects + Actions 完整生態
- **Telegram 整合度高**：
  - GitHub Actions 可發送 Telegram 通知（透過 webhook）
  - 現成 GitHub Actions：`appleboy/telegram-action` 可直接使用
  - 可用 `/task` 指令在 Telegram 建立 Issue → 自動同步到 Projects
- **即時更新**：GitHub webhook 即時推送狀態變更
- **中文支援**：完整中文 UI，標籤、描述皆支援
- **部署難度**：零部署，開 repo 即用

**缺點：**
- 非開發者學習曲線較陡（需理解 Issue/PR 概念）
- 無法直接顯示 Ideas 目錄（需另建機制）

**整合方案：**
```
Telegram → GitHub Bot → GitHub Issues → GitHub Projects
                ↓
         OpenClaw cron 定時同步
```

**實作步驟：**
1. 建立 GitHub repo（已有）
2. 啟用 GitHub Projects（Board view）
3. 建立 Telegram bot：
   - 使用 `node-telegram-bot-api` 或 `python-telegram-bot`
   - 指令：`/task`, `/done`, `/list`
4. 設定 GitHub Actions：
   - Issue created → 通知 Telegram 群組
   - Issue closed → 更新 Projects 狀態

---

### 2. 騰訊文檔（備選方案）

**優點：**
- **免費**：個人版完全免費
- **中文原生**：騰訊出品，中文體驗最佳
- **即時協作**：多人同時編輯，自動存檔
- **智能表格**：支援看板視圖、甘特圖、任務分配
- **微信/QQ 整合**：可直接分享給微信好友協作

**缺點：**
- **Telegram 整合弱**：需自建 bot，無現成方案
- **API 限制**：企業版才有完整 API，個人版功能受限
- **無法直接讀取本地 Tasks/ 目錄**：需手動匯入

**適用場景：**
- 團隊成員習慣微信/QQ 協作
- 不想處理技術細節
- 需要中文友善介面

---

### 3. Notion（可考慮）

**優點：**
- **功能強大**：Database + Kanban + Calendar + Timeline
- **Telegram 整合**：現成開源 bot：
  - `xheiop/notion-telegram-bot`：更新 Notion database
  - `mikhailsdv/notion-quick-note`：快速建立筆記
  - n8n workflow：Telegram → Notion 自動化
- **免費版夠用**：個人免費，團隊 $8/月
- **API 完整**：Notion API 可程式化操作

**缺點：**
- **速度較慢**：載入時間較長
- **中文支援**：有中文，但部分功能翻譯不完整
- **學習曲線**：功能多，需時間熟悉

**整合方案：**
```
Telegram → notion-telegram-bot → Notion Database
                ↓
         OpenClaw 定時同步到本地
```

---

### 4. 自建 Dashboard（投入成本高）

**優點：**
- **完全掌控**：資料在本地，無隱私疑慮
- **客製化**：完全符合團隊需求
- **Telegram 整合**：可完全自定義

**缺點：**
- **開發成本高**：需前端 + 後端 + 資料庫
- **維護成本**：需持續維護、更新
- **即時性**：需實現即時同步機制（WebSocket / polling）

**技術選項：**
- 前端：React + Tailwind CSS
- 後端：Node.js + Express
- 資料庫：SQLite（輕量）或 PostgreSQL
- 部署：Docker + 本地或 VPS

**預估工時：**
- MVP：40-60 小時
- 完整功能：100+ 小時

---

### 5. Planka / WeKan（開源 Kanban）

**優點：**
- **免費 self-host**：無授權費用
- **功能完整**：看板、標籤、成員分配、截止日期
- **Docker 部署**：一鍵啟動

**缺點：**
- **無 Telegram 整合**：需自建
- **中文支援**：社群翻譯，可能不完整
- **技術門檻**：需維護 Docker 環境

**推薦工具：**
- **Planka**：現代、輕量、Trello-like（GitHub 4.2k stars）
- **WeKan**：功能豐富、穩定（GitHub 19k stars）
- **OpenProject**：企業級、功能完整

---

## 三、推薦方案

### 🏆 首選：GitHub Projects

**理由：**
1. **零成本 + 零部署**：開 repo 即用
2. **與現有工作流高度整合**：已有 repo，直接啟用 Projects
3. **Telegram 整合成熟**：現成 GitHub Actions 可用
4. **OpenClaw 友善**：可用 `gh` CLI 操作，易於自動化
5. **即時更新**：webhook 即時推送

**實作路徑：**
1. **Phase 1**：啟用 GitHub Projects，建立 Board view
2. **Phase 2**：建立 Telegram bot，實現 `/task`, `/done`, `/list` 指令
3. **Phase 3**：GitHub Actions 自動通知到 Telegram 群組
4. **Phase 4**：OpenClaw cron 定時同步 Ideas 目錄到 GitHub Issues

---

### 🥈 備選：騰訊文檔

**適用條件：**
- 團隊成員偏好微信/QQ 協作
- 不想處理技術細節
- 需要最佳中文體驗

**實作路徑：**
1. 建立騰訊文檔智能表格（看板視圖）
2. 手動匯入現有 Tasks
3. 分享給團隊成員

---

### 🥉 可考慮：Notion

**適用條件：**
- 團隊願意付費（$8/月）
- 需要更強大的 Database 功能
- 需要多視圖（Calendar、Timeline）

---

## 四、不推薦方案

### ❌ 自建 Dashboard

**原因：**
- 開發 + 維護成本過高（100+ 小時）
- 團隊僅 6 人，ROI 不划算
- GitHub Projects 已能滿足需求

**例外：**
- 若未來有特殊需求（如高度客製化），再考慮

---

### ❌ Planka / WeKan

**原因：**
- 無 Telegram 整合，需額外開發
- 維護 Docker 環境增加負擔
- GitHub Projects 功能已涵蓋

---

## 五、實作建議

### GitHub Projects 設定建議

**Board 結構：**
```
| 待處理 | 進行中 | 審核中 | 完成 |
|--------|--------|--------|------|
| Ideas  |        |        |      |
| Tasks  |        |        |      |
```

**標籤設計：**
- `idea`：來自 Ideas 目錄
- `howto`：HOWTO 文檔相關
- `team:寶寶`, `team:碼農1號`, ...：成員分配

**自動化：**
1. Issue created → 加入 Projects
2. Issue labeled `idea` → 通知 Ideas 頻道
3. Issue closed → 移動到「完成」欄位

---

### Telegram Bot 指令設計

```
/task <標題>        建立 Issue
/done <Issue#>      標記完成
/list               列出我的任務
/ideas              列出 Ideas 待處理
/assign <Issue#> <成員>  分配任務
```

---

## 六、結論

**推薦採用 GitHub Projects**，原因：

1. ✅ **免費**：零成本
2. ✅ **整合度高**：與現有 repo + OpenClaw + Telegram 無縫整合
3. ✅ **即時更新**：webhook 即時推送
4. ✅ **中文支援**：完整
5. ✅ **部署簡單**：零部署

**下一步：**
1. 啟用 GitHub Projects
2. 建立 Telegram bot（可用現成 `appleboy/telegram-action`）
3. 設定 GitHub Actions 自動化
4. OpenClaw cron 同步 Ideas 目錄

---

**參考資料：**
- GitHub Projects 官方文檔：https://docs.github.com/en/issues/planning-and-tracking-with-projects
- Telegram Bot API：https://core.telegram.org/bots/api
- appleboy/telegram-action：https://github.com/appleboy/telegram-action
- notion-telegram-bot：https://github.com/xheiop/notion-telegram-bot
- Planka：https://planka.app/
