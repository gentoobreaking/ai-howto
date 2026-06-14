# GPT-SoVITS 技術與授權研究報告

**研究日期**：2026-04-21  
**研究員**：研研  
**來源**：GitHub 官方 repo、LICENSE、README、ElevenLabs 官網

---

## 執行摘要

GPT-SoVITS 是開源的 few-shot 語音合成（TTS）系統，只需 5 秒音檔即可 zero-shot 推論，1 分鐘訓練資料即可 fine-tune。採用 **MIT License**，允許任意商業使用、修改、分發，無專利限制。技術上結合 GPT 語言模型與 SoVITS 聲音合成模型，支援中英日韓粵五語言，跨語言推理能力強。與 ElevenLabs 相比，GPT-SoVITS 完全免費、可本地部署、資料不出本地，但需自備 GPU 且技術門檻較高。

---

## 一、技術架構

### 1.1 核心概念：GPT + SoVITS

**GPT-SoVITS** 名稱來自兩個核心元件：

| 元件 | 功能 | 技術基礎 |
|------|------|----------|
| **GPT** | 語言建模、韻律預測 | 類 SoundStorm 的 AR 模型，預測 semantic tokens |
| **SoVITS** | 聲音合成（Vocoder） | 基於 VITS/So-VITS-SVC 的聲學模型 |

**運作流程**：
1. 文字 → GPT 模型 → 預測 semantic tokens（韻律、停頓、情感）
2. Semantic tokens + 參考音檔 → SoVITS → 合成目標語音

### 1.2 Few-shot 語音克隆機制

| 模式 | 所需資料 | 用途 |
|------|----------|------|
| **Zero-shot** | 5 秒參考音檔 | 即時推理，無需訓練 |
| **Few-shot** | 1 分鐘訓練資料 | Fine-tune 提升相似度與自然度 |

**關鍵技術**：
- 使用 **ContentVec** 提取聲音特徵
- 預訓練模型基於 5000+ 小時多語言語料
- 支援 **跨語言推理**（用中文資料訓練，推理英文/日文）

### 1.3 版本演進

| 版本 | 特性 | 推薦場景 |
|------|------|----------|
| **v1/v2** | 穩定、對音質要求不敏感 | 一般用途 |
| **v3** | 音色相似度更高、情感更豐富 | 高品質需求 |
| **v4** | 原生 48kHz 輸出，修正 v3 金屬雜音 | 最高品質 |
| **v2Pro/v2ProPlus** | 效能超越 v4，硬體成本接近 v2 | 效能優先 |

### 1.4 推論速度（RTF）

| 硬體 | RTF | 說明 |
|------|-----|------|
| RTX 4060 Ti | 0.028 | 1400 字約 3.36 秒 |
| RTX 4090 | 0.014 | 極快 |
| M4 CPU | 0.526 | 可用但較慢 |

---

## 二、授權與法律條款 ⭐最重要

### 2.1 LICENSE 全文

```
MIT License

Copyright (c) 2024 RVC-Boss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 2.2 授權解讀

| 權利 | 狀態 | 說明 |
|------|------|------|
| **商業使用** | ✅ 允許 | MIT 明確允許 sell、sublicense |
| **修改** | ✅ 允許 | 無限制 |
| **分發** | ✅ 允許 | 需保留版權聲明 |
| **專利授權** | ✅ 隱含 | MIT 包含隱含專利授權 |
| **閉源使用** | ✅ 允許 | 可整合至閉源產品，僅需保留聲明 |

### 2.3 法律風險評估

**低風險**：
- MIT 是最寬鬆的開源授權之一
- 無 copyleft（GPL 的傳染性），不強迫開源衍生作品
- 無專利聲明或額外限制條款

**注意事項**：
- 需在衍生作品中保留原始 LICENSE 文件
- 使用他人聲音需取得授權（這是法律問題，非授權問題）
- 模型權重可能受不同授權規範（需確認預訓練模型來源）

### 2.4 預訓練模型授權

專案引用的預訓練模型來源多元：
- **BigVGAN**（NVIDIA）- MIT 授權
- **Chinese-Roberta** - Apache 2.0
- **FunASR**（阿里）- MIT 授權
- **Faster-Whisper** - MIT 授權

**結論**：整體依賴鏈無授權衝突，可安心商用。

---

## 三、安裝與使用門檻

### 3.1 硬體需求

| 項目 | 最低需求 | 建議配置 |
|------|----------|----------|
| **GPU** | GTX 1060 6GB | RTX 3060 12GB+ |
| **VRAM** | 6GB（推論） | 12GB+（訓練） |
| **RAM** | 16GB | 32GB |
| **儲存** | 20GB | 50GB+（含模型） |

**支援平台**：
- Windows 10+（整合包，雙擊啟動）
- Linux（CUDA 12.6/12.8、ROCm）
- macOS（Apple Silicon / CPU，訓練品質較差）
- Docker

### 3.2 安裝難度

| 方式 | 難度 | 說明 |
|------|------|------|
| **Windows 整合包** | ⭐ 簡單 | 下載 .7z，雙擊 go-webui.bat |
| **Docker** | ⭐⭐ 中等 | docker compose run |
| **手動安裝** | ⭐⭐⭐ 較難 | conda + pip + ffmpeg 配置 |

### 3.3 技術門檻

| 能力 | 是否需要 | 說明 |
|------|----------|------|
| 機器學習背景 | ❌ 不需要 | WebUI 完整封裝 |
| Python 基礎 | ⭐ 可選 | 除錯時有用 |
| 命令列操作 | ⭐⭐ 基本 | 需執行安裝腳本 |
| 音訊處理知識 | ⭐ 可選 | 幫助理解參數 |

**WebUI 功能**：
- 音訊切片（自動分割訓練集）
- 人聲分離（UVR5）
- ASR 轉錄（中文 FunASR、英文/日文 Faster-Whisper）
- 一鍵訓練 + 推理

---

## 四、與 ElevenLabs 比較

### 4.1 技術比較

| 項目 | GPT-SoVITS | ElevenLabs |
|------|------------|------------|
| **部署方式** | 本地 / 雲端 | 僅雲端 API |
| **資料隱私** | 完全本地 | 上傳至 ElevenLabs |
| **訓練資料** | 1 分鐘 | 專業克隆需數分鐘高品質音檔 |
| **跨語言** | ✅ 5 語言 | ✅ 29 語言 |
| **音質** | 24-48kHz | 44.1kHz，最高 192kbps |
| **推論速度** | RTF 0.014-0.526 | API 延遲約 200-500ms |
| **情感控制** | 基本 | 進階（穩定度、相似度、風格） |

### 4.2 授權與商業使用

| 項目 | GPT-SoVITS | ElevenLabs |
|------|------------|------------|
| **授權類型** | MIT（開源） | 商業服務條款 |
| **免費商用** | ✅ 完全免費 | ❌ 需付費（$6/月起） |
| **商用授權** | 自動取得 | 需訂閱 Starter 以上方案 |
| **輸出所有權** | 完全歸用戶 | 用戶保留，但 ElevenLabs 有使用授權 |
| **資料使用** | 不上傳 | 可選擇退出訓練 |

### 4.3 成本比較

| 方案 | GPT-SoVITS | ElevenLabs |
|------|------------|------------|
| **免費** | 全功能 | 10k credits/月，僅非商用 |
| **入門** | GPU 電費 | $6/月（30k credits） |
| **專業** | 持續免費 | $22/月（121k credits） |
| **企業** | 自建成本 | $99-990/月 |

### 4.4 適用場景

| 場景 | 推薦 | 原因 |
|------|------|------|
| **個人創作、研究** | GPT-SoVITS | 免費、可控、可定制 |
| **隱私敏感應用** | GPT-SoVITS | 資料不出本地 |
| **快速原型** | ElevenLabs | API 即用，無需部署 |
| **企業級服務** | ElevenLabs | SLA、支援、合規 |
| **大量生產** | GPT-SoVITS | 無用量限制 |
| **多語言內容** | ElevenLabs | 支援 29 語言 |

---

## 五、結論與建議

### 5.1 核心結論

1. **授權無虞**：MIT License 允許任意商業使用，無專利限制，適合整合至商業產品。

2. **技術成熟**：v2ProPlus 版本在效能與品質間取得平衡，推論速度達 RTF 0.014（RTX 4090）。

3. **門檻適中**：Windows 整合包讓非技術人員也能使用，但訓練調參仍需一定學習。

4. **隱私優勢**：本地部署確保語音資料不出本地，適合隱私敏感場景。

### 5.2 使用建議

**選擇 GPT-SoVITS 當**：
- 需要商業使用但不想付費
- 語音資料敏感（醫療、法律、個人）
- 需要大量生成（無 API 限制）
- 願意投入時間學習與部署

**選擇 ElevenLabs 當**：
- 需要快速上線，無維運能力
- 需要多語言支援（超出 5 語言）
- 企業合規需求（SLA、審計）
- 預算充足且追求極致品質

### 5.3 法律合規提醒

⚠️ **重要**：無論使用何種工具，使用他人聲音需取得明確授權。這是法律問題，與軟體授權無關。

- 公眾人物聲音：需取得本人或經紀公司授權
- 一般人聲音：需取得當事人書面同意
- 已故人物聲音：需確認遺產權利歸屬

---

## 附錄：參考來源

1. GPT-SoVITS GitHub：https://github.com/RVC-Boss/GPT-SoVITS
2. LICENSE：https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/LICENSE
3. README：https://raw.githubusercontent.com/RVC-Boss/GPT-SoVITS/main/README.md
4. ElevenLabs Pricing：https://elevenlabs.io/pricing
5. ElevenLabs Terms：https://elevenlabs.io/terms-of-use

---

*報告完成於 2026-04-21*
