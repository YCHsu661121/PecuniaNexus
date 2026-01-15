# 使用 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴和 TA-Lib C 庫
RUN apt-get update && apt-get install -y \
    wget \
    build-essential \
    gcc \
    g++ \
    make \
    python3-dev \
    && wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib ta-lib-0.4.0-src.tar.gz \
    && ldconfig

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴套件（需要在 build-essential 還在時安裝 TA-Lib）
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir numpy==1.26.4 \
    && pip install --no-cache-dir TA-Lib==0.4.28 \
    && pip install --no-cache-dir Flask==3.0.0 requests==2.31.0 Werkzeug==3.0.1 "psycopg[binary]==3.1.18"

# 清理編譯工具以減小映像大小
RUN apt-get remove -y wget \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

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
