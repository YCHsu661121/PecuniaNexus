from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import sqlite3
from contextlib import closing
import os
import hashlib
import pandas as pd
try:
    import ta
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: ta library not installed. Technical indicators will not be available.")

# AI API 支持
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai library not installed.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai library not installed.")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama library not installed.")

from bs4 import BeautifulSoup
import time

DB_URL = os.environ.get('DATABASE_URL', '').strip()
DB_IS_PG = DB_URL.startswith('postgres://') or DB_URL.startswith('postgresql://')

# AI API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434').strip()

# SQLite 数据库文件路径
SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'stocks.db')

if DB_IS_PG:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except Exception as e:
        raise RuntimeError(f"PostgreSQL support requires psycopg: {e}")

app = Flask(__name__)

# 初始化 AI 服務
if OLLAMA_AVAILABLE:
    try:
        ollama.Client(host=OLLAMA_HOST).list()
        print(f"✓ Ollama 已連接 ({OLLAMA_HOST})")
    except Exception as e:
        print(f"✗ Ollama 連接失敗: {e}")
        OLLAMA_AVAILABLE = False

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    print("✓ OpenAI API 已初始化")

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✓ Gemini API 已初始化")

# 初始化資料庫
def q(sql: str) -> str:
    # 轉換參數佔位符: SQLite 使用 ?, PostgreSQL 使用 %s
    if DB_IS_PG:
        return sql.replace('?', '%s')
    return sql


def get_conn():
    if DB_IS_PG:
        return psycopg.connect(DB_URL)
    else:
        # 确保 data 目录存在
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        return sqlite3.connect(SQLITE_DB_PATH)


def hash_password(password: str) -> str:
    """使用 SHA256 編碼密碼"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def check_user_is_admin(user_id: str) -> bool:
    """檢查使用者是否為管理員"""
    try:
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('SELECT is_admin FROM users WHERE user_id = ?'), (user_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                if DB_IS_PG:
                    return row.get('is_admin', False)
                else:
                    return bool(row['is_admin'])
    except Exception:
        return False


def init_db():
    with closing(get_conn()) as conn:
        # row 工廠設定（SQLite 使用 conn 層級，PG 使用 cursor 參數）
        if not DB_IS_PG:
            conn.row_factory = sqlite3.Row
        with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
            if DB_IS_PG:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS watchlist (
                        id SERIAL PRIMARY KEY,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        category TEXT NOT NULL,
                        added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS search_history (
                        id SERIAL PRIMARY KEY,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS favorites (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        liked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_fav_user_time ON favorites(user_id, liked_time)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        user_id TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_config (
                        config_key TEXT PRIMARY KEY,
                        config_value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            else:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS watchlist (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        category TEXT NOT NULL,
                        added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        stock_code TEXT NOT NULL,
                        stock_name TEXT,
                        liked_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_fav_user_time ON favorites(user_id, liked_time)
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL UNIQUE,
                        password_hash TEXT NOT NULL,
                        is_admin INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS app_config (
                        config_key TEXT PRIMARY KEY,
                        config_value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
            conn.commit()

init_db()

def get_twse_data(stock_code, years=5):
    """
    從台灣證券交易所獲取股票資料（多年份）
    """
    try:
        from dateutil.relativedelta import relativedelta
        import time
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        all_data = []
        current_date = datetime.now()
        
        # 計算起始日期（往前推 years 年）
        start_date = current_date - relativedelta(years=years)
        
        # 遍歷每個月
        temp_date = start_date
        while temp_date <= current_date:
            try:
                date_str = temp_date.strftime('%Y%m%d')
                url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date_str}&stockNo={stock_code}'
                
                response = requests.get(url, headers=headers, timeout=10)
                data = response.json()
                
                if data.get('stat') == 'OK' and data.get('data'):
                    all_data.extend(data['data'])
                
                # 避免請求過快，加入延遲
                time.sleep(0.5)
                
            except Exception as e:
                print(f"獲取 {date_str} 數據失敗: {e}")
            
            # 移到下個月
            temp_date = temp_date + relativedelta(months=1)
        
        if all_data:
            return {
                'success': True,
                'stock_code': stock_code,
                'data': all_data,
                'fields': ['日期', '成交股數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '成交筆數']
            }
        else:
            return {
                'success': False,
                'message': '查無此股票代碼或資料尚未更新'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'錯誤: {str(e)}'
        }

def get_stock_info(stock_code):
    """
    獲取即時股票資訊（使用 mis API）並包含歷史數據
    """
    try:
        url = f'https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_{stock_code}.tw'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('msgArray') and len(data['msgArray']) > 0:
            stock = data['msgArray'][0]
            result = {
                'success': True,
                'stock_code': stock.get('c', ''),
                'stock_name': stock.get('n', ''),
                'current_price': stock.get('z', '-'),
                'change': stock.get('y', '-'),
                'open': stock.get('o', '-'),
                'high': stock.get('h', '-'),
                'low': stock.get('l', '-'),
                'volume': stock.get('v', '-'),
                'time': stock.get('t', '')
            }
            
            # 獲取歷史數據用於 K 線圖
            history_data = get_twse_data(stock_code)
            if history_data.get('success') and history_data.get('data'):
                kline_data = []
                for row in history_data['data']:
                    try:
                        # TWSE 數據格式: [日期, 成交股數, 成交金額, 開盤價, 最高價, 最低價, 收盤價, 漲跌價差, 成交筆數]
                        date = row[0].replace('/', '-')
                        open_price = float(row[3].replace(',', ''))
                        high_price = float(row[4].replace(',', ''))
                        low_price = float(row[5].replace(',', ''))
                        close_price = float(row[6].replace(',', ''))
                        volume = float(row[1].replace(',', ''))
                        
                        kline_data.append([date, open_price, close_price, low_price, high_price, volume])
                    except (ValueError, IndexError):
                        continue
                
                result['kline_data'] = kline_data
                
                # 計算技術指標
                if kline_data and len(kline_data) > 0:
                    result['technical_indicators'] = calculate_technical_indicators(kline_data)
            
            return result
        else:
            return {
                'success': False,
                'message': '查無此股票代碼'
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'錯誤: {str(e)}'
        }


def calculate_technical_indicators(kline_data):
    """
    計算技術指標
    """
    try:
        if not TALIB_AVAILABLE or len(kline_data) < 20:
            return {}
        
        # 提取收盤價
        closes = [item[2] for item in kline_data]
        highs = [item[4] for item in kline_data]
        lows = [item[3] for item in kline_data]
        
        df = pd.DataFrame({
            'close': closes,
            'high': highs,
            'low': lows
        })
        
        indicators = {}
        
        # RSI
        try:
            rsi = ta.momentum.RSIIndicator(df['close'], window=14)
            indicators['RSI'] = float(rsi.rsi().iloc[-1])
        except:
            pass
        
        # MACD
        try:
            macd = ta.trend.MACD(df['close'])
            indicators['MACD'] = float(macd.macd().iloc[-1])
            indicators['MACD_SIGNAL'] = float(macd.macd_signal().iloc[-1])
        except:
            pass
        
        # 布林通道
        try:
            bollinger = ta.volatility.BollingerBands(df['close'])
            indicators['BB_UPPER'] = float(bollinger.bollinger_hband().iloc[-1])
            indicators['BB_MIDDLE'] = float(bollinger.bollinger_mavg().iloc[-1])
            indicators['BB_LOWER'] = float(bollinger.bollinger_lband().iloc[-1])
        except:
            pass
        
        # KD
        try:
            stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'])
            indicators['KD_K'] = float(stoch.stoch().iloc[-1])
            indicators['KD_D'] = float(stoch.stoch_signal().iloc[-1])
        except:
            pass
        
        return indicators
    except Exception as e:
        print(f"計算技術指標失敗: {e}")
        return {}
@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """
    API 端點：獲取關注清單
    """
    try:
        category = request.args.get('category', '')
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                if category:
                    cursor.execute(q('SELECT * FROM watchlist WHERE category = ? ORDER BY added_time DESC'), (category,))
                else:
                    cursor.execute('SELECT * FROM watchlist ORDER BY added_time DESC')
                
                rows = cursor.fetchall()
                if DB_IS_PG:
                    watchlist = rows
                else:
                    watchlist = [dict(row) for row in rows]
                
        return jsonify({'success': True, 'data': watchlist})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watchlist', methods=['POST'])
def add_to_watchlist():
    """
    API 端點：添加股票到關注清單
    """
    try:
        data = request.json
        stock_code = data.get('stock_code', '').strip()
        category = data.get('category', '').strip()
        
        if not stock_code or not category:
            return jsonify({'success': False, 'message': '股票代碼和分類不能為空'})
        
        # 獲取股票名稱
        stock_info = get_stock_info(stock_code)
        stock_name = stock_info.get('stock_name', '') if stock_info.get('success') else ''
        
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                # 檢查是否已存在
                cursor.execute(q('SELECT id FROM watchlist WHERE stock_code = ?'), (stock_code,))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': '此股票已在關注清單中'})
                
                # 添加到資料庫
                cursor.execute(q('INSERT INTO watchlist (stock_code, stock_name, category) VALUES (?, ?, ?)'), (stock_code, stock_name, category))
                conn.commit()
                
        return jsonify({'success': True, 'message': '已成功添加到關注清單'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/watchlist/<int:id>', methods=['DELETE'])
def delete_from_watchlist(id):
    """
    API 端點：從關注清單刪除股票
    """
    try:
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('DELETE FROM watchlist WHERE id = ?'), (id,))
                conn.commit()
                
        return jsonify({'success': True, 'message': '已從關注清單移除'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/history', methods=['GET'])
def get_search_history():
    """
    API 端點：獲取查詢歷史
    """
    try:
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute('SELECT * FROM search_history ORDER BY search_time DESC LIMIT 50')
                rows = cursor.fetchall()
                history = rows if DB_IS_PG else [dict(row) for row in rows]
                
        return jsonify({'success': True, 'data': history})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/history', methods=['POST'])
def add_search_history():
    """
    API 端點：添加查詢歷史
    """
    try:
        data = request.json
        stock_code = data.get('stock_code', '').strip()
        stock_name = data.get('stock_name', '').strip()
        
        if not stock_code:
            return jsonify({'success': False, 'message': '股票代碼不能為空'})
        
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('INSERT INTO search_history (stock_code, stock_name) VALUES (?, ?)'), (stock_code, stock_name))
                conn.commit()
                
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """
    API 端點：獲取所有分類
    """
    categories = [
        '半導體',
        '電子零組件',
        '電腦及週邊',
        '光電',
        '通信網路',
        '電子通路',
        '金融保險',
        '航運',
        '鋼鐵',
        '塑膠',
        '食品',
        '生技醫療',
        '其他'
    ]
    return jsonify({'success': True, 'data': categories})


@app.route('/api/news/<stock_code>')
def get_stock_news(stock_code):
    """
    API 端點：獲取股票相關新聞
    """
    try:
        news_list = []
        
        # 獲取股票名稱
        stock_info = get_stock_info(stock_code)
        stock_name = stock_info.get('stock_name', stock_code) if stock_info.get('success') else stock_code
        
        # Google News RSS (台股新聞)
        search_term = f"{stock_code} {stock_name} 台股"
        google_news_url = f'https://news.google.com/rss/search?q={search_term}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant'
        
        try:
            response = requests.get(google_news_url, timeout=10)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item')[:10]:  # 取前10則
                    title = item.find('title')
                    link = item.find('link')
                    pub_date = item.find('pubDate')
                    
                    if title is not None and link is not None:
                        news_list.append({
                            'title': title.text,
                            'link': link.text,
                            'date': pub_date.text if pub_date is not None else '',
                            'source': 'Google News'
                        })
        except Exception as e:
            print(f"Google News fetch error: {e}")
        
        # 如果沒有新聞，返回預設訊息
        if not news_list:
            news_list.append({
                'title': f'暫無 {stock_code} {stock_name} 相關新聞',
                'link': f'https://www.google.com/search?q={stock_code}+{stock_name}+新聞',
                'date': '',
                'source': '搜尋建議'
            })
        
        return jsonify({'success': True, 'data': news_list})
    except Exception as e:
        return jsonify({'success': False, 'message': f'獲取新聞失敗: {str(e)}'})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_page():
    return '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API 测试</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        input, button { padding: 10px; margin: 5px; }
        .result { background: #f5f5f5; padding: 10px; margin-top: 10px; border-radius: 3px; white-space: pre-wrap; }
        button { background: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🧪 登入/註冊 API 測試</h1>
    
    <div class="test-section">
        <h3>註冊測試</h3>
        <input type="text" id="regUserId" placeholder="使用者 ID" value="testuser">
        <input type="password" id="regPassword" placeholder="密碼" value="123456">
        <button onclick="testRegister()">測試註冊</button>
        <div class="result" id="regResult"></div>
    </div>

    <div class="test-section">
        <h3>登入測試</h3>
        <input type="text" id="loginUserId" placeholder="使用者 ID" value="testuser">
        <input type="password" id="loginPassword" placeholder="密碼" value="123456">
        <button onclick="testLogin()">測試登入</button>
        <div class="result" id="loginResult"></div>
    </div>

    <script>
        async function testRegister() {
            const userId = document.getElementById('regUserId').value;
            const password = document.getElementById('regPassword').value;
            const resultDiv = document.getElementById('regResult');
            
            try {
                resultDiv.textContent = '正在註冊...';
                const res = await fetch('/api/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, password: password })
                });
                const data = await res.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                resultDiv.textContent = '錯誤: ' + e.message;
            }
        }

        async function testLogin() {
            const userId = document.getElementById('loginUserId').value;
            const password = document.getElementById('loginPassword').value;
            const resultDiv = document.getElementById('loginResult');
            
            try {
                resultDiv.textContent = '正在登入...';
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, password: password })
                });
                const data = await res.json();
                resultDiv.textContent = JSON.stringify(data, null, 2);
            } catch (e) {
                resultDiv.textContent = '錯誤: ' + e.message;
            }
        }
    </script>
</body>
</html>'''

@app.route('/api/stock/<stock_code>')
def get_stock(stock_code):
    """
    API 端點：獲取股票即時資訊
    """
    result = get_stock_info(stock_code)
    return jsonify(result)

@app.route('/api/stock/history/<stock_code>')
def get_stock_history(stock_code):
    """
    API 端點：獲取股票歷史資料
    """
    result = get_twse_data(stock_code)
    return jsonify(result)


@app.route('/api/stock/indicators/<stock_code>')
def get_stock_indicators(stock_code):
    """
    API 端點：使用 ta 庫計算技術指標
    返回 K 線數據 + MA + RSI + MACD + BOLL 等指標
    """
    if not TALIB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'ta library not installed'
        })
    
    try:
        # 獲取原始歷史數據
        raw_data = get_twse_data(stock_code)
        if not raw_data.get('success') or not raw_data.get('data'):
            return jsonify(raw_data)
        
        data = raw_data['data']
        if len(data) < 60:  # 至少需要 60 天數據計算 MA60
            return jsonify({
                'success': False,
                'message': '歷史數據不足 (需要至少 60 天)'
            })
        
        # 轉換為 DataFrame
        df = pd.DataFrame(data, columns=['date', 'volume', 'amount', 'open', 'high', 'low', 'close'])
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # 計算技術指標
        # 1. 移動平均線 (MA)
        df['ma5'] = ta.trend.sma_indicator(df['close'], window=5)
        df['ma10'] = ta.trend.sma_indicator(df['close'], window=10)
        df['ma20'] = ta.trend.sma_indicator(df['close'], window=20)
        df['ma60'] = ta.trend.sma_indicator(df['close'], window=60)
        
        # 2. RSI 相對強弱指標
        df['rsi6'] = ta.momentum.rsi(df['close'], window=6)
        df['rsi12'] = ta.momentum.rsi(df['close'], window=12)
        
        # 3. MACD 指標
        macd_indicator = ta.trend.MACD(df['close'], window_slow=26, window_fast=12, window_sign=9)
        df['macd'] = macd_indicator.macd()
        df['macd_signal'] = macd_indicator.macd_signal()
        df['macd_hist'] = macd_indicator.macd_diff()
        
        # 4. 布林通道 (Bollinger Bands)
        bollinger = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['boll_upper'] = bollinger.bollinger_hband()
        df['boll_middle'] = bollinger.bollinger_mavg()
        df['boll_lower'] = bollinger.bollinger_lband()
        
        # 5. KD 指標 (Stochastic)
        stoch = ta.momentum.StochasticOscillator(df['high'], df['low'], df['close'], window=9, smooth_window=3)
        df['kd_k'] = stoch.stoch()
        df['kd_d'] = stoch.stoch_signal()
        
        # 6. 成交量移動平均
        df['volume_ma5'] = ta.trend.sma_indicator(df['volume'], window=5)
        df['volume_ma10'] = ta.trend.sma_indicator(df['volume'], window=10)
        
        # 7. ATR 真實波動幅度均值
        df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=14)
        
        # 組裝返回數據
        indicators = []
        for _, row in df.iterrows():
            indicators.append({
                'date': row['date'],
                'open': float(row['open']) if pd.notna(row['open']) else None,
                'high': float(row['high']) if pd.notna(row['high']) else None,
                'low': float(row['low']) if pd.notna(row['low']) else None,
                'close': float(row['close']) if pd.notna(row['close']) else None,
                'volume': float(row['volume']) if pd.notna(row['volume']) else None,
                'ma5': float(row['ma5']) if pd.notna(row['ma5']) else None,
                'ma10': float(row['ma10']) if pd.notna(row['ma10']) else None,
                'ma20': float(row['ma20']) if pd.notna(row['ma20']) else None,
                'ma60': float(row['ma60']) if pd.notna(row['ma60']) else None,
                'rsi6': float(row['rsi6']) if pd.notna(row['rsi6']) else None,
                'rsi12': float(row['rsi12']) if pd.notna(row['rsi12']) else None,
                'macd': float(row['macd']) if pd.notna(row['macd']) else None,
                'macd_signal': float(row['macd_signal']) if pd.notna(row['macd_signal']) else None,
                'macd_hist': float(row['macd_hist']) if pd.notna(row['macd_hist']) else None,
                'boll_upper': float(row['boll_upper']) if pd.notna(row['boll_upper']) else None,
                'boll_middle': float(row['boll_middle']) if pd.notna(row['boll_middle']) else None,
                'boll_lower': float(row['boll_lower']) if pd.notna(row['boll_lower']) else None,
                'kd_k': float(row['kd_k']) if pd.notna(row['kd_k']) else None,
                'kd_d': float(row['kd_d']) if pd.notna(row['kd_d']) else None,
                'volume_ma5': float(row['volume_ma5']) if pd.notna(row['volume_ma5']) else None,
                'volume_ma10': float(row['volume_ma10']) if pd.notna(row['volume_ma10']) else None,
                'atr': float(row['atr']) if pd.notna(row['atr']) else None
            })
        
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'data': indicators,
            'count': len(indicators)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'計算技術指標失敗: {str(e)}'
        })

# User registration and login
@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        print(f"[DEBUG] 註冊請求收到")
        data = request.json or {}
        print(f"[DEBUG] 請求數據: {data}")
        
        user_id = (data.get('user_id') or '').strip()
        password = (data.get('password') or '').strip()
        
        print(f"[DEBUG] user_id={user_id}, password_len={len(password)}")
        
        if not user_id or not password:
            return jsonify({'success': False, 'message': '使用者 ID 與密碼不能為空'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密碼至少需要 6 個字元'})
        
        password_hash = hash_password(password)
        print(f"[DEBUG] password_hash={password_hash[:20]}...")
        
        with closing(get_conn()) as conn:
            print(f"[DEBUG] 數據庫連接成功, DB_IS_PG={DB_IS_PG}")
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                # 檢查是否已存在
                cursor.execute(q('SELECT id FROM users WHERE user_id = ?'), (user_id,))
                existing = cursor.fetchone()
                print(f"[DEBUG] 檢查用戶是否存在: {existing}")
                if existing:
                    return jsonify({'success': False, 'message': '此使用者 ID 已被註冊'})
                
                # 檢查是否為第一個使用者（管理員）
                cursor.execute('SELECT COUNT(*) as cnt FROM users')
                count_row = cursor.fetchone()
                is_first_user = False
                if DB_IS_PG:
                    is_first_user = (count_row.get('cnt', 0) == 0)
                else:
                    is_first_user = (count_row[0] == 0)
                
                print(f"[DEBUG] 用戶計數: {count_row}, is_first_user={is_first_user}")
                
                # 插入新使用者
                if DB_IS_PG:
                    cursor.execute(
                        q('INSERT INTO users (user_id, password_hash, is_admin) VALUES (?, ?, ?)'),
                        (user_id, password_hash, is_first_user)
                    )
                else:
                    cursor.execute(
                        q('INSERT INTO users (user_id, password_hash, is_admin) VALUES (?, ?, ?)'),
                        (user_id, password_hash, 1 if is_first_user else 0)
                    )
                conn.commit()
                print(f"[DEBUG] 用戶註冊成功: {user_id}")
        
        return jsonify({
            'success': True,
            'is_admin': is_first_user,
            'message': '註冊成功' + ('（您是管理員）' if is_first_user else '')
        })
    except Exception as e:
        print(f"[ERROR] 註冊失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'註冊失敗: {str(e)}'})


@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        print(f"[DEBUG] 登入請求收到")
        data = request.json or {}
        user_id = (data.get('user_id') or '').strip()
        password = (data.get('password') or '').strip()
        
        print(f"[DEBUG] user_id={user_id}, password_len={len(password)}")
        
        if not user_id or not password:
            return jsonify({'success': False, 'message': '使用者 ID 與密碼不能為空'})
        
        password_hash = hash_password(password)
        
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('SELECT * FROM users WHERE user_id = ?'), (user_id,))
                row = cursor.fetchone()
                
                print(f"[DEBUG] 查詢用戶結果: {row}")
                
                if not row:
                    return jsonify({'success': False, 'message': '使用者不存在'})
                
                stored_hash = row['password_hash'] if DB_IS_PG else row['password_hash']
                print(f"[DEBUG] stored_hash={stored_hash[:20]}..., input_hash={password_hash[:20]}...")
                
                if stored_hash != password_hash:
                    return jsonify({'success': False, 'message': '密碼錯誤'})
                
                is_admin = row.get('is_admin', False) if DB_IS_PG else bool(row['is_admin'])
                print(f"[DEBUG] 登入成功: {user_id}, is_admin={is_admin}")
                
        return jsonify({
            'success': True,
            'user_id': user_id,
            'is_admin': is_admin,
            'message': '登入成功'
        })
    except Exception as e:
        print(f"[ERROR] 登入失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'登入失敗: {str(e)}'})


# Favorites APIs (per user)
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    try:
        user_id = request.args.get('user_id', '').strip()
        if not user_id:
            return jsonify({'success': False, 'message': '需要 user_id'})
        
        # 檢查是否為管理員
        is_admin = check_user_is_admin(user_id)
        
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                if is_admin:
                    # 管理員可查看所有使用者的最愛
                    cursor.execute('SELECT * FROM favorites ORDER BY user_id, liked_time DESC')
                else:
                    # 一般使用者只能看自己的
                    cursor.execute(q('SELECT * FROM favorites WHERE user_id = ? ORDER BY liked_time DESC'), (user_id,))
                rows = cursor.fetchall()
                data = rows if DB_IS_PG else [dict(r) for r in rows]
        
        # 返回簡化格式
        favorites = [{'stock_code': row['stock_code'], 'stock_name': row.get('stock_name', '')} for row in data]
        return jsonify({'success': True, 'favorites': favorites, 'is_admin': is_admin})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    try:
        data = request.json or {}
        user_id = (data.get('user_id') or '').strip()
        stock_code = (data.get('stock_code') or '').strip()
        if not user_id or not stock_code:
            return jsonify({'success': False, 'message': 'user_id 與 stock_code 不能為空'})

        # 查股票名稱
        stock_info = get_stock_info(stock_code)
        stock_name = stock_info.get('stock_name', '') if stock_info.get('success') else ''

        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                # 檢查是否已存在同一 user 的同一股票
                cursor.execute(q('SELECT id FROM favorites WHERE user_id = ? AND stock_code = ?'), (user_id, stock_code))
                if cursor.fetchone():
                    # 更新時間為最新
                    cursor.execute(q('UPDATE favorites SET liked_time = CURRENT_TIMESTAMP, stock_name = ? WHERE user_id = ? AND stock_code = ?'), (stock_name, user_id, stock_code))
                else:
                    cursor.execute(q('INSERT INTO favorites (user_id, stock_code, stock_name) VALUES (?, ?, ?)'), (user_id, stock_code, stock_name))
                conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/favorites/last', methods=['GET'])
def get_last_favorite():
    try:
        user_id = request.args.get('user_id', '').strip()
        if not user_id:
            return jsonify({'success': False, 'message': '需要 user_id'})
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('SELECT * FROM favorites WHERE user_id = ? ORDER BY liked_time DESC LIMIT 1'), (user_id,))
                row = cursor.fetchone()
                data = row if DB_IS_PG else (dict(row) if row else None)
        return jsonify({'success': True, 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/favorites/<int:fav_id>', methods=['DELETE'])
def delete_favorite(fav_id: int):
    try:
        user_id = request.args.get('user_id', '').strip()
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                if user_id:
                    cursor.execute(q('DELETE FROM favorites WHERE id = ? AND user_id = ?'), (fav_id, user_id))
                else:
                    cursor.execute(q('DELETE FROM favorites WHERE id = ?'), (fav_id,))
                conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/favorites/<stock_code>', methods=['DELETE'])
def delete_favorite_by_code(stock_code: str):
    try:
        user_id = request.args.get('user_id', '').strip()
        if not user_id:
            return jsonify({'success': False, 'message': '需要 user_id'})
        
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('DELETE FROM favorites WHERE user_id = ? AND stock_code = ?'), (user_id, stock_code))
                conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """
    AI 聊天端點 - 支援 OpenAI 和 Gemini
    """
    try:
        data = request.json or {}
        message = data.get('message', '').strip()
        provider = data.get('provider', 'openai').lower()
        stock_context = data.get('stock_context', {})
        
        if not message:
            return jsonify({'success': False, 'message': '訊息不能為空'})
        
        # 構建系統提示詞
        system_prompt = """你是一個專業的台灣股市分析助手。你可以：
1. 分析股票技術指標（RSI、MACD、KD、布林通道等）
2. 解讀 K 線圖形態
3. 提供投資建議（但要提醒風險）
4. 解釋財經名詞
5. 分析市場趨勢

請用繁體中文回答，語氣專業但友善。"""
        
        # 如果有股票上下文，添加到訊息中
        if stock_context:
            context_info = f"\n\n當前查詢的股票資訊：\n"
            context_info += f"代碼: {stock_context.get('stock_code', 'N/A')}\n"
            context_info += f"名稱: {stock_context.get('stock_name', 'N/A')}\n"
            context_info += f"現價: {stock_context.get('current_price', 'N/A')}\n"
            
            if stock_context.get('technical_indicators'):
                ti = stock_context['technical_indicators']
                context_info += f"\n技術指標：\n"
                context_info += f"RSI: {ti.get('RSI', 'N/A')}\n"
                context_info += f"MACD: {ti.get('MACD', 'N/A')}\n"
                context_info += f"KD K值: {ti.get('KD_K', 'N/A')}\n"
                context_info += f"KD D值: {ti.get('KD_D', 'N/A')}\n"
            
            message = context_info + "\n\n使用者問題：" + message
        
        # 根據提供者調用不同的 API
        if provider == 'openai' and OPENAI_AVAILABLE and OPENAI_API_KEY:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            reply = response.choices[0].message.content
            return jsonify({
                'success': True,
                'reply': reply,
                'provider': 'openai'
            })
        
        elif provider == 'gemini' and GEMINI_AVAILABLE and GEMINI_API_KEY:
            model = genai.GenerativeModel('gemini-pro')
            full_prompt = f"{system_prompt}\n\n{message}"
            response = model.generate_content(full_prompt)
            reply = response.text
            return jsonify({
                'success': True,
                'reply': reply,
                'provider': 'gemini'
            })
        
        else:
            available = []
            if OPENAI_AVAILABLE and OPENAI_API_KEY:
                available.append('openai')
            if GEMINI_AVAILABLE and GEMINI_API_KEY:
                available.append('gemini')
            
            if not available:
                return jsonify({
                    'success': False,
                    'message': 'AI 服務未配置。請設置 OPENAI_API_KEY 或 GEMINI_API_KEY 環境變數'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'不支援的提供者：{provider}。可用: {", ".join(available)}'
                })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'AI 請求失敗: {str(e)}'
        })


@app.route('/api/ai/providers', methods=['GET'])
def get_ai_providers():
    """
    獲取可用的 AI 提供者
    """
    providers = []
    
    # Ollama 優先
    if OLLAMA_AVAILABLE:
        providers.append({
            'id': 'ollama',
            'name': 'Ollama (本地)',
            'available': True
        })
    
    if OPENAI_AVAILABLE and OPENAI_API_KEY:
        providers.append({
            'id': 'openai',
            'name': 'OpenAI GPT',
            'available': True
        })
    
    if GEMINI_AVAILABLE and GEMINI_API_KEY:
        providers.append({
            'id': 'gemini',
            'name': 'Google Gemini',
            'available': True
        })
    
    return jsonify({
        'success': True,
        'providers': providers
    })


def get_stock_news(stock_code):
    """
    爬取股票新聞（從 Yahoo 財經台灣）
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f'https://tw.stock.yahoo.com/quote/{stock_code}.TW/news'
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        
        # 查找新聞項目
        news_elements = soup.find_all('div', class_='Ov(h)')[:5]  # 取前5條
        
        for element in news_elements:
            title_elem = element.find('h3')
            if title_elem:
                title = title_elem.get_text(strip=True)
                news_items.append({
                    'title': title,
                    'source': 'Yahoo 財經'
                })
        
        return news_items
    except Exception as e:
        print(f"獲取新聞失敗: {e}")
        return []


def get_financial_data(stock_code):
    """
    爬取基本財務數據（從 Goodinfo）
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        url = f'https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={stock_code}'
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return {}
        
        soup = BeautifulSoup(response.text, 'html.parser')
        financial_data = {
            'pe_ratio': 'N/A',
            'dividend_yield': 'N/A',
            'eps': 'N/A',
            'roe': 'N/A'
        }
        
        # 嘗試提取財務數據（簡化版）
        try:
            tables = soup.find_all('table')
            for table in tables[:3]:
                text = table.get_text()
                if '本益比' in text:
                    financial_data['pe_ratio'] = '資料擷取中'
                if 'EPS' in text:
                    financial_data['eps'] = '資料擷取中'
        except:
            pass
        
        return financial_data
    except Exception as e:
        print(f"獲取財務數據失敗: {e}")
        return {}


@app.route('/api/analyze/stock/<stock_code>', methods=['GET'])
def analyze_stock(stock_code):
    """
    自動分析股票：整合歷史數據、技術指標、財務報表、新聞
    使用 Ollama 本地 AI 生成買賣建議
    """
    try:
        # 1. 獲取股票基本信息和一年歷史數據
        stock_info = get_stock_info(stock_code)
        if not stock_info.get('success'):
            return jsonify({
                'success': False,
                'message': '無法獲取股票數據'
            })
        
        # 2. 計算一年內最高最低價
        kline_data = stock_info.get('data', {}).get('kline_data', [])
        if not kline_data:
            return jsonify({
                'success': False,
                'message': '無歷史數據'
            })
        
        # 取最近252個交易日（約一年）
        year_data = kline_data[-252:] if len(kline_data) > 252 else kline_data
        
        highs = [float(d['high']) for d in year_data]
        lows = [float(d['low']) for d in year_data]
        closes = [float(d['close']) for d in year_data]
        
        year_high = max(highs)
        year_low = min(lows)
        current_price = closes[-1]
        
        # 計算今日預測（使用技術指標）
        indicators = stock_info.get('data', {}).get('technical_indicators', {})
        
        # 3. 獲取財務數據和新聞
        financial_data = get_financial_data(stock_code)
        news = get_stock_news(stock_code)
        
        # 4. 構建分析提示詞
        stock_name = stock_info.get('data', {}).get('name', stock_code)
        
        analysis_prompt = f"""請分析以下台灣股票 {stock_code} ({stock_name}) 的數據並提供買賣建議：

【價格數據】
- 當前價格：{current_price:.2f} 元
- 一年最高價：{year_high:.2f} 元
- 一年最低價：{year_low:.2f} 元
- 相對位置：{((current_price - year_low) / (year_high - year_low) * 100):.1f}%

【技術指標】
- RSI(14)：{indicators.get('rsi', {}).get('current', 'N/A')}
- MACD：{indicators.get('macd', {}).get('macd', 'N/A')}
- 布林通道：上軌 {indicators.get('bb', {}).get('upper', 'N/A')}，中軌 {indicators.get('bb', {}).get('middle', 'N/A')}，下軌 {indicators.get('bb', {}).get('lower', 'N/A')}
- KD指標：K值 {indicators.get('kd', {}).get('k', 'N/A')}，D值 {indicators.get('kd', {}).get('d', 'N/A')}

【財務數據】
- 本益比：{financial_data.get('pe_ratio', 'N/A')}
- EPS：{financial_data.get('eps', 'N/A')}
- ROE：{financial_data.get('roe', 'N/A')}
- 股息殖利率：{financial_data.get('dividend_yield', 'N/A')}

【最新新聞】
{chr(10).join([f"- {n['title']}" for n in news[:3]]) if news else "暫無新聞"}

請根據以上數據：
1. 分析當前股價處於年度價格區間的位置
2. 技術指標顯示的買賣訊號
3. 預測今日可能的高低點範圍
4. 給出明確的操作建議（強烈買入/買入/持有/賣出/強烈賣出）
5. 設定建議的買入價位和賣出價位

請用繁體中文回答，簡潔明確。"""

        # 5. 使用 AI 生成分析（優先使用 Ollama）
        ai_response = ""
        
        if OLLAMA_AVAILABLE:
            try:
                # 獲取默認模型
                default_model = 'llama2'
                try:
                    with closing(get_conn()) as conn:
                        if not DB_IS_PG:
                            conn.row_factory = sqlite3.Row
                        with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                            cursor.execute(q('SELECT config_value FROM app_config WHERE config_key = ?'), ('default_ollama_model',))
                            row = cursor.fetchone()
                            if row:
                                default_model = row['config_value'] if DB_IS_PG else row['config_value']
                except:
                    pass  # 使用默認值
                
                client = ollama.Client(host=OLLAMA_HOST)
                response = client.chat(
                    model=default_model,
                    messages=[
                        {
                            'role': 'system',
                            'content': '你是一個專業的台灣股市分析師，擅長技術分析和基本面分析。'
                        },
                        {
                            'role': 'user',
                            'content': analysis_prompt
                        }
                    ]
                )
                ai_response = response['message']['content']
            except Exception as e:
                print(f"Ollama 分析失敗: {e}")
                ai_response = f"Ollama 分析失敗，請在設置頁面下載模型\n錯誤: {str(e)}"
        
        elif OPENAI_AVAILABLE and OPENAI_API_KEY:
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一個專業的台灣股市分析師。"},
                        {"role": "user", "content": analysis_prompt}
                    ]
                )
                ai_response = response.choices[0].message.content
            except Exception as e:
                ai_response = f"OpenAI 分析失敗: {str(e)}"
        
        elif GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-pro')
                response = model.generate_content(analysis_prompt)
                ai_response = response.text
            except Exception as e:
                ai_response = f"Gemini 分析失敗: {str(e)}"
        
        else:
            ai_response = "無可用的 AI 服務。請安裝 Ollama 或配置 OpenAI/Gemini API。"
        
        # 6. 返回分析結果
        return jsonify({
            'success': True,
            'analysis': {
                'stock_code': stock_code,
                'stock_name': stock_name,
                'current_price': current_price,
                'year_high': year_high,
                'year_low': year_low,
                'price_position': round((current_price - year_low) / (year_high - year_low) * 100, 1),
                'technical_indicators': indicators,
                'financial_data': financial_data,
                'news': news[:3],
                'ai_recommendation': ai_response
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分析失敗: {str(e)}'
        })


# ========== 設置頁面路由 ==========
@app.route('/settings')
def settings_page():
    """設置頁面"""
    return render_template('settings.html')


@app.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    """獲取已安裝的 Ollama 模型列表"""
    if not OLLAMA_AVAILABLE:
        return jsonify({'success': False, 'message': 'Ollama 未啟用'})
    
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        models = client.list()
        model_list = []
        for model in models.get('models', []):
            model_list.append({
                'name': model.get('name', ''),
                'size': model.get('size', 0),
                'modified_at': model.get('modified_at', '')
            })
        return jsonify({'success': True, 'models': model_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/ollama/models/pull', methods=['POST'])
def pull_ollama_model():
    """下載 Ollama 模型"""
    if not OLLAMA_AVAILABLE:
        return jsonify({'success': False, 'message': 'Ollama 未啟用'})
    
    data = request.get_json()
    model_name = data.get('model_name', '').strip()
    
    if not model_name:
        return jsonify({'success': False, 'message': '模型名稱不能為空'})
    
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        # 使用 pull 方法下載模型（這是一個同步操作，可能需要時間）
        client.pull(model_name)
        return jsonify({'success': True, 'message': f'模型 {model_name} 下載完成'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'下載失敗: {str(e)}'})


@app.route('/api/ollama/models/delete', methods=['POST'])
def delete_ollama_model():
    """刪除 Ollama 模型"""
    if not OLLAMA_AVAILABLE:
        return jsonify({'success': False, 'message': 'Ollama 未啟用'})
    
    data = request.get_json()
    model_name = data.get('model_name', '').strip()
    
    if not model_name:
        return jsonify({'success': False, 'message': '模型名稱不能為空'})
    
    try:
        client = ollama.Client(host=OLLAMA_HOST)
        client.delete(model_name)
        return jsonify({'success': True, 'message': f'模型 {model_name} 已刪除'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'刪除失敗: {str(e)}'})


@app.route('/api/ollama/default-model', methods=['GET', 'POST'])
def manage_default_model():
    """獲取或設置默認 Ollama 模型"""
    if request.method == 'GET':
        # 從數據庫或配置中讀取默認模型
        try:
            with closing(get_conn()) as conn:
                if not DB_IS_PG:
                    conn.row_factory = sqlite3.Row
                with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                    cursor.execute(q('SELECT config_value FROM app_config WHERE config_key = ?'), ('default_ollama_model',))
                    row = cursor.fetchone()
                    if row:
                        return jsonify({'success': True, 'model': row['config_value'] if DB_IS_PG else row['config_value']})
                    else:
                        return jsonify({'success': True, 'model': 'llama2'})  # 默認值
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
    
    elif request.method == 'POST':
        # 設置默認模型
        data = request.get_json()
        model_name = data.get('model_name', '').strip()
        
        if not model_name:
            return jsonify({'success': False, 'message': '模型名稱不能為空'})
        
        try:
            with closing(get_conn()) as conn:
                if not DB_IS_PG:
                    conn.row_factory = sqlite3.Row
                with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                    # 使用 UPSERT 語法
                    if DB_IS_PG:
                        cursor.execute(
                            """
                            INSERT INTO app_config (config_key, config_value) 
                            VALUES (%s, %s)
                            ON CONFLICT (config_key) DO UPDATE SET config_value = EXCLUDED.config_value
                            """,
                            ('default_ollama_model', model_name)
                        )
                    else:
                        cursor.execute(
                            q('INSERT OR REPLACE INTO app_config (config_key, config_value) VALUES (?, ?)'),
                            ('default_ollama_model', model_name)
                        )
                    conn.commit()
            return jsonify({'success': True, 'message': f'默認模型已設置為 {model_name}'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5788, debug=True)
