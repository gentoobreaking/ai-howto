# QClaw 環境下使用 OpenClaw CLI

## 重要限制

**QClaw 環境沒有全局 `openclaw` CLI。** 直接執行 `openclaw` 命令會失敗。

必須使用 QClaw 提供的 wrapper 腳本：

```bash
# macOS
bash ~/Library/Application\ Support/QClaw/openclaw/config/skills/qclaw-openclaw/scripts/openclaw-mac.sh <command>

# 常見別名
alias qclaw-cli='bash ~/Library/Application\ Support/QClaw/openclaw/config/skills/qclaw-openclaw/scripts/openclaw-mac.sh'
```

## 允許的命令

| 類別 | 命令 |
|------|------|
| 配置管理 | `config get/set/unset` |
| 定時任務 | `cron add/list/edit/rm/run` |
| 模型管理 | `models list/status/set/fallbacks` |
| Skills | `skills list/info/check` |
| Plugins | `plugins list/info/enable/disable` |
| 狀態查詢 | `status/health/doctor` |

## 禁止的命令

以下命令會破壞 QClaw 的服務管理：

| 命令 | 原因 |
|------|------|
| `gateway run/start/stop/restart` | 服務由 QClaw Electron 管理 |
| `daemon start/stop/restart` | 同上 |
| `reset/uninstall` | 破壞性操作 |

## 配置熱加載

OpenClaw 配置修改後自動熱加載，無需重啟：

```bash
# 修改配置
qclaw-cli config set agents.defaults.model.primary "openrouter/qwen/qwen3.6-plus:free"

# 自動生效，無需重啟
```

## 快速參考

```bash
# 查看網關狀態
qclaw-cli status

# 查看當前配置
qclaw-cli config get agents.defaults.model

# 列出定時任務
qclaw-cli cron list

# 查看健康狀態
qclaw-cli health

# 診斷問題
qclaw-cli doctor
```

---

*文檔建立：2026-04-05*
*相關 Task：T004*
*詳細說明：參見 qclaw-openclaw skill 的 SKILL.md*
