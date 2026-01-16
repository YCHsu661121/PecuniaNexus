# 台灣股票 AI 分析系統 - 完整使用指南

## 🚀 最新功能：Ollama 本地 AI 自動分析

系統已整合 **Ollama 本地 AI**，可自動分析股票並提供買賣建議！

### ✨ 新功能亮點

1. **自動 AI 分析**：搜尋股票後自動觸發深度分析
2. **完整數據整合**：
   - 一年內最高/最低價分析
   - 技術指標（RSI、MACD、KD、布林通道）
   - 財務報表數據（本益比、EPS、ROE）
   - 最新新聞資訊
3. **智能建議**：AI 自動生成買入/賣出建議和價位
4. **本地免費**：使用 Ollama 完全免費，無 API 費用

---

## 📋 系統架構

```
┌─────────────────────────────────────────┐
│         台灣股票 AI 分析系統            │
├─────────────────────────────────────────┤
│                                         │
│  🔍 股票查詢 → 📊 K線圖表              │
│       ↓                                 │
│  🤖 AI 自動分析                        │
│       ↓                                 │
│  📈 買賣建議                            │
│                                         │
├─────────────────────────────────────────┤
│  數據來源：                             │
│  • 證交所 API（即時行情）               │
│  • Yahoo 財經（新聞）                   │
│  • Goodinfo（財務數據）                 │
├─────────────────────────────────────────┤
│  AI 引擎：                              │
│  • Ollama（本地，免費）  ← 優先使用    │
│  • OpenAI GPT（雲端，付費）             │
│  • Google Gemini（雲端，免/付費）       │
└─────────────────────────────────────────┘
```

---

## 🛠️ 快速啟動（3 步驟）

### 步驟 1：安裝 Ollama（推薦）

**Windows：**
```powershell
# 1. 下載 Ollama
# 訪問：https://ollama.com/download/windows
# 安裝 OllamaSetup.exe

# 2. 安裝 AI 模型
ollama pull llama2

# 3. 驗證安裝
ollama list
```

**macOS/Linux：**
```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# 安裝模型
ollama pull llama2
```

### 步驟 2：啟動 Docker 容器

```powershell
# 切換到項目目錄
cd E:\taiwan-stock-app

# 啟動所有服務
docker-compose up -d

# 查看運行狀態
docker ps

# 查看應用日誌
docker logs pecunianexus --tail=30
```

### 步驟 3：訪問應用

打開瀏覽器訪問：**http://localhost:5788**

**測試帳號：**
- 帳號：`test001`
- 密碼：`123456`

---

## 📖 完整使用流程

### 1. 登入系統

![登入畫面]
- 輸入帳號和密碼
- 點擊「登入」按鈕

### 2. 搜尋股票

```
1. 在搜尋框輸入股票代碼（例如：2330）
2. 點擊「查詢」按鈕
3. 系統會顯示：
   - 即時股價資訊
   - K 線圖（含 MA5/MA10/MA20）
   - 成交量圖
   - 技術指標（RSI/MACD/KD/布林通道）
```

### 3. AI 自動分析

**✨ 自動觸發！無需手動操作**

搜尋股票後，AI 助手會自動：

1. **分析價格位置**
   - 計算當前價格在年度高低點的位置
   - 評估價格是偏高還是偏低

2. **技術指標解讀**
   - RSI 超買超賣訊號
   - MACD 趨勢判斷
   - KD 短期買賣訊號
   - 布林通道支撐壓力

3. **財務數據評估**
   - 本益比合理性
   - EPS 成長性
   - ROE 獲利能力

4. **新聞情緒分析**
   - 最新 3 條相關新聞
   - 市場情緒判斷

5. **生成操作建議**
   - 明確的買入/賣出/持有建議
   - 建議的買入價位
   - 建議的賣出價位
   - 風險提示

### 4. 查看分析結果

AI 分析結果會自動顯示在右側「AI 投資助手」面板：

```
📊 2330 - 台積電 完整分析

💰 價格分析：
當前價格：580.00 元
年度高點：625.00 元
年度低點：485.00 元
價格位置：67.9%

📰 最新新聞：
• 台積電宣布 3 奈米製程量產
• 法說會釋出正面訊息
• 外資持續加碼

🤖 AI 投資建議：
根據技術分析和基本面評估，目前台積電處於
相對合理價位...
[詳細建議內容]

建議操作：持有
買入價位：570 元以下
賣出價位：620 元以上
```

### 5. 管理關注清單

```
1. 點擊「+ 新增」按鈕
2. 輸入股票代碼
3. 點擊「確認新增」
4. 關注的股票會顯示在右側面板
5. 點擊股票代碼快速查詢
6. 點擊「刪除」移除關注
```

---

## 🎯 AI 提供者選擇

系統支援三種 AI 服務，優先順序：

### 1. **Ollama（推薦）** ⭐
- ✅ 完全免費
- ✅ 本地運行，隱私保護
- ✅ 無限次數使用
- ✅ 無網絡延遲
- ⚠️ 需要安裝 Ollama
- ⚠️ 需要 8GB+ RAM

### 2. **OpenAI GPT**
- ✅ 強大的分析能力
- ✅ 中文理解優秀
- ⚠️ 需要 API 金鑰
- ⚠️ 按使用量收費
- 💰 約 $0.002/次分析

### 3. **Google Gemini**
- ✅ 有免費層級
- ✅ 速度快
- ⚠️ 需要 API 金鑰
- ⚠️ 有使用配額限制

---

## 🔧 進階配置

### 配置 OpenAI（可選）

1. 創建 `.env` 文件：
```bash
cp .env.example .env
```

2. 編輯 `.env` 添加 API 金鑰：
```bash
OPENAI_API_KEY=sk-your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

3. 重啟容器：
```bash
docker-compose restart pecunianexus
```

### 配置 Ollama 連接

Docker 容器已配置好連接主機上的 Ollama：

```yaml
environment:
  - OLLAMA_HOST=http://host.docker.internal:11434
```

**Linux 用戶**需要修改為：
```yaml
  - OLLAMA_HOST=http://172.17.0.1:11434
```

---

## 📊 分析示例

### 案例 1：台積電（2330）

**搜尋後自動分析結果：**

```markdown
📊 2330 - 台積電 完整分析

💰 價格分析：
當前價格：580.00 元
年度高點：625.00 元
年度低點：485.00 元
價格位置：67.9%（相對偏高）

📈 技術指標：
- RSI(14)：62.5（中性偏強）
- MACD：0.85（多頭）
- KD：K=68, D=65（偏多）
- 布林通道：價格接近上軌（可能回調）

📰 最新新聞：
• 台積電3奈米製程量產順利
• 美國客戶訂單增加
• 外資目標價上調至650元

🤖 AI 投資建議：

**綜合評估：持有**

**分析要點：**
1. 價格位置：目前處於年度價格區間的 67.9%，
   屬於相對偏高但未過熱區域

2. 技術面：
   - RSI 未進入超買（70以上），仍有上漲空間
   - MACD 呈現多頭排列，趨勢向上
   - 價格接近布林通道上軌，短期可能震盪

3. 基本面：
   - 3奈米製程順利量產是重大利多
   - 美國客戶訂單增加支撐營收
   - 外資持續看好長期發展

**操作建議：**
- 已持有：繼續持有，設定停利 620 元
- 未持有：等待回調至 560-570 元區間再買入
- 風險控管：跌破 550 元停損

**今日預測：**
- 預估高點：590 元
- 預估低點：575 元
- 盤勢：震盪偏多

**風險提示：**
注意美股科技股走勢、台股大盤表現，以及
半導體產業庫存去化情況。
```

### 案例 2：鴻海（2317）

**自動分析：**

```markdown
📊 2317 - 鴻海 完整分析

💰 價格分析：
當前價格：105.50 元
年度高點：118.00 元
年度低點：92.00 元
價格位置：51.9%（中性）

🤖 AI 投資建議：買入

價格處於年度中位，技術指標顯示超賣反彈訊號，
建議分批買入...
```

---

## 🐛 常見問題

### Q1: Ollama 連接失敗怎麼辦？

**症狀：**
```
✗ Ollama 連接失敗: Connection refused
```

**解決方法：**
```powershell
# 1. 確認 Ollama 已啟動
ollama list

# 2. 檢查 Ollama 服務
# 瀏覽器訪問：http://localhost:11434

# 3. 重啟 Ollama
# Windows：關閉系統托盤的 Ollama 圖標後重新打開

# 4. 檢查防火牆設置
# 允許端口 11434 通過
```

### Q2: 沒有顯示 AI 分析結果？

**可能原因：**
1. Ollama 未安裝或未啟動
2. 沒有安裝 AI 模型
3. API 金鑰未配置

**解決方法：**
```powershell
# 安裝 Ollama 模型
ollama pull llama2

# 查看可用的 AI 提供者
# 登入後在 AI 助手查看下拉選單

# 查看容器日誌
docker logs pecunianexus --tail=50
```

### Q3: 分析速度很慢？

**優化方法：**
1. **使用 Ollama**：本地運行最快
2. **升級硬體**：至少 8GB RAM，SSD 硬碟
3. **使用較小模型**：
   ```bash
   ollama pull llama2:7b-chat-q4_0  # 量化版本
   ```
4. **GPU 加速**：NVIDIA GPU 自動支持

### Q4: 無法爬取財務數據或新聞？

**原因：**
- 網站反爬蟲機制
- 網絡連接問題
- 網站結構變更

**處理：**
- 系統會繼續使用技術指標進行分析
- 稍後重試或手動查看相關網站

### Q5: Docker 容器無法啟動？

**檢查步驟：**
```powershell
# 1. 查看容器狀態
docker ps -a

# 2. 查看日誌
docker logs pecunianexus
docker logs pecunianexus-postgres

# 3. 重建容器
docker-compose down
docker-compose up -d --build

# 4. 檢查端口占用
netstat -ano | findstr :5788
```

---

## 📚 API 文檔

### 股票數據 API

```http
GET /api/stock/{stock_code}
```

**Response:**
```json
{
  "success": true,
  "stock_code": "2330",
  "stock_name": "台積電",
  "current_price": "580.00",
  "kline_data": [...],
  "technical_indicators": {...}
}
```

### AI 分析 API

```http
GET /api/analyze/stock/{stock_code}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "stock_code": "2330",
    "stock_name": "台積電",
    "current_price": 580.0,
    "year_high": 625.0,
    "year_low": 485.0,
    "price_position": 67.9,
    "technical_indicators": {...},
    "financial_data": {...},
    "news": [...],
    "ai_recommendation": "詳細分析文字..."
  }
}
```

### 關注清單 API

```http
GET /api/favorites
POST /api/favorites
DELETE /api/favorites/{stock_code}
```

---

## 🔐 安全性

1. **密碼加密**：使用 SHA256 哈希存儲
2. **本地 AI**：數據不離開本機
3. **Docker 隔離**：容器化部署
4. **環境變數**：敏感信息不上傳 Git

---

## 📈 系統需求

### 最低配置
- CPU：4 核心
- RAM：8GB
- 硬碟：20GB
- 網絡：寬帶連接

### 推薦配置
- CPU：8 核心
- RAM：16GB
- 硬碟：SSD 40GB
- GPU：NVIDIA（可選）

---

## 🆘 技術支援

### 相關文檔
- [Ollama 設定指南](OLLAMA_SETUP.md)
- [AI 功能說明](AI_SETUP.md)
- [Docker 部署文檔](README.md)

### 聯絡方式
- GitHub Issues
- Email Support
- 線上文檔

---

## 📝 更新日誌

### v2.0.0 (2026-01-16)
- ✨ 整合 Ollama 本地 AI
- ✨ 自動股票分析功能
- ✨ 財務報表爬蟲
- ✨ 新聞資訊整合
- ✨ 一年歷史數據分析
- ✨ 智能買賣建議

### v1.0.0 (2026-01-15)
- 基礎股票查詢功能
- K 線圖表顯示
- 技術指標計算
- 關注清單管理

---

## ⚖️ 免責聲明

**重要提示：**

本系統提供的所有分析和建議僅供參考，不構成投資建議。

- 投資有風險，入市需謹慎
- AI 分析可能存在誤差
- 請自行承擔投資決策責任
- 建議結合專業投資顧問意見

使用本系統即表示您同意以上條款。

---

## 🎉 開始使用

1. 確保 Ollama 已安裝並運行
2. 啟動 Docker 容器
3. 訪問 http://localhost:5788
4. 登入並搜尋股票代碼
5. 查看 AI 自動分析結果
6. 根據建議做出投資決策

祝您投資順利！📈🚀
