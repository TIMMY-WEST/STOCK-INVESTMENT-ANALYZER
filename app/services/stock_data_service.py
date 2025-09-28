"""
株価データ取得・保存サービス
Issue #37: 各時間軸でのデータ取得・保存機能実装
"""

import logging
import yfinance as yf
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import time
from datetime import datetime, timedelta

from app.models import (
    get_db_session,
    TIMEFRAME_MODELS,
)

logger = logging.getLogger(__name__)


class StockDataServiceError(Exception):
    """StockDataService専用例外クラス"""
    pass


class DataFetchError(StockDataServiceError):
    """データ取得エラー"""
    pass


class DataSaveError(StockDataServiceError):
    """データ保存エラー"""
    pass


class ValidationError(StockDataServiceError):
    """バリデーションエラー"""
    pass


class StockDataService:
    """株価データ取得・保存サービスクラス"""
    
    SUPPORTED_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
    
    # パフォーマンス最適化設定
    BATCH_SIZE = 1000  # バッチ処理サイズ
    MAX_RETRY_COUNT = 3  # 最大リトライ回数
    RETRY_DELAY = 1.0  # リトライ間隔（秒）
    
    @classmethod
    def fetch_and_save_data(cls, symbol: str, period: str, interval: str) -> Dict[str, Any]:
        """
        指定された銘柄、期間、時間軸でデータを取得し、適切なテーブルに保存
        
        Args:
            symbol: 銘柄コード
            period: 取得期間 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: 時間軸 (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)
            
        Returns:
            Dict: 処理結果
        """
        start_time = time.time()
        
        try:
            # 入力値の検証
            cls._validate_inputs(symbol, period, interval)
            
            # yfinanceでデータ取得（リトライ機能付き）
            logger.info(f"データ取得開始: {symbol}, period={period}, interval={interval}")
            data = cls._fetch_data_with_retry(symbol, period, interval)
            
            if data.empty:
                return {
                    'success': False,
                    'message': f'指定された条件でデータが見つかりませんでした: {symbol} ({period}, {interval})',
                    'error_code': 'NO_DATA_FOUND',
                    'data_count': 0,
                    'symbol': symbol,
                    'interval': interval,
                    'period': period
                }
            
            # データベースに保存（バッチ処理）
            saved_count, skipped_count = cls._save_data_to_database_optimized(symbol, interval, data)
            
            processing_time = time.time() - start_time
            logger.info(f"データ処理完了: {symbol}, interval={interval}, 保存件数={saved_count}, スキップ件数={skipped_count}, 処理時間={processing_time:.2f}秒")
            
            return {
                'success': True,
                'message': f'{symbol}の{interval}データを{saved_count}件保存しました（{skipped_count}件スキップ）',
                'data_count': saved_count,
                'skipped_count': skipped_count,
                'total_records': len(data),
                'symbol': symbol,
                'interval': interval,
                'period': period,
                'processing_time': round(processing_time, 2),
                'date_range': {
                    'start': data.index.min().isoformat() if not data.empty else None,
                    'end': data.index.max().isoformat() if not data.empty else None
                }
            }
            
        except ValidationError as e:
            logger.warning(f"バリデーションエラー: {str(e)}")
            return {
                'success': False,
                'message': str(e),
                'error_code': 'VALIDATION_ERROR',
                'data_count': 0
            }
            
        except DataFetchError as e:
            logger.error(f"データ取得エラー: {str(e)}")
            return {
                'success': False,
                'message': f'データ取得に失敗しました: {str(e)}',
                'error_code': 'DATA_FETCH_ERROR',
                'data_count': 0
            }
            
        except DataSaveError as e:
            logger.error(f"データ保存エラー: {str(e)}")
            return {
                'success': False,
                'message': f'データ保存に失敗しました: {str(e)}',
                'error_code': 'DATA_SAVE_ERROR',
                'data_count': 0
            }
            
        except Exception as e:
            logger.error(f"予期しないエラー: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'予期しないエラーが発生しました: {str(e)}',
                'error_code': 'UNEXPECTED_ERROR',
                'data_count': 0
            }
    
    @classmethod
    def _validate_inputs(cls, symbol: str, period: str, interval: str) -> None:
        """入力値の検証"""
        if not symbol or not isinstance(symbol, str):
            raise ValidationError("銘柄コード (symbol) が必要です")
        
        if not period or not isinstance(period, str):
            raise ValidationError("期間 (period) が必要です")
        
        if interval not in cls.SUPPORTED_INTERVALS:
            raise ValidationError(f"サポートされていない時間軸です: {interval}. サポート対象: {', '.join(cls.SUPPORTED_INTERVALS)}")
        
        # 銘柄コードの基本的な形式チェック
        if len(symbol.strip()) == 0:
            raise ValidationError("銘柄コードが空です")
    
    @classmethod
    def _fetch_data_with_retry(cls, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """リトライ機能付きデータ取得"""
        last_exception = None
        
        for attempt in range(cls.MAX_RETRY_COUNT):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                if data.empty and attempt < cls.MAX_RETRY_COUNT - 1:
                    logger.warning(f"データ取得失敗 (試行 {attempt + 1}/{cls.MAX_RETRY_COUNT}): {symbol}")
                    time.sleep(cls.RETRY_DELAY * (attempt + 1))  # 指数バックオフ
                    continue
                
                return data
                
            except Exception as e:
                last_exception = e
                logger.warning(f"データ取得エラー (試行 {attempt + 1}/{cls.MAX_RETRY_COUNT}): {str(e)}")
                
                if attempt < cls.MAX_RETRY_COUNT - 1:
                    time.sleep(cls.RETRY_DELAY * (attempt + 1))
                    continue
                else:
                    break
        
        raise DataFetchError(f"データ取得に失敗しました（{cls.MAX_RETRY_COUNT}回試行）: {str(last_exception)}")
    
    @classmethod
    def _save_data_to_database_optimized(cls, symbol: str, interval: str, data: pd.DataFrame) -> Tuple[int, int]:
        """
        最適化されたデータベース保存処理
        
        Returns:
            Tuple[int, int]: (保存件数, スキップ件数)
        """
        if interval not in TIMEFRAME_MODELS:
            raise DataSaveError(f"サポートされていない時間軸です: {interval}")
        
        model_info = TIMEFRAME_MODELS[interval]
        crud_class = model_info['crud']
        
        try:
            with get_db_session() as session:
                if interval == '1d':
                    return cls._save_daily_data_optimized(session, symbol, data, crud_class)
                elif interval in ['1m', '5m', '15m', '30m', '1h']:
                    return cls._save_intraday_data_optimized(session, symbol, interval, data, crud_class)
                elif interval == '1wk':
                    return cls._save_weekly_data_optimized(session, symbol, data, crud_class)
                elif interval == '1mo':
                    return cls._save_monthly_data_optimized(session, symbol, data, crud_class)
                else:
                    raise DataSaveError(f"未対応の時間軸です: {interval}")
                    
        except SQLAlchemyError as e:
            raise DataSaveError(f"データベースエラー: {str(e)}")
        except Exception as e:
            raise DataSaveError(f"データ保存処理エラー: {str(e)}")

    @classmethod
    def _save_daily_data_optimized(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> Tuple[int, int]:
        """最適化された日足データの保存"""
        saved_count = 0
        skipped_count = 0
        
        # 既存データの日付リストを一括取得（パフォーマンス最適化）
        existing_dates = set()
        try:
            existing_records = crud_class.get_by_symbol(session, symbol)
            existing_dates = {record.date for record in existing_records}
        except Exception as e:
            logger.warning(f"既存データ取得エラー: {str(e)}")
        
        # バッチ処理でデータを保存
        batch_data = []
        for index, row in data.iterrows():
            try:
                date_value = index.date()
                
                # 重複チェック（メモリ上で高速処理）
                if date_value in existing_dates:
                    skipped_count += 1
                    continue
                
                # バッチデータに追加
                stock_data = {
                    'symbol': symbol,
                    'date': date_value,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                batch_data.append(stock_data)
                
                # バッチサイズに達したら保存
                if len(batch_data) >= cls.BATCH_SIZE:
                    saved_count += cls._save_batch_data(session, crud_class, batch_data)
                    batch_data = []
                    
            except Exception as e:
                logger.warning(f"日足データ処理エラー (スキップ): {symbol}, {index.date()}, {str(e)}")
                skipped_count += 1
                continue
        
        # 残りのデータを保存
        if batch_data:
            saved_count += cls._save_batch_data(session, crud_class, batch_data)
        
        return saved_count, skipped_count
    
    @classmethod
    def _save_intraday_data_optimized(cls, session: Session, symbol: str, interval: str, data: pd.DataFrame, crud_class) -> Tuple[int, int]:
        """最適化された分足・時間足データの保存"""
        saved_count = 0
        skipped_count = 0
        
        # 既存データの日時リストを一括取得（パフォーマンス最適化）
        existing_datetimes = set()
        try:
            existing_records = crud_class.get_by_symbol_and_interval(session, symbol, interval)
            existing_datetimes = {record.datetime for record in existing_records}
        except Exception as e:
            logger.warning(f"既存データ取得エラー: {str(e)}")
        
        # バッチ処理でデータを保存
        batch_data = []
        for index, row in data.iterrows():
            try:
                datetime_value = index.to_pydatetime()
                
                # 重複チェック（メモリ上で高速処理）
                if datetime_value in existing_datetimes:
                    skipped_count += 1
                    continue
                
                # バッチデータに追加
                stock_data = {
                    'symbol': symbol,
                    'datetime': datetime_value,
                    'interval': interval,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                batch_data.append(stock_data)
                
                # バッチサイズに達したら保存
                if len(batch_data) >= cls.BATCH_SIZE:
                    saved_count += cls._save_batch_data(session, crud_class, batch_data)
                    batch_data = []
                    
            except Exception as e:
                logger.warning(f"分足データ処理エラー (スキップ): {symbol}, {index}, {str(e)}")
                skipped_count += 1
                continue
        
        # 残りのデータを保存
        if batch_data:
            saved_count += cls._save_batch_data(session, crud_class, batch_data)
        
        return saved_count, skipped_count
    
    @classmethod
    def _save_weekly_data_optimized(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> Tuple[int, int]:
        """最適化された週足データの保存"""
        saved_count = 0
        skipped_count = 0
        
        # 既存データの週開始日リストを一括取得
        existing_weeks = set()
        try:
            existing_records = crud_class.get_by_symbol(session, symbol)
            existing_weeks = {record.week_start_date for record in existing_records}
        except Exception as e:
            logger.warning(f"既存データ取得エラー: {str(e)}")
        
        # バッチ処理でデータを保存
        batch_data = []
        for index, row in data.iterrows():
            try:
                week_start_date = index.date() - timedelta(days=index.weekday())
                
                # 重複チェック
                if week_start_date in existing_weeks:
                    skipped_count += 1
                    continue
                
                # バッチデータに追加
                stock_data = {
                    'symbol': symbol,
                    'week_start_date': week_start_date,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                batch_data.append(stock_data)
                
                # バッチサイズに達したら保存
                if len(batch_data) >= cls.BATCH_SIZE:
                    saved_count += cls._save_batch_data(session, crud_class, batch_data)
                    batch_data = []
                    
            except Exception as e:
                logger.warning(f"週足データ処理エラー (スキップ): {symbol}, {index}, {str(e)}")
                skipped_count += 1
                continue
        
        # 残りのデータを保存
        if batch_data:
            saved_count += cls._save_batch_data(session, crud_class, batch_data)
        
        return saved_count, skipped_count
    
    @classmethod
    def _save_monthly_data_optimized(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> Tuple[int, int]:
        """最適化された月足データの保存"""
        saved_count = 0
        skipped_count = 0
        
        # 既存データの年月リストを一括取得
        existing_months = set()
        try:
            existing_records = crud_class.get_by_symbol(session, symbol)
            existing_months = {(record.year, record.month) for record in existing_records}
        except Exception as e:
            logger.warning(f"既存データ取得エラー: {str(e)}")
        
        # バッチ処理でデータを保存
        batch_data = []
        for index, row in data.iterrows():
            try:
                year = index.year
                month = index.month
                
                # 重複チェック
                if (year, month) in existing_months:
                    skipped_count += 1
                    continue
                
                # バッチデータに追加
                stock_data = {
                    'symbol': symbol,
                    'year': year,
                    'month': month,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                batch_data.append(stock_data)
                
                # バッチサイズに達したら保存
                if len(batch_data) >= cls.BATCH_SIZE:
                    saved_count += cls._save_batch_data(session, crud_class, batch_data)
                    batch_data = []
                    
            except Exception as e:
                logger.warning(f"月足データ処理エラー (スキップ): {symbol}, {year}-{month}, {str(e)}")
                skipped_count += 1
                continue
        
        # 残りのデータを保存
        if batch_data:
            saved_count += cls._save_batch_data(session, crud_class, batch_data)
        
        return saved_count, skipped_count
    
    @classmethod
    def _save_batch_data(cls, session: Session, crud_class, batch_data: List[Dict]) -> int:
        """バッチデータの保存"""
        saved_count = 0
        
        for data in batch_data:
            try:
                crud_class.create(session, **data)
                saved_count += 1
            except IntegrityError:
                # 重複データの場合はスキップ（念のため）
                session.rollback()
                continue
            except Exception as e:
                logger.warning(f"個別データ保存エラー: {str(e)}")
                session.rollback()
                continue
        
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"バッチコミットエラー: {str(e)}")
            raise DataSaveError(f"バッチ保存に失敗しました: {str(e)}")
        
        return saved_count

    @classmethod
    def get_supported_intervals(cls) -> List[str]:
        """サポートされている時間軸のリストを取得"""
        return cls.SUPPORTED_INTERVALS.copy()
    
    @classmethod
    def validate_interval(cls, interval: str) -> bool:
        """時間軸の妥当性を検証"""
        return interval in cls.SUPPORTED_INTERVALS
    
    @classmethod
    def get_data_summary(cls, symbol: str, interval: str) -> Dict[str, Any]:
        """指定された銘柄・時間軸のデータサマリーを取得"""
        try:
            if interval not in TIMEFRAME_MODELS:
                return {
                    'success': False,
                    'error': f'サポートされていない時間軸です: {interval}',
                    'error_code': 'INVALID_INTERVAL'
                }
            
            model_info = TIMEFRAME_MODELS[interval]
            crud_class = model_info['crud']
            
            with get_db_session() as session:
                if interval == '1d':
                    count = crud_class.count_by_symbol(session, symbol)
                    latest_date = crud_class.get_latest_date_by_symbol(session, symbol)
                    return {
                        'success': True,
                        'symbol': symbol,
                        'interval': interval,
                        'data_count': count,
                        'latest_date': latest_date.isoformat() if latest_date else None
                    }
                elif interval in ['1m', '5m', '15m', '30m', '1h']:
                    latest_datetime = crud_class.get_latest_datetime_by_symbol_and_interval(session, symbol, interval)
                    # 分足・時間足の件数取得は実装が複雑なため、簡易版として最新日時のみ返す
                    return {
                        'success': True,
                        'symbol': symbol,
                        'interval': interval,
                        'latest_datetime': latest_datetime.isoformat() if latest_datetime else None
                    }
                else:
                    # 週足・月足の場合も簡易版
                    return {
                        'success': True,
                        'symbol': symbol,
                        'interval': interval,
                        'message': 'データサマリー機能は開発中です'
                    }
                    
        except Exception as e:
            logger.error(f"データサマリー取得エラー: {str(e)}")
            return {
                'success': False,
                'error': f'データサマリー取得中にエラーが発生しました: {str(e)}',
                'error_code': 'SUMMARY_ERROR'
            }