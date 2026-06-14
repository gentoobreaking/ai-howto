# twstock 四大買賣點判斷（Best Four Point）研究報告

**研究對象**：[mlouielu/twstock](https://github.com/mlouielu/twstock)  
**原始碼版本**：master branch  
**研究日期**：2026-05-06  
**研究者**：研研

---

## 摘要

twstock 的 `twstock -b <stock_id>` 指令背後，是一套名為「四大買賣點判斷」（Best Four Point, BFP）的技術指標系統。該系統結合量價關係、三日均線趨勢、六日均線比較，以及 3/6 日乖離率的極轉點偵測，構成一套多條件過濾的短線買賣訊號。本報告完整解讀其計算邏輯，並分析各指標的優缺點與實務建議。

---

## 一、系統架構

```
Stock 實體（價格/成交量/Open/High/Low/Close）
         ↓
    Analytics 類（父類，提供基礎計算工具）
         ↓
  BestFourPoint 類（繼承分析能力，實作四大買賣點）
         ↓
  CLI: twstock -b <stock_id> → 輸出 Buy/Sell/Dont't touch
```

核心模組：
| 檔案 | 職責 |
|------|------|
| `twstock/stock.py` | 資料抓取 + Stock 類（封裝 OHLCV 屬性）|
| `twstock/analytics.py` | Analytics 類（均線/乖離率等工具）+ `BestFourPoint` 實作 |
| `twstock/cli/best_four_point.py` | CLI 入口 |

---

## 二、依賴模組：Analytics 類

`BestFourPoint` 依賴 `Analytics` 類中的四個核心方法，以下逐一解讀。

### 2.1 `moving_average(data, days)`

```python
def moving_average(self, data, days):
    result = []
    data = data[:]          # 複製一份，避免修改原資料
    for _ in range(len(data) - days + 1):
        result.append(round(sum(data[-days:]) / days, 2))
        data.pop()           # 每次移除最後一筆（即往前滾動一天）
    return result[::-1]      # 逆序返回，使 index 0 為最早的均線值
```

**計算方式**：移動平均法（SMA，Simple Moving Average）。  
**特點**：
- 採用「往前滾動」寫法，`result[0]` 是最舊的均線值，`result[-1]` 是最新的均線值。
- 輸出長度 = `len(data) - days + 1`，即資料天數減去均線期數加一。

**以三日均線為例**（股價 data = [10, 11, 12, 13, 14]）：
```
第3天 MA3 = (10 + 11 + 12) / 3 = 11.0  → result[0]
第4天 MA3 = (11 + 12 + 13) / 3 = 12.0  → result[1]
第5天 MA3 = (12 + 13 + 14) / 3 = 13.0  → result[2]
```

### 2.2 `continuous(data)`

```python
def continuous(self, data):
    # 計算相鄰日差值方向
    diff = [1 if data[-i] > data[-i - 1] else -1 for i in range(1, len(data))]
    cont = 0
    for v in diff:
        if v == diff[0]:
            cont += 1
        else:
            break
    return cont * diff[0]
```

**計算方式**：連續N日趨勢判斷。  
**邏輯**：
1. 取最新 N 筆資料（傳入的是 `moving_average(price, 3)`，即三日均線）。
2. 從倒數第2筆往前比較，記錄方向（漲 = +1，跌 = -1）。
3. 計算從最新到最舊，連續同向的天數 `cont`。
4. 返回 `cont * 方向`：正數 = 持續上漲；負數 = 持續下跌。

**實例**（三日均線 = [11, 12, 13, 14, 15]）：
```
diff = [1, 1, 1, 1]  （均線每天都比前一天高）
cont = 4
返回值 = 4 * 1 = 4（持續上漲4天）
```

### 2.3 `ma_bias_ratio(day1, day2)`

```python
def ma_bias_ratio(self, day1, day2):
    data1 = self.moving_average(self.price, day1)  # 短均線
    data2 = self.moving_average(self.price, day2)  # 長均線
    result = [
        data1[-i] - data2[-i] for i in range(1, min(len(data1), len(data2)) + 1)
    ]
    return result[::-1]
```

**計算方式**：乖離率 = 短均線 − 長均線  
**特點**：
- `day1 < day2` 時（day1=3, day2=6），正值代表短均線在長均線之上（偏多），負值相反。
- 輸出為陣列，取 `result[-1]` 為最新一期的乖離率。

### 2.4 `ma_bias_ratio_pivot(data, sample_size=5, position=False)`

```python
def ma_bias_ratio_pivot(self, data, sample_size=5, position=False):
    sample = data[-sample_size:]  # 取最近5期乖離率

    if position is True:          # 檢查極小值（買點條件）
        check_value = min(sample)  # 找最低乖離率
        pre_check_value = max(sample) > 0  # 前期必須為正
    elif position is False:       # 檢查極大值（賣點條件）
        check_value = max(sample)  # 找最高乖離率
        pre_check_value = max(sample) < 0  # 前期必須為負

    # 極轉點條件：
    # 1. 極值在最近3天內（sample_size - index < 4）
    # 2. 極值不在最後一天（还没形成死交叉）
    # 3. 前期乖離率滿足預期方向
    return (
        (
            sample_size - sample.index(check_value) < 4
            and sample.index(check_value) != sample_size - 1
            and pre_check_value
        ),
        sample_size - sample.index(check_value) - 1,  # 極值距今天數
        check_value,                                  # 極值本身
    )
```

**計算方式**：乖離率極轉點偵測（Pivot Point Detection）  
**實質意義**：
- 乖離率代表短均線偏離長均線的程度。
- 當乖離率過高（正值過大）時，代表價格偏離均值太遠，容易均值回歸（下跌）。
- 當乖離率過低（負值過大）時，代表價格偏低，容易反彈（買進）。
- `position=True`（極小值，買點）→ 前期乖離率 > 0（正乖離），極值在最近3天內
- `position=False`（極大值，賣點）→ 前期乖離率 < 0（負乖離），極值在最近3天內

---

## 三、四大買賣點完整計算邏輯

### 3.1 四大買點（Best Four Buy Points）

| 編號 | 名稱 | 觸發條件 | 代碼 |
|------|------|----------|------|
| 買點1 | **量大收紅** | 今日成交量 > 昨日成交量 **且** 今日收盤價 > 今日開盤價 | `best_buy_1()` |
| 買點2 | **量縮價不跌** | 今日成交量 < 昨日成交量 **且** 今日收盤價 > **昨日**開盤價 | `best_buy_2()` |
| 買點3 | **三日均價由下往上** | 三日均線連續上漲（`continuous(MA3) > 0`） | `best_buy_3()` |
| 買點4 | **三日均價大於六日均價** | MA3[-1] > MA6[-1] | `best_buy_4()` |

#### 買點1：量大收紅

```python
def best_buy_1(self):
    return (
        self.stock.capacity[-1] > self.stock.capacity[-2]
        and self.stock.price[-1] > self.stock.open[-1]
    )
```

**實質意涵**：在資金大量湧入的情況下，股價能在開盤價以上收盤，代表多頭力道強勁，供需結構有利於多方。

#### 買點2：量縮價不跌

```python
def best_buy_2(self):
    return (
        self.stock.capacity[-1] < self.stock.capacity[-2]
        and self.stock.price[-1] > self.stock.open[-2]
    )
```

**實質意涵**：在成交量萎縮時，股價仍能維持在昨日開盤價之上，代表拋壓不重，空方已無力打壓，是潛在的反轉訊號。  
**注意**：代碼中用的是 `self.stock.open[-2]`（昨日開盤價），而非 `self.stock.price[-2]`（昨日收盤價）。

#### 買點3：三日均價由下往上

```python
def best_buy_3(self):
    return (
        self.stock.continuous(self.stock.moving_average(self.stock.price, 3)) == 1
    )
```

**實質意涵**：三日均線持續上揚，代表短期價格趨勢向上，動能持續。

#### 買點4：三日均價大於六日均價

```python
def best_buy_4(self):
    return (
        self.stock.moving_average(self.stock.price, 3)[-1]
        > self.stock.moving_average(self.stock.price, 6)[-1]
    )
```

**實質意涵**：短均線（MA3）在長均線（MA6）之上，是經典的均線多頭排列，屬於趨勢性買進訊號。

---

### 3.2 四大賣點（Best Four Sell Points）

| 編號 | 名稱 | 觸發條件 | 代碼 |
|------|------|----------|------|
| 賣點1 | **量大收黑** | 今日成交量 > 昨日成交量 **且** 今日收盤價 < 今日開盤價 | `best_sell_1()` |
| 賣點2 | **量縮價跌** | 今日成交量 < 昨日成交量 **且** 今日收盤價 < **昨日**開盤價 | `best_sell_2()` |
| 賣點3 | **三日均價由上往下** | 三日均線連續下跌（`continuous(MA3) < 0`） | `best_sell_3()` |
| 賣點4 | **三日均價小於六日均價** | MA3[-1] < MA6[-1] | `best_sell_4()` |

#### 賣點1：量大收黑

```python
def best_sell_1(self):
    return (
        self.stock.capacity[-1] > self.stock.capacity[-2]
        and self.stock.price[-1] < self.stock.open[-1]
    )
```

**實質意涵**：在高量下殺，收盤低於開盤，代表空方力道強勁，大戶或機構可能在出貨。

#### 賣點2：量縮價跌

```python
def best_sell_2(self):
    return (
        self.stock.capacity[-1] < self.stock.capacity[-2]
        and self.stock.price[-1] < self.stock.open[-2]
    )
```

**實質意涵**：成交量萎縮但價格仍在下跌，代表承接意願薄弱，跌勢尚未結束，屬於持續觀望或空方訊號。

#### 賣點3：三日均價由上往下

```python
def best_sell_3(self):
    return (
        self.stock.continuous(self.stock.moving_average(self.stock.price, 3)) == -1
    )
```

**實質意涵**：三日均線持續下滑，代表短期動能轉弱。

#### 賣點4：三日均價小於六日均價

```python
def best_sell_4(self):
    return (
        self.stock.moving_average(self.stock.price, 3)[-1]
        < self.stock.moving_average(self.stock.price, 6)[-1]
    )
```

**實質意涵**：MA3 < MA6，形成均線空頭排列，是趨勢性賣出訊號。

---

## 四、觸發門檻：乖離率極轉點閘門

**這是整個系統最關鍵的前置條件**——如果沒有滿足極轉點條件，即使滿足了買/賣點條件，系統也不會輸出訊號。

### 買點觸發邏輯

```python
def best_four_point_to_buy(self):
    # ...
    if self.mins_bias_ratio() and any(check):
        # → mins_bias_ratio() = plus_bias_ratio() = ma_bias_ratio_pivot(position=False)
        #   等價於：3/6乖離率極大值在最近3天內，且前期乖離率<0
        for index, v in enumerate(check):
            if v:
                result.append(self.BEST_BUY_WHY[index])
    else:
        return False
    return ", ".join(result)
```

**買點的極轉點條件**：`mins_bias_ratio()` = `plus_bias_ratio()` = `bias_ratio(position=False)`  
**意義**：  
- 前期（倒數第2期）乖離率必須為正（`max(sample) > 0`）→ 代表之前處於正乖離（偏貴）  
- 極大值在最近3天內 → 代表乖離率已由正轉負，形成「極點」  
- 這個條件確保：只有在正乖離達到峰值並開始回落（均值回歸起點）時，才認定為買點

### 賣點觸發邏輯

```python
def best_four_point_to_sell(self):
    # ...
    if self.plus_bias_ratio() and any(check):
        # → plus_bias_ratio() = bias_ratio(position=True)
        #   等價於：3/6乖離率極小值在最近3天內，且前期乖離率>0
        for index, v in enumerate(check):
            if v:
                result.append(self.BEST_SELL_WHY[index])
    else:
        return False
    return ", ".join(result)
```

**賣點的極轉點條件**：`plus_bias_ratio()` = `bias_ratio(position=True)`  
**意義**：  
- 前期乖離率必須為負（`max(sample) < 0`）→ 代表之前處於負乖離（偏便宜）  
- 極小值在最近3天內 → 代表乖離率已由負轉正，形成「極點」  
- 這個條件確保：只有在負乖離觸底回升後，才認定為賣點

### 極轉點條件的實質意義

```
【買點極轉點邏輯】：3日均線在6日均線之上（正乖離）→ 正乖離持續擴大 → 然後正乖離縮小（均值回歸）
                  ↑                    ↑                        ↑
              前置條件              乖離率的峰值             觸發買點
              (max>0)            (極大值在最近3天)        (各買點條件)

【賣點極轉點邏輯】：3日均線在6日均線之下（負乖離）→ 負乖離持續擴大 → 然後負乖離縮小（均值回歸）
                  ↑                    ↑                        ↑
              前置條件              乖離率的谷底             觸發賣點
              (max<0)            (極小值在最近3天)        (各賣點條件)
```

---

## 五、完整訊號邏輯流程圖

```
┌─────────────────────────────────────────┐
│           twstock -b <stock_id>         │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│        抓取最近31天 OHLCV 資料           │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
┌──────────────┐      ┌──────────────┐
│ 乖離率極轉點？│      │ 乖離率極轉點？│
│ mins_bias() │      │ plus_bias() │
│ (position=  │      │ (position=  │
│   False)   │      │   True)     │
└──────┬──────┘      └──────┬──────┘
       │                    │
   極大值+近期         極小值+近期
   前期乖離>0         前期乖離<0
       │                    │
  ┌────▼────┐         ┌────▼────┐
  │買點閘門？│         │賣點閘門？│
  │any(4個  │         │any(4個  │
  │買點條件)│         │賣點條件)│
  └────┬────┘         └────┬────┘
       │NO                 │NO
       │                   │
   返回False           返回False
       │                   │
  ┌────▼────┐         ┌────▼────┐
  │  買點！ │          │  賣點！ │
  │(符合哪些│          │(符合哪些│
  │條件就列)│          │條件就列)│
  └─────────┘          └─────────┘
```

---

## 六、優勢分析

### 6.1 買點優勢

| 優點 | 說明 |
|------|------|
| **量價結合** | 買點1/2 直接結合成交量與價格，過濾假突破 |
| **趨勢確認** | 買點3/4 分別從動能與均線排列確認趨勢方向 |
| **多條件過濾** | 極轉點閘門 + 四大條件，雙重確認降低假訊號 |
| **實作簡潔** | 全部基於 OHLCV 資料，無需其他外部數據來源 |
| **非均線金叉死叉** | 不同於傳統 MA5/MA10 交叉系統，使用 MA3/MA6 更敏感 |

### 6.2 賣點優勢

| 優點 | 說明 |
|------|------|
| **量大收黑捕捉機構行為** | 高量+收黑是機構/大戶出貨的典型特徵 |
| **量縮價跌識別弱勢股** | 在無量下殺的環境確認空方尚未耗盡 |
| **極轉點避免逆勢** | 確保只在均值回歸起點附近才發訊號 |

---

## 七、風險與缺點分析

### 7.1 重大缺點

| 缺點 | 說明 | 嚴重程度 |
|------|------|----------|
| **只適用短線** | MA3/MA6 極度敏感，震盪市場會來回交叉產生大量假訊號 | ⚠️ 高 |
| **極轉點閘門過嚴** | 若乖離率尚未形成明確極點，即使四個條件全滿也不輸出 | ⚠️ 高 |
| **無停損停利機制** | 系統只輸出訊號，無明確的止損/目標價設定 | ⚠️ 高 |
| **歷史資料依賴** | 必須有至少6天資料（MA6 需要），新掛牌股票不適用 | ⚠️ 中 |
| **只考慮技術面** | 完全不考慮基本面、籌碼面、總經環境 | ⚠️ 高 |
| **市場情境不區分** | 區間整理、趨勢盤、暴跌/暴漲市場採用相同參數 | ⚠️ 中 |
| **資料時間差** | 抓取的31天資料可能不包含今日完整交易，臨收盤訊號可能失準 | ⚠️ 中 |

### 7.2 買點2 的潛在 Bug

```python
def best_buy_2(self):
    return (
        self.stock.capacity[-1] < self.stock.capacity[-2]
        and self.stock.price[-1] > self.stock.open[-2]  # 拿昨日開盤價對比今日收盤價
    )
```

**問題**：買點2 用「今日收盤 > 昨日開盤」來判斷價不跌，但昨日開盤與今日收盤價之間並無直接的價格連續性邏輯（中間經過一整個交易日）。建議改為 `price[-1] >= price[-2]`（今日收盤 >= 昨日收盤）更合理。

### 7.3 賣點2 的同樣問題

```python
def best_sell_2(self):
    return (
        self.stock.capacity[-1] < self.stock.capacity[-2]
        and self.stock.price[-1] < self.stock.open[-2]  # 與買點2相同的邏輯問題
    )
```

**建議**：改為 `price[-1] < price[-2]`（今日收盤 < 昨日收盤）。

---

## 八、實務使用建議

### 8.1 適當的使用情境

| 情境 | 建議 |
|------|------|
| **短線交易（1-5天）** | 可作為進出场參考 |
| **強趨勢市場** | 乖離率極轉點訊號較準確 |
| **有明確支撐/壓力位** | 結合支撐位增強訊號可靠性 |
| **作為輔助工具** | 搭配基本面、題材面做最後確認 |

### 8.2 不建議使用的情境

| 情境 | 原因 |
|------|------|
| **盤整/震盪市場** | 來回交叉導致大量假訊號 |
| **作為唯一進場依據** | 無停損機制，單靠訊號交易風險極高 |
| **長期投資決策** | 參數太短，不反映中長期趨勢 |
| **消息面/題材發酵期** | 技術指標落後於消息 |

### 8.3 可改進的方向

1. **加入停損/停利機制**：可參考 ATR（Average True Range）設定動態停損
2. **自適應參數**：在盤整市場使用更長均線（如 MA5/MA20），在趨勢市場使用原參數
3. **搭配成交量確認**：在量能不足時過濾掉極轉點訊號
4. **加入 RSI 或 MACD**：增加多指標確認，提高訊號品質

---

## 九、結論

twstock 的「四大買賣點判斷」是一套以均線乖離率極轉點為核心閘門，以量價關係和均線趨勢為觸發條件的短線技術指標系統。設計上具有以下特點：

1. **核心創新**：乖離率極轉點閘門（`ma_bias_ratio_pivot`）是區別於其他均線系統的關鍵，它試圖在「均值回歸的起點」捕捉買賣點
2. **實用價值**：全部基於開盤/收盤/成交量四個 OHLCV 欄位，無需外部數據，適合散戶快速實作
3. **根本限制**：MA3/MA6 參數過短，在台股個股這種高波動市場，假訊號比例高，必須搭配其他分析框架使用

**風險提醒**：本系統不包含任何停損或資金管理機制，直接根據訊號交易存在極高風險，投資人應謹慎評估。

---

## 附錄：原始碼索引

| 檔案 | URL |
|------|-----|
| `analytics.py` | https://github.com/mlouielu/twstock/blob/master/twstock/analytics.py |
| `stock.py` | https://github.com/mlouielu/twstock/blob/master/twstock/stock.py |
| `cli/best_four_point.py` | https://github.com/mlouielu/twstock/blob/master/twstock/cli/best_four_point.py |
| `cli/__init__.py` | https://github.com/mlouielu/twstock/blob/master/twstock/cli/__init__.py |
| README（範例輸出） | https://github.com/mlouielu/twstock |

---

*本報告由研研研究產生，資料來源為 twstock 開源專案原始碼。投資人依此報告進行任何投資行為，須自行承擔風險。*
