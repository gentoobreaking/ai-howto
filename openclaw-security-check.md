# OpenClaw 安全評估報告

> 評估日期：2026-04-04
> 最後更新：2026-04-04 14:22
> 評估依據：[OpenClaw 安全嗎？5 個必做的安全設定](https://yu-wenhao.com/zh-TW/blog/2026-02-04-is-openclaw-safe-security-guide/)

---

## 📊 執行狀態總覽

| 設定 | 狀態 | 說明 |
|------|------|------|
| Token 上限 | ✅ | Qclaw 已有每日限制 |
| 保護機密資訊 | ✅ | API Key 已改用環境變數 |
| exec 審批 | ✅ | 已啟用 + Telegram allowlist |
| Skill 攔截 | ✅ | skill-interceptor 攔截 8 個高風險 Skills |
| 網路隔離 | ✅ | loopback 綁定 + SSRF 防護 |

**詳細執行記錄**：見 `/Users/claw/Tasks/security-improvements/`

---

## 文章來源

本評估基於以下兩篇文章進行：
1. [OpenClaw 安全嗎？5 個必做的安全設定](https://yu-wenhao.com/zh-TW/blog/2026-02-04-is-openclaw-safe-security-guide/)
2. [OpenClaw 教學：26 個 Tools + 53 個 Skills 完整指南](https://yu-wenhao.com/zh-TW/blog/openclaw-tools-skills-tutorial/)

---

## 安全設定評估

### 設定 1：Token 上限 + 定期回報

| 項目 | 文章建議 | 我的環境 | 狀態 |
|------|---------|---------|------|
| LLM Provider 上限 | 設定 spending limit | 使用 Qclaw modelroute（有每日限制） | ✅ 已有上限 |
| 用量監控 | 定期查看 provider dashboard | 可透過 /status 查看 token 用量 | ✅ 可監控 |
| cron 定期回報 | 可選功能 | 目前未設定 | ⚠️ 可加強 |

**建議**：可考慮設定 cron 定期推送用量報告到 Telegram。

---

### 設定 2：保護機密資訊

| 項目 | 文章建議 | 我的環境 | 狀態 |
|------|---------|---------|------|
| ~/.openclaw 不同步雲端 | 排除在 iCloud/Dropbox 外 | 檢查結果：未發現同步 | ✅ 安全 |
| API Key 存放 | 使用環境變數 | 已改用 `${OPENROUTER_API_KEY}` 等 | ✅ **已完成** |
| 敏感設定檔 | 不 commit 到 Git | 已加入全域 + workspace .gitignore | ✅ **已完成** |
| 敏感檔案鎖定 | chflags schg | 已鎖定 id_ed25519, .zshrc, hosts.yml | ✅ **已完成** |

**已執行改善**（2026-04-04）：
1. ✅ 4 個明文 API Key 改用環境變數（OpenRouter、Telegram、Gateway、WeChat）
2. ✅ 建立 `~/.config/git/ignore` 全域 gitignore
3. ✅ 建立 workspace `.gitignore`
4. ✅ 鎖定 3 個敏感檔案（schg flag）

**環境變數清單**（定義於 `~/.zshrc`）：
- `OPENROUTER_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `OPENCLAW_GATEWAY_TOKEN`
- `WECHAT_ACCESS_TOKEN`

---

### 設定 3：只開必要 Tools + exec 審批

| 項目 | 文章建議 | 我的環境 | 狀態 |
|------|---------|---------|------|
| exec 審批啟用 | `"approvals": { "exec": { "enabled": true } }` | 已啟用 + Telegram allowlist | ✅ **已設定** |
| Tools 白名單 | 只開需要的 tools | 評估後維持現狀（現有防護已足夠） | ✅ **已評估** |
| 敏感路徑鎖定 | chflags schg | 已鎖定 3 個檔案 | ✅ **已完成** |

**已鎖定檔案**：
```
~/.ssh/id_ed25519    schg
~/.zshrc             schg
~/.config/gh/hosts.yml  schg
```

**驗證刪除保護**：
```bash
$ rm ~/.zshrc
rm: /Users/claw/.zshrc: Operation not permitted
```

---

### 設定 4：不亂裝 Skill + OAuth 最小化

| 項目 | 文章建議 | 我的環境 | 狀態 |
|------|---------|---------|------|
| Skill 審查 | 只裝可信來源 | 已安裝多個 ClawHub Skills | ✅ 已審查 |
| Skill 攔截 | 阻擋高風險 Skill | skill-interceptor 已啟用 | ✅ 已設定 |
| OAuth 最小化 | 只開必要權限 | GitHub CLI 有 token | ⚠️ 需檢查權限 |

**已攔截的 Skills**（透過 skill-interceptor）：
- tencent-docs, tencent-survey, notion
- 163-email-skill, qq-email-skill
- tencent-meeting, tencent-meeting-mcp, ima

---

### 設定 5：網路隔離

| 項目 | 文章建議 | 我的環境 | 狀態 |
|------|---------|---------|------|
| Gateway 綁定 | bind: loopback | `"bind": "loopback"` | ✅ 安全 |
| Tailscale | 按需開啟 | `"mode": "off"` | ✅ 關閉 |
| SSRF 防護 | 禁止私有網路存取 | `"dangerouslyAllowPrivateNetwork": false` | ✅ 安全 |

---

## exec 審批思考過程

### 什麼是 exec 審批？

exec 審批是指在 OpenClaw 執行系統命令前，先顯示命令內容給用戶確認的機制。這是最重要的防線，可以攔截：
- 外部攻擊（Prompt Injection）
- Agent 誤判（理解錯誤、過度行動）

### 我的思考過程

**Q1：為什麼需要 exec 審批？**

OpenClaw 的 exec tool 可以執行任何 shell 命令，包括 `rm -rf`。如果 Agent 被騙或誤判，可能執行危險操作。審批機制讓我有最後一道防線可以拒絕可疑命令。

**Q2：會不會很煩？**

老實說會。每次執行命令都要確認，會增加操作步驟。但這是「安全 vs 便利」的取捨——我選擇安全。

**Q3：如何平衡？**

1. **allowlist 機制**：對於信任的來源（如我的 Telegram），可以設定 allowlist，減少審批次數
2. **SOUL.md 規則**：讓 Agent 在執行前說明原因，幫助我判斷是否合理

### 最後作法

1. 啟用 exec 審批（預設）
2. 設定 Telegram allowlist
3. 在 SOUL.md 加入執行規則：
   ```markdown
   ## exec 執行規則
   執行任何命令前，必須：
   1. 說明這個命令要做什麼
   2. 說明為什麼需要執行
   3. 等待用戶確認後才執行
   ```

---

## 改善項目執行狀態

### ✅ 已完成（6/7）

| # | 項目 | 執行結果 |
|---|------|---------|
| 1 | API Key 改用環境變數 | ✅ 4 個 Key 已移至 `~/.zshrc` |
| 2 | .gitignore 設定 | ✅ 全域 + workspace 已建立 |
| 3 | 鎖定敏感檔案 | ✅ 3 個檔案已設 schg |
| 4 | tools.allow/deny | ✅ 評估後維持現狀 |
| 6 | GitHub token 權限 | ✅ 已評估，維持現狀 |
| 7 | LLM spending limit | ✅ Qclaw 已有每日限制 |

### ⏳ 待處理（1/7）

| # | 項目 | 說明 |
|---|------|------|
| 5 | 用量報告 cron | 需設計數據來源和報告格式 |

---

## 參考資料

- [OpenClaw 安全嗎？5 個必做的安全設定](https://yu-wenhao.com/zh-TW/blog/2026-02-04-is-openclaw-safe-security-guide/)
- [OpenClaw 教學：26 個 Tools + 53 個 Skills 完整指南](https://yu-wenhao.com/zh-TW/blog/openclaw-tools-skills-tutorial/)
- [Microsoft Security Blog - Running OpenClaw Safely](https://www.microsoft.com/en-us/security/blog/2026/02/19/running-openclaw-safely-identity-isolation-runtime-risk/)
- [SlowMist OpenClaw Security Practice Guide](https://github.com/slowmist/openclaw-security-practice-guide)
