"""
JPX銘柄一覧データの分析スクリプト.

目的:
- JPXからダウンロードしたExcelファイル (data_j.xls) の構造を分析
- 作成したstock_masterテーブルとの整合性を確認。
"""

import io
from pathlib import Path
import sys
from typing import Any, Dict, Optional

import pandas as pd


# UTF-8エンコーディング設定
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def analyze_jpx_data(file_path: str) -> None:
    """JPXデータファイルを分析.

    Args:
        file_path: 分析対象のExcelファイルパス。
    """

    print("=" * 80)
    print("JPX銘柄一覧データ分析")
    print("=" * 80)

    # Excelファイルを読み込み
    print(f"\n[1] ファイル読み込み: {file_path}")
    try:
        df: pd.DataFrame = pd.read_excel(file_path)
        print(f"✓ 読み込み成功: {len(df)} 行 × {len(df.columns)} 列")
    except Exception as e:
        print(f"❌ 読み込み失敗: {e}")
        return

    # カラム情報表示
    print("\n[2] カラム情報")
    print("-" * 80)
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    # データ型情報
    print("\n[3] データ型情報")
    print("-" * 80)
    print(df.dtypes)

    # 先頭5行のサンプルデータ
    print("\n[4] サンプルデータ（先頭5行）")
    print("-" * 80)
    print(df.head())

    # 各カラムの統計情報
    print("\n[5] 各カラムの統計情報")
    print("-" * 80)

    for col in df.columns:
        print(f"\n【{col}】")
        print(f"  - データ型: {df[col].dtype}")
        print(f"  - NULL数: {df[col].isnull().sum()}")
        print(f"  - ユニーク数: {df[col].nunique()}")

        if df[col].dtype == "object":
            # 文字列型の場合、最大文字数を確認
            max_length = df[col].astype(str).str.len().max()
            print(f"  - 最大文字数: {max_length}")

            # サンプル値（重複除外）
            unique_values = df[col].dropna().unique()
            if len(unique_values) <= 10:
                print(f"  - 全ユニーク値: {list(unique_values)}")
            else:
                print(f"  - サンプル値（5件）: {list(unique_values[:5])}")

    # テーブル設計との対応確認
    print("\n" + "=" * 80)
    print("stock_master テーブル設計との対応確認")
    print("=" * 80)

    # 想定されるカラムマッピング
    mapping_candidates = {
        "stock_code": ["コード", "銘柄コード", "Code"],
        "stock_name": ["銘柄名", "名称", "Name"],
        "market_category": ["市場・商品区分", "市場区分", "Market"],
        "sector": ["業種", "33業種区分", "Sector"],
    }

    print("\n想定されるカラムマッピング:")
    print("-" * 80)

    for table_col, candidates in mapping_candidates.items():
        found = False
        for candidate in candidates:
            if candidate in df.columns:
                print(f"✓ {table_col:20} ← {candidate}")
                found = True
                break
        if not found:
            print(f"⚠ {table_col:20} ← [候補なし]")

    # データ格納可能性の検証
    print("\n" + "=" * 80)
    print("データ格納可能性の検証")
    print("=" * 80)

    validation_results = []

    # stock_code (VARCHAR(10))
    if "コード" in df.columns:
        code_col = "コード"
        max_code_length = df[code_col].astype(str).str.len().max()
        result = (
            "✓ OK"
            if max_code_length <= 10
            else f"❌ NG (最大{max_code_length}文字)"
        )
        validation_results.append(f"stock_code VARCHAR(10): {result}")
        print(f"  - {validation_results[-1]}")

    # stock_name (VARCHAR(100))
    if "銘柄名" in df.columns:
        name_col = "銘柄名"
        max_name_length = df[name_col].astype(str).str.len().max()
        result = (
            "✓ OK"
            if max_name_length <= 100
            else f"❌ NG (最大{max_name_length}文字)"
        )
        validation_results.append(f"stock_name VARCHAR(100): {result}")
        print(f"  - {validation_results[-1]}")

    # market_category (VARCHAR(50))
    if "市場・商品区分" in df.columns:
        market_col = "市場・商品区分"
        max_market_length = df[market_col].astype(str).str.len().max()
        result = (
            "✓ OK"
            if max_market_length <= 50
            else f"❌ NG (最大{max_market_length}文字)"
        )
        validation_results.append(f"market_category VARCHAR(50): {result}")
        print(f"  - {validation_results[-1]}")

    # sector (VARCHAR(100))
    if "33業種区分" in df.columns:
        sector_col = "33業種区分"
        max_sector_length = df[sector_col].astype(str).str.len().max()
        result = (
            "✓ OK"
            if max_sector_length <= 100
            else f"❌ NG (最大{max_sector_length}文字)"
        )
        validation_results.append(f"sector VARCHAR(100): {result}")
        print(f"  - {validation_results[-1]}")

    # 総合判定
    print("\n" + "=" * 80)
    print("総合判定")
    print("=" * 80)

    all_ok = all("✓ OK" in result for result in validation_results)

    if all_ok:
        print("✅ 現在のテーブル設計で全てのデータを格納可能です")
    else:
        print("⚠ 一部のカラムでサイズ調整が必要です")

    # 推奨される変更（必要な場合）
    print("\n[推奨される変更]")
    for result in validation_results:
        if "❌ NG" in result:
            print(f"  - {result}")

    if all_ok:
        print("  - 変更不要")

    print("\n" + "=" * 80)
    print("分析完了")
    print("=" * 80)


def analyze_column_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """カラムの統計情報を分析.

    Args:
        df: 分析対象のDataFrame

    Returns:
        統計情報の辞書。
    """
    stats: Dict[str, Any] = {}

    for col in df.columns:
        col_stats: Dict[str, Any] = {
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
            "sample_values": df[col].dropna().head(3).tolist(),
        }

        if df[col].dtype in ["int64", "float64"]:
            col_stats.update(
                {
                    "min": (
                        float(df[col].min())
                        if pd.notna(df[col].min())
                        else None
                    ),
                    "max": (
                        float(df[col].max())
                        if pd.notna(df[col].max())
                        else None
                    ),
                    "mean": (
                        float(df[col].mean())
                        if pd.notna(df[col].mean())
                        else None
                    ),
                }
            )

        stats[col] = col_stats

    return stats


def validate_stock_master_compatibility(df: pd.DataFrame) -> Dict[str, bool]:
    """stock_masterテーブルとの互換性をチェック.

    Args:
        df: JPXデータのDataFrame

    Returns:
        検証結果の辞書。
    """
    validation_results: Dict[str, bool] = {}

    # 必要なカラムの存在チェック
    required_columns: list[str] = [
        "コード",
        "銘柄名",
        "市場・商品区分",
        "33業種コード",
        "33業種区分",
    ]

    for col in required_columns:
        validation_results[f"has_{col}"] = col in df.columns

    # データ品質チェック
    if "コード" in df.columns:
        validation_results["code_format_valid"] = bool(
            df["コード"].astype(str).str.match(r"^\d{4}$").all()
        )

    if "銘柄名" in df.columns:
        validation_results["name_not_empty"] = bool(df["銘柄名"].notna().all())

    return validation_results


def print_validation_results(results: Dict[str, bool]) -> None:
    """検証結果を表示.

    Args:
        results: 検証結果の辞書。
    """
    print("\n[6] stock_masterテーブル互換性チェック")
    print("-" * 80)

    for check, passed in results.items():
        status: str = "✓" if passed else "❌"
        print(f"  {status} {check}: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    file_path: str = "data_j.xls"

    if not Path(file_path).exists():
        print(f"❌ ファイルが見つかりません: {file_path}")
        print("先にファイルをダウンロードしてください:")
        print(
            'curl -L -o data_j.xls "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"'
        )
        sys.exit(1)

    analyze_jpx_data(file_path)
