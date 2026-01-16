# Ollama 本地 AI 設定指南

## 什麼是 Ollama？

Ollama 是一個在本地運行大型語言模型（LLM）的工具，完全免費且無需 API 金鑰。推薦用於股票分析，因為：
- ✅ **完全免費**：無 API 調用費用
- ✅ **隱私保護**：數據不會發送到外部服務器
- ✅ **快速響應**：本地運行，無網絡延遲
- ✅ **無限使用**：沒有請求次數限制

## 安裝步驟

### Windows 安裝

1. **下載 Ollama**
   - 訪問：https://ollama.com/download/windows
   - 下載 `OllamaSetup.exe`
   - 運行安裝程序

2. **安裝語言模型**
   打開 PowerShell 或命令提示符：
   ```powershell
   # 安裝 Llama 2（推薦，7B 參數）
   ollama pull llama2
   
   # 或安裝 Llama 3（更強大，但需要更多資源）
   ollama pull llama3
   
   # 或安裝 Mistral（適合中等配置）
   ollama pull mistral
   
   # 或安裝台灣繁體中文優化模型（如果有）
   ollama pull taiwan-llama
   ```

3. **驗證安裝**
   ```powershell
   # 檢查 Ollama 服務狀態
   ollama list
   
   # 測試模型
   ollama run llama2 "你好，請簡單介紹自己"
   ```

4. **確認服務運行**
   - Ollama 會自動在背景運行
   - 默認端口：`http://localhost:11434`
   - 檢查：在瀏覽器訪問 http://localhost:11434

### macOS 安裝

```bash
# 使用 Homebrew 安裝
brew install ollama

# 或下載安裝包
# 訪問：https://ollama.com/download/mac

# 安裝模型
ollama pull llama2

# 驗證
ollama list
```

### Linux 安裝

```bash
# 安裝 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 安裝模型
ollama pull llama2

# 啟動服務
systemctl start ollama
```

## Docker 環境配置

應用程序已配置好連接到主機上的 Ollama：

```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
```

**Windows Docker Desktop 用戶**：
- 確保 Ollama 在主機上運行
- Docker 會自動通過 `host.docker.internal` 連接

**Linux Docker 用戶**：
如果遇到連接問題，修改 `.env` 文件：
```bash
OLLAMA_HOST=http://172.17.0.1:11434
```

## 推薦模型選擇

| 模型 | 大小 | 記憶體需求 | 推薦用途 |
|------|------|-----------|---------|
| **llama2** | 7B | 8GB RAM | 一般股票分析（推薦） |
| **llama3** | 8B | 16GB RAM | 深度分析 |
| **mistral** | 7B | 8GB RAM | 快速響應 |
| **qwen** | 7B | 8GB RAM | 中文優化 |

## 使用方式

1. **啟動 Ollama**
   - Windows：Ollama 安裝後自動啟動
   - 檢查系統托盤圖標

2. **啟動股票應用**
   ```powershell
   docker-compose up -d
   ```

3. **測試 AI 分析**
   - 登入應用程序
   - 搜尋任意股票代碼（如 2330）
   - AI 助手會自動分析並顯示建議

4. **查看 AI 提供者**
   - AI 下拉選單會顯示 "Ollama (本地)"
   - 優先使用 Ollama（免費且快速）

## 常見問題

### Q1: Ollama 連接失敗
```
✗ Ollama 連接失敗: Connection refused
```

**解決方法：**
1. 確認 Ollama 已安裝並運行
2. 檢查 PowerShell：`ollama list`
3. 重啟 Ollama：關閉後重新打開
4. 檢查防火牆設置

### Q2: 沒有安裝任何模型
```
Error: no models installed
```

**解決方法：**
```powershell
ollama pull llama2
```

### Q3: 記憶體不足
```
Error: insufficient memory
```

**解決方法：**
- 關閉其他應用程序
- 使用更小的模型：`ollama pull llama2:7b-chat-q4_0`（量化版本）
- 至少需要 8GB RAM

### Q4: 分析速度慢
**優化方法：**
- 使用 GPU 加速（NVIDIA GPU 自動支持）
- 升級到 SSD 硬盤
- 增加系統記憶體
- 使用量化模型

### Q5: Docker 無法連接主機 Ollama
**Windows：**
確保 Docker Desktop 設置中啟用了 "Allow the default Docker socket to be used"

**Linux：**
修改 docker-compose.yml：
```yaml
extra_hosts:
  - "host.docker.internal:172.17.0.1"
```

## 進階設置

### 自定義模型參數

創建 Modelfile：
```bash
# modelfile
FROM llama2
PARAMETER temperature 0.7
PARAMETER top_p 0.9
SYSTEM 你是一個專業的台灣股市分析師，精通技術分析和基本面分析。
```

創建自定義模型：
```bash
ollama create taiwan-stock-analyst -f ./modelfile
```

### API 測試

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama2",
  "prompt": "分析台積電的投資價值",
  "stream": false
}'
```

## 性能對比

| AI 服務 | 成本 | 速度 | 隱私 | 限制 |
|---------|------|------|------|------|
| **Ollama** | 免費 | 快（本地） | 高 | 無 |
| OpenAI GPT | 按量計費 | 中等 | 中 | 有配額 |
| Google Gemini | 免費層/付費 | 快 | 中 | 有配額 |

## 系統需求

**最低配置：**
- CPU：4 核心
- RAM：8GB
- 硬盤：10GB 可用空間

**推薦配置：**
- CPU：8 核心
- RAM：16GB
- GPU：NVIDIA（可選，加速推理）
- 硬盤：SSD，20GB 可用空間

## 技術支援

- Ollama 官網：https://ollama.com
- GitHub：https://github.com/ollama/ollama
- 模型庫：https://ollama.com/library
