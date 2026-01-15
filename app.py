from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import sqlite3
from contextlib import closing
import os
import hashlib
import numpy as np
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not installed. Technical indicators will not be available.")

DB_URL = os.environ.get('DATABASE_URL', '').strip()
DB_IS_PG = DB_URL.startswith('postgres://') or DB_URL.startswith('postgresql://')

if DB_IS_PG:
    try:
        import psycopg
        from psycopg.rows import dict_row
    except Exception as e:
        raise RuntimeError(f"PostgreSQL support requires psycopg: {e}")

app = Flask(__name__)

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
        return sqlite3.connect('stocks.db')


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
            conn.commit()

init_db()

def get_twse_data(stock_code):
    """
    從台灣證券交易所獲取股票資料
    """
    try:
        # 使用台灣證券交易所的 API
        date = datetime.now().strftime('%Y%m%d')
        url = f'https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={date}&stockNo={stock_code}'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        if data.get('stat') == 'OK':
            return {
                'success': True,
                'stock_code': stock_code,
                'title': data.get('title', ''),
                'data': data.get('data', []),
                'fields': data.get('fields', [])
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
    獲取即時股票資訊（使用 mis API）
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
            return {
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
    API 端點：使用 TA-Lib 計算技術指標
    返回 K 線數據 + MA + RSI + MACD + BOLL 等指標
    """
    if not TALIB_AVAILABLE:
        return jsonify({
            'success': False,
            'message': 'TA-Lib not installed'
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
        
        # 提取 OHLCV 數據
        dates = [row[0] for row in data]
        opens = np.array([float(row[3]) for row in data], dtype=float)
        highs = np.array([float(row[4]) for row in data], dtype=float)
        lows = np.array([float(row[5]) for row in data], dtype=float)
        closes = np.array([float(row[6]) for row in data], dtype=float)
        volumes = np.array([float(row[1]) for row in data], dtype=float)
        
        # 計算技術指標
        # 1. 移動平均線 (MA)
        ma5 = talib.SMA(closes, timeperiod=5)
        ma10 = talib.SMA(closes, timeperiod=10)
        ma20 = talib.SMA(closes, timeperiod=20)
        ma60 = talib.SMA(closes, timeperiod=60)
        
        # 2. RSI 相對強弱指標
        rsi6 = talib.RSI(closes, timeperiod=6)
        rsi12 = talib.RSI(closes, timeperiod=12)
        
        # 3. MACD 指標
        macd, macd_signal, macd_hist = talib.MACD(closes, fastperiod=12, slowperiod=26, signalperiod=9)
        
        # 4. 布林通道 (Bollinger Bands)
        upper_band, middle_band, lower_band = talib.BBANDS(closes, timeperiod=20, nbdevup=2, nbdevdn=2)
        
        # 5. KD 指標 (Stochastic)
        slowk, slowd = talib.STOCH(highs, lows, closes, fastk_period=9, slowk_period=3, slowd_period=3)
        
        # 6. 成交量移動平均
        volume_ma5 = talib.SMA(volumes, timeperiod=5)
        volume_ma10 = talib.SMA(volumes, timeperiod=10)
        
        # 7. ATR 真實波動幅度均值
        atr = talib.ATR(highs, lows, closes, timeperiod=14)
        
        # 組裝返回數據
        indicators = []
        for i in range(len(dates)):
            indicators.append({
                'date': dates[i],
                'open': float(opens[i]),
                'high': float(highs[i]),
                'low': float(lows[i]),
                'close': float(closes[i]),
                'volume': float(volumes[i]),
                'ma5': float(ma5[i]) if not np.isnan(ma5[i]) else None,
                'ma10': float(ma10[i]) if not np.isnan(ma10[i]) else None,
                'ma20': float(ma20[i]) if not np.isnan(ma20[i]) else None,
                'ma60': float(ma60[i]) if not np.isnan(ma60[i]) else None,
                'rsi6': float(rsi6[i]) if not np.isnan(rsi6[i]) else None,
                'rsi12': float(rsi12[i]) if not np.isnan(rsi12[i]) else None,
                'macd': float(macd[i]) if not np.isnan(macd[i]) else None,
                'macd_signal': float(macd_signal[i]) if not np.isnan(macd_signal[i]) else None,
                'macd_hist': float(macd_hist[i]) if not np.isnan(macd_hist[i]) else None,
                'boll_upper': float(upper_band[i]) if not np.isnan(upper_band[i]) else None,
                'boll_middle': float(middle_band[i]) if not np.isnan(middle_band[i]) else None,
                'boll_lower': float(lower_band[i]) if not np.isnan(lower_band[i]) else None,
                'kd_k': float(slowk[i]) if not np.isnan(slowk[i]) else None,
                'kd_d': float(slowd[i]) if not np.isnan(slowd[i]) else None,
                'volume_ma5': float(volume_ma5[i]) if not np.isnan(volume_ma5[i]) else None,
                'volume_ma10': float(volume_ma10[i]) if not np.isnan(volume_ma10[i]) else None,
                'atr': float(atr[i]) if not np.isnan(atr[i]) else None
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
        data = request.json or {}
        user_id = (data.get('user_id') or '').strip()
        password = (data.get('password') or '').strip()
        
        if not user_id or not password:
            return jsonify({'success': False, 'message': '使用者 ID 與密碼不能為空'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': '密碼至少需要 6 個字元'})
        
        password_hash = hash_password(password)
        
        with closing(get_conn()) as conn:
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                # 檢查是否已存在
                cursor.execute(q('SELECT id FROM users WHERE user_id = ?'), (user_id,))
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': '此使用者 ID 已被註冊'})
                
                # 檢查是否為第一個使用者（管理員）
                cursor.execute('SELECT COUNT(*) as cnt FROM users')
                count_row = cursor.fetchone()
                is_first_user = False
                if DB_IS_PG:
                    is_first_user = (count_row.get('cnt', 0) == 0)
                else:
                    is_first_user = (count_row[0] == 0)
                
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
        
        return jsonify({
            'success': True,
            'is_admin': is_first_user,
            'message': '註冊成功' + ('（您是管理員）' if is_first_user else '')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'註冊失敗: {str(e)}'})


@app.route('/api/login', methods=['POST'])
def login_user():
    try:
        data = request.json or {}
        user_id = (data.get('user_id') or '').strip()
        password = (data.get('password') or '').strip()
        
        if not user_id or not password:
            return jsonify({'success': False, 'message': '使用者 ID 與密碼不能為空'})
        
        password_hash = hash_password(password)
        
        with closing(get_conn()) as conn:
            if not DB_IS_PG:
                conn.row_factory = sqlite3.Row
            with closing(conn.cursor(row_factory=dict_row) if DB_IS_PG else conn.cursor()) as cursor:
                cursor.execute(q('SELECT * FROM users WHERE user_id = ?'), (user_id,))
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'success': False, 'message': '使用者不存在'})
                
                stored_hash = row['password_hash'] if DB_IS_PG else row['password_hash']
                if stored_hash != password_hash:
                    return jsonify({'success': False, 'message': '密碼錯誤'})
                
                is_admin = row.get('is_admin', False) if DB_IS_PG else bool(row['is_admin'])
                
        return jsonify({
            'success': True,
            'user_id': user_id,
            'is_admin': is_admin,
            'message': '登入成功'
        })
    except Exception as e:
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
        return jsonify({'success': True, 'data': data, 'is_admin': is_admin})
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5788, debug=True)
