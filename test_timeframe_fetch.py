#!/usr/bin/env python3
"""
時間軸対応のfetch-dataエンドポイントのテストスクリプト
"""

import requests
import json
import time
from datetime import datetime

# テスト用の設定
BASE_URL = "http://localhost:8000"
TEST_SYMBOL = "7203.T"  # トヨタ自動車

def test_fetch_data_with_timeframes():
    """各時間軸でのfetch-dataエンドポイントをテスト"""
    
    # テスト対象の時間軸
    timeframes = [
        {"timeframe": "1m", "period": "1d", "description": "1分足"},
        {"timeframe": "5m", "period": "5d", "description": "5分足"},
        {"timeframe": "15m", "period": "7d", "description": "15分足"},
        {"timeframe": "30m", "period": "7d", "description": "30分足"},
        {"timeframe": "1h", "period": "7d", "description": "1時間足"},
        {"timeframe": "1d", "period": "1mo", "description": "1日足"},
        {"timeframe": "1wk", "period": "3mo", "description": "1週足"},
        {"timeframe": "1mo", "period": "1y", "description": "1ヶ月足"}
    ]
    
    print(f"時間軸対応fetch-dataエンドポイントのテスト")
    print(f"対象銘柄: {TEST_SYMBOL}")
    print("=" * 60)
    
    for test_case in timeframes:
        timeframe = test_case["timeframe"]
        period = test_case["period"]
        description = test_case["description"]
        
        print(f"\n{description} ({timeframe}) のテスト:")
        print("-" * 40)
        
        # リクエストデータ
        request_data = {
            "symbol": TEST_SYMBOL,
            "period": period,
            "timeframe": timeframe
        }
        
        try:
            # APIリクエスト
            response = requests.post(
                f"{BASE_URL}/api/fetch-data",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    result_data = data.get("data", {})
                    print(f"✓ 成功: {result_data.get('records_count', 0)}件のデータを取得")
                    print(f"  保存件数: {result_data.get('saved_records', 0)}件")
                    print(f"  スキップ件数: {result_data.get('skipped_records', 0)}件")
                    print(f"  テーブル: {result_data.get('table_name', 'N/A')}")
                    print(f"  期間: {result_data.get('date_range', {}).get('start', 'N/A')} ～ {result_data.get('date_range', {}).get('end', 'N/A')}")
                else:
                    print(f"✗ APIエラー: {data.get('message', 'Unknown error')}")
            else:
                print(f"✗ HTTPエラー {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"✗ リクエストエラー: {str(e)}")
        except Exception as e:
            print(f"✗ 予期しないエラー: {str(e)}")
        
        # 次のリクエストまで少し待機
        time.sleep(1)

def test_invalid_timeframe():
    """無効な時間軸のテスト"""
    
    print(f"\n無効な時間軸のテスト:")
    print("-" * 40)
    
    invalid_timeframes = ["2m", "10m", "invalid", ""]
    
    for invalid_timeframe in invalid_timeframes:
        request_data = {
            "symbol": TEST_SYMBOL,
            "period": "1d",
            "timeframe": invalid_timeframe
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/fetch-data",
                json=request_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 400:
                data = response.json()
                print(f"✓ 無効な時間軸 '{invalid_timeframe}' が正しく拒否されました")
                print(f"  エラーメッセージ: {data.get('message', 'N/A')}")
            else:
                print(f"✗ 無効な時間軸 '{invalid_timeframe}' が予期せず受け入れられました")
                
        except Exception as e:
            print(f"✗ エラー: {str(e)}")

def test_database_connection():
    """データベース接続テスト"""
    
    print(f"\nデータベース接続テスト:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/test-connection", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✓ データベース接続正常")
                print(f"  データベース: {data.get('database', 'N/A')}")
                print(f"  ユーザー: {data.get('user', 'N/A')}")
            else:
                print(f"✗ データベース接続エラー: {data.get('message', 'Unknown error')}")
        else:
            print(f"✗ HTTPエラー {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"✗ 接続テストエラー: {str(e)}")

def main():
    """メイン関数"""
    
    print("時間軸対応fetch-dataエンドポイント テストスイート")
    print("=" * 60)
    print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # データベース接続テスト
    test_database_connection()
    
    # 無効な時間軸のテスト
    test_invalid_timeframe()
    
    # 各時間軸でのテスト
    test_fetch_data_with_timeframes()
    
    print()
    print("=" * 60)
    print(f"テスト完了: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()