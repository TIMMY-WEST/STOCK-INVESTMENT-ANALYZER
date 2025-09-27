#!/usr/bin/env python3
"""
データベース初期化スクリプトのテストコード

このテストは以下を検証します：
1. 8つのテーブルが正しく作成されること
2. 各テーブルの構造が設計通りであること
3. インデックスが正しく作成されること
4. 制約が正しく設定されること
5. トリガー関数が正しく動作すること
"""

import os
import sys
import psycopg2
import pytest
from datetime import datetime, date
from decimal import Decimal

# テスト用データベース設定
TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_data_system_test',
    'user': 'stock_user',
    'password': 'stock_password'
}

# 期待されるテーブル一覧
EXPECTED_TABLES = [
    'stocks_1d',
    'stocks_1m', 
    'stocks_5m',
    'stocks_15m',
    'stocks_30m',
    'stocks_1h',
    'stocks_1wk',
    'stocks_1mo'
]

# 日足・週足・月足テーブル（dateカラム使用）
DATE_TABLES = ['stocks_1d', 'stocks_1wk', 'stocks_1mo']

# 分足・時間足テーブル（datetimeカラム使用）
DATETIME_TABLES = ['stocks_1m', 'stocks_5m', 'stocks_15m', 'stocks_30m', 'stocks_1h']

class TestDatabaseSetup:
    """データベースセットアップのテストクラス"""
    
    @classmethod
    def setup_class(cls):
        """テストクラス開始時の初期化"""
        cls.conn = None
        cls.cursor = None
        
    @classmethod
    def teardown_class(cls):
        """テストクラス終了時のクリーンアップ"""
        if cls.cursor:
            cls.cursor.close()
        if cls.conn:
            cls.conn.close()
    
    def setup_method(self):
        """各テストメソッド開始時の初期化"""
        try:
            self.conn = psycopg2.connect(**TEST_DB_CONFIG)
            self.cursor = self.conn.cursor()
        except psycopg2.Error as e:
            pytest.skip(f"テストデータベースに接続できません: {e}")
    
    def teardown_method(self):
        """各テストメソッド終了時のクリーンアップ"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def test_tables_exist(self):
        """8つのテーブルが存在することを確認"""
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in EXPECTED_TABLES:
            assert table in existing_tables, f"テーブル {table} が存在しません"
    
    def test_table_columns(self):
        """各テーブルのカラム構成を確認"""
        for table in EXPECTED_TABLES:
            self.cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table,))
            
            columns = {row[0]: {'type': row[1], 'nullable': row[2], 'default': row[3]} 
                      for row in self.cursor.fetchall()}
            
            # 共通カラムの確認
            assert 'id' in columns, f"{table}: idカラムが存在しません"
            assert 'symbol' in columns, f"{table}: symbolカラムが存在しません"
            assert 'open' in columns, f"{table}: openカラムが存在しません"
            assert 'high' in columns, f"{table}: highカラムが存在しません"
            assert 'low' in columns, f"{table}: lowカラムが存在しません"
            assert 'close' in columns, f"{table}: closeカラムが存在しません"
            assert 'volume' in columns, f"{table}: volumeカラムが存在しません"
            assert 'created_at' in columns, f"{table}: created_atカラムが存在しません"
            assert 'updated_at' in columns, f"{table}: updated_atカラムが存在しません"
            
            # 時間カラムの確認
            if table in DATE_TABLES:
                assert 'date' in columns, f"{table}: dateカラムが存在しません"
                assert columns['date']['type'] == 'date', f"{table}: dateカラムの型が正しくありません"
            
            if table in DATETIME_TABLES:
                assert 'datetime' in columns, f"{table}: datetimeカラムが存在しません"
                assert 'timestamp' in columns['datetime']['type'], f"{table}: datetimeカラムの型が正しくありません"
    
    def test_primary_keys(self):
        """主キー制約を確認"""
        for table in EXPECTED_TABLES:
            self.cursor.execute("""
                SELECT column_name
                FROM information_schema.key_column_usage
                WHERE table_name = %s
                AND constraint_name = %s
            """, (table, f"{table}_pkey"))
            
            pk_columns = [row[0] for row in self.cursor.fetchall()]
            assert 'id' in pk_columns, f"{table}: 主キーが正しく設定されていません"
    
    def test_unique_constraints(self):
        """ユニーク制約を確認"""
        for table in EXPECTED_TABLES:
            self.cursor.execute("""
                SELECT tc.constraint_name, kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s
                AND tc.constraint_type = 'UNIQUE'
                ORDER BY kcu.ordinal_position
            """, (table,))
            
            constraints = {}
            for row in self.cursor.fetchall():
                constraint_name = row[0]
                column_name = row[1]
                if constraint_name not in constraints:
                    constraints[constraint_name] = []
                constraints[constraint_name].append(column_name)
            
            # symbol + date/datetime のユニーク制約があることを確認
            found_unique = False
            for columns in constraints.values():
                if 'symbol' in columns:
                    if table in DATE_TABLES and 'date' in columns:
                        found_unique = True
                    elif table in DATETIME_TABLES and 'datetime' in columns:
                        found_unique = True
            
            assert found_unique, f"{table}: symbol + date/datetime のユニーク制約が存在しません"
    
    def test_indexes(self):
        """インデックスを確認"""
        for table in EXPECTED_TABLES:
            self.cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = %s
                AND schemaname = 'public'
            """, (table,))
            
            indexes = {row[0]: row[1] for row in self.cursor.fetchall()}
            
            # 期待されるインデックスの確認
            expected_indexes = [
                f"idx_{table}_symbol",
                f"idx_{table}_symbol_date_desc" if table in DATE_TABLES else f"idx_{table}_symbol_datetime_desc"
            ]
            
            if table in DATE_TABLES:
                expected_indexes.append(f"idx_{table}_date")
            else:
                expected_indexes.append(f"idx_{table}_datetime")
            
            for expected_index in expected_indexes:
                assert expected_index in indexes, f"{table}: インデックス {expected_index} が存在しません"
    
    def test_triggers(self):
        """トリガーを確認"""
        for table in EXPECTED_TABLES:
            self.cursor.execute("""
                SELECT trigger_name, event_manipulation, action_timing
                FROM information_schema.triggers
                WHERE event_object_table = %s
            """, (table,))
            
            triggers = self.cursor.fetchall()
            
            # updated_at自動更新トリガーがあることを確認
            trigger_found = False
            for trigger in triggers:
                if 'updated_at' in trigger[0].lower() and trigger[1] == 'UPDATE' and trigger[2] == 'BEFORE':
                    trigger_found = True
                    break
            
            assert trigger_found, f"{table}: updated_at自動更新トリガーが存在しません"
    
    def test_data_insertion_and_trigger(self):
        """データ挿入とトリガー動作を確認"""
        # stocks_1dテーブルでテスト
        table = 'stocks_1d'
        
        # テストデータ挿入
        test_data = {
            'symbol': 'TEST.T',
            'date': date(2024, 1, 1),
            'open': Decimal('1000.00'),
            'high': Decimal('1100.00'),
            'low': Decimal('950.00'),
            'close': Decimal('1050.00'),
            'volume': 100000
        }
        
        # 挿入前のクリーンアップ
        self.cursor.execute(f"DELETE FROM {table} WHERE symbol = %s", (test_data['symbol'],))
        self.conn.commit()
        
        # データ挿入
        self.cursor.execute(f"""
            INSERT INTO {table} (symbol, date, open, high, low, close, volume)
            VALUES (%(symbol)s, %(date)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s)
        """, test_data)
        self.conn.commit()
        
        # 挿入されたデータを確認
        self.cursor.execute(f"""
            SELECT symbol, date, open, high, low, close, volume, created_at, updated_at
            FROM {table} WHERE symbol = %s
        """, (test_data['symbol'],))
        
        result = self.cursor.fetchone()
        assert result is not None, "データが挿入されていません"
        
        # created_atとupdated_atが設定されていることを確認
        assert result[7] is not None, "created_atが設定されていません"
        assert result[8] is not None, "updated_atが設定されていません"
        
        # 初期状態ではcreated_atとupdated_atが同じ
        initial_updated_at = result[8]
        
        # データ更新
        import time
        time.sleep(1)  # 時間差を作るため
        
        self.cursor.execute(f"""
            UPDATE {table} SET close = %s WHERE symbol = %s
        """, (Decimal('1075.00'), test_data['symbol']))
        self.conn.commit()
        
        # 更新後のデータを確認
        self.cursor.execute(f"""
            SELECT updated_at FROM {table} WHERE symbol = %s
        """, (test_data['symbol'],))
        
        updated_result = self.cursor.fetchone()
        assert updated_result[0] > initial_updated_at, "updated_atが自動更新されていません"
        
        # テストデータのクリーンアップ
        self.cursor.execute(f"DELETE FROM {table} WHERE symbol = %s", (test_data['symbol'],))
        self.conn.commit()


def run_tests():
    """テストを実行する関数"""
    print("データベース初期化スクリプトのテストを開始します...")
    
    # pytest実行
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    if exit_code == 0:
        print("\n✅ すべてのテストが成功しました！")
    else:
        print("\n❌ テストに失敗しました。")
    
    return exit_code


if __name__ == '__main__':
    run_tests()