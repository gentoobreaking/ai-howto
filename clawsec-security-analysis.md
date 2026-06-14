# ClawSec 安全建議分析

## 功能概述

ClawSec 是一個完整的安全 skill suite，提供：

| 功能 | 說明 |
|------|------|
| 📦 Suite Installer | 一鍵安裝所有安全 skills |
| 🛡️ File Integrity Protection | SOUL.md、IDENTITY.md 等關鍵檔案的 drift detection |
| 📡 Live Security Advisories | 自動 NVD CVE 輪詢和社群威脅情報 |
| 🔍 Security Audits | 自檢腳本檢測 prompt injection 標記 |
| 🔐 Checksum Verification | SHA256 校驗所有 skill artifacts |

## 安裝方式

```bash
npx clawhub@latest install clawsec-suite
```

或從 source：
```bash
# 讀取最新 SKILL.md
curl -sL https://github.com/prompt-security/clawsec/releases/latest/download/SKILL.md
```

## 適用場景

### ✅ 推薦安裝

- **生產環境 AI agent**：暴露在公網、處理敏感數據
- **多人協作 agent**：需要保護 SOUL.md 不被竄改
- **高風險 skill 使用**：安裝來自第三方的 skills

### ⚠️ 可選安裝

- **個人開發環境**：風險較低
- **隔離環境**：無外部連接

## 與現有安全措施的整合

### 已有措施

| 措施 | 說明 |
|------|------|
| skill-interceptor plugin | 阻擋敏感 skills（tencent-docs, notion 等） |
| prompt-injection-filter skill | Prompt injection 防護 |
| self-improving skill | 錯誤學習與改進 |

### ClawSec 可補充

1. **File Integrity** → 保護 SOUL.md、IDENTITY.md
2. **Advisory Feed** → 主動通知 CVE 和安全公告
3. **Checksum Verification** → Skill 安裝完整性驗證

## 建議

### 短期

- ✅ 已有 `skill-interceptor` 和 `prompt-injection-filter`
- ⏸️ 暫緩安裝 ClawSec，觀察現有措施效果

### 中期

- 當安裝更多第三方 skills 時，考慮啟用 ClawSec 的 advisory monitoring
- 如需保護 SOUL.md 等關鍵檔案，啟用 File Integrity Protection

### 長期

- 生產環境部署時，完整安裝 ClawSec suite

## 結論

**目前不急著安裝**。現有的 `skill-interceptor` 和 `prompt-injection-filter` 已提供基本防護。當以下情況發生時再考慮：

1. 安裝大量第三方 skills
2. 將 agent 部署到生產環境
3. 需要 SOUL.md 完整性監控

---

*文檔建立：2026-04-05*
*相關 Task：T005*
