from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import yfinance as yf
from datetime import datetime, date
from app.models import Base, StockDaily, StockDailyCRUD, get_db_session, engine, DatabaseError, StockDataError

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)

# テーブル作成
Base.metadata.create_all(bind=engine)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test-connection', methods=['GET'])
def test_connection():
    """データベース接続テスト用エンドポイント"""
    from sqlalchemy import text
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))

        return jsonify({
            "success": True,
            "message": "データベース接続が正常に動作しています",
            "database": os.getenv('DB_NAME'),
            "user": os.getenv('DB_USER')
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_CONNECTION_ERROR",
            "message": f"データベース接続に失敗しました: {str(e)}"
        }), 500

@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '7203.T')
        period = data.get('period', '1mo')
        interval = data.get('interval', '1d')

        # intervalパラメータのバリデーション
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        if interval not in valid_intervals:
            return jsonify({
                "success": False,
                "error": "INVALID_INTERVAL",
                "message": f"無効な足種別です。有効な値: {', '.join(valid_intervals)}"
            }), 400

        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            return jsonify({
                "success": False,
                "error": "INVALID_SYMBOL",
                "message": "指定された銘柄コードのデータが取得できません"
            }), 400

        # データベースに保存
        with get_db_session() as session:
            saved_records = []
            skipped_records = 0

            for date_index, row in hist.iterrows():
                try:
                    # 日付をdate型に変換
                    stock_date = date_index.date()

                    # 既存データの確認
                    existing_data = StockDailyCRUD.get_by_symbol_and_date(session, symbol, stock_date)
                    if existing_data:
                        skipped_records += 1
                        continue

                    # 新しいデータを作成
                    stock_data = StockDailyCRUD.create(
                        session,
                        symbol=symbol,
                        date=stock_date,
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume'])
                    )
                    saved_records.append(stock_data)

                except (StockDataError, DatabaseError):
                    # 重複データの場合はスキップ
                    skipped_records += 1
                    continue

        return jsonify({
            "success": True,
            "message": "データを正常に取得し、データベースに保存しました",
            "data": {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "records_count": len(hist),
                "saved_records": len(saved_records),
                "skipped_records": skipped_records,
                "date_range": {
                    "start": hist.index[0].strftime('%Y-%m-%d'),
                    "end": hist.index[-1].strftime('%Y-%m-%d')
                }
            }
        })
    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": f"データベース保存に失敗しました: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "EXTERNAL_API_ERROR",
            "message": f"データ取得に失敗しました: {str(e)}"
        }), 502

# CRUD API エンドポイント

@app.route('/api/stocks', methods=['POST'])
def create_stock():
    """株価データを作成"""
    try:
        data = request.get_json()
        required_fields = ['symbol', 'date', 'open', 'high', 'low', 'close', 'volume']

        # 必須フィールドのバリデーション
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": f"必須フィールド '{field}' が不足しています"
                }), 400

        # 日付のパース
        try:
            if isinstance(data['date'], str):
                data['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "日付の形式が正しくありません (YYYY-MM-DD)"
            }), 400

        with get_db_session() as session:
            stock_data = StockDailyCRUD.create(session, **data)
            return jsonify({
                "success": True,
                "message": "株価データを作成しました",
                "data": stock_data.to_dict()
            }), 201

    except StockDataError as e:
        return jsonify({
            "success": False,
            "error": "STOCK_DATA_ERROR",
            "message": str(e)
        }), 400
    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/stocks/<int:stock_id>', methods=['GET'])
def get_stock_by_id(stock_id):
    """ID で株価データを取得"""
    try:
        with get_db_session() as session:
            stock_data = StockDailyCRUD.get_by_id(session, stock_id)
            if not stock_data:
                return jsonify({
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"ID {stock_id} の株価データが見つかりません"
                }), 404

            return jsonify({
                "success": True,
                "data": stock_data.to_dict()
            })

    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """株価データを取得（クエリパラメータに応じて）"""
    try:
        # クエリパラメータの取得
        symbol = request.args.get('symbol')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 日付のパース
        parsed_start_date = None
        parsed_end_date = None
        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "start_date の形式が正しくありません (YYYY-MM-DD)"
                }), 400

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "end_date の形式が正しくありません (YYYY-MM-DD)"
                }), 400

        # バリデーション
        if limit <= 0:
            return jsonify({
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "limit は1以上の値を指定してください"
            }), 400

        if offset < 0:
            return jsonify({
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "offset は0以上の値を指定してください"
            }), 400

        with get_db_session() as session:
            # データ取得
            stocks = StockDailyCRUD.get_with_filters(
                session, symbol, limit, offset, parsed_start_date, parsed_end_date
            )
            
            # 総件数取得
            total_count = StockDailyCRUD.count_with_filters(
                session, symbol, parsed_start_date, parsed_end_date
            )

            # ページネーション情報
            has_next = (offset + len(stocks)) < total_count

            return jsonify({
                "success": True,
                "data": [stock.to_dict() for stock in stocks],
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_next": has_next
                }
            })

    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/stocks/<int:stock_id>', methods=['PUT'])
def update_stock(stock_id):
    """株価データを更新"""
    try:
        data = request.get_json()

        # 日付のパース
        if 'date' in data and isinstance(data['date'], str):
            try:
                data['date'] = datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "error": "VALIDATION_ERROR",
                    "message": "日付の形式が正しくありません (YYYY-MM-DD)"
                }), 400

        with get_db_session() as session:
            stock_data = StockDailyCRUD.update(session, stock_id, **data)
            if not stock_data:
                return jsonify({
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"ID {stock_id} の株価データが見つかりません"
                }), 404

            return jsonify({
                "success": True,
                "message": "株価データを更新しました",
                "data": stock_data.to_dict()
            })

    except StockDataError as e:
        return jsonify({
            "success": False,
            "error": "STOCK_DATA_ERROR",
            "message": str(e)
        }), 400
    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/stocks/<int:stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    """株価データを削除"""
    try:
        with get_db_session() as session:
            if StockDailyCRUD.delete(session, stock_id):
                return jsonify({
                    "success": True,
                    "message": f"ID {stock_id} の株価データを削除しました"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"ID {stock_id} の株価データが見つかりません"
                }), 404

    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

@app.route('/api/stocks/test-data', methods=['POST'])
def create_test_data():
    """テスト用サンプルデータを作成"""
    try:
        test_data = [
            {
                'symbol': '7203.T',
                'date': date(2024, 9, 9),
                'open': 2500.00,
                'high': 2550.00,
                'low': 2480.00,
                'close': 2530.00,
                'volume': 1500000
            },
            {
                'symbol': '7203.T',
                'date': date(2024, 9, 8),
                'open': 2480.00,
                'high': 2520.00,
                'low': 2460.00,
                'close': 2500.00,
                'volume': 1200000
            },
            {
                'symbol': '6502.T',
                'date': date(2024, 9, 9),
                'open': 4500.00,
                'high': 4580.00,
                'low': 4450.00,
                'close': 4550.00,
                'volume': 800000
            }
        ]

        with get_db_session() as session:
            created_stocks = StockDailyCRUD.bulk_create(session, test_data)
            return jsonify({
                "success": True,
                "message": f"{len(created_stocks)} 件のテストデータを作成しました",
                "data": [stock.to_dict() for stock in created_stocks]
            }), 201

    except StockDataError as e:
        return jsonify({
            "success": False,
            "error": "STOCK_DATA_ERROR",
            "message": str(e)
        }), 400
    except DatabaseError as e:
        return jsonify({
            "success": False,
            "error": "DATABASE_ERROR",
            "message": str(e)
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": f"予期しないエラーが発生しました: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        port=int(os.getenv('FLASK_PORT', 8000)),
        host='0.0.0.0'
    )