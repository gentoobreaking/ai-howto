# pi — 語音溝通方案

> 建立日期：2026-08-24
> 用途：與 pi agent 用語音互動的可行做法，由淺到深

---

## 做法 1：macOS 內建聽寫（零成本，先試這個）

系統設定 → 鍵盤 → 聽寫 → 開啟，然後在 pi 的 TUI 輸入框**按 F5／🎤（麥克風）鍵**開始講話，文字會直接打進終端機。

> 註：新版 macOS（Sonoma 以後）預設快捷鍵是 **F5／麥克風鍵**；舊版才是按兩下 Fn 鍵。可在「系統設定 → 鍵盤 → 聽寫 → 快捷鍵」自訂。

- ✅ 最快上手、任何 App 通用
- ❌ 中文工程詞彙（TUI、frontmatter、commit）辨識率普通

## 做法 2：本地 Whisper 語音輸入工具（推薦日常使用）

裝一套「按熱鍵講話 → Whisper 轉字 → 自動貼上」的工具：

- **Superwhisper / MacWhisper / VoiceInk**（GUI）或 Hammerspoon 自己綁
- 可跑**本地 whisper large-v3**（Apple Silicon 適用；本機已有 `transcribe` skill 用同款技術棧，模型可共用）、完全離線、中文＋技術名詞準確度高
- 轉出的文字直接落在 pi 輸入框，體驗就像打字

## 做法 3：語音指令直送 pi headless（一問一答式）

寫個小 wrapper：

```
🎤 錄音（sox/ffmpeg）→ whisper 轉字 → pi -p "<轉出的指令>" → 🔊 say 回覆結果
```

- 適合「執行 tw-quant-pickup 專案」這類**一句話觸發**的場景
- 配合已建好的 `run-project` skill 很搭：喊一句就開工，做完 `say "修復任務都完成了"` 回報——整條鏈已經通了
- 不適合需要看著畫面追問的長互動

## 做法 4：完整語音對話介面（進階）

用 pi 的 **SDK**（`docs/sdk.md`）以程式方式驅動 agent，外面包一個常駐 loop：

VAD 偵測說話 → STT → pi SDK 執行 → TTS 念回覆

- 等於自製一支語音助理，pi 是後端大腦
- 工程量最大，除非想要「不用開終端機」的體驗，否則 CP 值不如做法 2+3

---

## 建議路線

1. 先做法 1 試水溫
2. 不滿意就上做法 2（本地 Whisper 熱鍵工具）
3. 「喊一句讓它自己跑完任務」的需求，加上做法 3 的 wrapper 即完整

---

## 相關檔案

- `~/notes/pi.md` — run-project skill 設定說明
- `~/.pi/agent/skills/run-project/SKILL.md` — 任務自動執行 skill（含異常語音通報）
