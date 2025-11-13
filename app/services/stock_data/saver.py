"""Saves stock price data for each timeframe to the database."""

from datetime import date, datetime
import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import get_db_session
from app.types import Interval
from app.utils.timeframe_utils import (
    get_display_name,
    get_model_for_interval,
    is_intraday_interval,
    validate_interval,
)


logger = logging.getLogger(__name__)


class StockDataSaveError(Exception):
    """データ保存エラー."""

    pass


class StockDataSaver:
    """株価データ保存クラス."""

    def __init__(self):
        """初期化."""
        self.logger = logger

    def save_stock_data(
        self,
        symbol: str,
        interval: Interval,
        data_list: List[Dict[str, Any]],
        session: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """株価データを保存.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            data_list: 保存するデータのリスト
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            保存結果の統計情報

        Raises:
            StockDataSaveError: データ保存失敗時。
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)

        # セッション管理
        if session:
            return self._save_with_session(
                session, symbol, interval, model_class, data_list
            )
        else:
            with get_db_session() as session:
                return self._save_with_session(
                    session, symbol, interval, model_class, data_list
                )

    def _save_with_session(
        self,
        session: Session,
        symbol: str,
        interval: Interval,
        model_class: Type[Any],
        data_list: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """セッションを使用してデータを保存(内部メソッド).

        Args:
            session: SQLAlchemyセッション
            symbol: 銘柄コード
            interval: 時間軸
            model_class: データベースモデルクラス
            data_list: 保存するデータのリスト

        Returns:
            保存結果の統計情報。

        Raises:
            StockDataSaveError: データ保存失敗時。
        """
        self.logger.info(
            f"データ保存開始: {symbol} (時間軸: {get_display_name(interval)}, "
            f"件数: {len(data_list)})"
        )

        existing_dates = self._get_existing_dates(
            session, model_class, symbol, interval
        )
        records_to_insert, stats = self._prepare_records(
            data_list, symbol, interval, existing_dates
        )

        self._bulk_insert(
            session, model_class, records_to_insert, symbol, interval
        )

        # コミットは呼び出し側で行う(トランザクション管理を分離)
        result = {
            "symbol": symbol,
            "interval": interval,
            "total": stats["total"],
            "saved": stats["saved"],
            "skipped": stats["skipped"],
            "errors": stats["errors"],
            "date_range": {
                "start": (
                    stats["date_start"].strftime("%Y-%m-%d")
                    if stats["date_start"]
                    else None
                ),
                "end": (
                    stats["date_end"].strftime("%Y-%m-%d")
                    if stats["date_end"]
                    else None
                ),
            },
        }

        self.logger.info(
            f"データ保存完了: {symbol} (時間軸: {get_display_name(interval)}) - "
            f"保存: {stats['saved']}, スキップ: {stats['skipped']}, エラー: {stats['errors']}"
        )

        return result

    def save_multiple_timeframes(
        self, symbol: str, data_dict: Dict[Interval, List[Dict[str, Any]]]
    ) -> Dict[Interval, Dict[str, Any]]:
        """複数時間軸のデータを一度に保存.

        Args:
            symbol: 銘柄コード
            data_dict: {interval: data_list} の辞書

        Returns:
            {interval: 保存結果} の辞書

        Raises:
            StockDataSaveError: データ保存失敗時。
        """
        results = {}

        with get_db_session() as session:
            for interval, data_list in data_dict.items():
                try:
                    result = self.save_stock_data(
                        symbol=symbol,
                        interval=interval,
                        data_list=data_list,
                        session=session,
                    )
                    results[interval] = result

                except Exception as e:
                    self.logger.error(f"時間軸 {interval} のデータ保存エラー: {e}")
                    results[interval] = {
                        "symbol": symbol,
                        "interval": interval,
                        "error": str(e),
                    }

        return results

    def save_batch_stock_data(
        self,
        symbols_data: Dict[str, List[Dict[str, Any]]],
        interval: Interval,
    ) -> Dict[str, Any]:
        """複数銘柄のデータをバッチ保存(重複データ事前除外方式).

        Args:
            symbols_data: {銘柄コード: データリスト} の辞書
            interval: 時間軸

        Returns:
            バッチ保存結果の統計情報

        Raises:
            StockDataSaveError: データ保存失敗時。
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)

        total_saved = 0
        total_skipped = 0
        total_errors = 0
        results_by_symbol: Dict[str, Dict[str, Any]] = {}

        self.logger.info(
            f"バッチデータ保存開始: {len(symbols_data)}銘柄 "
            f"(時間軸: {get_display_name(interval)})"
        )

        def _build_batch_inserts_and_stats(
            filtered_symbols_data: Dict[str, List[Dict[str, Any]]],
            original_symbols_data: Dict[str, List[Dict[str, Any]]],
        ) -> Tuple[
            List[Dict[str, Any]], Dict[str, Dict[str, Any]], Dict[str, int]
        ]:
            """バッチ用の挿入レコードと統計を構築する."""
            all_records: List[Dict[str, Any]] = []
            results_by_symbol: Dict[str, Dict[str, Any]] = {}
            total_saved = 0
            total_skipped = 0
            total_errors = 0
            for symbol, data_list in filtered_symbols_data.items():
                saved_count = 0
                skipped_count = len(
                    original_symbols_data.get(symbol, [])
                ) - len(data_list)
                error_count = 0
                for data in data_list:
                    try:
                        all_records.append({**data, "symbol": symbol})
                        saved_count += 1
                    except Exception as e:
                        error_count += 1
                        self.logger.error(f"レコード作成エラー: {symbol}: {e}")
                results_by_symbol[symbol] = {
                    "saved": saved_count,
                    "skipped": skipped_count,
                    "errors": error_count,
                    "total": len(original_symbols_data.get(symbol, [])),
                }
                total_saved += saved_count
                total_skipped += skipped_count
                total_errors += error_count
            totals: Dict[str, int] = {
                "total_records": sum(
                    len(lst) for lst in original_symbols_data.values()
                ),
                "total_saved": total_saved,
                "total_skipped": total_skipped,
                "total_errors": total_errors,
            }
            return all_records, results_by_symbol, totals

        try:
            with get_db_session() as session:
                # 全銘柄の重複チェックを一括実行
                filtered_symbols_data = self._filter_duplicate_data(
                    session, model_class, symbols_data, interval
                )

                # バルクインサート用のレコードリストと統計を構築
                (
                    all_records_to_insert,
                    results_by_symbol,
                    totals,
                ) = _build_batch_inserts_and_stats(
                    filtered_symbols_data, symbols_data
                )
                total_saved = totals["total_saved"]
                total_skipped = totals["total_skipped"]
                total_errors = totals["total_errors"]

                # バルクインサートを実行
                self._bulk_insert(
                    session,
                    model_class,
                    all_records_to_insert,
                    "batch",
                    interval,
                )

                total_records = sum(
                    len(data_list) for data_list in symbols_data.values()
                )
                self.logger.info(
                    f"バッチデータ保存完了: {len(symbols_data)}銘柄 "
                    f"(時間軸: {get_display_name(interval)}) - "
                    f"対象データ数: {total_records}, 保存: {total_saved}, "
                    f"重複スキップ: {total_skipped}, エラー: {total_errors}"
                )

        except StockDataSaveError:
            # StockDataSaveErrorはそのまま再送出
            raise
        except Exception as e:
            # その他の予期しないエラー
            raise StockDataSaveError(
                f"バッチデータ保存中に予期しないエラー: "
                f"(時間軸: {get_display_name(interval)}): {e}"
            )

        return {
            "interval": interval,
            "total_symbols": len(symbols_data),
            "total_saved": total_saved,
            "total_skipped": total_skipped,
            "total_errors": total_errors,
            "results_by_symbol": results_by_symbol,
        }

    def _filter_duplicate_data(
        self,
        session: Session,
        model_class: type,
        symbols_data: Dict[str, List[Dict[str, Any]]],
        interval: Interval,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """重複データを事前に除外.

        Args:
            session: SQLAlchemyセッション
            model_class: データベースモデルクラス
            symbols_data: 元のデータ
            interval: 時間軸

        Returns:
            重複除外後のデータ。
        """
        filtered_data: Dict[str, List[Dict[str, Any]]] = {}

        # 時間軸に応じて適切なカラム名を決定
        date_column_name = (
            "date" if not is_intraday_interval(interval) else "datetime"
        )
        date_column = getattr(model_class, date_column_name)

        for symbol, data_list in symbols_data.items():
            if not data_list:
                filtered_data[symbol] = []
                continue

            # 該当銘柄の既存データの日付/日時を取得
            existing_dates = set()
            try:
                existing_records = (
                    session.query(date_column)
                    .filter(model_class.symbol == symbol)  # type: ignore[attr-defined]
                    .all()
                )
                existing_dates = {record[0] for record in existing_records}
            except Exception as e:
                self.logger.warning(f"既存データ取得エラー: {symbol}: {e}")
                # エラーの場合は安全のため全データを保存対象とする
                filtered_data[symbol] = data_list
                continue

            # 重複していないデータのみを抽出
            non_duplicate_data = []
            for data in data_list:
                data_date = data.get("date") or data.get("datetime")
                if data_date and data_date not in existing_dates:
                    non_duplicate_data.append(data)
                elif data_date in existing_dates:
                    self.logger.debug(
                        f"重複データをスキップ: {symbol} ({data_date}) "
                        f"(時間軸: {get_display_name(interval)})"
                    )

            filtered_data[symbol] = non_duplicate_data

            if len(non_duplicate_data) < len(data_list):
                skipped_count = len(data_list) - len(non_duplicate_data)
                self.logger.info(
                    f"重複データ除外: {symbol} - "
                    f"対象: {len(data_list)}件, 保存対象: {len(non_duplicate_data)}件, "
                    f"重複スキップ: {skipped_count}件"
                )

        return filtered_data

    def get_latest_date(
        self,
        symbol: str,
        interval: Interval,
        session: Optional[Session] = None,
    ) -> Optional[datetime | date]:
        """データベース内の最新データ日時を取得.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            最新データの日時、データがない場合はNone。
        """
        # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)
        is_intraday = is_intraday_interval(interval)

        # 最新日時の取得
        def _get_latest(sess: Session):
            if is_intraday:
                # 分足・時間足: datetime
                result = (
                    sess.query(model_class.datetime)  # type: ignore[attr-defined]
                    .filter(model_class.symbol == symbol)
                    .order_by(model_class.datetime.desc())  # type: ignore[attr-defined]
                    .first()
                )
            else:
                # 日足・週足・月足: date
                result = (
                    sess.query(model_class.date)  # type: ignore[attr-defined]
                    .filter(model_class.symbol == symbol)
                    .order_by(model_class.date.desc())  # type: ignore[attr-defined]
                    .first()
                )

            return result[0] if result else None

        if session:
            return _get_latest(session)
        else:
            with get_db_session() as session:
                return _get_latest(session)

    def count_records(
        self,
        symbol: str,
        interval: Interval,
        session: Optional[Session] = None,
    ) -> int:
        """データベース内のレコード数を取得.

        Args:
            symbol: 銘柄コード
            interval: 時間軸
            session: SQLAlchemyセッション（Noneの場合は新規作成）

        Returns:
            レコード数。
        """  # 時間軸の検証
        if not validate_interval(interval):
            raise ValueError(f"サポートされていない時間軸: {interval}")

        # モデルクラスの取得
        model_class = get_model_for_interval(interval)

        # レコード数の取得
        def _count(sess: Session):
            return (
                sess.query(model_class)
                .filter(model_class.symbol == symbol)
                .count()
            )

        if session:
            return _count(session)
        else:
            with get_db_session() as session:
                return _count(session)

    def _get_existing_dates(
        self,
        session: Session,
        model_class: type,
        symbol: str,
        interval: Interval,
    ) -> set:
        """既存データの日付/日時を安全に取得する."""
        try:
            date_column_name = (
                "date" if not is_intraday_interval(interval) else "datetime"
            )
            date_column = getattr(model_class, date_column_name)
            existing_records = (
                session.query(date_column)
                .filter(model_class.symbol == symbol)  # type: ignore[attr-defined]
                .all()
            )
            return {record[0] for record in existing_records}
        except Exception as e:
            self.logger.warning(f"既存データ取得エラー: {symbol}: {e}")
            return set()

    def _prepare_records(
        self,
        data_list: List[Dict[str, Any]],
        symbol: str,
        interval: Interval,
        existing_dates: set,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """保存対象レコードを構築し、統計値も更新する."""
        saved_count = 0
        skipped_count = 0
        error_count = 0
        date_start: Optional[Any] = None
        date_end: Optional[Any] = None
        records: List[Dict[str, Any]] = []
        for data in data_list:
            current_date = data.get("date") or data.get("datetime")
            if current_date is not None:
                if date_start is None:
                    date_start = current_date
                elif current_date < date_start:
                    date_start = current_date
                if date_end is None:
                    date_end = current_date
                elif current_date > date_end:
                    date_end = current_date
            try:
                if current_date in existing_dates:
                    skipped_count += 1
                    self.logger.debug(
                        f"重複データをスキップ: {symbol} ({current_date}) "
                        f"(時間軸: {get_display_name(interval)})"
                    )
                    continue
                records.append({**data, "symbol": symbol})
                saved_count += 1
            except Exception as e:
                error_count += 1
                self.logger.error(f"レコード準備エラー: {symbol} ({current_date}): {e}")
        stats = {
            "saved": saved_count,
            "skipped": skipped_count,
            "errors": error_count,
            "date_start": date_start,
            "date_end": date_end,
            "total": len(data_list),
        }
        return records, stats

    def _bulk_insert(
        self,
        session: Session,
        model_class: Type[Any],
        records: List[Dict[str, Any]],
        symbol: str,
        interval: Interval,
    ) -> None:
        """レコードをバルクインサートする."""
        if not records:
            return
        mapper_or_class: Any = getattr(model_class, "__mapper__", model_class)
        try:
            session.bulk_insert_mappings(mapper_or_class, records)
            self.logger.debug(f"バルクインサート実行: {len(records)}件")
        except SQLAlchemyError as e:
            self.logger.error(
                f"バルクインサートエラー: {symbol} "
                f"(時間軸: {get_display_name(interval)}): {e}"
            )
            raise StockDataSaveError(
                f"データ保存に失敗: {symbol} "
                f"(時間軸: {get_display_name(interval)}): {e}"
            )
