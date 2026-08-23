# QClaw 功能請求：任務看板 + Sub-agent 狀態可見

## 提案人
OpenClaw 進階用戶（6人 AI 團隊協作場景）

## 背景
目前使用 OpenClaw 運行 6 人 AI 團隊（Planner + 2 Coders + DocWriter + Reviewer + Researcher），每天 spawn 大量 sub-agent sessions。核心痛點：

1. **Sub-agent 執行過程不可見**：QClaw App 只能看到主 session 對話，sub-agent 的執行進度、中間狀態完全看不到
2. **任務狀態缺乏視覺化**：我們用 T*.md 檔案追蹤任務，但在 QClaw App 裡無法一覽各專案進度
3. **多 session 切換困難**：6 個 agent 各自有獨立 session，目前只能逐一查看

## 功能請求

### FR-1：任務看板面板
在 QClaw App 中新增一個「任務」分頁：
- 自動掃描 workspace 下的任務檔案（如 Tasks/ 目錄的 T*.md）
- 看板視圖：按狀態分欄（Pending / In-Progress / Done）
- 支持按專案、按負責人篩選
- 點擊任務卡片可查看詳情或跳轉到對應 session

### FR-2：Sub-agent 執行狀態
在主 session 介面中顯示 sub-agent 的即時狀態：
- Spawn 的 sub-agent 列表（名稱、狀態：running/completed/failed）
- 執行時間和進度指示
- 完成時推送通知到主 session
- 支持點擊查看 sub-agent 的 session log

### FR-3：團隊總覽儀表板
一個高層次視角：
- 各 agent 的當前狀態（idle / working）
- 今日完成的任務數
- 待處理任務佇列

## 目前 workaround
- 自建 `task_callback.py` 腳本：sub-agent 開始/完成時更新 T*.md + Telegram 通知
- 在 Telegram 群組追蹤通知
- 手動查詢 Tasks/ 目錄

## 期望優先級
FR-2 > FR-1 > FR-3（sub-agent 可見性最迫切）

## 環境
- macOS (Apple Silicon)
- QClaw Desktop App
- OpenClaw Gateway
- Telegram channel
