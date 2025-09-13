from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import yfinance as yf

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '7203.T')
        period = data.get('period', '1mo')

        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty:
            return jsonify({
                "success": False,
                "error": "INVALID_SYMBOL",
                "message": "指定された銘柄コードのデータが取得できません"
            }), 400

        return jsonify({
            "success": True,
            "message": "データを正常に取得しました",
            "data": {
                "symbol": symbol,
                "records_count": len(hist),
                "date_range": {
                    "start": hist.index[0].strftime('%Y-%m-%d'),
                    "end": hist.index[-1].strftime('%Y-%m-%d')
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "EXTERNAL_API_ERROR",
            "message": f"データ取得に失敗しました: {str(e)}"
        }), 502

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        port=int(os.getenv('FLASK_PORT', 8000)),
        host='0.0.0.0'
    )