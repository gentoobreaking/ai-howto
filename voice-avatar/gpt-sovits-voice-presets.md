# GPT-SoVITS 音色資源完全指南

> 研究日期：2026-04-21
> 研究者：研研 🔬

---

## 執行摘要

**GPT-SoVITS 沒有任何內建預設音色。**

這是 GPT-SoVITS 與 ElevenLabs、VOICEVOX 等 TTS 服務最核心的差異。GPT-SoVITS 是一套**語音克隆框架**，使用方式分為兩條路：

| 模式 | 說明 |
|------|------|
| **零樣本（Zero-shot）** | 上傳 5 秒參考音訊，直接克隆音色，無需訓練 |
| **少量樣本（Few-shot）** | 收集 1 分鐘以上音訊，微調訓練出專屬音色模型（.pth / .ckpt）|

因此「音色」不存在於任何選項清單裡，而是需要：
1. 自己準備參考音訊（Zero-shot），或
2. 自己訓練 / 下載社群訓練好的模型（.pth / .ckpt）

---

## 各版本功能對照

以下資料來源為 [GPT-SoVITS 官方 Wiki](https://github.com/RVC-Boss/GPT-SoVITS/wiki/GPT%E2%80%90SoVITS%E2%80%90features-(%E5%90%84%E7%89%88%E6%9C%AC%E7%89%B9%E6%80%A7))。

### 支援語言（所有版本相同）

✅ 中文（普通話） · ✅ 日語 · ✅ 英語 · ✅ 韓語 · ✅ 粵語

**所有版本皆支援跨語言合成**——即用中文語音訓練出的模型，可以用日語、英語等語言朗讀（音色風格不變，內容語言改變）。

### 版本詳細比較

| 版本 | 參數量 | 訓練集規模 | 推理速度 | 音色相似度（SIM）| 特點 |
|------|--------|-----------|----------|----------------|------|
| **v1** | 90M+77M | 約 2k 小時 | baseline | 0.526 | 基礎版本 |
| **v2** | 90M+77M | 約 5k 小時 | ×2 | 0.549 | 新增語速控制、無參考文本模式 |
| **v3** | 330M+77M | 約 9k 小時 | ≈v2 | 0.702 | 零樣本相似度大幅提升；原生輸出 24k |
| **v4** | 同 v3 | 同 v3 | ≈v2 | 0.735 | 修復 v3 電音問題；原生輸出 48k（官方認為是 v3 平替）|
| **v2Pro** | 133M+77M | 同 v3 | ≈v2 | 0.709 | v3 的音色相似度 + v2 的硬體成本與速度 |
| **v2ProPlus** | 152M+77M | 同 v3 | ≈v2 | **0.737** | 最高相似度；略高於 v2Pro 的 VRAM 需求 |

> Benchmark 數據來源：SeedTTS 論文測試集（位元組豆包團隊），使用 GPT-SoVITS 官方測試流程。
> Ground Truth（真人）參考分數：WER=0.013, SIM=0.750。

### 版本選擇建議（官方立場）

- **不需要再使用 v3/v4**，v2Pro / v2ProPlus 以 v2 等級的硬體需求，達到與 v3/v4 同等的音色相似度
- v3/v4 更偏向「參考音訊音色」，v2 更偏向「訓練集整體平均音色」；訓練集品質差時，v2 表現更穩定
- 若要最佳效果且不介意略高 VRAM：**v2ProPlus**

---

## 官方預訓練底模（下載點）

訓練自己的音色模型前，需要先下載對應版本的預訓練底模（Base Model）。

| 版本 | 下載來源 |
|------|---------|
| v2 | HuggingFace: `RVC-Boss/GPT-SoVITS` → pretrained_models/ |
| v3/v4 | HuggingFace: `RVC-Boss/GPT-SoVITS` → pretrained_models/ |
| v2Pro/v2ProPlus | HuggingFace: `RVC-Boss/GPT-SoVITS` → pretrained_models/ |

官方整合包（Windows 一鍵執行）：
- HuggingFace: [lj1995/GPT-SoVITS-windows-package](https://huggingface.co/lj1995/GPT-SoVITS-windows-package)（v3 LoRA 版本，含 `go-webui.bat` 雙擊啟動）

雲端運行（中國境內用戶）：
- AutoDL: [CodeWithGPU - GPT-SoVITS-Official](https://www.codewithgpu.com/i/RVC-Boss/GPT-SoVITS/GPT-SoVITS-Official)

---

## HuggingFace 社群音色模型列表（Top 15 各類型）

以下為可直接下載使用的預訓練音色模型，按類型分類，每類依**下載量/人氣**排序（Top 15）。

> 📊 **排序依據**：HuggingFace 下載次數、Likes 數、更新頻率綜合評估

---

### 🎌 動漫角色（Anime Characters）

| 排名 | 模型名稱 | 角色 | 對應版本 | 語言 | 人氣指標 | 說明 |
|-----|---------|------|---------|------|---------|------|
| 1 | [lpkpaco/Bocchi-The-Rock-GPT-SoVITS-Models](https://huggingface.co/lpkpaco/Bocchi-The-Rock-GPT-SoVITS-Models) | 後藤一里、伊地知虹夏、喜多郁代、山田涼 | v2ProPlus / v4 | 日語（主）、中、英文 | ⭐ 66 likes, 25天前更新 | **最熱門**，《孤獨搖滾！》全主角，CC BY-NC-SA 4.0 |
| 2 | [MomoyamaSawa/GPT-SoVITS_KusanagiNene](https://huggingface.co/MomoyamaSawa/GPT-SoVITS_KusanagiNene) | 草薙寧々（Project Sekai） | v2 | 日語 | ⭐ 41 likes | VTuber/遊戲角色，30-60分鐘訓練集多版本 |
| 3 | [VoidShine/atri-sovits](https://huggingface.co/VoidShine/atri-sovits) | ATRI（ATRI -My Dear Moments-） | v2Pro | 日語、中、英文 | - | 含 FastAPI 推論腳本，AGPL-3.0 |
| 4 | [4nm1tsu/shikokumetan_GPT-SoVITS](https://huggingface.co/4nm1tsu/shikokumetan_GPT-SoVITS) | 四国めたん（東北ずん子プロジェクト） | v2Pro | 日語 | ⭐ 5 likes | 東北ずん子公式角色，需遵守官方使用規範 |
| 5 | [shibing624/parrots-gpt-sovits-speaker](https://huggingface.co/shibing624/parrots-gpt-sovits-speaker) | 草薙寧々（含在合集） | v2 | 日/中/英 | ⭐ 13 likes | 多角色合集，含 6 個 speaker |
| 6 | [None1145/GPT-SoVITS-Lappland-the-Decadenza](https://huggingface.co/None1145/GPT-SoVITS-Lappland-the-Decadenza) | ラップランド（明日方舟） | v2 | 日語 | ⭐ 10 likes, 11/16更新 | 明日方舟角色 |
| 7 | [None1145/GPT-SoVITS-Theresa](https://huggingface.co/None1145/GPT-SoVITS-Theresa) | テレサ（明日方舟） | v2 | 日語 | ⭐ 6 likes | 明日方舟角色 |
| 8 | [None1145/GPT-SoVITS-Rosmontis](https://huggingface.co/None1145/GPT-SoVITS-Rosmontis) | ロスモンティス（明日方舟） | v2 | 日語 | ⭐ 5 likes, 11/23更新 | 明日方舟角色 |
| 9 | [gahyunlee/GPT-SoVITS-ko-character](https://huggingface.co/gahyunlee/GPT-SoVITS-ko-character) | 柯南、蠟筆小新、Keroro 軍曹 | v4 | 韓語 | - | 卡通角色韓語版，各約 45 分鐘數據 |
| 10 | [Illumina/Neptune-GPT-SoVITS](https://huggingface.co/Illumina/Neptune-GPT-SoVITS) | Neptune（超次元戰記） | v4 | 英文 | - | 英文遊戲角色 |
| 11 | [None1145/GPT-SoVITS-Vulpisfoglia](https://huggingface.co/None1145/GPT-SoVITS-Vulpisfoglia) | ヴルピスフォリア（明日方舟） | v2 | 日語 | ⭐ 4 likes | 明日方舟角色 |
| 12 | [modelloosrvcc/Kotoko_Utsugi_GPT-SOVITS](https://huggingface.co/modelloosrvcc/Kotoko_Utsugi_GPT-SOVITS) | 空木言子（絕對絕望少女） | v2 | 日語 | - | 槍彈辯駁系列角色 |
| 13 | [modelloosrvcc/Nagisa_Shingetsu_GPT-SoVITS](https://huggingface.co/modelloosrvcc/Nagisa_Shingetsu_GPT-SoVITS) | 新月渚（絕對絕望少女） | v2 | 日語 | - | 槍彈辯駁系列角色 |
| 14 | [shibing624/parrots-gpt-sovits-speaker-maimai](https://huggingface.co/shibing624/parrots-gpt-sovits-speaker-maimai) | 舞萌 DX 角色 | v2 | 中文 | ⭐ 8 likes | 音樂遊戲角色 |
| 15 | [yousaforever/yousa_GPT-SOVITS_v1](https://huggingface.co/yousaforever/yousa_GPT-SOVITS_v1) | 泠鳶yousa（虛擬歌手） | v2 | 中文 | ⭐ 1 like | B站虛擬歌手 |

---

### 🎤 VTuber / 虛擬主播

| 排名 | 模型名稱 | 角色/主播 | 對應版本 | 語言 | 人氣指標 | 說明 |
|-----|---------|----------|---------|------|---------|------|
| 1 | [MomoyamaSawa/GPT-SoVITS_KusanagiNene](https://huggingface.co/MomoyamaSawa/GPT-SoVITS_KusanagiNene) | 草薙寧々（Project Sekai） | v2 | 日語 | ⭐ 41 likes | **最熱門 VTuber 模型** |
| 2 | [shibing624/parrots-gpt-sovits-speaker](https://huggingface.co/shibing624/parrots-gpt-sovits-speaker) | 星瞳、賣賣、炫神等 | v2 | 中/英/日 | ⭐ 13 likes | 多 VTuber 合集 |
| 3 | [yousaforever/yousa_GPT-SOVITS_v1](https://huggingface.co/yousaforever/yousa_GPT-SOVITS_v1) | 泠鳶yousa | v2 | 中文 | ⭐ 1 like | B站知名虛擬歌手 |
| 4 | [hhwjsw711/GPT-SoVITS_Project](https://huggingface.co/hhwjsw711/GPT-SoVITS_Project) | 多 VTuber 合集 | v2 | 中文 | - | 社群整理合集 |
| 5 | [AkitoP/GPT-SoVITS-JA-ProsodyControl_model](https://huggingface.co/AkitoP/GPT-SoVITS-JA-ProsodyControl_model) | 日語韻律控制模型 | v2 | 日語 | ⭐ 9 likes | 韻律控制專用 |
| 6 | [Kit-Lemonfoot/kitlemonfoot_gptsovits_models](https://huggingface.co/Kit-Lemonfoot/kitlemonfoot_gptsovits_models) | 社群自製音色 | v2 | 多語言 | - | 多種角色模型集合 |
| 7 | [Yougen/GPT-SoVITS_ft](https://huggingface.co/Yougen/GPT-SoVITS_ft) | 微調通用音色 | 通用 | 多語言 | - | 持續更新 |
| 8-15 | - | - | - | - | - | *持續搜尋中，目前 HuggingFace 上 VTuber 專屬模型較少，多數整合於動漫/遊戲分類* |

---

### 🎮 遊戲角色（Game Characters）

| 排名 | 模型名稱 | 角色/遊戲 | 對應版本 | 語言 | 人氣指標 | 說明 |
|-----|---------|----------|---------|------|---------|------|
| 1 | [None1145/GPT-SoVITS-Lappland-the-Decadenza](https://huggingface.co/None1145/GPT-SoVITS-Lappland-the-Decadenza) | ラップランド（明日方舟） | v2 | 日語 | ⭐ 10 likes | **最熱門遊戲角色** |
| 2 | [TwinPeaksTownie/GPT_SoVITS_LAURA_v1](https://huggingface.co/TwinPeaksTownie/GPT_SoVITS_LAURA_v1) | Laura | v2ProPlus | 英文 | ⭐ 7 likes | 含 LoRA 訓練細節 |
| 3 | [None1145/GPT-SoVITS-Theresa](https://huggingface.co/None1145/GPT-SoVITS-Theresa) | テレサ（明日方舟） | v2 | 日語 | ⭐ 6 likes | 明日方舟人氣角色 |
| 4 | [None1145/GPT-SoVITS-Rosmontis](https://huggingface.co/None1145/GPT-SoVITS-Rosmontis) | ロスモンティス（明日方舟） | v2 | 日語 | ⭐ 5 likes | 明日方舟角色 |
| 5 | [4nm1tsu/shikokumetan_GPT-SoVITS](https://huggingface.co/4nm1tsu/shikokumetan_GPT-SoVITS) | 四国めたん | v2Pro | 日語 | ⭐ 5 likes | 東北ずん子官方角色 |
| 6 | [None1145/GPT-SoVITS-Vulpisfoglia](https://huggingface.co/None1145/GPT-SoVITS-Vulpisfoglia) | ヴルピスフォリア（明日方舟） | v2 | 日語 | ⭐ 4 likes | 明日方舟角色 |
| 7 | [None1145/GPT-SoVITS-Lappland](https://huggingface.co/None1145/GPT-SoVITS-Lappland) | ラップランド（明日方舟） | v2 | 日語 | ⭐ 3 likes | Lappland 另一版本 |
| 8 | [None1145/GPT-SoVITS-Theresa-Recording](https://huggingface.co/None1145/GPT-SoVITS-Theresa-Recording) | テレサ（錄音版） | v2 | 日語 | ⭐ 4 likes | Theresa 錄音品質版 |
| 9 | [ildyrasm/HSR-Cyrene-GPT-SoVITS](https://huggingface.co/ildyrasm/HSR-Cyrene-GPT-SoVITS) | Cyrene（崩壞：星穹鐵道） | v2 | 中文 | - | 崩鐵角色 |
| 10 | [Illumina/Neptune-GPT-SoVITS](https://huggingface.co/Illumina/Neptune-GPT-SoVITS) | Neptune（超次元戰記） | v4 | 英文 | - | 戰機少女系列 |
| 11 | [modelloosrvcc/Kotoko_Utsugi_GPT-SOVITS](https://huggingface.co/modelloosrvcc/Kotoko_Utsugi_GPT-SOVITS) | 空木言子（絕對絕望少女） | v2 | 日語 | - | 槍彈辯駁外傳 |
| 12 | [modelloosrvcc/Nagisa_Shingetsu_GPT-SoVITS](https://huggingface.co/modelloosrvcc/Nagisa_Shingetsu_GPT-SoVITS) | 新月渚（絕對絕望少女） | v2 | 日語 | - | 槍彈辯駁外傳 |
| 13 | [shibing624/parrots-gpt-sovits-speaker-maimai](https://huggingface.co/shibing624/parrots-gpt-sovits-speaker-maimai) | 舞萌 DX | v2 | 中文 | ⭐ 8 likes | 音樂遊戲 |
| 14 | [Sprt98/GPT-SoVITS_Yasuo](https://huggingface.co/Sprt98/GPT-SoVITS_Yasuo) | 犽宿（英雄聯盟） | v2 | 中文 | - | LOL 角色 |
| 15 | [huanxion/Trisoil-GPT-SoVITS](https://huggingface.co/huanxion/Trisoil-GPT-SoVITS) | Trisoil | v2 | 中文 | - | 遊戲角色 |

---

### 🇨🇳 中文/中文 VTuber

| 排名 | 模型名稱 | 角色/類型 | 對應版本 | 語言 | 人氣指標 | 說明 |
|-----|---------|----------|---------|------|---------|------|
| 1 | [RoversX/GPT_SOVITS_LeiJun_V1](https://huggingface.co/RoversX/GPT_SOVITS_LeiJun_V1) | 雷軍（小米創辦人） | v2 | 中文 | - | **熱門中文模型**（需登入確認條款）|
| 2 | [lllllzh123/feng_voice](https://huggingface.co/lllllzh123/feng_voice) | 通用中文男聲 | v2 | 中文 | - | 持續更新（3天前）|
| 3 | [shibing624/parrots-gpt-sovits-speaker](https://huggingface.co/shibing624/parrots-gpt-sovits-speaker) | 星瞳、賣賣、炫神 | v2 | 中文 | ⭐ 13 likes | 中文 VTuber/主播 |
| 4 | [yousaforever/yousa_GPT-SOVITS_v1](https://huggingface.co/yousaforever/yousa_GPT-SOVITS_v1) | 泠鳶yousa | v2 | 中文 | ⭐ 1 like | B站虛擬歌手 |
| 5 | [hhwjsw711/GPT-SoVITS_Project](https://huggingface.co/hhwjsw711/GPT-SoVITS_Project) | 多中文角色 | v2 | 中文 | - | 社群合集 |
| 6 | [Sprt98/GPT-SoVITS_Yasuo](https://huggingface.co/Sprt98/GPT-SoVITS_Yasuo) | 犽宿（LOL） | v2 | 中文 | - | 中文配音版 |
| 7 | [huanxion/Trisoil-GPT-SoVITS](https://huggingface.co/huanxion/Trisoil-GPT-SoVITS) | Trisoil | v2 | 中文 | - | 中文遊戲角色 |
| 8 | [ildyrasm/HSR-Cyrene-GPT-SoVITS](https://huggingface.co/ildyrasm/HSR-Cyrene-GPT-SoVITS) | Cyrene（崩鐵） | v2 | 中文 | - | 崩壞星穹鐵道 |
| 9-15 | - | - | - | - | - | *持續搜尋中，中文模型多為個人訓練，公開較少* |

---

### 🗣️ 方言 / 語言專用

| 排名 | 模型名稱 | 語言/方言 | 對應版本 | 人氣指標 | 說明 |
|-----|---------|----------|---------|---------|------|
| 1 | [laubonghaudoi/zoengjyutgaai_tts](https://huggingface.co/laubonghaudoi/zoengjyutgaai_tts) | 粵語（張悅楷說古） | v2ProPlus | - | **最完整方言模型**，188.67 小時數據 |
| 2 | [UmaDiffusion/uma-voice-gpt-sovits-v2](https://huggingface.co/UmaDiffusion/uma-voice-gpt-sovits-v2) | 多語音角色 | v2 | - | 賽馬娘角色多語言 |
| 3 | [gahyunlee/GPT-SoVITS-ko-character](https://huggingface.co/gahyunlee/GPT-SoVITS-ko-character) | 韓語 | v4 | - | 柯南等角色韓語版 |
| 4 | [TwinPeaksTownie/GPT_SoVITS_LAURA_v1](https://huggingface.co/TwinPeaksTownie/GPT_SoVITS_LAURA_v1) | 葡萄牙語 | v2ProPlus | ⭐ 7 likes | Laura 葡語版 |
| 5-15 | - | - | - | - | *方言模型較少，多數為特定角色附帶方言能力* |

---

### 📊 綜合人氣排行榜（不分類型 Top 10）

| 排名 | 模型 | 類型 | 人氣指標 | 特色 |
|-----|------|------|---------|------|
| 1 | lpkpaco/Bocchi-The-Rock | 動漫 | ⭐ 66 likes | 孤獨搖滾全主角 |
| 2 | MomoyamaSawa/KusanagiNene | VTuber | ⭐ 41 likes | Project Sekai |
| 3 | shibing624/parrots-speaker | 合集 | ⭐ 13 likes | 6 角色多語言 |
| 4 | None1145/Lappland-Decadenza | 遊戲 | ⭐ 10 likes | 明日方舟 |
| 5 | AkitoP/JA-ProsodyControl | 工具 | ⭐ 9 likes | 韻律控制 |
| 6 | TwinPeaksTownie/LAURA | 遊戲 | ⭐ 7 likes | 含 LoRA 細節 |
| 7 | None1145/Theresa | 遊戲 | ⭐ 6 likes | 明日方舟 |
| 8 | 4nm1tsu/shikokumetan | 動漫 | ⭐ 5 likes | 東北ずん子官方 |
| 9 | None1145/Rosmontis | 遊戲 | ⭐ 5 likes | 明日方舟 |
| 10 | shibing624/maimai | 遊戲 | ⭐ 8 likes | 舞萌 DX |

### 搜尋更多模型

- HuggingFace 搜尋：`https://huggingface.co/models?other=gpt-sovits`
- 或使用頁面左側 Filters → Other → 輸入 `gpt-sovits`
- ModelScope 搜尋：`https://www.modelscope.cn` → 搜尋 `GPT-SoVITS`

---

## ModelScope（魔搭）資源

ModelScope 上的 GPT-SoVITS 相關資源以整合包、訓練好的音色模型和教學文檔為主。

**熱門音色模型頁面**：
- [bailandali/GPT-SoVITS-VC-List](https://www.modelscope.cn/models/bailandali/GPT-SoVITS-VC-List/summary)（含多種角色音色整合列表）

**ModelScope 搜尋關鍵字**：`GPT-SoVITS`、`GPT-SoVITS音色`、`GPT-SoVITS模型`

> 注意：ModelScope 頁面需登入才能完整查看模型列表，建議直接用頁面內的搜尋功能。

---

## Bilibili / 社群分享資源

| 平台 | 說明 |
|------|------|
| [GPT-SoVITS 官方 Demo 影片](https://www.bilibili.com/video/BV12g4y1m7Uw) | 官方展示零樣本與少樣本效果 |
| [Rentry 教學指南](https://rentry.co/GPT-SoVITS-guide#/) | 英文新手入門教程 |
| [語雀中文教學](https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e) | 詳細中文教學文件 |

> ⚠️ Bilibili 創作者分享的模型多為私人分享連結，容易失效，建議首選 HuggingFace / ModelScope 公開資源。

---

## 如何使用音色模型

### 方法一：Zero-shot（零樣本，無需訓練）

最簡單的方式，適合快速體驗或一次性使用：

1. 準備一段 **5~10 秒** 的乾淨語音（無背景音樂、噪音）
2. 進入 GPT-SoVITS WebUI → **推理（Inference）** 頁面
3. 上傳該音訊作為「參考音」
4. 輸入文字，點擊生成

**此方式不需要下載任何 .pth 權重檔**，但每次推論都需要提供參考音訊。

### 方法二：載入預訓練音色模型（需下載權重檔）

當你從 HuggingFace 或 ModelScope 下載了一個 `.pth` 或 `.ckpt` 檔：

#### Step 1：確認版本對應

| 模型類型 | 存放位置（相對於 GPT-SoVITS 根目錄）|
|---------|--------------------------------|
| SoVITS 權重（.pth）| `GPT_SoVITS/weights/` |
| GPT 權重（.ckpt/.pth）| `GPT_SoVITS/weights/` |

**版本必須對齊**：用 v3 底模訓練的音色，必須用 v3 或對應版本推論；v2ProPlus 訓練的音色需要 v2ProPlus 底模。

#### Step 2：下載對應底模

以 [laubonghaudoi/zoengjyutgaai_tts](https://huggingface.co/laubonghaudoi/zoengjyutgaai_tts) 為例：

```python
from huggingface_hub import hf_hub_download

# 下載 GPT 模型
gpt_model = hf_hub_download(
    repo_id="laubonghaudoi/zoengjyutgaai_tts",
    filename="gpt/dpo1-e1000.ckpt"
)

# 下載 SoVITS 模型
sovits_model = hf_hub_download(
    repo_id="laubonghaudoi/zoengjyutgaai_tts",
    filename="sovits/e1_e50_s5950.pth"
)
```

#### Step 3：放入專案目錄

```
GPT-SoVITS/
├── GPT_SoVITS/
│   └── weights/
│       ├── dpo1-e1000.ckpt   ← GPT 權重
│       └── e1_e50_s5950.pth  ← SoVITS 權重
└── webui.py
```

#### Step 4：在 WebUI 中載入

1. 進入 **模型推理（Inference）** 頁面
2. 在「GPT 模型」下拉選單中選擇 `dpo1-e1000.ckpt`
3. 在「SoVITS 模型」下拉選單中選擇 `e1_e50_s5950.pth`
4. 上傳該模型頁面提供的 `ref_audio.wav`（參考音訊）
5. 輸入文字，點擊生成

### 方法三：透過 API 呼叫

部分模型（如 [VoidShine/atri-sovits](https://huggingface.co/VoidShine/atri-sovits)）提供 FastAPI 推論腳本：

```bash
# 啟動 API 伺服器
cd /path/to/GPT-SoVITS
python api_atri.py
# API 文件：http://127.0.0.1:9880/docs
```

---

## 常見問題

### Q1：為什麼下載的模型音色效果不好？

可能原因：
- 底模版本不匹配（用 v2 底模推論 v3 訓練的音色）
- 參考音訊品質差（有噪音、音量過小、錄音失真）
- 訓練數據量不足（少於 1 分鐘）
- 跨語言時，目標語言與訓練語言差異過大

### Q2：v2Pro 和 v2ProPlus 有什麼實際差異？

官方建議：如果不確定用哪個，直接用 **v2ProPlus**。兩者差異在 VRAM 需求（約高 200MB），但音色相似度提升最明顯。

### Q3：訓練一個自訂音色需要多少數據？

官方最低要求：**1 分鐘**高品質語音即可訓練出可用的音色。但數據越多（10 分鐘以上）、品質越好，效果越接近真人。

### Q4：如何在其他應用中使用這些音色？

- **RVC（整合進其他語音處理流程）**：將 .pth 權重載入 RVC 框架
- **API 推論**：使用各模型提供的 FastAPI / Gradio 接口
- **整合進遊戲/動畫專案**：需評估授權條款（見下方法律風險）

---

## 法律風險提醒

⚠️ **使用前務必了解以下風險：**

### 1. 肖像權 / 姓名權
克隆真實人物的聲音（名人、親友、未經同意的第三方）可能涉及：
- 肖像權侵權（部分國家/地區）
- 姓名權侵權
- 聲音權侵權（如中國《民法典》第 1023條參照肖像權保護）

### 2. 版權風險
- 動漫、遊戲角色的聲音素材：用於訓練可能侵犯原作版權
- 大多數社群模型的授權為 **CC BY-NC-SA 4.0**（非商業用途）
- 商業使用前務必確認模型 License

### 3. 詐騙與虛假內容
- **嚴禁**用於：假冒他人語音、生成虛假新聞語音、欺詐性語音訊息
- 部分國家已立法規範 AI 語音合成（如美國部分州、中國相關規定）

### 4. 授權條款速查

| 模型 | 授權 |
|------|------|
| [Bocchi-The-Rock 音色模型](https://huggingface.co/lpkpaco/Bocchi-The-Rock-GPT-SoVITS-Models) | CC BY-NC-SA 4.0（非商業）|
| [ATRI 音色模型](https://huggingface.co/VoidShine/atri-sovits) | AGPL-3.0 |
| [粵語說古模型](https://huggingface.co/laubonghaudoi/zoengjyutgaai_tts) | 未註明，請自行確認 |
| 官方底模 [RVC-Boss/GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | AGPL-3.0 |

### 5. 建議
- **個人研究 / 非商業用途**：風險較低，但仍需謹慎
- **內容創作**：建議使用原創素材或已獲授權的聲音
- **商業用途**：務必諮詢法律專業人士，確認各模型授權條款

---

## 總結行動建議

| 需求 | 推薦做法 |
|------|---------|
| 快速體驗，無需下載 | 直接用 [HuggingFace 線上 Demo](https://lj1995-gpt-sovits-proplus.hf.space/) 上傳參考音訊 |
| 想用特定動漫/遊戲角色音色 | 從 HuggingFace 下載對應 .pth / .ckpt 檔（注意授權）|
| 想克隆自己/親友的聲音 | 錄製 5 秒音訊 → Zero-shot 模式直接使用 |
| 想訓練專屬高品質音色 | 收集 1 分鐘以上音訊 → 用 v2ProPlus 底模微調訓練 |
| 在 Windows 上快速運行 | 下載 [lj1995/GPT-SoVITS-windows-package](https://huggingface.co/lj1995/GPT-SoVITS-windows-package)，雙擊 `go-webui.bat` |

---

## 參考來源

1. [GPT-SoVITS GitHub 主頁](https://github.com/RVC-Boss/GPT-SoVITS) — 官方資訊
2. [GPT-SoVITS 版本特性 Wiki](https://github.com/RVC-Boss/GPT-SoVITS/wiki/GPT%E2%80%90SoVITS%E2%80%90features-(%E5%90%84%E7%89%88%E6%9C%AC%E7%89%B9%E6%80%A7)) — 各版本詳細比較與 Benchmark 數據
3. [HuggingFace - GPT-SoVITS 模型列表](https://huggingface.co/models?other=gpt-sovits) — 社群音色模型
4. [HuggingFace lj1995/GPT-SoVITS-windows-package](https://huggingface.co/lj1995/GPT-SoVITS-windows-package) — Windows 一鍵整合包
5. 各音色模型 HuggingFace 頁面（見上方模型列表）
