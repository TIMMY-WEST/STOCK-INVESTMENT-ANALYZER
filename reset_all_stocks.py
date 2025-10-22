#!/usr/bin/env python
"""
全ての株式データテーブル（1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo）の全レコードを削除するスクリプト
"""
import os
import sys


# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from models import (
    Stocks1d,
    Stocks1h,
    Stocks1m,
    Stocks1mo,
    Stocks1wk,
    Stocks5m,
    Stocks15m,
    Stocks30m,
    get_db_session,
)


def main():
    # 全ての株式データテーブル
    stock_tables = [
        ("stocks_1m", Stocks1m),
        ("stocks_5m", Stocks5m),
        ("stocks_15m", Stocks15m),
        ("stocks_30m", Stocks30m),
        ("stocks_1h", Stocks1h),
        ("stocks_1d", Stocks1d),
        ("stocks_1wk", Stocks1wk),
        ("stocks_1mo", Stocks1mo),
    ]

    print("=" * 60)
    print("全株式データテーブルのリセットを開始します")
    print("=" * 60)

    with get_db_session() as session:
        try:
            # 各テーブルの現在のレコード数を確認
            total_count = 0
            table_info = []

            print("\n現在のレコード数:")
            for table_name, table_class in stock_tables:
                count = session.query(table_class).count()
                table_info.append((table_name, table_class, count))
                total_count += count
                print(f"  {table_name:15s}: {count:,} 件")

            print(f"\n合計: {total_count:,} 件")

            if total_count == 0:
                print("\n全てのテーブルは既に空です。")
                return

            # 確認メッセージ
            print(
                f"\n警告: 全テーブルから合計 {total_count:,} 件のレコードを削除しようとしています。"
            )
            response = input("本当に削除しますか? (yes/no): ")

            if response.lower() != "yes":
                print("\n削除をキャンセルしました。")
                return

            # 全レコードを削除
            print("\nレコードを削除中...")
            total_deleted = 0

            for table_name, table_class, count_before in table_info:
                if count_before > 0:
                    deleted_count = session.query(table_class).delete()
                    total_deleted += deleted_count
                    print(f"  {table_name:15s}: {deleted_count:,} 件を削除")

            session.commit()

            # 削除後の確認
            print(f"\n削除完了:")
            print(f"  - 削除されたレコード数: {total_deleted:,} 件")

            # 各テーブルの削除後レコード数を確認
            print("\n削除後のレコード数:")
            remaining_total = 0
            for table_name, table_class in stock_tables:
                count_after = session.query(table_class).count()
                remaining_total += count_after
                print(f"  {table_name:15s}: {count_after:,} 件")

            print(f"\n残り合計: {remaining_total:,} 件")
            print("\n" + "=" * 60)
            print("全株式データテーブルのリセットが完了しました")
            print("=" * 60)

        except Exception as e:
            session.rollback()
            print(f"\nエラーが発生しました: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
