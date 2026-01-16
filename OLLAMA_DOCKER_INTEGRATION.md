# Ollama 集成更新說明

## 更新內容

### 1. Ollama 內置到 Docker 容器
- ✅ Ollama 現在完全在 Docker 容器內運行，無需在主機上單獨安裝
- ✅ 自動啟動 Ollama 服務（端口 11434）
- ✅ 模型數據持久化存儲（使用 Docker Volume）

### 2. 新增設置頁面
- ✅ 訪問路徑：http://localhost:5788/settings
- ✅ 功能：
  - 查看已安裝的 Ollama 模型列表
  - 一鍵下載推薦模型（Llama 2, Llama 3.2, Mistral, Qwen 2.5）
  - 自定義下載任意 Ollama 模型
  - 刪除不需要的模型
  - 設置默認分析模型

### 3. 推薦模型

| 模型名稱 | 大小 | 特點 | 適用場景 |
|---------|------|------|---------|
| llama2 | ~3.8GB | Meta 出品，平衡性好 | 入門推薦 |
| llama3.2 | ~2GB | 最新版本，響應快 | 快速分析 |
| mistral | ~4.1GB | 高質量輸出 | 專業分析 |
| qwen2.5:7b | ~4.4GB | 阿里巴巴，中文優化 | 中文股市分析 |

## 部署步驟

### 1. 重新構建 Docker 鏡像

```bash
cd e:\taiwan-stock-app
docker-compose down
docker-compose build --no-cache pecunianexus
docker-compose up -d
```

### 2. 檢查服務狀態

```bash
# 查看容器狀態
docker ps

# 查看 Ollama 日誌
docker exec pecunianexus cat /tmp/ollama.log

# 查看應用日誌
docker logs pecunianexus --tail=50
```

### 3. 訪問設置頁面

打開瀏覽器訪問：http://localhost:5788/settings

### 4. 下載模型

**方式一：快速下載（推薦）**
- 點擊推薦模型卡片（如 Llama 2）
- 等待下載完成（首次下載約需 5-10 分鐘，取決於網速）

**方式二：自定義下載**
- 在輸入框輸入模型名稱（如 `codellama:7b`）
- 點擊「下載模型」按鈕
- 完整模型列表：https://ollama.com/library

### 5. 設置默認模型

- 在已安裝模型列表中
- 點擊「設為默認」按鈕
- 該模型將用於所有股票分析

## 配置說明

### Docker Compose 更新
```yaml
services:
  pecunianexus:
    ports:
      - "5788:5788"   # Flask Web 應用
      - "11434:11434" # Ollama API (可選對外暴露)
    environment:
      - OLLAMA_HOST=http://localhost:11434
    volumes:
      - ollama-models:/root/.ollama  # 模型持久化存儲
```

### Dockerfile 更新
- 安裝 Ollama 二進制文件
- 創建啟動腳本同時運行 Ollama 和 Flask
- 暴露 11434 端口

## 使用示例

### 1. 自動股票分析
1. 登入系統（test001 / 123456）
2. 搜尋股票代碼（如 2330）
3. AI 助手會自動使用配置的默認模型進行分析
4. 分析內容包括：
   - 價格位置分析（年度高低點）
   - 技術指標解讀（RSI, MACD, KD, 布林通道）
   - 財務數據評估
   - 最新新聞摘要
   - 買賣建議和目標價位

### 2. 更換分析模型
1. 訪問設置頁面
2. 下載新模型（如 mistral）
3. 設置為默認模型
4. 返回首頁重新分析股票

## 故障排除

### 模型下載失敗
```bash
# 進入容器手動下載
docker exec -it pecunianexus bash
ollama pull llama2
```

### Ollama 服務未啟動
```bash
# 查看 Ollama 日誌
docker exec pecunianexus cat /tmp/ollama.log

# 重啟容器
docker-compose restart pecunianexus
```

### 分析失敗提示
- 確認已下載至少一個模型
- 確認默認模型已設置
- 查看容器日誌排查錯誤

## API 參考

### 獲取模型列表
```http
GET /api/ollama/models
```

### 下載模型
```http
POST /api/ollama/models/pull
Content-Type: application/json

{
  "model_name": "llama2"
}
```

### 刪除模型
```http
POST /api/ollama/models/delete
Content-Type: application/json

{
  "model_name": "llama2"
}
```

### 獲取默認模型
```http
GET /api/ollama/default-model
```

### 設置默認模型
```http
POST /api/ollama/default-model
Content-Type: application/json

{
  "model_name": "llama2"
}
```

## 性能考量

### 磁盤空間
- 每個 7B 模型約需 4GB 空間
- 建議預留至少 20GB 用於模型存儲

### 內存要求
- 運行 7B 模型需要至少 8GB RAM
- 推薦 16GB RAM 以獲得更好性能

### CPU/GPU
- CPU 模式可運行，但速度較慢
- 有 GPU 的環境可以顯著提升推理速度

## 更新歷史

- **v3.0** (2026-01-16)
  - Ollama 完全集成到 Docker
  - 新增模型管理設置頁面
  - 支持自定義默認模型
  - 模型數據持久化

- **v2.0** (2026-01-15)
  - 初始 Ollama 支持（需主機安裝）
  - 自動股票分析功能
  - 財務數據爬蟲
  - 新聞聚合
