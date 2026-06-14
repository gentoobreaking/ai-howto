# HOWTO: 在不啟動 OpenClaw 的情況下安裝 Plugins

## ⚠️ 前置說明

本文件的假設：
- 你希望離線或在 QClaw App 未運行的狀態下，提前安裝好 Plugins
- 你知道要安裝哪些 Plugins 的名稱或來源
- 你的作業系統：**macOS**

---

## 一、基本概念

| 術語 | 說明 |
|------|------|
| **Plugin** | OpenClaw 的功能擴展模組，存放於 `skills/` 目錄 |
| **Bundled Skills** | QClaw 內建的 Plugins，位於 Application Support |
| **Workspace Skills** | 使用者自訂的 Plugins，位於 `~/.openclaw/workspace/skills/` |
| **ClawHub** | OpenClaw 官方 Plugin 商店 |

---

## 二、安裝 Plugins 的兩種方式

### 方式 A：用 CLI 離線安裝（不需 OpenClaw 運行）

適用場景：你知道 Plugin 的名稱，但 OpenClaw/QClaw 目前未啟動。

#### 步驟 1：確認 CLI 已安裝

```bash
# 檢查 openclaw CLI 是否可用（即使未啟動服務）
openclaw --version
```

若未安裝，先用 npm 安裝：
```bash
npm install -g openclaw
```

#### 步驟 2：用 clawhub CLI 安裝 Plugin

```bash
# 搜尋 Plugin
clawhub search <keyword>

# 安裝 Plugin（不需要啟動 Gateway）
clawhub install <plugin-name>
```

#### 步驟 3：確認安裝結果

```bash
# 查看已安裝的 Plugins
openclaw skills list
```

---

### 方式 B：手動複製 Plugin 目錄（完全離線）

適用場景：你已有 Plugin 的完整目錄（如從另一台機器複製過來）。

#### 步驟 1：確認 Plugin 目錄結構

一個有效的 Plugin 目錄應包含：

```
skill-name/
├── SKILL.md          # 必要：Plugin 描述與觸發條件
├── scripts/          # 可選：Python/Shell 腳本
├── assets/           # 可選：圖片、範本等資源
└── README.md          # 可選：使用說明
```

#### 步驟 2：複製到正確位置

**自訂 Plugins（Workspace Skills）：**
```bash
cp -r /path/to/your-skill/ ~/.openclaw/workspace/skills/
```

**內建 Plugins（需確認寫入權限）：**
```bash
cp -r /path/to/your-skill/ ~/Library/Application\ Support/QClaw/openclaw/config/skills/
```

#### 步驟 3：驗證 Plugin 結構

```bash
# 確認 SKILL.md 存在
ls ~/.openclaw/workspace/skills/<skill-name>/SKILL.md

# 確認 JSON 語法正確
cat ~/.openclaw/workspace/skills/<skill-name>/SKILL.md | head -5
```

---

## 三、使用 SkillHub 安裝（需要網路）

> ⚠️ 這需要網路連線，但不需要 QClaw App 運行。

#### 步驟 1：確認 skillhub CLI

```bash
skillhub --version
```

#### 步驟 2：搜尋並安裝

```bash
# 搜尋
skillhub search <keyword>

# 安裝
skillhub install <skill-name>
```

#### 步驟 3：安裝後確認

```bash
# 查看已安裝列表
skillhub list

# 或透過 openclaw
openclaw skills list
```

---

## 四、批量預先安裝多個 Plugins

如果你需要一次安裝多個 Plugins，可以建立一個安裝腳本：

```bash
#!/bin/bash
# install-plugins.sh

SKILLS_DIR="$HOME/Library/Application Support/QClaw/openclaw/config/skills"

# 定義要安裝的 Plugins 清單
PLUGINS=(
  "openclaw-timer"           # 計時器
  "openclaw-weather"         # 天氣
  "openclaw-reminder"        # 提醒
  "openclaw-git"             # Git 管理
)

for plugin in "${PLUGINS[@]}"; do
  echo "Installing $plugin..."
  clawhub install "$plugin"
  echo "✅ $plugin installed"
done

echo "All plugins installed:"
openclaw skills list
```

執行：
```bash
chmod +x install-plugins.sh
./install-plugins.sh
```

---

## 五、Plugin 安裝後的驗證清單

| 檢查項目 | 確認方式 |
|---------|---------|
| Plugin 目錄存在 | `ls ~/.openclaw/workspace/skills/` |
| SKILL.md 存在 | `ls ~/.openclaw/workspace/skills/<name>/SKILL.md` |
| 語法正確 | `cat ~/.openclaw/workspace/skills/<name>/SKILL.md` 可讀 |
| 已列入清單 | `openclaw skills list` 或 `clawhub list` |
| QClaw App 重啟後可見 | 重啟 QClaw App 並檢查 |

---

## 六、常見問題與解決方式

### Q1：Plugin 已安裝但 OpenClaw 看不到

**可能原因：**
- Plugin 目錄名稱與 SKILL.md 內的 `name` 不一致
- SKILL.md 的 JSON 格式有錯誤

**解決方式：**
```bash
# 確認目錄名稱與 SKILL.md 的 name 欄位一致
cat ~/.openclaw/workspace/skills/<skill-name>/SKILL.md | grep '"name"'
```

### Q2：權限不足，無法寫入 Skills 目錄

**解決方式：**
```bash
# 修正目錄權限
chmod 755 ~/.openclaw/workspace/skills/
chmod -R 755 ~/.openclaw/workspace/skills/<skill-name>/
```

### Q3：安裝失敗，clawhub 報 404

**可能原因：**
- Plugin 名稱拼寫錯誤
- Plugin 不存在於 ClawHub

**解決方式：**
```bash
# 先搜尋確認名稱
clawhub search <keyword>
```

### Q4：Plugin 無法啟動（缺少相依套件）

**可能原因：**
- Plugin 需要 Python、Node.js 等特定環境

**解決方式：**
```bash
# 查看 Plugin 的 README 或 SKILL.md
cat ~/.openclaw/workspace/skills/<skill-name>/SKILL.md
```

---

## 七、工作流程總結

```
需求評估
    ↓
選擇安裝方式
    ├── 有網路 → clawhub install / skillhub install
    └── 無網路 → 手動複製目錄
    ↓
複製到正確位置
    ├── Workspace Skills → ~/.openclaw/workspace/skills/
    └── Bundled Skills → ~/Library/Application Support/QClaw/openclaw/config/skills/
    ↓
驗證安裝
    ↓
啟動 QClaw App 或重啟 Gateway
```

---

## 八、相關參考

- OpenClaw 架構：`openclaw --help`
- ClawHub 使用：`clawhub --help`
- SkillHub 使用：`skillhub --help`
- 備份 Skills：建議在安裝後備份 `~/.openclaw/workspace/skills/` 到外部儲存
