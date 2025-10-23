"""JPX銘柄一覧取得・更新サービス.

JPX公式サイトからExcel形式の銘柄一覧をダウンロードし、
データベースの銘柄マスタを更新する機能を提供します。
"""

from datetime import datetime
from io import BytesIO
import logging
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import requests
from sqlalchemy.orm import Session

from models import StockMaster, StockMasterUpdate, get_db_session


logger = logging.getLogger(__name__)


class JPXStockServiceError(Exception):
    """JPX銘柄サービス関連エラーの基底クラス."""

    pass


class JPXDownloadError(JPXStockServiceError):
    """JPXからのダウンロードエラー."""

    pass


class JPXParseError(JPXStockServiceError):
    """JPXデータのパースエラー."""

    pass


class JPXStockService:
    """JPX銘柄一覧取得・更新サービス."""

    # JPX銘柄一覧のURL
    JPX_STOCK_LIST_URL = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"

    # リクエストタイムアウト（秒）
    REQUEST_TIMEOUT = 30

    def __init__(self):
        self.session = requests.Session()
        # User-Agentを設定してブロックを回避
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

    def fetch_jpx_stock_list(self) -> pd.DataFrame:
        """JPXから銘柄一覧を取得してDataFrameとして返す.

        Returns:
            pd.DataFrame: 正規化された銘柄一覧データ

        Raises:
            JPXDownloadError: ダウンロードに失敗した場合
            JPXParseError: データのパースに失敗した場合。
        """
        try:
            logger.info(
                f"JPX銘柄一覧をダウンロード中: {self.JPX_STOCK_LIST_URL}"
            )

            # Excelファイルをダウンロード
            response = self.session.get(
                self.JPX_STOCK_LIST_URL, timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()

            logger.info(f"ダウンロード完了: {len(response.content)} bytes")

            # Excelデータを読み込み
            df = pd.read_excel(BytesIO(response.content))

            logger.info(f"Excel読み込み完了: {len(df)} 行")

            # データを正規化
            normalized_data = self._normalize_jpx_data(df)

            # 正規化されたデータをDataFrameに変換（後方互換性のため）
            normalized_df = pd.DataFrame(normalized_data)

            logger.info(f"データ正規化完了: {len(normalized_df)} 銘柄")

            return normalized_df

        except requests.exceptions.RequestException as e:
            error_msg = f"JPXからのダウンロードに失敗しました: {str(e)}"
            logger.error(error_msg)
            raise JPXDownloadError(error_msg) from e

        except Exception as e:
            error_msg = f"JPXデータの処理に失敗しました: {str(e)}"
            logger.error(error_msg)
            raise JPXParseError(error_msg) from e

    def _normalize_jpx_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """JPXのExcelデータを正規化する.

        Args:
            df: 生のJPXデータ

        Returns:
            List[Dict[str, Any]]: 正規化されたデータ（辞書のリスト）

        Raises:
            JPXParseError: データの正規化に失敗した場合。
        """
        try:
            # JPXのExcelフォーマットに応じて列名をマッピング
            # 実際のJPXファイルの列名に合わせて調整が必要
            expected_columns = [
                "コード",
                "銘柄名",
                "市場・商品区分",
                "33業種コード",
                "33業種区分",
                "17業種コード",
                "17業種区分",
                "規模コード",
                "規模区分",
            ]

            # 利用可能な列を確認
            available_columns = df.columns.tolist()
            logger.debug(f"利用可能な列: {available_columns}")

            # 必要な列を抽出（存在する列のみ）
            column_mapping = {}
            for expected_col in expected_columns:
                if expected_col in available_columns:
                    column_mapping[expected_col] = expected_col

            # 最低限必要な列（コード、銘柄名）が存在するかチェック
            if (
                "コード" not in column_mapping
                and "stock_code" not in available_columns
            ):
                # フォールバック: 最初の列をコードとして使用
                if len(available_columns) >= 1:
                    column_mapping[available_columns[0]] = "コード"

            if (
                "銘柄名" not in column_mapping
                and "stock_name" not in available_columns
            ):
                # フォールバック: 2番目の列を銘柄名として使用
                if len(available_columns) >= 2:
                    column_mapping[available_columns[1]] = "銘柄名"

            if not column_mapping:
                raise JPXParseError("必要な列が見つかりません")

            # データを抽出
            selected_df = df[list(column_mapping.keys())].copy()
            selected_df.columns = [
                column_mapping[col] for col in selected_df.columns
            ]

            # 標準的な列名にマッピング
            normalized_df = pd.DataFrame()
            normalized_df["stock_code"] = selected_df.get("コード", "")
            normalized_df["stock_name"] = selected_df.get("銘柄名", "")
            normalized_df["market_category"] = selected_df.get(
                "市場・商品区分", ""
            )
            normalized_df["sector_code_33"] = selected_df.get(
                "33業種コード", ""
            )
            normalized_df["sector_name_33"] = selected_df.get("33業種区分", "")
            normalized_df["sector_code_17"] = selected_df.get(
                "17業種コード", ""
            )
            normalized_df["sector_name_17"] = selected_df.get("17業種区分", "")
            normalized_df["scale_code"] = selected_df.get("規模コード", "")
            normalized_df["scale_category"] = selected_df.get("規模区分", "")

            # データクリーニング
            normalized_df = normalized_df.dropna(
                subset=["stock_code", "stock_name"]
            )
            normalized_df["stock_code"] = (
                normalized_df["stock_code"].astype(str).str.strip()
            )
            normalized_df["stock_name"] = (
                normalized_df["stock_name"].astype(str).str.strip()
            )

            # 空の銘柄コードを除外
            normalized_df = normalized_df[normalized_df["stock_code"] != ""]

            # データ取得日を追加
            normalized_df["data_date"] = datetime.now().strftime("%Y%m%d")

            # 辞書のリストに変換
            result = []
            for _, row in normalized_df.iterrows():
                result.append(
                    {
                        "stock_code": row["stock_code"],
                        "stock_name": row["stock_name"],
                        "market_category": (
                            row["market_category"]
                            if pd.notna(row["market_category"])
                            and row["market_category"] != ""
                            else None
                        ),
                        "sector_code_33": (
                            row["sector_code_33"]
                            if pd.notna(row["sector_code_33"])
                            and row["sector_code_33"] != ""
                            else None
                        ),
                        "sector_name_33": (
                            row["sector_name_33"]
                            if pd.notna(row["sector_name_33"])
                            and row["sector_name_33"] != ""
                            else None
                        ),
                        "sector_code_17": (
                            row["sector_code_17"]
                            if pd.notna(row["sector_code_17"])
                            and row["sector_code_17"] != ""
                            else None
                        ),
                        "sector_name_17": (
                            row["sector_name_17"]
                            if pd.notna(row["sector_name_17"])
                            and row["sector_name_17"] != ""
                            else None
                        ),
                        "scale_code": (
                            row["scale_code"]
                            if pd.notna(row["scale_code"])
                            and row["scale_code"] != ""
                            else None
                        ),
                        "scale_category": (
                            row["scale_category"]
                            if pd.notna(row["scale_category"])
                            and row["scale_category"] != ""
                            else None
                        ),
                        "data_date": row["data_date"],
                    }
                )

            return result

        except Exception as e:
            error_msg = f"データの正規化に失敗しました: {str(e)}"
            logger.error(error_msg)
            raise JPXParseError(error_msg) from e

    def update_stock_master(
        self, update_type: str = "manual"
    ) -> Dict[str, Any]:
        """銘柄マスタを更新する.

        Args:
            update_type: 更新タイプ ('manual' または 'scheduled')

        Returns:
            Dict[str, Any]: 更新結果のサマリー

        Raises:
            JPXStockServiceError: 更新処理に失敗した場合。
        """
        update_record = {
            "update_type": update_type,
            "total_stocks": 0,
            "added_stocks": 0,
            "updated_stocks": 0,
            "removed_stocks": 0,
            "status": "success",
            "error_message": None,
        }

        update_id = None

        try:
            # JPXから最新データを取得
            df = self.fetch_jpx_stock_list()
            update_record["total_stocks"] = len(df)

            with get_db_session() as session:
                # 更新履歴レコードを作成
                update_id = self._create_update_record(session, update_record)

                # 既存の銘柄コード一覧を取得
                existing_codes = self._get_existing_stock_codes(session)

                # 新規銘柄と更新銘柄を処理
                new_codes = set(df["stock_code"].tolist())

                for _, row in df.iterrows():
                    code = str(row["stock_code"]).strip()
                    if not code:
                        continue

                    if code not in existing_codes:
                        # 新規銘柄を追加
                        self._insert_stock(session, row)
                        update_record["added_stocks"] += 1
                    else:
                        # 既存銘柄を更新
                        self._update_stock(session, row)
                        update_record["updated_stocks"] += 1

                # 削除された銘柄を無効化
                removed_codes = existing_codes - new_codes
                update_record["removed_stocks"] = len(removed_codes)
                if removed_codes:
                    self._deactivate_stocks(session, removed_codes)

                # 更新履歴を完了
                self._complete_update_record(session, update_id, update_record)

                session.commit()

            logger.info(f"銘柄マスタ更新完了: {update_record}")
            return update_record

        except Exception as e:
            error_msg = f"銘柄マスタの更新に失敗しました: {str(e)}"
            logger.error(error_msg)

            update_record["status"] = "failed"
            update_record["error_message"] = error_msg

            # エラー時も更新履歴を記録
            if update_id:
                try:
                    with get_db_session() as session:
                        self._complete_update_record(
                            session, update_id, update_record
                        )
                        session.commit()
                except Exception as log_error:
                    logger.error(f"エラーログの記録に失敗: {log_error}")

            raise JPXStockServiceError(error_msg) from e

    def _create_update_record(
        self, session: Session, update_record: Dict[str, Any]
    ) -> int:
        """更新履歴レコードを作成."""
        update = StockMasterUpdate(
            update_type=update_record["update_type"],
            total_stocks=update_record["total_stocks"],
            status="running",
        )
        session.add(update)
        session.flush()
        return update.id

    def _get_existing_stock_codes(self, session: Session) -> Set[str]:
        """既存の有効な銘柄コード一覧を取得."""
        result = (
            session.query(StockMaster.stock_code)
            .filter(StockMaster.is_active == 1)
            .all()
        )
        return {code[0] for code in result}

    def _insert_stock(self, session: Session, row: pd.Series) -> None:
        """新規銘柄を挿入."""
        stock = StockMaster(
            stock_code=str(row["stock_code"]).strip(),
            stock_name=str(row["stock_name"]).strip(),
            market_category=str(row.get("market_category", "")).strip()
            or None,
            sector_code_33=str(row.get("sector_code_33", "")).strip() or None,
            sector_name_33=str(row.get("sector_name_33", "")).strip() or None,
            sector_code_17=str(row.get("sector_code_17", "")).strip() or None,
            sector_name_17=str(row.get("sector_name_17", "")).strip() or None,
            scale_code=str(row.get("scale_code", "")).strip() or None,
            scale_category=str(row.get("scale_category", "")).strip() or None,
            data_date=str(row.get("data_date", "")).strip() or None,
            is_active=1,
        )
        session.add(stock)

    def _update_stock(self, session: Session, row: pd.Series) -> None:
        """既存銘柄を更新."""
        stock = (
            session.query(StockMaster)
            .filter(StockMaster.stock_code == str(row["stock_code"]).strip())
            .first()
        )

        if stock:
            stock.stock_name = str(row["stock_name"]).strip()
            stock.market_category = (
                str(row.get("market_category", "")).strip() or None
            )
            stock.sector_code_33 = (
                str(row.get("sector_code_33", "")).strip() or None
            )
            stock.sector_name_33 = (
                str(row.get("sector_name_33", "")).strip() or None
            )
            stock.sector_code_17 = (
                str(row.get("sector_code_17", "")).strip() or None
            )
            stock.sector_name_17 = (
                str(row.get("sector_name_17", "")).strip() or None
            )
            stock.scale_code = str(row.get("scale_code", "")).strip() or None
            stock.scale_category = (
                str(row.get("scale_category", "")).strip() or None
            )
            stock.data_date = str(row.get("data_date", "")).strip() or None
            stock.is_active = 1

    def _deactivate_stocks(
        self, session: Session, stock_codes: Set[str]
    ) -> None:
        """指定された銘柄を無効化."""
        session.query(StockMaster).filter(
            StockMaster.stock_code.in_(stock_codes)
        ).update({"is_active": 0}, synchronize_session=False)

    def _complete_update_record(
        self, session: Session, update_id: int, update_record: Dict[str, Any]
    ) -> None:
        """更新履歴レコードを完了."""
        update = (
            session.query(StockMasterUpdate)
            .filter(StockMasterUpdate.id == update_id)
            .first()
        )

        if update:
            update.added_stocks = update_record["added_stocks"]
            update.updated_stocks = update_record["updated_stocks"]
            update.removed_stocks = update_record["removed_stocks"]
            update.status = update_record["status"]
            update.error_message = update_record.get("error_message")
            update.completed_at = datetime.now()

    def get_stock_list(
        self,
        is_active: Optional[bool] = True,
        market_category: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0,
    ) -> Dict[str, Any]:
        """銘柄マスタ一覧を取得.

        Args:
            is_active: 有効フラグでフィルタ (None=全て, True=有効のみ, False=無効のみ)
            market_category: 市場区分でフィルタ
            limit: 取得件数上限
            offset: オフセット

        Returns:
            Dict[str, Any]: 銘柄一覧と総件数。
        """
        try:
            with get_db_session() as session:
                query = session.query(StockMaster)

                # フィルタ条件を適用
                if is_active is not None:
                    query = query.filter(
                        StockMaster.is_active == (1 if is_active else 0)
                    )

                if market_category:
                    query = query.filter(
                        StockMaster.market_category.ilike(
                            f"%{market_category}%"
                        )
                    )

                # 総件数を取得
                total = query.count()

                # ページネーション
                stocks = query.offset(offset).limit(limit).all()

                return {
                    "total": total,
                    "stocks": [stock.to_dict() for stock in stocks],
                }

        except Exception as e:
            error_msg = f"銘柄一覧の取得に失敗しました: {str(e)}"
            logger.error(error_msg)
            raise JPXStockServiceError(error_msg) from e
