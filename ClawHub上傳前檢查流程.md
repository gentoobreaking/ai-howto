# ClawHub 上傳前檢查流程

上傳任何 Skill 到 ClawHub 前，必須執行以下標準流程。

---

## 📋 標準流程（三步驟）

### 步驟 1：重構腳本 - 移除敏感資訊

**必須移除的敏感資訊：**

| 類型 | 說明 | 處理方式 |
|------|------|----------|
| API Keys | 任何 API Token/Key | 改用環境變數或配置檔 |
| 帳號資訊 | Chat ID、User ID、Email | 改用配置檔 |
| 個人識別資訊 | 姓名、電話、地址 | 完全移除 |
| 內網資訊 | IP、內網 URL、密碼 | 完全移除 |

**重構範例：**

```python
# ❌ 錯誤 - 硬編碼敏感資訊
TELEGRAM_BOT_TOKEN = "123456:ABC-DEF"
TELEGRAM_CHAT_ID = "987654321"

# ✅ 正確 - 使用環境變數 + 配置檔
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# 在函數中從配置檔讀取
config = load_config()
bot_token = config.get("telegram_bot_token", TELEGRAM_BOT_TOKEN)
chat_id = config.get("telegram_chat_id", TELEGRAM_CHAT_ID)
```

---

### 步驟 2：建立 SKILL.md - 完整的 Skill 定義

**SKILL.md 必要欄位：**

```yaml
---
name: skill-name           # Skill 名稱（小寫、連字符）
version: 1.0.0             # 版本號（semver 格式）
description: 簡短描述       # 一句話說明功能
metadata:
  emoji: 🎯                # 代表 emoji
  requires:                # 環境需求
    bins:                  # 必要執行檔
      - ffmpeg
    pip:                   # Python 套件
      - package-name
  install:                 # 安裝指令
    - id: brew
      kind: brew
      formula: ffmpeg
      label: "brew install ffmpeg"
---
```

**檢查清單：**

| 項目 | 必須 |
|------|------|
| name | ✅ 小寫 + 連字符 |
| version | ✅ semver 格式 (1.0.0) |
| description | ✅ 簡短清楚 |
| metadata.emoji | ✅ 代表性 emoji |
| 功能說明 | ✅ 完整使用方式 |
| 環境需求 | ✅ 列出所有依賴 |

---

### 步驟 3：上傳到 ClawHub

**命名規則：**

- ✅ 使用 `free-` 前綴 + 功能名稱
- ✅ 例如：`free-voice-reply`、`free-gold-monitor`
- ❌ 禁止使用個人資訊（如 `yuhao-`）

**上傳指令：**

```bash
clawhub publish ~/.qclaw/workspace/skills/<skill-dir> --slug free-<skill-name> --version 1.0.0
```

---

## 🔒 安全檢查清單

上傳前必須執行以下檢查：

### 檔案內容檢查

```bash
# 檢查是否包含敏感資訊
grep -rn "token\|password\|secret\|api_key\|apikey" ~/.qclaw/workspace/skills/<skill-dir>/

# 檢查是否包含個人資訊
grep -rn "yuhao\|個人姓名\|電話\|email" ~/.qclaw/workspace/skills/<skill-dir>/

# 檢查是否包含硬編碼 ID
grep -rn "[0-9]\{9,15\}" ~/.qclaw/workspace/skills/<skill-dir>/
```

### 結構檢查

```bash
# 確認 SKILL.md 存在
ls ~/.qclaw/workspace/skills/<skill-dir>/SKILL.md

# 確認必要欄位
grep "name:\|version:\|description:" ~/.qclaw/workspace/skills/<skill-dir>/SKILL.md
```

---

## 📊 檢查結果範本

每次上傳前，輸出以下格式的檢查結果：

```
📋 Skill 結構檢查

| 項目 | 狀態 | 說明 |
|------|------|------|
| SKILL.md | ✅/❌ | 存在/不存在 |
| name | ✅/❌ | 格式正確/錯誤 |
| version | ✅/❌ | semver 格式 |
| description | ✅/❌ | 簡短清楚 |
| 敏感資訊 | ✅/❌ | 已移除/包含敏感資訊 |
| 個人資訊 | ✅/❌ | 無/包含個人資訊 |

⚠️ 需要處理（如有）：
- [列出問題]

✅ 準備上傳（如通過）
```

---

## 🚨 安全建議

### 1. 敏感資訊處理

- **永遠不要**將 Token、Key、密碼硬編碼在程式中
- **使用環境變數**或**配置檔**儲存敏感資訊
- 配置檔（如 `~/.qclaw/config.json`）**不上傳**到 ClawHub

### 2. 個人資訊保護

- **禁止**使用姓名、暱稱作為 slug 或名稱
- **禁止**包含電話、Email、地址等個人資訊
- **使用通用名稱**：`free-` + 功能描述

### 3. 程式碼審計

- 上傳前執行 `grep` 檢查敏感資訊
- 確認所有 ID、Token 都已改用配置檔
- 檢查註解中是否包含敏感資訊

### 4. 版本控制

- 使用 semver 格式（1.0.0）
- 每次更新遞增版本號
- 保留 changelog 記錄

---

## 📝 執行範例

```
1. 檢查敏感資訊
   → 執行 grep 指令
   → 發現 Token 硬編碼

2. 重構腳本
   → 移除 Token，改用環境變數
   → 更新配置檔讀取邏輯

3. 建立 SKILL.md
   → 確認必要欄位完整
   → 加入環境需求說明

4. 最終檢查
   → 再次執行 grep 確認無敏感資訊
   → 確認 SKILL.md 結構正確

5. 上傳
   → clawhub publish --slug free-xxx --version 1.0.0
```

---

## 📌 建立日期

2026-04-03
