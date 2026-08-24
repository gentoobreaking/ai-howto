# pi agent skill — spec-to-tasks（規格書 → 任務書拆分）

> 建立日期：2026-08-24
> Skill 位置：`~/.pi/agent/skills/spec-to-tasks/SKILL.md`
> 配套文件：[pi-run-project.md](pi-run-project.md)（拆好的任務書如何交給排程器自動執行）

---

## 一、這是什麼

讓 pi agent 聽到「幫 XX 專案拆任務／根據規格書建立任務」時，自動把
`~/tasks/<專案>/spec.md` ＋ `algs/*.md` 拆解成符合範本的任務書
（T001–T0xx），並完成依賴驗證與追溯矩陣。

這個 skill 固化了一次完整的實戰審查循環——六個教訓直接寫成鐵律：

| 鐵律 | 來源 |
|---|---|
| 附錄式演算法會被遺失 → 演算法獨立成 `algs/` 檔，任務書強制引用 | slo-sentinel 拆分時發現的風險 |
| 「依 §X 全數實作」不是驗收標準 → 枚舉展開到可勾選粒度 | 第一版任務書被退回「好像簡化很多」 |
| 外包計算 ≠ 減少模組 | Sloth 整合時誤把「實作深度減少」寫成「架構縮水」 |
| 站在成熟工具上，自研只做差異化增量 | Sloth / awesome-prometheus-alerts 評估 |
| 同一事件只能有一條通知路徑 | ai-oncall「寫回指標 vs 直推」雙路通知矛盾 |
| 看得到建議的人 ≠ 動手的人 | Compute Optimizer 可視性問題 → 自研引擎進 v1 |

## 二、使用方式

```
# 自動觸發（說到拆任務就會匹配）
幫 slo-sentinel 根據規格書進行任務拆分及撰寫
spec 在 ~/tasks/slo-sentinel/，拆出任務書

# 或明確呼叫
/skill:spec-to-tasks slo-sentinel
```

### 輸入約定（可被使用者訊息覆寫）

| 項目 | 預設路徑 |
|---|---|
| 主規格書 | `~/tasks/<專案>/spec.md` |
| 演算法規格 | `~/tasks/<專案>/algs/*.md` |
| 任務範本 | `~/Projects/ai-skills/clw-ideas2tasks/templates/task-template.md` |
| 輸出 | `~/tasks/<專案>/tasks/T###-kebab-name.md` |

## 三、Skill 內建的六步流程

1. **讀取全部輸入**——範本、spec、所有 algs 全文讀完；`tasks/` 已有任務書則接續編號不覆蓋
2. **規格書健檢**——non-goals 有無、功能是否編號（F1–Fxx）、演算法細節在哪、
   後期/選配項、外部依賴；有缺口先提出再動工
3. **設計任務地圖**——每模組 ≥1 張、每演算法檔 ≥1 張、e2e 排最後；
   依賴圖禁循環；粒度原則：單張在一個 agent session 內可完成（25–50 行）
4. **產出任務書**——frontmatter 規範＋四條撰寫鐵律（見下節）
5. **追溯索引寫回 spec.md**——「演算法檔 ↔ 功能 ↔ 模組 ↔ 任務編號」四欄矩陣
6. **驗證**——deps 存在且無循環、frontmatter 完整、`depends_on: []` 單行格式、
   雙向覆蓋矩陣、無模糊引用

## 四、任務書關鍵慣例

### frontmatter（照 clw-ideas2tasks 範本欄位）

```yaml
---
github_issue: N/A
title: <中文標題，含模組路徑>
type: feat | fix | chore | docs | test
priority: high | medium | low
status: pending            # 只允許 pending/done/in-progress
depends_on:
- T00X-xxx                 # 無依賴時寫 depends_on: []（單行！）
assignee: "pi with opencode/x-preview-f-free"
created: YYYY-MM-DD
updated: YYYY-MM-DD
blocked_on:                # 僅條件式任務需要
- "<具體可驗證的前置條件>"
---
```

### 驗收標準撰寫鐵律

1. **展開而非引用**：「依 §A.5 全數實作」是壞例子——把規則連預設值逐一列成 checkbox；
   演算法檔降級為深究原理時的參照
2. **固定測試案例**：演算法檔的數值例轉成斷言具體數字的測試要求
3. **枚舉語料集**：解析/驗證類任務要求 ≥N 個壞輸入案例逐一斷言行為
4. **介面契約**：基礎任務要在驗收標準定義 interface 簽名（下游任務依賴它）
5. **負面測試**：涉及認證/遮蔽/執行面的任務必須驗證拒絕行為

### 條件式任務（後期/選配/外部依賴）

後期或選配功能**仍然拆出任務書**（範圍要可見），但：

- frontmatter 加 `blocked_on:` 列出可驗證的前置條件
- 目標第一行放 ⛔ 約束聲明：排程器挑到時先逐項驗條件，未滿足則跳過並記錄
- priority 一律 low；功能設計仍預先想好寫進去（解鎖即可直接開工）
- 實例見 `~/tasks/slo-sentinel/tasks/T019-ci-budget-gate.md`、`T020-oncall-integration.md`

## 五、拆完之後

1. spec.md 會多出「演算法規格文件索引（任務拆解必讀）」章節：
   演算法檔 ↔ 功能 ↔ 模組 ↔ 任務編號 的四欄追溯矩陣＋支援性任務清單＋延後批次聲明
2. 到 `~/Projects/<專案>` 建 repo（git init）後，
   說「執行 <專案名> 專案」（見 [pi-run-project.md](pi-run-project.md)）即可讓排程器開始消化任務書
3. 若 spec 後續修改，重跑本 skill 會接續既有編號；記得同步更新被引用的小節號

## 六、實測紀錄

| 專案 | 任務數 | 特點 |
|---|---|---|
| slo-sentinel | T001–T020（含 2 張 blocked_on） | Go 單 binary + UI；四個感測家族共用 ETA 引擎 |
| ai-oncall | T001–T019 | gate(Go)/core(Python)/ui 三服務；F1–F21 |

## 七、配套：task-audit skill（完成度誠實稽核）

> 位置：`~/.pi/agent/skills/task-audit/SKILL.md`（含共用 `scripts/validate_tasks.py`）

拆完、跑完之後的第三步——對 status:done 的任務書逐條驗證：

```
/skill:task-audit slo-sentinel
```

五步流程：結構驗證（validate_tasks.py）→ 逐條三態判定（✅達成打勾／⬜未達成保留／🔀部分）→
缺口分流處理（可快補的直接補＋commit）→ 執行紀錄附註 → ✅/⬜ 統計報告。

核心紀律：
1. 打勾必須能指出測試名稱／程式碼位置／產出檔案
2. 多項核心未達成 → 任務書降級 in-progress，不得維持 done
3. 快速可補的缺口直接補實作＋補測試，獨立 commit

實測成果：slo-sentinel 首輪稽核抓出 daemon 未接熱載入、UI 缺四頁等真實缺口，
最終統計 ✅92 ⬜38（含 8 項條件式任務）。

## 八、配套：write-readme skill（證據導向 README 產生）

> 位置：`~/.pi/agent/skills/write-readme/SKILL.md`

```
/skill:write-readme slo-sentinel
```

五階段流程：Product Understanding → Architecture Understanding →
Spec vs Implementation 比對表 → Information Gaps → Final README。

核心紀律：
1. 「目前實際行為」以 source code 為準；與規格不一致時明確指出，不偷偷選邊
2. 無法確認的資訊標記 [NEEDS VERIFICATION]，不自行填空——完整與正確衝突時優先正確
3. 未實作功能寫進 Limitations，不包裝成特色
4. 完稿後有自審清單（command/env/API 是否真實存在等）
5. 任務書的執行紀錄（勾選狀態）可作為「哪些功能真的完成」的佐證

實測：slo-sentinel 的 README 即以此流程重寫。
