# Session 完整對話存檔 - 分析報告

> **任務**: T002 - Session 完整對話存檔
> **負責人**: 樂樂
> **分析日期**: 2026-04-06

---

## 📋 需求回顧

讓 AI 完整輸出對話（包含思考過程及完整 cmd），每個 session 內獨立存到 `~/sessions/*.log`，檔名以 Timestamp + topic 命名。

---

## 🔍 現況分析

### OpenClaw 現有機制

| 機制 | 說明 | 包含 Thinking | 包含完整 cmd |
|------|------|---------------|--------------|
| **Lossless LCM** | 對話壓縮存儲 | ✅ 部分 | ✅ |
| **Session History** | `sessions_history` API | ✅ | ✅ |
| **SQLite DB** | `~/.qclaw/memory/main.sqlite` | ✅ | ✅ |
| **Cron 導出** | 無內建定時導出 | ❌ | ❌ |

### 現有導出方式

1. **手動導出**: 使用 `sessions_history` API
2. **LCM 導出**: `lcm_expand` 可恢復壓縮內容
3. **手動補捉**: 從 websocket 消息流獲取

---

## 🛠️ 實現方案

### 方案 A: Hook 方式（推薦）

透過 OpenClaw plugin 或 skill interceptor 攔截完整輸出：

```python
# 概念驗證
def log_session(message, thinking, commands):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"~/sessions/{timestamp}_session.log"
    with open(filename, "a") as f:
        f.write(f"[Thinking]\n{thinking}\n\n")
        f.write(f"[Commands]\n{commands}\n\n")
```

**限制**: 需要 plugin 開發，QClaw 目前無此 plugin。

### 方案 B: 外掛腳本監聽

定時從 `sessions_history` 導出：

```bash
# cron job 示例（每小時）
0 * * * * curl -s "http://localhost:28789/sessions/history?session=main" \
  > ~/sessions/$(date +\%Y-\%m-\%d_\%H\%M)_session.log
```

**限制**: 需要 Gateway API token，格式可能不完整。

### 方案 C: 現有工具組合

利用 `sessions_history` + 手動格式化：

```bash
# 獲取當前 session 完整歷史
openclaw sessions history --session main --limit 100
```

---

## 📦 建議產出

由於完整實現需要 Plugin 開發（非配置層面可達成），建議：

1. **短期**: 使用 `sessions_history` 手動導出腳本
2. **中期**: 開發 session-logger plugin
3. **長期**: 作為 Feature Request 回饋給 OpenClaw 團隊

---

## ✅ 建議動作

- [ ] 建立 `~/sessions/` 目錄
- [ ] 撰寫導出腳本 `~/scripts/session-export.sh`
- [ ] 設定 cron 每小時導出

---

_分析完成，待用戶確認後續方向_