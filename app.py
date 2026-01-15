from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import json
import sqlite3
from contextlib import closing

app = Flask(__name__)

# 初始化資料庫
def init_db():
    with closing(sqlite3.connect('stocks.db')) as conn:
        with closing(conn.cursor()) as cursor:
            # 關注股票清單
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    category TEXT NOT NULL,
                    added_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # 查詢歷史記錄
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT,
                    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
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
        with closing(sqlite3.connect('stocks.db')) as conn:
            conn.row_factory = sqlite3.Row
            with closing(conn.cursor()) as cursor:
                if category:
                    cursor.execute(
                        'SELECT * FROM watchlist WHERE category = ? ORDER BY added_time DESC',
                        (category,)
                    )
                else:
                    cursor.execute('SELECT * FROM watchlist ORDER BY added_time DESC')
                
                rows = cursor.fetchall()
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
        
        with closing(sqlite3.connect('stocks.db')) as conn:
            with closing(conn.cursor()) as cursor:
                # 檢查是否已存在
                cursor.execute(
                    'SELECT id FROM watchlist WHERE stock_code = ?',
                    (stock_code,)
                )
                if cursor.fetchone():
                    return jsonify({'success': False, 'message': '此股票已在關注清單中'})
                
                # 添加到資料庫
                cursor.execute(
                    'INSERT INTO watchlist (stock_code, stock_name, category) VALUES (?, ?, ?)',
                    (stock_code, stock_name, category)
                )
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
        with closing(sqlite3.connect('stocks.db')) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute('DELETE FROM watchlist WHERE id = ?', (id,))
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
        with closing(sqlite3.connect('stocks.db')) as conn:
            conn.row_factory = sqlite3.Row
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    'SELECT * FROM search_history ORDER BY search_time DESC LIMIT 50'
                )
                rows = cursor.fetchall()
                history = [dict(row) for row in rows]
                
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
        
        with closing(sqlite3.connect('stocks.db')) as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    'INSERT INTO search_history (stock_code, stock_name) VALUES (?, ?)',
                    (stock_code, stock_name)
                )
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5788, debug=True)
