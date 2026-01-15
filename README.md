# 台股即時查詢系統

一個使用 Docker 容器化的台灣股票市場即時查詢網頁應用程式。

## 功能特色

- 📈 即時股票資訊查詢
- 📊 歷史交易資料顯示
- 🎨 美觀的使用者介面
- 🚀 快速查詢熱門股票
- 🐳 Docker 容器化部署

## 系統需求

- Docker
- Docker Compose (可選)

## 快速開始

### 方法 1: 使用 Docker Compose（推薦）

1. 啟動應用程式：
```bash
cd PecuniaNexus
docker-compose up -d
```

2. 開啟瀏覽器訪問：
```
http://localhost:5788
```

3. 停止應用程式：
```bash
docker-compose down
```

### 方法 2: 使用 Docker

1. 建立 Docker 映像：
```bash
docker build -t pecunianexus .
```

2. 執行容器：
```bash
docker run -d -p 5788:5788 --name pecunianexus pecunianexus
```

3. 開啟瀏覽器訪問：
```
http://localhost:5788
```

4. 停止容器：
```bash
docker stop pecunianexus
docker rm pecunianexus
```

## 使用說明

1. 在搜尋框中輸入股票代碼（例如：2330）
2. 點擊「查詢」按鈕或按 Enter 鍵
3. 查看即時股票資訊和歷史資料
4. 也可以點擊熱門股票快速查詢

## 熱門股票代碼

- 2330 台積電
- 2317 鴻海
- 2454 聯發科
- 2412 中華電
- 2882 國泰金
- 2303 聯電

## 資料來源

- 台灣證券交易所（TWSE）公開 API

## 技術架構

- **後端**: Python Flask
- **前端**: HTML5 + CSS3 + JavaScript
- **容器化**: Docker
- **API**: 台灣證券交易所公開資料

## 專案結構

```
PecuniaNexus/
├── app.py              # Flask 應用程式主檔案
├── templates/
│   └── index.html      # 前端網頁模板
├── Dockerfile          # Docker 映像檔定義
├── docker-compose.yml  # Docker Compose 設定
├── requirements.txt    # Python 套件需求
└── README.md          # 專案說明文件
```

## 注意事項

- 股票資料來自台灣證券交易所公開 API
- 資料更新時間依台灣證交所而定
- 非交易時間可能無法獲取即時資料
- 僅供參考，不構成投資建議

## License

MIT License
