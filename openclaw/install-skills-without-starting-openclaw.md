# HOWTO T033：不啟動 OpenClaw 也能安裝預先定義的 OpenClaw Skills

## 基本資訊
- **Type**: howto
- **Assignee**: 碼農 1 號
- **Date**: 2026-04-10
- **難度**: ⭐⭐☆☆☆（簡單）

---

## 前提條件

### 確認已安裝 CLI 工具
```bash
# 檢查 clawhub CLI 是否可用（不需要 OpenClaw 運行）
which clawhub
clawhub --version

# 檢查 skillhub CLI 是否可用
which skillhub_install 2>/dev/null || echo "需要先安裝 skillhub"
```

如果沒有 `clawhub`，需要先安裝：
```bash
npm install -g clawhub
# 或
brew install clawhub
```

---

## 方式一：用 clawhub 安裝（推薦）

clawhub 是獨立的 CLI，不依賴 OpenClaw Gateway 運行。

### 語法
```bash
clawhub install <skill-slug> --workdir <workspace路徑> --dir skills
```

### 步驟一：確認工作區路徑
```bash
# OpenClaw 預設 skills 目錄
SKILLS_DIR=~/.openclaw/workspace/skills

# QClaw 預設 skills 目錄
SKILLS_DIR=~/.qclaw/workspace/skills
```

### 步驟二：安裝技能
```bash
# 安裝到 OpenClaw workspace
clawhub install ideas2tasks \
  --workdir ~/.openclaw/workspace \
  --dir skills

# 安裝到 QClaw workspace
clawhub install summarize \
  --workdir ~/.qclaw/workspace \
  --dir skills

# 安裝多個
clawhub install gold-monitor \
  --workdir ~/.openclaw/workspace \
  --dir skills

clawhub install self-improving \
  --workdir ~/.openclaw/workspace \
  --dir skills
```

### 步驟三：驗證安裝
```bash
ls ~/.openclaw/workspace/skills/
```

---

## 方式二：用 skillhub_install（QClaw 用戶推薦）

如果使用 QClaw，可以用 `skillhub_install` 工具（不需要 OpenClaw 運行）：

```bash
# 檢查環境
skillhub_install check_env

# 安裝單個技能（自動處理所有依賴）
skillhub_install install_skill ideas2tasks

# 安裝多個技能
skillhub_install install_skill summarize
skillhub_install install_skill pdf
skillhub_install install_skill docx
skillhub_install install_skill xlsx
```

---

## 方式三：手動複製（離線環境可用）

如果網路不可達，可以手動複製 skill 目錄：

### 步驟
```bash
# 從 source 複製到 target
SOURCE=~/Library/Application\ Support/QClaw/openclaw/config/skills/ideas2tasks
TARGET=~/.openclaw/workspace/skills/

mkdir -p "$TARGET"
cp -r "$SOURCE" "$TARGET"

# 確認複製成功
ls "$TARGET/ideas2tasks/"
```

---

## 預先定義的推薦 Skills（可直接安裝）

| Skill | slug | 用途 |
|-------|------|------|
| ideas2tasks | `ideas2tasks` | 想法 → 敏捷任務 |
| self-improving | `self-improving` | 持續自我改進 |
| summarize | `summarize` | 網頁/PDF 摘要 |
| gold-monitor | `gold-monitor` | 黃金價格監控 |
| pdf | `pdf` | PDF 處理 |
| docx | `docx` | Word 文件處理 |
| xlsx | `xlsx` | Excel 處理 |
| news-summary | `news-summary` | RSS 新聞摘要 |

### 一鍵安裝推薦套裝
```bash
# 所有推薦技能，一次安裝
for SKILL in ideas2tasks self-improving summarize gold-monitor; do
  clawhub install $SKILL \
    --workdir ~/.openclaw/workspace \
    --dir skills \
    --no-input
  echo "✅ $SKILL 安裝完成"
done
```

---

## 離線批量安裝脚本

如果需要在多台機器上安裝同一套 Skills，可以建立離線安裝脚本：

```bash
#!/bin/bash
# offline-skill-install.sh
# 不需要網路，不需要 OpenClaw 運行

SKILLS_DIR=~/.openclaw/workspace/skills
mkdir -p "$SKILLS_DIR"

# 定義要安裝的 skill 清單
SKILLS=(
  "ideas2tasks"
  "self-improving"
  "summarize"
  "gold-monitor"
)

for SKILL in "${SKILLS[@]}"; do
  echo "Installing $SKILL..."
  clawhub install "$SKILL" \
    --workdir ~/.openclaw/workspace \
    --dir skills \
    --no-input
done

echo "全部完成！"
ls "$SKILLS_DIR"
```

使用方法：
```bash
chmod +x offline-skill-install.sh
./offline-skill-install.sh
```

---

## Skill 目錄結構說明

成功安裝後，Skills 會出現在以下位置之一：

```
~/.openclaw/workspace/skills/     ← OpenClaw workspace skills
~/.qclaw/workspace/skills/         ← QClaw workspace skills
~/Library/.../skills/              ← Bundled skills（預設）
```

每個 Skill 的標準結構：
```
skill-name/
├── SKILL.md         ← 主要配置（必填）
├── scripts/         ← 附帶腳本
├── references/      ← 參考文檔
└── _meta.json       ← 元數據
```

---

## 常見問題

| 問題 | 解決方式 |
|------|----------|
| `clawhub: command not found` | `npm install -g clawhub` 或 `brew install clawhub` |
| `clawhub install` 一直失敗 | 確認 `--workdir` 指向正確的 workspace |
| Skills 安裝後 OpenClaw 看不到 | 重啟 OpenClaw Gateway 或重啟 CLI |
| 只想安裝到特定目錄 | `--dir` 參數指定子目錄 |

---

## 結論

**不需要運行 OpenClaw Gateway 就能安裝 Skills**。核心方式：
1. `clawhub install <slug>` — clawhub CLI 獨立運行
2. `skillhub_install install_skill <name>` — QClaw 工具（自動處理依賴）
3. 手動複製 — 離線環境備選

建議用 `clawhub install` 批量安裝推薦套裝，一次設定好所有常用技能。

---

_文件日期: 2026-04-10_  
_作者: 碼農 1 號_
