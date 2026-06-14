# HOWTO T031：QClaw 運行中啟動 OpenClaw，兩者同時運行

## 基本資訊
- **Type**: howto
- **Assignee**: 碼農 1 號
- **Date**: 2026-04-10
- **難度**: ⭐⭐☆☆☆（中等）

---

## 目標

讓 QClaw（Port 28789）和 OpenClaw（Port 18789）在同一台 Mac 上同時運行。

---

## 當前狀態

| 組件 | Port | Config 路徑 |
|------|------|------------|
| QClaw Gateway | 28789 | `~/.qclaw/openclaw.json` |
| OpenClaw Gateway | 18789 | `~/.openclaw/openclaw.json` |

---

## 步驟一：確認目前狀態

```bash
# 查看哪個 gateway 在用哪個 port
lsof -i :28789 | grep LISTEN   # QClaw
lsof -i :18789 | grep LISTEN   # OpenClaw

# 檢查 QClaw Gateway 狀態
openclaw gateway status

# 查看 openclaw CLI 位置
which openclaw
openclaw --version
```

---

## 步驟二：啟動 OpenClaw（獨立於 QClaw）

### 方式 A：直接用 openclaw CLI 啟動
```bash
# openclaw CLI 預設讀取 ~/.openclaw/openclaw.json
openclaw gateway start

# 或指定 port
openclaw gateway start --port 18789
```

### 方式 B：用 launchd 服務啟動（推薦，開機自啟）
```bash
# 啟動 LaunchAgent
launchctl load ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# 或用 brew（如果已用 brew 安裝）
brew services start openclaw
```

### 方式 C：手動後台運行（測試用）
```bash
# 不綁定 TTY，後台運行
nohup openclaw gateway start > /tmp/openclaw-gateway.log 2>&1 &
echo $!  # 記住 PID，方便之後 kill
```

---

## 步驟三：驗證雙開成功

```bash
# 檢查兩個 port 都在 listen
lsof -i :28789 -i :18789 | grep LISTEN

# 測試 OpenClaw 健康狀態
curl http://127.0.0.1:18789/health 2>/dev/null || \
curl http://127.0.0.1:18789/ 2>/dev/null | head -20

# 測試 QClaw 健康狀態
curl http://127.0.0.1:28789/health 2>/dev/null
```

---

## 步驟四：停止 OpenClaw

```bash
# 方式 A：CLI
openclaw gateway stop --port 18789

# 方式 B：launchd
launchctl unload ~/Library/LaunchAgents/ai.openclaw.gateway.plist

# 方式 C：kill by port
lsof -ti :18789 | xargs kill -9
```

---

## 衝突說明與解決方式

### 衝突 1：Port 被占用

**徵兆**：`Error: listen EADDRINUSE :::18789`

**原因**：另一個程式已佔用 18789 port

**解決**：
```bash
# 找出是什麼佔用了 port
lsof -i :18789

# 如果是 QClaw（或另一個 OpenClaw），選擇：
# 1. 換一個 port：openclaw gateway start --port 19898
# 2. 停止佔用的程式
```

### 衝突 2：Config 衝突

**徵兆**：QClaw 的 agent 配置被 OpenClaw 覆蓋

**原因**：兩個 CLI 可能讀取相同的 config 檔案

**解決**：確認各自使用獨立的 config：
```bash
# OpenClaw 專用 config（不影響 QClaw）
export OPENCLAW_CONFIG=~/.openclaw/openclaw.json

# QClaw 使用自己的 config
export QCLAW_CONFIG=~/.qclaw/openclaw.json

# 各自啟動
openclaw gateway start --config ~/.openclaw/openclaw.json
```

### 衝突 3：Model Provider 競爭

**徵兆**：同一個 LLM API key 同時被兩個 Gateway 使用，配額瞬間用完

**解決**：
```json
// ~/.openclaw/openclaw.json 中，只給 OpenClaw 分配部分 key
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "ollama/llama3.2"  // 本地模型，零費用
      }
    }
  }
}
```

### 衝突 4：Workspace 目錄重疊

**徵兆**：兩個 Gateway 寫入同一個 workspace，檔案被覆蓋

**解決**：OpenClaw 使用獨立 workspace：
```json
// ~/.openclaw/openclaw.json
{
  "agents": {
    "defaults": {
      "workspace": "/Users/claw/.openclaw/workspace"
    }
  }
}
```

---

## 推薦的雙開配置

### OpenClaw 專用配置（推薦使用本地 LLM）
```json
// ~/.openclaw/openclaw.json
{
  "gateway": {
    "mode": "local",
    "port": 18789,
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "your-openclaw-token-here"
    }
  },
  "agents": {
    "defaults": {
      "workspace": "/Users/claw/.openclaw/workspace",
      "model": {
        "primary": "ollama/llama3.2"  // 本地模型，QClaw 不干擾
      }
    }
  }
}
```

---

## 常見問題

| 問題 | 解決方式 |
|------|----------|
| 兩個 Gateway 都在跑，分不清哪個回應？ | 查看回應中的 session id 或 agent name |
| 想讓 Subagent 只走 OpenClaw？ | spawn 時指定 node/id |
| OpenClaw 一直重啟？ | 檢查 log：`tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log` |
| Port 18789 無法綁定？ | 先 `lsof -i :18789` 確認無衝突，否則換 port |

---

## 總結

```
QClaw (Port 28789)     ← 主要生產環境
OpenClaw (Port 18789)  ← 實驗/測試/Subagent 任務

兩者完全獨立，通過各自的 config 檔案隔離。
建議 OpenClaw 使用本地 Ollama 模型，避免和 QClaw 爭搶 API 配額。
```

---

_文件日期: 2026-04-10_  
_作者: 碼農 1 號_
