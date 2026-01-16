# 使用 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝 Ollama 依賴套件
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    bash \
    zstd \
    && rm -rf /var/lib/apt/lists/*

# 下載並安裝 Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# 複製需求檔案
COPY requirements.txt .

# 安裝 Python 依賴套件
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# 複製應用程式檔案
COPY . .

# 建立資料庫目錄和 Ollama 模型目錄
RUN mkdir -p /app/data /root/.ollama

# 暴露端口 (Flask + Ollama)
EXPOSE 5788 11434

# 設定環境變數
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_HOST=http://localhost:11434

# 創建啟動腳本
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting Ollama service..."\n\
ollama serve > /tmp/ollama.log 2>&1 &\n\
sleep 5\n\
echo "Starting Flask application..."\n\
python app.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# 啟動應用程式 (啟動 Ollama 和 Flask)
CMD ["/bin/bash", "/app/start.sh"]
