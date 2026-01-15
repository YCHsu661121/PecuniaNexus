# 使用 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴和 TA-Lib C 庫
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && apt-get remove -y wget build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 建立資料庫目錄
RUN mkdir -p /app/data

# 暴露端口
EXPOSE 5788

# 設定環境變數
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# 啟動應用程式
CMD ["python", "app.py"]
