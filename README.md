# 🤖 AI 智慧選股高手 / AI Smart Stock Picker

> 運用 TA-Lib 技術分析與 AI 輔助您的投資決策，提供台灣股市即時資訊查詢與專業技術指標分析
> 
> TA-Lib powered technical analysis and AI-assisted investment decision tool providing real-time Taiwan stock market information and professional technical indicators

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![TA-Lib](https://img.shields.io/badge/TA--Lib-0.4.28-orange.svg)](https://ta-lib.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

📅 **最後更新**: 2026-01-16

---

## 📖 語言 / Language

- [繁體中文](#繁體中文)
- [English](#english)

---

## 繁體中文

### ✨ 核心功能

#### 🎯 核心查詢功能
- **即時股價查詢**：透過台灣證券交易所 API 獲取最新股價資訊
- **歷史資料分析**：提供每月歷史交易數據與趨勢分析
- **TA-Lib 技術指標**：
  - 📊 **K線圖 + 移動平均線（MA5/10/20/60）**
  - 📈 **布林通道（Bollinger Bands）**：上中下軌道
  - 📦 **成交量分析 + VOL MA**：量能趨勢判斷
  - 📉 **RSI + MACD 指標**：相對強弱與趨勢背離分析
- **專業技術分析**：
  - RSI（相對強弱指標）：6日/12日
  - MACD（移動平均收斂發散）：快線/慢線/柱狀圖
  - ATR（真實波動幅度）
  - KD 指標（隨機指標）
- **📰 即時新聞整合**：自動抓取 Google News 相關股票新聞

#### 👥 使用者系統
- **帳號註冊/登入**：多用戶支援，每位使用者擁有獨立空間
- **個人收藏夾**：儲存並快速查詢最愛股票
- **自動載入最愛**：登入後自動顯示第一支最愛股票
- **SHA256 密碼加密**：確保帳戶安全性
- **會話管理**：記住登入狀態

#### 👑 管理員特權
- **首位註冊自動升級**：第一個註冊的使用者自動成為管理員
- **全域收藏查看**：管理員可以查看所有使用者的收藏股票
- **使用者數據統計**：了解系統整體使用情況

#### 🌐 多語言支援
- **中英文切換**：一鍵切換介面語言
- **完整雙語翻譯**：所有文字、按鈕、提示訊息均支援雙語

#### 🌙 深色護眼模式
- **深色主題設計**：降低眼睛疲勞，適合長時間使用

#### ⚡ 自動更新功能
- **5秒自動刷新**：即時追蹤股價變化
- **倒數計時顯示**：清楚掌握更新時間
- **一鍵開關**：彈性控制更新狀態
- **高對比配色**：確保資訊清晰易讀
- **現代化 UI**：流暢動畫與漸變效果

### 🚀 快速開始

#### 方式一：Docker Compose（推薦）

```bash
# 克隆專案
git clone https://github.com/YCHsu661121/PecuniaNexus.git
cd PecuniaNexus

# 啟動服務
docker compose up -d

# 存取應用程式
# 開啟瀏覽器訪問 http://localhost:5788
```

#### 方式二：本地 Python 環境

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動應用
python app.py

# 存取應用程式
# 開啟瀏覽器訪問 http://localhost:5788
```

### 📊 使用說明

1. **註冊/登入**
   - 首次使用請註冊帳號（首位註冊者自動成為管理員）
   - 密碼至少需要 6 個字元

2. **查詢股票**
   - 在搜尋框輸入股票代碼（例如：2330）
   - 點擊熱門股票標籤快速查詢

3. **切換圖表類型**
   - 📊 K線圖：詳細的價格走勢分析
   - 📈 高低曲線：簡化的趨勢視圖

4. **管理收藏**
   - 查詢股票後點擊「加入最愛」
   - 點擊「載入我的最愛」快速查看收藏股票

5. **切換語言**
   - 點擊右上角語言按鈕（中文/English）

### 🔥 熱門股票代碼

- **2330** 台積電 (TSMC)
- **2317** 鴻海 (Foxconn)
- **2454** 聯發科 (MediaTek)
- **2412** 中華電 (Chunghwa Telecom)
- **2882** 國泰金 (Cathay Financial)
- **2303** 聯電 (UMC)

### 🛠️ 技術架構

#### 後端技術
- **框架**: Python Flask 3.0
- **資料庫**: PostgreSQL 16 (主要) / SQLite 3 (備援)
- **資料庫驅動**: psycopg 3.1.18
- **加密**: SHA256 密碼雜湊
- **資料來源**: 台灣證券交易所 API + Google News RSS

#### 前端技術
- **基礎**: HTML5 + CSS3 + JavaScript ES6+
- **圖表庫**: ECharts 5.x
- **設計**: 深色主題 + 漸層效果 + 響應式佈局

#### 部署方案
- **容器化**: Docker + Docker Compose
- **健康檢查**: PostgreSQL 啟動依賴管理
- **資料持久化**: Docker Volume

### 📡 API 端點

#### 認證相關
- `POST /api/register` - 使用者註冊
- `POST /api/login` - 使用者登入

#### 股票查詢
- `GET /api/stock/<code>` - 查詢即時股價
- `GET /api/stock/history/<code>` - 查詢歷史原始資料
- `GET /api/stock/indicators/<code>` - 查詢 TA-Lib 技術指標（MA, RSI, MACD, BOLL, KD, ATR）
- `GET /api/news/<code>` - 查詢相關新聞

#### 收藏管理
- `GET /api/favorites` - 取得收藏清單
- `POST /api/favorites` - 新增收藏
- `DELETE /api/favorites/<code>` - 刪除收藏

### 📊 TA-Lib 技術指標

系統使用 TA-Lib 0.4.28 提供以下專業技術指標：

#### 趨勢指標
- **SMA（簡單移動平均）**: MA5, MA10, MA20, MA60
- **MACD（移動平均收斂發散）**: 快線、慢線、柱狀圖
- **Bollinger Bands（布林通道）**: 上軌、中軌、下軌

#### 動量指標
- **RSI（相對強弱指標）**: RSI6, RSI12
- **Stochastic（KD 指標）**: %K, %D

#### 波動率指標
- **ATR（真實波動幅度均值）**: 14日 ATR
- **Volume MA（成交量移動平均）**: VOL MA5, VOL MA10

### 🗄️ 資料庫架構

#### users 表
- `id` (INTEGER) - 使用者 ID
- `user_id` (TEXT) - 使用者帳號
- `password_hash` (TEXT) - SHA256 密碼雜湊
- `is_admin` (INTEGER) - 管理員標記
- `created_at` (TIMESTAMP) - 建立時間

#### favorites 表
- `id` (INTEGER) - 紀錄 ID
- `user_id` (TEXT) - 使用者帳號
- `stock_code` (TEXT) - 股票代碼
- `stock_name` (TEXT) - 股票名稱
- `added_at` (TIMESTAMP) - 新增時間

### 🔒 安全性

- ✅ SHA256 密碼雜湊加密
- ✅ SQL 參數化查詢防注入
- ✅ 會話管理機制
- ✅ Docker 容器隔離

### 🎯 未來規劃

- [x] 技術指標分析（MA、RSI、MACD、BOLL、KD、ATR）✨
- [ ] 價格提醒功能
- [ ] 多股票比較視圖
- [ ] 投資組合追蹤
- [ ] 匯出報表功能
- [ ] AI 選股建議

---

## English

### ✨ Core Features

#### 🎯 Stock Query Functions
- **Real-time Stock Prices**: Fetch latest stock information via Taiwan Stock Exchange API
- **Historical Data Analysis**: Monthly historical trading data and trend analysis
- **Multiple Visualization Charts**:
  - 📊 **K-Line Chart (Candlestick)**: Display open, high, low, close prices
  - 📈 **High-Low Line Chart**: Historical price trend lines
  - One-click chart type switching
- **📰 Real-time News Integration**: Auto-fetch related stock news from Google News

#### 👥 User System
- **Account Registration/Login**: Multi-user support with independent user spaces
- **Personal Favorites**: Save and quickly query favorite stocks
- **SHA256 Password Encryption**: Ensure account security
- **Session Management**: Remember login status

#### 👑 Admin Privileges
- **First User Auto-Promotion**: First registered user automatically becomes admin
- **Global Favorites View**: Admins can view all users' favorite stocks
- **User Statistics**: Understand overall system usage

#### 🌐 Multi-Language Support
- **Chinese/English Toggle**: One-click interface language switching
- **Complete Bilingual Translation**: All text, buttons, and messages support both languages

#### 🌙 Dark Eye-Care Mode
- **Dark Theme Design**: Reduce eye fatigue for extended usage
- **High Contrast Colors**: Ensure clear and readable information
- **Modern UI**: Smooth animations and gradient effects

### 🚀 Quick Start

#### Method 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/YCHsu661121/PecuniaNexus.git
cd PecuniaNexus

# Start services
docker compose up -d

# Access the application
# Open browser and visit http://localhost:5788
```

#### Method 2: Local Python Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Start application
python app.py

# Access the application
# Open browser and visit http://localhost:5788
```

### 📊 Usage Guide

1. **Register/Login**
   - Register an account for first-time use (first user becomes admin automatically)
   - Password must be at least 6 characters

2. **Query Stocks**
   - Enter stock code in search box (e.g., 2330)
   - Click popular stock tags for quick queries

3. **Switch Chart Types**
   - 📊 K-Line Chart: Detailed price movement analysis
   - 📈 High-Low Line: Simplified trend view

4. **Manage Favorites**
   - Click "Add to Favorites" after querying a stock
   - Click "Load My Favorites" to quickly view saved stocks

5. **Switch Language**
   - Click language button in top-right corner (中文/English)

### 🔥 Popular Stock Codes

- **2330** TSMC (Taiwan Semiconductor)
- **2317** Hon Hai (Foxconn)
- **2454** MediaTek
- **2412** Chunghwa Telecom
- **2882** Cathay Financial Holdings
- **2303** United Microelectronics (UMC)

### 🛠️ Technology Stack

#### Backend
- **Framework**: Python Flask 3.0
- **Database**: PostgreSQL 16 (Primary) / SQLite 3 (Fallback)
- **Database Driver**: psycopg 3.1.18
- **Encryption**: SHA256 password hashing
- **Data Source**: Taiwan Stock Exchange API + Google News RSS

#### Frontend
- **Foundation**: HTML5 + CSS3 + JavaScript ES6+
- **Charts**: ECharts 5.x
- **Design**: Dark theme + Gradient effects + Responsive layout

#### Deployment
- **Containerization**: Docker + Docker Compose
- **Health Check**: PostgreSQL startup dependency management
- **Data Persistence**: Docker Volume

### 📡 API Endpoints

#### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

#### Stock Queries
- `GET /api/stock/<code>` - Query real-time stock price
- `GET /api/history/<code>` - Query historical data
- `GET /api/news/<code>` - Query related news

#### Favorites Management
- `GET /api/favorites` - Get favorites list
- `POST /api/favorites` - Add favorite
- `DELETE /api/favorites/<code>` - Remove favorite

### 🗄️ Database Schema

#### users Table
- `id` (INTEGER) - User ID
- `user_id` (TEXT) - User account
- `password_hash` (TEXT) - SHA256 password hash
- `is_admin` (INTEGER) - Admin flag
- `created_at` (TIMESTAMP) - Creation time

#### favorites Table
- `id` (INTEGER) - Record ID
- `user_id` (TEXT) - User account
- `stock_code` (TEXT) - Stock code
- `stock_name` (TEXT) - Stock name
- `added_at` (TIMESTAMP) - Added time

### 🔒 Security

- ✅ SHA256 password hash encryption
- ✅ SQL parameterized queries to prevent injection
- ✅ Session management mechanism
- ✅ Docker container isolation

### 🎯 Future Roadmap

- [ ] Technical indicators analysis (MA, RSI, MACD)
- [ ] Price alert notifications
- [ ] Multi-stock comparison view
- [ ] Investment portfolio tracking
- [ ] Export report functionality

---

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Contact

GitHub: [@YCHsu661121](https://github.com/YCHsu661121)
