# PecuniaNexus - 台股即時查詢系統

一個功能完整的台灣股票市場即時查詢與分析平台，支援多用戶管理、圖表分析與新聞追蹤。

## ✨ 功能特色

### 核心功能
- 📈 **即時股票資訊查詢** - 查詢台股即時價格、開高低收與成交量
- 📊 **雙圖表模式** - K線圖與高低曲線圖即時切換
- 📰 **新聞整合** - 自動抓取股票相關新聞（Google News RSS）
- 🎨 **美觀介面** - 現代化 UI 設計，響應式佈局

### 用戶系統
- 🔐 **註冊與登入** - SHA256 密碼加密，安全可靠
- 👑 **管理員機制** - 首位註冊用戶自動成為管理員
- 💖 **個人最愛** - 收藏常用股票，快速查詢
- 👥 **多帳號支援** - 每位用戶獨立管理最愛清單

### 管理員特權
- 📊 **全域監控** - 查看所有用戶的最愛股票
- 📈 **用戶分析** - 了解熱門關注股票
- 🔍 **數據透明** - 分組顯示各用戶收藏

### 技術特性
- 🗄️ **PostgreSQL 資料庫** - 穩定可靠的數據儲存
- 🐳 **Docker 容器化** - 一鍵部署，環境隔離
- 🔄 **SQLite 備援** - 未設定資料庫時自動降級
- 📉 **ECharts 視覺化** - 專業級圖表展示

## 🖥️ 系統需求

- Docker & Docker Compose
- 或 Python 3.11+ (本機運行模式)

## 🚀 快速開始

### 方法 1: Docker Compose（推薦）

```bash
cd PecuniaNexus
docker compose up -d
```

訪問：http://localhost:5788

停止服務：
```bash
docker compose down
```

### 方法 2: 本機 Python（SQLite 模式）

```bash
pip install -r requirements.txt
python app.py
```

## 📖 使用說明

### 首次使用
1. 開啟 http://localhost:5788
2. 點擊「✨ 註冊」建立帳號（首位註冊者為管理員）
3. 使用帳號密碼登入系統

### 查詢股票
1. 輸入股票代碼（例：2330）
2. 查看即時資訊、價格走勢
3. 點擊「📊 K線圖」或「📈 高低曲線」切換圖表
4. 右側查看相關新聞報導

### 管理最愛
1. 查詢股票後點擊「加入最愛」按鈕
2. 點擊「💖 載入我的最愛」查看收藏
3. 管理員可查看所有用戶的最愛清單

## 🔥 熱門股票代碼

- 2330 台積電 (TSMC)
- 2317 鴻海 (Foxconn)
- 2454 聯發科 (MediaTek)
- 2412 中華電 (Chunghwa Telecom)
- 2882 國泰金 (Cathay Financial)
- 2303 聯電 (UMC)

## 🛠️ 技術架構

### 後端
- **框架**: Python Flask 3.0
- **資料庫**: PostgreSQL 16 (主) / SQLite 3 (備)
- **ORM**: psycopg 3.1 (PostgreSQL adapter)
- **API**: 台灣證券交易所公開資料

### 前端
- **基礎**: HTML5 + CSS3 + JavaScript (ES6+)
- **圖表**: ECharts 5.x
- **設計**: 漸層背景、卡片式佈局、響應式網格

### 容器化
- **服務編排**: Docker Compose
- **應用容器**: Python 3.11-slim
- **資料庫容器**: PostgreSQL 16-alpine
- **持久化**: Docker Volumes

## 📁 專案結構

```
PecuniaNexus/
├── app.py                  # Flask 主程式 (API 端點、資料庫邏輯)
├── templates/
│   └── index.html          # 前端 SPA (含圖表與新聞模組)
├── Dockerfile              # 應用容器定義
├── docker-compose.yml      # 服務編排設定 (含 PostgreSQL)
├── requirements.txt        # Python 依賴清單
├── .gitignore              # Git 忽略規則
└── README.md               # 專案說明文件
```

## 🔗 API 端點

### 股票查詢
- `GET /api/stock/<code>` - 取得即時股票資訊
- `GET /api/stock/history/<code>` - 取得歷史交易資料
- `GET /api/news/<code>` - 取得股票相關新聞

### 用戶系統
- `POST /api/register` - 用戶註冊
- `POST /api/login` - 用戶登入

### 最愛管理
- `GET /api/favorites?user_id=<id>` - 取得最愛清單（管理員可查看全部）
- `POST /api/favorites` - 新增最愛股票
- `GET /api/favorites/last?user_id=<id>` - 取得最後一筆最愛
- `DELETE /api/favorites/<id>` - 刪除最愛

### 其他
- `GET /api/watchlist` - 取得關注清單
- `POST /api/watchlist` - 新增關注股票
- `DELETE /api/watchlist/<id>` - 刪除關注
- `GET /api/history` - 取得查詢歷史
- `POST /api/history` - 新增查詢記錄
- `GET /api/categories` - 取得股票分類

## ⚙️ 環境變數

| 變數 | 說明 | 預設值 |
|------|------|--------|
| `DATABASE_URL` | PostgreSQL 連線字串 | 無（使用 SQLite） |
| `FLASK_ENV` | Flask 環境模式 | `development` |

範例（docker-compose.yml 已設定）：
```yaml
DATABASE_URL=postgresql://app:appsecret@postgres:5432/pecunia
```

## 📊 資料庫結構

### users（用戶表）
- `id` - 主鍵
- `user_id` - 用戶帳號（唯一）
- `password_hash` - SHA256 加密密碼
- `is_admin` - 管理員標記
- `created_at` - 建立時間

### favorites（最愛表）
- `id` - 主鍵
- `user_id` - 用戶帳號
- `stock_code` - 股票代碼
- `stock_name` - 股票名稱
- `liked_time` - 收藏時間

### watchlist（關注表）
- `id` - 主鍵
- `stock_code` - 股票代碼
- `stock_name` - 股票名稱
- `category` - 分類
- `added_time` - 加入時間

### search_history（查詢歷史）
- `id` - 主鍵
- `stock_code` - 股票代碼
- `stock_name` - 股票名稱
- `search_time` - 查詢時間

## 🔒 安全性

- ✅ 密碼使用 SHA256 雜湊儲存
- ✅ SQL 參數化查詢防止注入
- ✅ HTTPS 可透過反向代理啟用
- ✅ 環境變數管理敏感資訊

## 🌐 資料來源

- **即時資訊**: 台灣證券交易所（TWSE）mis API
- **歷史資料**: 台灣證券交易所 STOCK_DAY API
- **新聞來源**: Google News RSS Feed

## ⚠️ 注意事項

- 📅 資料更新時間依台灣證交所而定
- 🕒 非交易時間可能無法獲取即時資料
- 💡 僅供參考，不構成投資建議
- 🔐 首位註冊用戶自動成為管理員，請妥善保管帳號

## 🎯 未來規劃

- [ ] 技術指標計算（RSI、MACD、KD 等）
- [ ] 自選股價提醒（價格突破通知）
- [ ] 多股票比較功能
- [ ] 匯出報表（PDF/Excel）
- [ ] WebSocket 即時推送
- [ ] 行動版 App

## 📄 授權

MIT License

---

**專案名稱**: PecuniaNexus  
**意涵**: Pecunia（拉丁語：金錢） + Nexus（連結），金融數據的智慧樞紐  
**開發年份**: 2026
