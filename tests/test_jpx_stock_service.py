"""
JPX銘柄サービスのテストコード.
"""

from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
import requests

from services.jpx_stock_service import (
    JPXDownloadError,
    JPXParseError,
    JPXStockService,
    JPXStockServiceError,
)


class TestJPXStockService:
    """JPXStockServiceのテストクラス."""

    def setup_method(self):
        """各テストメソッドの前に実行される初期化処理."""
        self.service = JPXStockService()

    def test_init(self):
        """初期化のテスト."""
        assert (
            self.service.JPX_STOCK_LIST_URL
            == "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
        )
        assert self.service.REQUEST_TIMEOUT == 30
        assert "User-Agent" in self.service.session.headers

    @patch("services.jpx_stock_service.requests.Session.get")
    @patch("services.jpx_stock_service.pd.read_excel")
    def test_fetch_jpx_stock_list_success(self, mock_read_excel, mock_get):
        """JPX銘柄一覧取得の成功テスト."""
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.content = b"mock excel content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # モックDataFrameを設定
        mock_df = pd.DataFrame(
            {
                "コード": ["1301", "1332"],
                "銘柄名": ["極洋", "日本水産"],
                "市場・商品区分": ["プライム", "プライム"],
            }
        )
        mock_read_excel.return_value = mock_df

        # _normalize_jpx_dataメソッドをモック
        normalized_df = pd.DataFrame(
            {
                "stock_code": ["1301", "1332"],
                "stock_name": ["極洋", "日本水産"],
                "market_category": ["プライム", "プライム"],
                "data_date": ["20241201", "20241201"],
            }
        )

        with patch.object(
            self.service, "_normalize_jpx_data", return_value=normalized_df
        ):
            result = self.service.fetch_jpx_stock_list()

        # 検証
        assert len(result) == 2
        assert result.iloc[0]["stock_code"] == "1301"
        assert result.iloc[0]["stock_name"] == "極洋"
        mock_get.assert_called_once()
        mock_read_excel.assert_called_once()

    @patch("services.jpx_stock_service.requests.Session.get")
    def test_fetch_jpx_stock_list_download_error(self, mock_get):
        """JPX銘柄一覧取得のダウンロードエラーテスト."""
        # リクエストエラーを発生させる
        mock_get.side_effect = requests.exceptions.RequestException(
            "Connection error"
        )

        with pytest.raises(JPXDownloadError) as exc_info:
            self.service.fetch_jpx_stock_list()

        assert "JPXからのダウンロードに失敗しました" in str(exc_info.value)

    @patch("services.jpx_stock_service.requests.Session.get")
    @patch("services.jpx_stock_service.pd.read_excel")
    def test_fetch_jpx_stock_list_parse_error(self, mock_read_excel, mock_get):
        """JPX銘柄一覧取得のパースエラーテスト."""
        # モックレスポンスを設定
        mock_response = Mock()
        mock_response.content = b"mock excel content"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # パースエラーを発生させる
        mock_read_excel.side_effect = Exception("Parse error")

        with pytest.raises(JPXParseError) as exc_info:
            self.service.fetch_jpx_stock_list()

        assert "JPXデータの処理に失敗しました" in str(exc_info.value)

    def test_normalize_jpx_data_success(self):
        """JPXデータ正規化の成功テスト."""
        # テスト用のDataFrameを作成
        input_df = pd.DataFrame(
            {
                "コード": ["1301", "1332", ""],
                "銘柄名": ["極洋", "日本水産", ""],
                "市場・商品区分": [
                    "プライム（内国株式）",
                    "プライム（内国株式）",
                    "スタンダード",
                ],
                "33業種コード": ["050", "050", "060"],
                "33業種区分": ["水産・農林業", "水産・農林業", "鉱業"],
                "17業種コード": ["050", "050", "060"],
                "17業種区分": ["水産・農林業", "水産・農林業", "鉱業"],
                "規模コード": ["6", "6", "7"],
                "規模区分": ["TOPIX Mid400", "TOPIX Mid400", "TOPIX Small"],
            }
        )

        result = self.service._normalize_jpx_data(input_df)

        # 検証
        assert len(result) == 2  # 空のコードは除外される
        assert result[0]["stock_code"] == "1301"
        assert result[0]["stock_name"] == "極洋"
        assert result[0]["market_category"] == "プライム（内国株式）"
        assert result[0]["sector_code_33"] == "050"
        assert result[0]["sector_name_33"] == "水産・農林業"
        assert "data_date" in result[0]

    def test_normalize_jpx_data_minimal_columns(self):
        """最小限のカラムでのJPXデータ正規化テスト."""
        # 最小限のカラムのみのDataFrame
        test_data = pd.DataFrame(
            {"コード": ["1301", "1332"], "銘柄名": ["極洋", "日本水産"]}
        )

        result = self.service._normalize_jpx_data(test_data)

        # 検証
        assert len(result) == 2
        assert result[0]["stock_code"] == "1301"
        assert result[0]["stock_name"] == "極洋"
        assert result[0]["market_category"] is None  # 存在しない列はNone
        assert result[1]["stock_code"] == "1332"
        assert result[1]["stock_name"] == "日本水産"
        assert result[0]["sector_code_33"] is None

    def test_normalize_jpx_data_no_required_columns(self):
        """必要な列がない場合でもフォールバックで処理されることを確認."""
        # 必要な列がないDataFrameを作成
        input_df = pd.DataFrame(
            {
                "unknown_col1": ["1301", "1332"],
                "unknown_col2": ["極洋", "日本水産"],
            }
        )

        result = self.service._normalize_jpx_data(input_df)

        # フォールバックで処理される
        assert len(result) == 2
        assert result[0]["stock_code"] == "1301"
        assert result[0]["stock_name"] == "極洋"

    @patch("services.jpx_stock_service.get_db_session")
    @patch.object(JPXStockService, "fetch_jpx_stock_list")
    def test_update_stock_master_success(
        self, mock_fetch, mock_get_db_session
    ):
        """銘柄マスタ更新の成功テスト."""
        # モックDataFrameを設定
        mock_df = pd.DataFrame(
            {
                "stock_code": ["1301", "1332"],
                "stock_name": ["極洋", "日本水産"],
                "market_category": ["プライム", "プライム"],
            }
        )
        mock_fetch.return_value = mock_df

        # モックセッションを設定
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # 既存銘柄コードを設定
        mock_session.query.return_value.filter.return_value.all.return_value = [
            ("1301",)
        ]

        # 更新履歴レコードのモック
        mock_update = Mock()
        mock_update.id = 1
        mock_session.add = Mock()
        mock_session.flush = Mock()

        with patch.object(
            self.service, "_create_update_record", return_value=1
        ), patch.object(
            self.service, "_get_existing_stock_codes", return_value={"1301"}
        ), patch.object(
            self.service, "_insert_stock"
        ), patch.object(
            self.service, "_update_stock"
        ), patch.object(
            self.service, "_deactivate_stocks"
        ), patch.object(
            self.service, "_complete_update_record"
        ):

            result = self.service.update_stock_master("manual")

        # 検証
        assert result["status"] == "success"
        assert result["total_stocks"] == 2
        assert result["added_stocks"] == 1  # 1332は新規
        assert result["updated_stocks"] == 1  # 1301は更新
        assert result["removed_stocks"] == 0

    @patch.object(JPXStockService, "fetch_jpx_stock_list")
    def test_update_stock_master_fetch_error(self, mock_fetch):
        """銘柄マスタ更新のフェッチエラーテスト."""
        # フェッチエラーを発生させる
        mock_fetch.side_effect = JPXDownloadError("Download failed")

        with pytest.raises(JPXStockServiceError) as exc_info:
            self.service.update_stock_master("manual")

        assert "銘柄マスタの更新に失敗しました" in str(exc_info.value)

    @patch("services.jpx_stock_service.get_db_session")
    def test_get_stock_list_success(self, mock_get_db_session):
        """銘柄一覧取得の成功テスト."""
        # モックセッションを設定
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # モック銘柄データを設定
        mock_stock1 = MagicMock()
        mock_stock1.to_dict.return_value = {
            "id": 1,
            "stock_code": "1301",
            "stock_name": "極洋",
            "market_category": "プライム",
            "is_active": True,
        }
        mock_stock2 = MagicMock()
        mock_stock2.to_dict.return_value = {
            "id": 2,
            "stock_code": "1332",
            "stock_name": "日本水産",
            "market_category": "プライム",
            "is_active": True,
        }

        # クエリチェーンのモックを正しく設定
        mock_query = mock_session.query.return_value
        mock_filtered_query = mock_query.filter.return_value
        mock_filtered_query.count.return_value = 2
        mock_filtered_query.offset.return_value.limit.return_value.all.return_value = [
            mock_stock1,
            mock_stock2,
        ]

        result = self.service.get_stock_list()

        # 検証
        assert result["total"] == 2
        assert len(result["stocks"]) == 2
        assert result["stocks"][0]["stock_code"] == "1301"
        assert result["stocks"][1]["stock_code"] == "1332"

    @patch("services.jpx_stock_service.get_db_session")
    def test_get_stock_list_with_filters(self, mock_get_db_session):
        """フィルタ付き銘柄一覧取得のテスト."""
        # モックセッションを設定
        mock_session = MagicMock()
        mock_get_db_session.return_value.__enter__.return_value = mock_session

        # クエリチェーンのモックを正しく設定
        mock_query = mock_session.query.return_value
        mock_filtered_query1 = mock_query.filter.return_value
        mock_filtered_query2 = mock_filtered_query1.filter.return_value
        mock_filtered_query2.count.return_value = 0
        mock_filtered_query2.offset.return_value.limit.return_value.all.return_value = (
            []
        )

        result = self.service.get_stock_list(
            is_active=False, market_category="プライム", limit=50, offset=10
        )

        # 検証
        assert result["total"] == 0
        assert len(result["stocks"]) == 0

        # フィルタが適用されたことを確認
        mock_session.query.return_value.filter.assert_called()

    @patch("services.jpx_stock_service.get_db_session")
    def test_get_stock_list_database_error(self, mock_get_db_session):
        """銘柄一覧取得のデータベースエラーテスト."""
        # データベースエラーを発生させる
        mock_get_db_session.side_effect = Exception(
            "Database connection failed"
        )

        with pytest.raises(JPXStockServiceError) as exc_info:
            self.service.get_stock_list()

        assert "銘柄一覧の取得に失敗しました" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__])
