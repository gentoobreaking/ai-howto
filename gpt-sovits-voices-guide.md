# GPT-SoVITS 本地整合包語音庫結構與分類指南

> 研究日期：2026-04-21  
> 來源：本地目錄分析 + 線上社群資源  
> 適用版本：GPT-SoVITS v2 / v2Pro / v2ProPlus / v3

---

## 執行摘要

GPT-SoVITS 本地整合包 (`/Users/claw/Downloads/GPT-SoVITS`) 包含完整的預訓練模型體系，分為 **TTS 核心模型**、**特徵提取模型**、**輔助工具模型** 三大類。本地已安裝 v2final、v2Pro/v2ProPlus、v3 多個版本，總計約 600MB-1.2GB 模型權重。本文檔詳細說明各模型功能、版本差異、以及線上社群語音庫資源。

---

## 一、本地模型目錄結構

```
/Users/claw/Downloads/GPT-SoVITS/
├── GPT_SoVITS/
│   └── pretrained_models/          # 核心預訓練模型
│       ├── chinese-hubert-base/    # 中文語音特徵提取
│       ├── chinese-roberta-wwm-ext-large/  # 中文文本編碼
│       ├── fast_langdetect/        # 語言自動偵測
│       ├── gsv-v2final-pretrained/ # v2 最終版模型
│       │   ├── s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt  (155MB)
│       │   ├── s2D2333k.pth        (89MB)
│       │   └── s2G2333k.pth        (101MB)
│       ├── sv/                     # 說話人驗證模型
│       │   └── pretrained_eres2netv2w24s4ep4.ckpt  (103MB)
│       ├── v2Pro/                  # v2Pro / v2ProPlus
│       │   ├── s2Dv2Pro.pth        (121MB)
│       │   ├── s2Dv2ProPlus.pth    (121MB)
│       │   ├── s2Gv2Pro.pth        (155MB)
│       │   └── s2Gv2ProPlus.pth    (191MB)
│       └── s1v3.ckpt               # v3 版本 s1 模型 (148MB)
├── GPT_SoVITS/BigVGAN/             # NVIDIA BigVGAN 聲碼器
├── GPT_SoVITS/AR/models/           # AR 語言模型
├── GPT_SoVITS/f5_tts/model/        # F5-TTS 模型
├── tools/asr/models/               # ASR 語音辨識模型
├── tools/denoise-model/            # 降噪模型
└── tools/AP_BWE_main/models/       # 頻寬擴展模型
```

---

## 二、核心 TTS 模型版本比較

### 2.1 模型架構說明

GPT-SoVITS 採用 **雙階段架構**：
- **s1 (GPT/AR 模型)**：語言建模，預測 semantic tokens（韻律、停頓、情感）
- **s2 (SoVITS/Vocoder)**：聲音合成，將 semantic tokens 轉換為語音波形

### 2.2 各版本詳細比較

| 版本 | s1 模型 | s2 模型 | 訓練資料 | 音質 | 特色 |
|------|---------|---------|----------|------|------|
| **v2final** | s1bert25hz-5kh-longer | s2G2333k / s2D2333k | 2.5k 小時 | 24kHz | 穩定版，基準音質 |
| **v2Pro** | s1bert25hz-5kh-longer | s2Gv2Pro / s2Dv2Pro | 2.5k 小時 | 24kHz | 音質優化版 |
| **v2ProPlus** | s1bert25hz-5kh-longer | s2Gv2ProPlus / s2Dv2ProPlus | 2.5k 小時 | 24kHz | 最高音質，工程化突破 |
| **v3** | s1v3.ckpt | shortcut-CFM-DiT | 7k 小時 | 24kHz | 音色相似度大幅提升 |
| **v4** | - | - | - | 48kHz | 原生 48kHz，修正金屬雜音 |

### 2.3 版本特性詳解

#### v2final（穩定版）
- **檔案**：`s2G2333k.pth` (101MB) / `s2D2333k.pth` (89MB)
- **適用場景**：一般用途，對音質要求不敏感
- **硬體需求**：6GB VRAM 即可推論
- **特點**：經過充分驗證，社群資源最豐富

#### v2Pro / v2ProPlus（音質優化版）
- **檔案**：
  - v2Pro: `s2Gv2Pro.pth` (155MB) / `s2Dv2Pro.pth` (121MB)
  - v2ProPlus: `s2Gv2ProPlus.pth` (191MB) / `s2Dv2ProPlus.pth` (121MB)
- **適用場景**：高品質語音合成需求
- **硬體需求**：建議 8GB+ VRAM
- **特點**：
  - 獨立權重文件組織架構
  - 針對高音質優化的模型參數
  - v2ProPlus 為目前 v2 系列最高音質版本

#### v3（音色相似度強化版）
- **檔案**：`s1v3.ckpt` (148MB)
- **訓練資料**：7k 小時（MOS 音質過濾、標點停頓校驗）
- **架構變更**：s2 改為 shortcut Conditional Flow Matching Diffusion Transformers (shortcut-CFM-DiT)
- **適用場景**：追求極高音色相似度
- **特點**：
  - 基於參考音訊擴散補全，音色相似度大幅提升
  - 訓練輪數減少，整體訓練時長不變
  - 使用開源 24kHz BigVGANv2 作為聲碼器

#### v4（高取樣率版）
- **音質**：原生 48kHz 輸出
- **修正**：v3 金屬雜音問題
- **適用場景**：專業音訊製作、廣播級品質需求

---

## 三、輔助模型功能分類

### 3.1 特徵提取模型

| 模型 | 路徑 | 功能 | 大小 |
|------|------|------|------|
| **Chinese HuBERT Base** | `chinese-hubert-base/` | 中文語音特徵提取 | ~400MB |
| **Chinese RoBERTa** | `chinese-roberta-wwm-ext-large/` | 中文文本編碼 | ~1.2GB |
| **Fast LangDetect** | `fast_langdetect/` | 語言自動偵測 | ~50MB |
| **ERes2Net** | `sv/pretrained_eres2netv2w24s4ep4.ckpt` | 說話人驗證 | 103MB |

### 3.2 聲碼器與合成模型

| 模型 | 路徑 | 功能 |
|------|------|------|
| **BigVGAN** | `BigVGAN/` | NVIDIA 開源聲碼器，將 Mel 譜轉換為波形 |
| **F5-TTS** | `f5_tts/model/` | 額外 TTS 模型選項 |

### 3.3 工具鏈模型

| 工具 | 路徑 | 功能 |
|------|------|------|
| **ASR 模型** | `tools/asr/models/` | 自動語音辨識（FunASR / Faster-Whisper） |
| **降噪模型** | `tools/denoise-model/` | 音訊降噪處理 |
| **頻寬擴展** | `tools/AP_BWE_main/models/` | 音訊頻寬擴展 |
| **UVR5** | `tools/uvr5/` | 人聲伴奏分離 |

---

## 四、線上語音庫資源

### 4.1 ModelScope（魔搭社群）

ModelScope 是阿里雲推出的模型社群平台，有豐富的 GPT-SoVITS 相關資源：

**搜尋關鍵字**：`GPT-SoVITS`、`TTS`、`語音合成`

**常見資源類型**：
- 預訓練基座模型
- 微調後的角色語音模型
- 特定說話人音色模型
- 多語言支援模型

### 4.2 HuggingFace

**官方資源**：
- `RVC-Boss/GPT-SoVITS` - 官方倉庫

**社群貢獻**：
- 各類角色語音模型（動漫、遊戲、VTuber）
- 特定領域語音（新聞播報、有聲書、客服）
- 多語言擴展模型

### 4.3 Bilibili / 嗶哩嗶哩

許多創作者分享訓練好的語音模型：
- 搜尋：`GPT-SoVITS 模型分享`、`AI 語音模型`
- 常見分享形式：百度網盤、夸克網盤、123雲盤
- ⚠️ **注意**：社群分享的模型通常禁止商用，使用前請確認授權

### 4.4 常見語音庫分類

| 類型 | 說明 | 來源 |
|------|------|------|
| **動漫角色** | 二次元角色語音 | 社群訓練分享 |
| **VTuber** | 虛擬主播語音 | 粉絲訓練模型 |
| **遊戲角色** | 電玩角色語音 | 遊戲社群 |
| **名人聲音** | 明星、政治家等 | ⚠️ 法律風險高 |
| **專業播音** | 新聞、有聲書風格 | 開放資料集 |
| **方言/外語** | 粵語、日語、韓語等 | 多語言擴展 |

---

## 五、使用建議與最佳實踐

### 5.1 版本選擇建議

| 使用場景 | 推薦版本 | 原因 |
|----------|----------|------|
| 快速體驗 / 測試 | v2final | 穩定、資源多 |
| 一般品質需求 | v2Pro | 音質較好 |
| 高品質輸出 | v2ProPlus | 最佳音質 |
| 追求音色相似度 | v3 | 相似度最高 |
| 專業音訊製作 | v4 | 48kHz 輸出 |

### 5.2 硬體配置建議

| 用途 | 最低配置 | 建議配置 |
|------|----------|----------|
| **推論** | GTX 1060 6GB | RTX 3060 12GB |
| **訓練** | RTX 3060 12GB | RTX 4060 Ti 16GB |
| **高品質訓練** | RTX 4060 Ti 16GB | RTX 4090 24GB |

### 5.3 模型載入與切換

**WebUI 操作**：
1. 啟動 `go-webui.bat`（Windows）或 `python webui.py`（Linux/macOS）
2. 在「模型選擇」區塊選擇 s1 和 s2 權重檔
3. 點擊「加載模型」

**權重檔路徑對應**：
- s1 權重：`pretrained_models/` 下的 `.ckpt` 檔
- s2 權重：`pretrained_models/v2Pro/` 或 `gsv-v2final-pretrained/` 下的 `.pth` 檔

### 5.4 自訂語音庫訓練流程

```
1. 錄製訓練音訊（1-5 分鐘乾聲）
   ↓
2. 人聲分離（UVR5 - HP2/HP5 模型）
   ↓
3. 語音切割（自動分割為 3-10 秒片段）
   ↓
4. 降噪處理（denoise-model）
   ↓
5. ASR 自動標註（FunASR / Faster-Whisper）
   ↓
6. 人工校正標註檔
   ↓
7. 載入訓練集，選擇基礎模型
   ↓
8. 訓練（s1 和 s2 分開訓練）
   ↓
9. 推理測試，微調參數
```

### 5.5 注意事項

⚠️ **法律風險**：
- 使用他人聲音需取得明確授權
- 公眾人物聲音風險較高
- 社群分享模型通常禁止商用

⚠️ **技術限制**：
- 目前輸出為 24kHz（v4 為 48kHz），非 CD 音質 44.1kHz
- 跨語言合成品質因語言而異
- 訓練資料品質直接影響輸出效果

---

## 六、本地模型檔案清單

以下為 `/Users/claw/Downloads/GPT-SoVITS` 中已安裝的模型檔案：

### TTS 核心模型（~900MB）

| 檔案 | 大小 | 版本 | 用途 |
|------|------|------|------|
| s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt | 148 MB | v2 | s1 語言模型 |
| s2G2333k.pth | 89 MB | v2final | s2 生成器 |
| s2D2333k.pth | 89 MB | v2final | s2 判別器 |
| s2Gv2Pro.pth | 121 MB | v2Pro | s2 生成器（Pro） |
| s2Dv2Pro.pth | 121 MB | v2Pro | s2 判別器（Pro） |
| s2Gv2ProPlus.pth | 191 MB | v2ProPlus | s2 生成器（ProPlus） |
| s2Dv2ProPlus.pth | 121 MB | v2ProPlus | s2 判別器（ProPlus） |
| s1v3.ckpt | 148 MB | v3 | s1 語言模型（v3） |

### 輔助模型（~1.8GB）

| 檔案/目錄 | 大小 | 用途 |
|-----------|------|------|
| chinese-hubert-base/ | ~400 MB | 語音特徵提取 |
| chinese-roberta-wwm-ext-large/ | ~1.2 GB | 文本編碼 |
| fast_langdetect/ | ~50 MB | 語言偵測 |
| pretrained_eres2netv2w24s4ep4.ckpt | 103 MB | 說話人驗證 |

---

## 附錄：參考資源

1. **官方 GitHub**：https://github.com/RVC-Boss/GPT-SoVITS
2. **ModelScope**：https://www.modelscope.cn
3. **HuggingFace**：https://huggingface.co
4. **CSDN 教學**：搜尋「GPT-SoVITS 教程」
5. **Bilibili**：搜尋「GPT-SoVITS 模型分享」

---

*報告完成於 2026-04-21*
