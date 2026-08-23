# 建置 MNN 編譯環境（Mac M2 Metal 加速）

> **狀態**：✅ 已完成（T001 完成）
> 最後更新：2026-05-13（安安 / 寶寶）
> 執行者：碼農1號 / 寶寶

## Context

在 MacBook Air M2 (16GB RAM) 上編譯 Alibaba MNN 引擎，啟用 Metal（GPU）加速，
為後續 MNN-LLM 離線大腦模型執行奠定基礎。這是 Javis 專案第一階段核心任務。

## 硬體 / 軟體需求

- macOS 13+ (Ventura/Sonoma/Sequoia)
- MacBook Air M2 (16GB RAM) ✅ 實測可編譯
- Xcode Command Line Tools：`xcode-select --install`
- Homebrew 已安裝
- 磁碟空間：至少 5GB 可用

---

## 執行日誌

### 第一次嘗試（2026-05-13 09:14）— 失敗

**問題**：缺少編譯工具

```
cmake: command not found
ninja: command not found
```

**解法**：在 `setup-mnn.sh` 中加入自動安裝邏輯（Step 1 檢查 cmake + ninja，若未找到則自動 `brew install`）。

### 第二次嘗試（2026-05-13 09:21）— 成功 ✅

| 產物 | 大小 |
|------|------|
| `libMNN.a` | 7.2MB（含 Metal backend） |
| `MNNConvert` | ✅ 已編譯 |

**已知警告**（上游 MNN，無影響）：
- `half.hpp` deprecation warning
- `MTLResourceOption` deprecation warning
- `sprintf` deprecation warning

**CMake 參數語法修正**：
- 原本用 `\` 換行，Shell 將 `-DMNN_BUILD_SHARED_LIBS=OFF` 誤當獨立指令執行
- **修正**：將整條 cmake 指令賦值給變數 `$CMAKE_CMD` 再執行

**完整日誌**：`~/Projects/JARVIS-on-mac/mnn-build.log`

### Python Binding 安裝（2026-05-13 10:47）— 成功 ✅

**方法 A（推薦）**：pip 安裝（預編譯，5 秒完成）

```bash
pip3 install MNN
python3 -c "import MNN; print('✅ MNN', MNN.version)"
```

成功輸出：`✅ MNN <built-in function version>` + Device capabilities 訊息

**驗證 MNN-LLM API**：

```python
import MNN.llm as llm
help(llm.create)  # create(config_path) → Llm instance
llm.LLM.methods   # load(), response(prompt), generate(), tokenizer_encode/decode()
```

**方法 B（從原始碼編譯）**：

```bash
cd ~/Projects/JARVIS-on-mac/MNN/pymnn/pip_package
python3 build_deps.py
python3 setup.py install
```

> ⚠️ 需要先完成 C++ 編譯（第 4 步），setup.py 會連結 `MNN/build/` 靜態庫

---

## 安裝步驟

### Step 1：安裝編譯工具

```bash
brew install cmake ninja python@3.11
```

### Step 2：克隆 MNN 主倉庫

```bash
git clone --recurse-submodules https://github.com/alibaba/MNN.git
cd MNN
```

> ⚠️ 正確 Repo 為 `alibaba/MNN`，非 `tencent/MNN`（後者不存在）

### Step 3：配置 CMake（開啟 Metal）

```bash
mkdir build && cd build
cmake .. -G Ninja \
  -DMNN_METAL=ON \
  -DMNN_OPENMP=ON \
  -DMNN_BUILD_SHARED_LIBS=OFF \
  -DCMAKE_BUILD_TYPE=Release
```

### Step 4：編譯（預計 10-20 分鐘）

```bash
ninja
```

成功標誌：`libMNN.a`（7.2MB）+ `MNNConvert` 出現在 `build/` 目錄

### Step 5：安裝 Python Binding（二選一）

**方法 A（推薦）**：pip 安裝（預編譯，5 秒完成）
```bash
pip3 install MNN
```

**方法 B**：從原始碼編譯
```bash
cd ../pymnn/pip_package
python3 build_deps.py
python3 setup.py install
```

### Step 6：驗證

```bash
python3 -c "import MNN; print('✅ MNN OK')"
python3 -c "from MNN.llm import create; print('✅ MNN.llm OK')"
```

---

## 驗收標準 ✅

- [x] cmake + ninja 安裝成功
- [x] `git clone --recurse-submodules` 完成（含子模組）
- [x] CMake 配置有 `MNN_METAL=ON`
- [x] `ninja` 成功，build/ 產生 `libMNN.a`（7.2MB）
- [x] MNNConvert 已編譯
- [x] `pip3 install MNN` ✅ MNN 3.5.0 安裝成功
- [x] `import MNN` ✅ 無錯誤
- [x] `import MNN.llm` ✅ 有 `create()` / `LLM` API
- [x] brain_engine.py 已實作（MNN.llm.create 封裝）
- [x] test_brain.py 已實作（5 項測試）
- [x] 本文檔（howto）已完整記錄

---

## Troubleshooting

| 問題 | 解法 |
|------|------|
| `cmake: command not found` | `brew install cmake` |
| `ninja: command not found` | `brew install ninja` |
| `import MNN` ImportError | `pip3 install MNN` 重試 |
| Metal 不被識別 | 確認 CMake 設定 `MNN_METAL=ON` |
| 記憶體不足 | `ninja -j2`（只用 2 核心） |

---

## 相關連結

| 資源 | URL |
|------|-----|
| MNN GitHub | https://github.com/alibaba/MNN |
| MNN Wiki（LLM 專區）| https://github.com/alibaba/MNN/wiki/llm |
| MNN-LLM（模型匯出說明）| `~/Projects/JARVIS-on-mac/MNN/transformers/README.md` |
| MNN Python Binding | `~/Projects/JARVIS-on-mac/MNN/pymnn/INSTALL.md` |

---

## 更新紀錄

| 日期 | 更新者 | 變更內容 |
|------|--------|---------|
| 2026-05-13 | 安安 | 初版建立，修正 5 處錯誤 |
| 2026-05-13 | 安安 | 記錄 cmake/ninja 缺少問題 + setup-mnn.sh 修正 |
| 2026-05-13 | 安安 | 記錄第二次執行成功（libMNN.a 7.2MB）|
| 2026-05-13 10:47 | 寶寶 | ✅ T001 完成：pip install MNN 成功（3.5.0）；brain_engine.py 實作；test_brain.py 完成；MNN.llm.create() API 驗證 ✅ |
