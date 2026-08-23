# pi — 專案任務自動執行設定

> 建立日期：2026-08-24
> 用途：讓 pi agent 聽到「執行 <專案名> 專案」時，自動接手完成任務書裡所有未完成任務

---

## 專案分區慣例

| 項目 | 路徑 |
|---|---|
| 專案名稱（project name） | `tw-quant-pickup` |
| 專案程式碼路徑（code path） | `~/Projects/<專案名>/` |
| 專案開發文件路徑（doc path） | `~/tasks/<專案名>/tasks/T*.md` |

---

## 已設定的檔案

### ① `~/.pi/agent/skills/run-project/SKILL.md`

Global skill，內容重點：

1. **找出未完成任務**：掃描 frontmatter，`status: pending` / `in-progress` 為未完成；依 priority（high→medium→low）+ 編號排序；有 `depends_on` 未 done 的先跳過
2. **逐任務執行**：讀任務書 → 在 code path 實作 + 跑測試 → commit（一個任務一個 commit）→ 任務書改 `status: done` + 當天日期 → 回報後下一個
3. **收尾**：全部完成後 bash 執行 `say "修復任務都完成了"`

紀律：驗收標準是唯一完成依據、不得放水；遇阻塞註記原因留在 in-progress 並跳過，最後彙報。

### ② `~/.pi/agent/AGENTS.md`（新增段落）

```markdown
## 專案任務自動執行
- 當我說「執行 <專案名> 專案」時，載入並遵循 `run-project` skill：
  程式碼在 ~/Projects/<專案名>/，任務書在 ~/tasks/<專案名>/tasks/，
  持續完成所有未完成任務，每任務一個 commit，全部完成後 say "修復任務都完成了"
```

---

## 使用方式

```
執行 tw-quant-pickup 專案
```

或強制觸發（不靠語意比對）：

```
/skill:run-project tw-quant-pickup
```

---

## 驗證

1. 新啟動 pi session，確認 `/skills` 列表有 `run-project`
2. 下指令後觀察 agent 是否去讀 `~/tasks/<專案名>/tasks/`

---

## 疑難排解

| 症狀 | 解法 |
|---|---|
| 讀 `~/tasks/` 出現 `Operation not permitted` | agent 會先 `say "目前需要終端機授權"` 並停止；去「系統設定 → 隱私權與安全性 → 完整磁碟存取」授權跑 pi 的終端機 App 後再繼續 |
| Provider 連續 network_error / 長跑斷線 | agent 會先 `say "session長跑中斷線"`，並把進度註記在任務書（保持 in-progress）；用 `/resume` 或 `pi --fork` 接續 |
| Skill 沒被觸發 | 改用 `/skill:run-project <專案名>` 強制載入 |

---

## 相關背景：session 卡在 network_error

若續接舊 session 出現 `Error: Provider finish_reason: network_error`：

- 意義：opencode 中繼層回傳的錯誤（pi 的 `pi-ai/openai-completions.js` 所映射），非本機問題
- 特徵：同一對話前綴 100% 失敗、其他 session 正常 → 服務端狀態毒化（失敗結果被快取綁定到此對話）
- 解法：
  ```bash
  pi --fork <session-id 或檔案路徑>   # 分岔出新副本（原檔不動）
  # 進入後立刻 /compact 改寫前綴，繞開毒化狀態
  ```
- Session 檔位置：`~/.pi/agent/sessions/--<cwd 編碼>--/<時間>_<uuid>.jsonl`
