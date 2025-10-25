"""複数時間軸データ取得のテストスクリプト.

各時間軸でのデータ取得・保存機能を動作確認します。
"""

import os
import sys


# プロジェクトルートをパスに追加
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

import logging  # noqa: E402

from app.services.stock_data.orchestrator import (  # noqa: E402
    StockDataOrchestrator,
)
from app.utils.timeframe_utils import (  # noqa: E402
    get_all_intervals,
    get_display_name,
)


# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def test_single_timeframe(symbol: str, interval: str):
    """単一時間軸のテスト."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"単一時間軸テスト: {symbol} ({get_display_name(interval)})")
    logger.info(f"{'=' * 80}")

    orchestrator = StockDataOrchestrator()

    try:
        result = orchestrator.fetch_and_save(
            symbol=symbol, interval=interval, period=None  # 推奨期間を使用
        )

        if result["success"]:
            logger.info(f"✓ 成功: {get_display_name(interval)}")
            logger.info(f"  取得件数: {result['fetch_count']}")
            logger.info(f"  保存件数: {result['save_result']['saved']}")
            logger.info(f"  スキップ: {result['save_result']['skipped']}")
            logger.info(
                f"  レコード数: {result['integrity_check']['record_count']}"
            )
        else:
            logger.error(f"✗ 失敗: {get_display_name(interval)}")
            logger.error(f"  エラー: {result.get('error')}")

        return result

    except Exception as e:
        logger.error(f"✗ 例外発生: {e}")
        return {"success": False, "error": str(e)}


def test_multiple_timeframes(symbol: str, intervals: list[str] = None):
    """複数時間軸のテスト."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"複数時間軸テスト: {symbol}")
    logger.info(f"{'=' * 80}")

    if intervals is None:
        intervals = get_all_intervals()

    orchestrator = StockDataOrchestrator()

    try:
        results = orchestrator.fetch_and_save_multiple_timeframes(
            symbol=symbol, intervals=intervals, period=None
        )

        # サマリー表示
        logger.info(f"\n{'=' * 80}")
        logger.info("実行結果サマリー")
        logger.info(f"{'=' * 80}")

        success_count = 0
        total_saved = 0

        for interval, result in results.items():
            if result.get("success"):
                success_count += 1
                saved = result["save_result"]["saved"]
                total_saved += saved
                logger.info(
                    f"✓ {get_display_name(interval)}: " f"{saved}件保存"
                )
            else:
                logger.error(
                    f"✗ {get_display_name(interval)}: "
                    f"{result.get('error', '不明なエラー')}"
                )

        logger.info(f"\n成功: {success_count}/{len(intervals)} 時間軸")
        logger.info(f"合計保存件数: {total_saved}件")

        return results

    except Exception as e:
        logger.error(f"✗ 例外発生: {e}")
        return {}


def test_status(symbol: str):
    """データ状態の確認."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"データ状態確認: {symbol}")
    logger.info(f"{'=' * 80}")

    orchestrator = StockDataOrchestrator()

    try:
        status = orchestrator.get_status(symbol)

        for interval, info in status.items():
            if "error" in info:
                logger.warning(
                    f"{get_display_name(interval)}: エラー - {info['error']}"
                )
            else:
                logger.info(
                    f"{get_display_name(interval)}: "
                    f"{info['record_count']}件 "
                    f"(最新: {info['latest_date'] or 'データなし'})"
                )

        return status

    except Exception as e:
        logger.error(f"✗ 例外発生: {e}")
        return {}


def main():
    """メイン処理."""
    # テスト対象銘柄
    test_symbol = "7203.T"  # トヨタ自動車

    logger.info(f"\n{'#' * 80}")
    logger.info("# 複数時間軸データ取得テスト")
    logger.info(f"# テスト銘柄: {test_symbol}")
    logger.info(f"{'#' * 80}")

    # 1. 単一時間軸テスト（日足）
    logger.info("\n" + "=" * 80)
    logger.info("1. 単一時間軸テスト（日足）")
    logger.info("=" * 80)
    test_single_timeframe(test_symbol, "1d")

    # 2. データ状態確認
    logger.info("\n" + "=" * 80)
    logger.info("2. データ状態確認（初期）")
    logger.info("=" * 80)
    test_status(test_symbol)

    # 3. 複数時間軸テスト（一部の時間軸）
    logger.info("\n" + "=" * 80)
    logger.info("3. 複数時間軸テスト（一部）")
    logger.info("=" * 80)
    test_intervals = ["1h", "1d", "1wk"]
    test_multiple_timeframes(test_symbol, test_intervals)

    # 4. データ状態確認（最終）
    logger.info("\n" + "=" * 80)
    logger.info("4. データ状態確認（最終）")
    logger.info("=" * 80)
    test_status(test_symbol)

    logger.info(f"\n{'#' * 80}")
    logger.info("# テスト完了")
    logger.info(f"{'#' * 80}\n")


if __name__ == "__main__":
    main()
