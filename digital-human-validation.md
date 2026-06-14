# 數位人口型同步方案評估報告（Mac M2）

> 對應任務：T016
> 日期：2026-05-13

## 結論：LiveTalking 在 Mac M2 不適用

### 原因

| 項目 | 說明 |
|------|------|
| Mac 支援 | LiveTalking issue #156 仍 open，無官方回應 |
| GPU 需求 | 所有 benchmark 為 NVIDIA CUDA（Wav2Lip 需 RTX 3060+） |
| MPS 表現 | Wav2Lip on MPS 處理 30s 影片約 20 分鐘（非即時） |
| 記憶體 | 16GB 無法同時容納 LLM(~3GB) + TTS + 口型神經網路 |

### 替代方案：Viseme-Based 動畫

不依賴神經網路，改由 TTS 音頻特徵直接驅動預定義嘴型。

## Viseme-Based 架構

```
TTS (Kokoro) → phonemes → viseme mapping → avatar poses → animation frames
                      ↓
             渲染引擎 (render_engine.py)
                      ↓
              WebSocket / Canvas
```

## 實作方式

### 1. Viseme 定義

[Kokoro] 底層使用 phoneme 序列（misaki G2P），可從 pipeline 取得。將 phoneme 映射為 12 種基本嘴型：

| Viseme | 對應音素 | 嘴型 |
|--------|---------|------|
| A | aa, ae, ah | 張大 |
| B | b, p, m | 閉合 |
| C | ch, jh, sh | 噘嘴 |
| D | d, t, n | 微張 |
| E | eh, er | 扁平 |
| F | f, v | 下唇上齒 |
| G | g, k, h | 張開 |
| I | iy, ih | 微笑 |
| O | ow, ao | 圓形 |
| U | uw, uh | 小圓 |
| W | w | 噘圓 |
| rest | silence | 閉合 |

### 2. Render Engine API

```python
from render.render_engine import RenderEngine

engine = RenderEngine()
engine.load_avatar("path/to/avatar.png")
frames = engine.render(audio_array, sample_rate, phoneme_timings)
# frames → WebSocket to frontend
```

### 3. 前端渲染

前端接收 frames 後使用 Canvas/WebGL 繪製：

```javascript
// Frontend psuedocode
ws.onmessage = (frame) => {
    canvas.drawImage(frame.viseme_image, x, y);
};
```

## 建議整合路徑

1. 在 `render/render_engine.py` 實作 viseme mapping
2. 前端（HTML Canvas）接收 viseme ID 並顯示對應嘴型圖層
3. 不需 GPU、不需神經網路、可在 M2 上即時執行
