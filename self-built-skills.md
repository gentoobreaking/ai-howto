# 自建 Skills 清單

> 最後更新：2026-04-12 08:30 GMT+8

## 使用規範

1. **日後自建 skill 都要更新此 howto**
2. **上傳 ClawHub 前先參照此表**，避免重複 skill 不同名稱上傳
3. **上傳後同步更新 MEMORY.md**，最後回報使用者

---

## Skills 列表

| Skill | ClawHub Slug | 觸發關鍵字 | 範例語法 | MEMORY.md 同步 | ClawHub 同步 |
|-------|-------------|-----------|---------|---------------|-------------|
| GitHub CLI 整合 | `clw-github` | github, gh, issue, pr | 「幫我開一個 issue」「查看 PR 狀態」 | 2026-04-12 08:27 | 2026-04-12 08:19 |
| 本地語音轉文字 | `clw-whisper` | whisper, 語音轉文字, STT | 「用 whisper 轉這段錄音」 | 2026-04-12 08:27 | 2026-04-11 12:44 |
| URL/檔案摘要 | `clw-summarize` | summarize, 摘要, 總結 | 「摘要這個網址」「總結這份 PDF」 | 2026-04-12 08:27 | 2026-04-11 12:44 |
| 多金屬監控 | `free-gold-monitor-pro` | 黃金, 金價, gold, 白銀, 鉑金 | 「現在金價多少」「設定金價警報」 | 2026-04-12 08:27 | 已存在 |
| 語音雙模回覆 | `free-voice-reply` | 語音回覆, voice reply, TTS | 「用語音回覆」 | 2026-04-12 08:27 | 已存在 |
| Ideas 轉 Tasks | `ideas2tasks` | ideas, tasks, 待辦 | 「把 ideas 轉成 tasks」 | 2026-04-12 08:27 | 已存在 |
| Prompt 注入過濾 | `prompt-injection-filter` | prompt injection, 安全 | （自動觸發） | 2026-04-12 08:27 | 已存在 |
| Scrum Task 追蹤 | `scrum-task-tracker` | scrum, task, 追蹤 | 「追蹤這個 task」 | 2026-04-12 08:27 | 已存在 |
| Self-Improving Agent | `self-improving-agent` | 錯誤學習, 改進 | （自動觸發） | 原有 | 原有 |
| Self-Improving | `self-improving` | 自我改進, proactive | （自動觸發） | 原有 | 原有 |
| Browser Automation | `agent-browser-clawdbot` | browser, 瀏覽器, 截圖 | 「幫我截圖這個網頁」 | 原有 | 原有 |
| OpenClaw Backup | `openclaw-backup` | backup, 備份 | 「備份 OpenClaw 資料」 | 原有 | 原有 |

| GitHub Issue 管理 | `clw-github-issues` | GitHub Issue、Issue Migration、Draft Item、Board 去重 | 「幫我執行 Board Migration」「更新 Issue body」 | 2026-04-13 14:50 | ✅ 2026-04-13 06:50 |
| GitHub Projects 實驗（問題快照） | `clw-github-projects` | GitHub Projects v2 API 問題、Draft Item 限制、GraphQL 失敗經驗 | 「GitHub Board API」「Draft Issue body 問題」 | 2026-04-13 14:50 | ✅ 審核中 |

---

## 命名規範

- **前綴**：`clw-`（ClawHub 自建）
- **禁止**：不含 Yuhao 等個人資訊
- **避免重複**：上傳前先 `clawhub search <keyword>` 確認 slug 是否已存在

---

## 上傳流程

```bash
# 1. 確認 slug 未被佔用
clawhub search <skill-name>

# 2. 發布
clawhub publish /path/to/skill --name "Skill Name" --version 1.0.0

# 3. 更新此 howto
# 4. 更新 MEMORY.md
# 5. 執行 sync_all.sh
# 6. 回報使用者
```
