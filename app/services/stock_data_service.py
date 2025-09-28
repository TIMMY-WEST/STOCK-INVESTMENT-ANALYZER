"""
株価データ取得・保存サービス
各時間軸でのyfinanceデータ取得と適切なテーブルへの保存を行う
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
import logging

from models import (
    get_db_session, 
    StockDaily, StockIntraday, StockWeekly, StockMonthly,
    StockDailyCRUD, StockIntradayCRUD, StockWeeklyCRUD, StockMonthlyCRUD,
    TIMEFRAME_MODELS,
    DatabaseError, StockDataError
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataService:
    """株価データ取得・保存サービスクラス"""
    
    # サポートする時間軸
    SUPPORTED_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo']
    
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
        try:
            # 時間軸の検証
            if interval not in cls.SUPPORTED_INTERVALS:
                raise ValueError(f"サポートされていない時間軸です: {interval}")
            
            # yfinanceでデータ取得
            logger.info(f"データ取得開始: {symbol}, period={period}, interval={interval}")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return {
                    'success': False,
                    'message': f'データが取得できませんでした: {symbol}',
                    'data_count': 0
                }
            
            # データベースに保存
            saved_count = cls._save_data_to_database(symbol, interval, data)
            
            logger.info(f"データ保存完了: {symbol}, interval={interval}, 保存件数={saved_count}")
            
            return {
                'success': True,
                'message': f'{symbol}の{interval}データを{saved_count}件保存しました',
                'data_count': saved_count,
                'symbol': symbol,
                'interval': interval,
                'period': period
            }
            
        except Exception as e:
            logger.error(f"データ取得・保存エラー: {str(e)}")
            return {
                'success': False,
                'message': f'データ取得・保存中にエラーが発生しました: {str(e)}',
                'data_count': 0
            }
    
    @classmethod
    def _save_data_to_database(cls, symbol: str, interval: str, data: pd.DataFrame) -> int:
        """
        取得したデータを適切なテーブルに保存
        
        Args:
            symbol: 銘柄コード
            interval: 時間軸
            data: yfinanceから取得したデータ
            
        Returns:
            int: 保存件数
        """
        if interval not in TIMEFRAME_MODELS:
            raise ValueError(f"サポートされていない時間軸です: {interval}")
        
        model_info = TIMEFRAME_MODELS[interval]
        crud_class = model_info['crud']
        
        with get_db_session() as session:
            if interval == '1d':
                return cls._save_daily_data(session, symbol, data, crud_class)
            elif interval in ['1m', '5m', '15m', '30m', '1h']:
                return cls._save_intraday_data(session, symbol, interval, data, crud_class)
            elif interval == '1wk':
                return cls._save_weekly_data(session, symbol, data, crud_class)
            elif interval == '1mo':
                return cls._save_monthly_data(session, symbol, data, crud_class)
            else:
                raise ValueError(f"未対応の時間軸です: {interval}")
    
    @classmethod
    def _save_daily_data(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> int:
        """日足データの保存"""
        saved_count = 0
        
        for index, row in data.iterrows():
            try:
                # 既存データの確認
                existing = crud_class.get_by_symbol_and_date(session, symbol, index.date())
                if existing:
                    continue  # 重複データはスキップ
                
                # 新規データの作成
                stock_data = {
                    'symbol': symbol,
                    'date': index.date(),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                
                crud_class.create(session, **stock_data)
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"日足データ保存エラー (スキップ): {symbol}, {index.date()}, {str(e)}")
                continue
        
        return saved_count
    
    @classmethod
    def _save_intraday_data(cls, session: Session, symbol: str, interval: str, data: pd.DataFrame, crud_class) -> int:
        """分足・時間足データの保存"""
        saved_count = 0
        
        for index, row in data.iterrows():
            try:
                # 既存データの確認
                existing = crud_class.get_by_symbol_and_datetime(session, symbol, index, interval)
                if existing:
                    continue  # 重複データはスキップ
                
                # 新規データの作成
                stock_data = {
                    'symbol': symbol,
                    'datetime': index,
                    'interval': interval,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                
                crud_class.create(session, **stock_data)
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"分足・時間足データ保存エラー (スキップ): {symbol}, {interval}, {index}, {str(e)}")
                continue
        
        return saved_count
    
    @classmethod
    def _save_weekly_data(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> int:
        """週足データの保存"""
        saved_count = 0
        
        for index, row in data.iterrows():
            try:
                # 週の開始日を計算（月曜日を週の開始とする）
                week_start_date = (index - timedelta(days=index.weekday())).date()
                
                # 既存データの確認
                existing = crud_class.get_by_symbol_and_week(session, symbol, week_start_date)
                if existing:
                    continue  # 重複データはスキップ
                
                # 新規データの作成
                stock_data = {
                    'symbol': symbol,
                    'week_start_date': week_start_date,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                }
                
                crud_class.create(session, **stock_data)
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"週足データ保存エラー (スキップ): {symbol}, {index}, {str(e)}")
                continue
        
        return saved_count
    
    @classmethod
    def _save_monthly_data(cls, session: Session, symbol: str, data: pd.DataFrame, crud_class) -> int:
        """月足データの保存"""
        saved_count = 0
        
        for index, row in data.iterrows():
            try:
                year = index.year
                month = index.month
                
                # 既存データの確認
                existing = crud_class.get_by_symbol_and_month(session, symbol, year, month)
                if existing:
                    continue  # 重複データはスキップ
                
                # 新規データの作成
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
                
                crud_class.create(session, **stock_data)
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"月足データ保存エラー (スキップ): {symbol}, {year}-{month}, {str(e)}")
                continue
        
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
                return {'error': f'サポートされていない時間軸です: {interval}'}
            
            model_info = TIMEFRAME_MODELS[interval]
            crud_class = model_info['crud']
            
            with get_db_session() as session:
                if interval == '1d':
                    count = crud_class.count_by_symbol(session, symbol)
                    latest_date = crud_class.get_latest_date_by_symbol(session, symbol)
                    return {
                        'symbol': symbol,
                        'interval': interval,
                        'data_count': count,
                        'latest_date': latest_date.isoformat() if latest_date else None
                    }
                elif interval in ['1m', '5m', '15m', '30m', '1h']:
                    latest_datetime = crud_class.get_latest_datetime_by_symbol_and_interval(session, symbol, interval)
                    # 分足・時間足の件数取得は実装が複雑なため、簡易版として最新日時のみ返す
                    return {
                        'symbol': symbol,
                        'interval': interval,
                        'latest_datetime': latest_datetime.isoformat() if latest_datetime else None
                    }
                else:
                    # 週足・月足の場合も簡易版
                    return {
                        'symbol': symbol,
                        'interval': interval,
                        'message': 'データサマリー機能は開発中です'
                    }
                    
        except Exception as e:
            logger.error(f"データサマリー取得エラー: {str(e)}")
            return {'error': f'データサマリー取得中にエラーが発生しました: {str(e)}'}