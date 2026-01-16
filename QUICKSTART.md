# 快速部署指南

## 🚀 快速開始

### 1. 重新構建並啟動
```bash
cd e:\taiwan-stock-app

# 停止現有容器
docker-compose down

# 重新構建（首次構建約需 5-10 分鐘）
docker-compose build --no-cache pecunianexus

# 啟動服務
docker-compose up -d

# 查看日誌
docker logs pecunianexus -f
```

### 2. 訪問應用
- **主頁**: http://localhost:5788
- **設置頁面**: http://localhost:5788/settings

### 3. 初次使用
1. 登入系統（test001 / 123456）
2. 訪問設置頁面
3. 下載推薦模型（點擊 Llama 2 卡片）
4. 等待下載完成（約 3-5 分鐘）
5. 返回首頁搜尋股票，AI 將自動分析

## 📦 主要功能

### ⚙️ 設置頁面
- 📥 下載 Ollama 模型（支持快速選擇和自定義）
- 🗑️ 刪除不需要的模型
- ⭐ 設置默認分析模型
- 📊 查看已安裝模型列表和大小

### 🤖 推薦模型
| 模型 | 說明 |
|------|------|
| llama2 | 入門推薦，平衡性好 |
| llama3.2 | 最新版本，速度快 |
| mistral | 高質量輸出 |
| qwen2.5:7b | 中文優化，適合台股分析 |

### 📈 自動分析
- 一年價格區間分析
- 技術指標解讀（RSI、MACD、KD、布林通道）
- 財務數據整合
- 最新新聞摘要
- AI 買賣建議

## 🔧 故障排除

### 模型下載慢？
```bash
# 進入容器手動下載
docker exec -it pecunianexus bash
ollama pull llama2
```

### 查看 Ollama 狀態
```bash
# 查看 Ollama 日誌
docker exec pecunianexus cat /tmp/ollama.log

# 測試 Ollama API
docker exec pecunianexus curl http://localhost:11434/api/tags
```

### 重新初始化
```bash
# 完全清理並重新開始
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## 📝 技術細節

### 端口說明
- **5788**: Flask Web 應用
- **11434**: Ollama API（容器內部）

### 持久化存儲
- `stock-data`: 應用數據
- `pgdata`: PostgreSQL 數據
- `ollama-models`: Ollama 模型（重要！）

### 環境變量
```yaml
OLLAMA_HOST=http://localhost:11434  # Ollama 地址
OPENAI_API_KEY=...                  # OpenAI（可選）
GEMINI_API_KEY=...                  # Gemini（可選）
```

## 💡 使用建議

1. **首次使用**：先下載一個小模型（如 llama3.2）測試
2. **生產環境**：推薦 qwen2.5:7b（中文優化）或 mistral（高質量）
3. **資源有限**：選擇 llama3.2（2GB）而非 llama2（3.8GB）
4. **多模型**：可以下載多個模型，隨時切換

## 📚 更多資源

- [Ollama 模型庫](https://ollama.com/library)
- [完整文檔](./OLLAMA_DOCKER_INTEGRATION.md)
- [原始設置指南](./OLLAMA_SETUP.md)
