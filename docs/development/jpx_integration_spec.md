---
category: development
ai_context: medium
last_updated: 2025-10-18
related_docs:
  - ../api/api_jpx_sequential.md
  - ../guides/user_guide_jpx_sequential.md
  - ../architecture/database_design.md
---

# JPX連携仕様書

## 📋 概要
日本取引所グループ（JPX）提供の銘柄情報を活用した銘柄マスタ管理システムの仕様

**目的**: JPXから最新の上場銘柄情報を自動取得し、システムの銘柄マスタを常に最新状態に保つ

---

## 🎯 要件定義

### 機能要件
1. **JPX銘柄一覧取得**: JPX公式サイトからdata_j.xlsを自動ダウンロード
2. **銘柄データ解析**: Excelファイルから銘柄コード・銘柄名等を抽出
3. **銘柄マスタ更新**: 取得データを基に銘柄マスタテーブルを更新
4. **差分管理**: 新規上場・上場廃止銘柄の検出と処理
5. **データ検証**: 銘柄コード形式、重複チェック等のバリデーション

### 非機能要件
1. **自動化**: 定期実行による自動更新機能
2. **信頼性**: ダウンロード失敗時のリトライ機能
3. **トレーサビリティ**: 更新履歴の記録・管理
4. **パフォーマンス**: 高速な差分更新処理

---

## 📊 JPXデータ仕様

### JPX銘柄一覧ファイル情報
- **ファイル名**: `data_j.xls`
- **URL**: `https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls`
- **更新頻度**: 月末基準（直近月末の東証上場銘柄一覧）
- **ファイル形式**: Microsoft Excel (.xls) - Composite Document File V2
- **文字エンコード**: Shift_JIS (Code page: 932)
- **ファイルサイズ**: 約800KB (828,416 bytes)

### ファイル構造
```
data_j.xls
└── Sheet1: 上場銘柄一覧（総行数: 約4,410行）
    ├── A列: 基準日 (例: 20250829)
    ├── B列: コード (例: 1301)
    ├── C列: 銘柄名 (例: 極洋)
    ├── D列: 市場・商品区分 (例: プライム（内国株式）)
    ├── E列: 33業種コード (例: 50)
    ├── F列: 33業種区分 (例: 水産・農林業)
    ├── G列: 17業種コード (例: 1)
    ├── H列: 17業種区分 (例: 食品)
    ├── I列: 規模コード (例: 7)
    └── J列: 規模区分 (例: TOPIX Small 2)
```

### 実際のデータサンプル
```
基準日    | コード | 銘柄名 | 市場・商品区分        | 33業種コード | 33業種区分   | 17業種コード | 17業種区分 | 規模コード | 規模区分
20250829 | 1301  | 極洋   | プライム（内国株式）   | 50          | 水産・農林業  | 1          | 食品      | 7         | TOPIX Small 2
20250829 | 1305  | 上場インデックス...     | ETF・ETN     | -           | -          | -          | -        | -         | -
```

### 市場区分の種類（実際のデータより）
- **プライム（内国株式）**: 1,618銘柄
- **スタンダード（内国株式）**: 1,571銘柄
- **グロース（内国株式）**: 606銘柄
- **ETF・ETN**: 397銘柄
- **PRO Market**: 148銘柄
- **REIT・ベンチャーファンド・カントリーファンド・インフラファンド**: 63銘柄
- その他: 少数

### 業種分類の種類（33業種区分の上位10種類）
- **卸売・小売業**: 629銘柄
- **サービス業**: 586銘柄
- **その他製品**: 351銘柄
- **化学**: 306銘柄
- **電気機器**: 235銘柄
- **機械**: 220銘柄
- **医薬品**: 206銘柄
- **建設業**: 166銘柄
- **不動産業**: 153銘柄

### 銘柄コード形式の統計
- **4桁数字の銘柄**: 94.3%（例: 1301, 1305）
- **4桁数字+英字の銘柄**: 5.7%（例: 130A, 131A）
- **総銘柄数**: 約4,410銘柄（2025年8月29日基準）

---

## 🏗️ システム構成

### アーキテクチャ図
```
[JPX公式サイト]
       ↓ (HTTPSダウンロード)
[JPXデータ取得モジュール]
       ↓
[Excelファイル解析モジュール]
       ↓
[データ検証モジュール]
       ↓
[銘柄マスタ更新モジュール]
       ↓
[PostgreSQLデータベース]
```

### コンポーネント構成
```
jpx_integration/
├── downloader.py         # JPXデータダウンロード
├── parser.py            # Excelファイル解析
├── validator.py         # データ検証
├── master_updater.py    # 銘柄マスタ更新
├── differ.py           # 差分検出
├── scheduler.py        # 定期実行管理
├── config.py          # JPX連携設定
└── models.py          # データモデル
```

---

## 📊 データ構造

### 銘柄マスタテーブル (stock_master)
```sql
CREATE TABLE stock_master (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL UNIQUE,        -- 銘柄コード（4桁数字 + 英字の場合あり: 130A等）
    stock_name VARCHAR(200) NOT NULL,              -- 銘柄名（長い名称に対応）
    market_segment VARCHAR(100),                   -- 市場・商品区分（プライム（内国株式）等）
    industry_33_code VARCHAR(10),                  -- 33業種コード
    industry_33_category VARCHAR(100),             -- 33業種区分
    industry_17_code VARCHAR(10),                  -- 17業種コード
    industry_17_category VARCHAR(100),             -- 17業種区分
    scale_code VARCHAR(10),                        -- 規模コード
    scale_category VARCHAR(100),                   -- 規模区分
    jpx_base_date DATE,                           -- JPXファイルの基準日
    listing_date DATE,                            -- 上場日
    delisting_date DATE,                          -- 上場廃止日
    is_active BOOLEAN DEFAULT TRUE,               -- アクティブフラグ
    jpx_last_updated DATE,                        -- JPXデータ最終更新日
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX idx_stock_master_code ON stock_master(stock_code);
CREATE INDEX idx_stock_master_active ON stock_master(is_active);
CREATE INDEX idx_stock_master_market ON stock_master(market_segment);
CREATE INDEX idx_stock_master_industry_33 ON stock_master(industry_33_code);
CREATE INDEX idx_stock_master_industry_17 ON stock_master(industry_17_code);
CREATE INDEX idx_stock_master_scale ON stock_master(scale_code);
```

### JPX更新履歴テーブル (jpx_update_history)
```sql
CREATE TABLE jpx_update_history (
    id SERIAL PRIMARY KEY,
    update_date DATE NOT NULL,                 -- 更新実行日
    jpx_file_date DATE,                        -- JPXファイルの基準日
    total_stocks INTEGER NOT NULL,             -- 総銘柄数
    new_stocks INTEGER DEFAULT 0,              -- 新規上場銘柄数
    updated_stocks INTEGER DEFAULT 0,          -- 更新銘柄数
    delisted_stocks INTEGER DEFAULT 0,         -- 上場廃止銘柄数
    status VARCHAR(20) NOT NULL,               -- 'success', 'failed', 'partial'
    error_message TEXT,                        -- エラーメッセージ
    file_size INTEGER,                         -- ダウンロードファイルサイズ
    processing_time_seconds INTEGER,           -- 処理時間（秒）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 銘柄変更ログテーブル (stock_change_log)
```sql
CREATE TABLE stock_change_log (
    id SERIAL PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    change_type VARCHAR(20) NOT NULL,          -- 'new', 'updated', 'delisted'
    old_values JSONB,                          -- 変更前の値
    new_values JSONB,                          -- 変更後の値
    change_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔧 実装詳細

### JPXDownloader クラス
```python
import requests
import tempfile
from pathlib import Path
from typing import Optional

class JPXDownloader:
    def __init__(self, config: JPXConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    async def download_data_file(self) -> Optional[Path]:
        """JPX銘柄一覧ファイルダウンロード"""
        try:
            # ダウンロードURL取得（ページから最新のリンクを抽出）
            download_url = await self._get_latest_download_url()

            # ファイルダウンロード
            response = self.session.get(download_url, timeout=30)
            response.raise_for_status()

            # 一時ファイルに保存
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.xls',
                delete=False,
                dir=self.config.temp_dir
            )

            temp_file.write(response.content)
            temp_file.close()

            return Path(temp_file.name)

        except Exception as e:
            logger.error(f"JPXファイルダウンロード失敗: {e}")
            return None

    async def _get_latest_download_url(self) -> str:
        """最新のダウンロードURLを取得"""
        # JPXサイトをスクレイピングして最新のdata_j.xlsのURLを取得
        list_page_url = "https://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
        response = self.session.get(list_page_url)
        response.raise_for_status()

        # BeautifulSoupでHTMLを解析
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # data_j.xlsへのリンクを検索
        for link in soup.find_all('a', href=True):
            if 'data_j.xls' in link['href']:
                if link['href'].startswith('http'):
                    return link['href']
                else:
                    return f"https://www.jpx.co.jp{link['href']}"

        raise ValueError("JPXダウンロードURLが見つかりません")
```

### JPXParser クラス
```python
import pandas as pd
from typing import List, Dict

class JPXParser:
    def __init__(self):
        self.encoding = 'shift_jis'

    def parse_excel_file(self, file_path: Path) -> List[Dict]:
        """Excelファイルを解析して銘柄情報を抽出"""
        try:
            # pandasでExcelファイル読み込み（実際の列構造に対応）
            df = pd.read_excel(
                file_path,
                sheet_name='Sheet1',
                dtype={
                    'コード': str,          # 銘柄コードは文字列として読み込み
                    '33業種コード': str,    # 業種コードも文字列
                    '17業種コード': str,
                    '規模コード': str
                },
                na_filter=False
            )

            # データ清浄化
            df = self._clean_dataframe(df)

            # 辞書形式に変換
            stocks_data = []
            for _, row in df.iterrows():
                stock_data = {
                    'base_date': self._parse_date(row.get('基準日', '')),
                    'stock_code': self._format_stock_code(row.get('コード', '')),
                    'stock_name': str(row.get('銘柄名', '')).strip(),
                    'market_segment': str(row.get('市場・商品区分', '')).strip(),
                    'industry_33_code': self._format_code(row.get('33業種コード', '')),
                    'industry_33_category': str(row.get('33業種区分', '')).strip(),
                    'industry_17_code': self._format_code(row.get('17業種コード', '')),
                    'industry_17_category': str(row.get('17業種区分', '')).strip(),
                    'scale_code': self._format_code(row.get('規模コード', '')),
                    'scale_category': str(row.get('規模区分', '')).strip()
                }

                # 有効な銘柄コードのみ追加（ETF・ETNは除く場合の処理も考慮）
                if self._is_valid_stock_code(stock_data['stock_code']):
                    stocks_data.append(stock_data)

            return stocks_data

        except Exception as e:
            logger.error(f"Excelファイル解析エラー: {e}")
            raise

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """データフレームの清浄化"""
        # 空行を削除
        df = df.dropna(how='all')

        # 列名の正規化
        df.columns = df.columns.str.strip()

        return df

    def _parse_date(self, date_str: str) -> str:
        """基準日の解析（YYYYMMDD形式）"""
        date_str = str(date_str).strip()
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return None

    def _format_stock_code(self, code: str) -> str:
        """銘柄コードの書式統一"""
        # 実際のデータでは4桁数字 + 英字の場合もある（例: 130A）
        code = str(code).strip().upper()
        return code if code and code != 'nan' else None

    def _format_code(self, code: str) -> str:
        """各種コードの書式統一"""
        code = str(code).strip()
        return code if code and code != '-' and code != 'nan' else None

    def _normalize_market_segment(self, segment: str) -> str:
        """市場区分の正規化"""
        segment = str(segment).strip()
        # 実際のデータ形式に合わせて正規化
        segment_mapping = {
            'プライム（内国株式）': 'Prime',
            'スタンダード（内国株式）': 'Standard',
            'グロース（内国株式）': 'Growth',
            'ETF・ETN': 'ETF_ETN',
            'PRO Market': 'PRO_Market',
            'REIT・ベンチャーファンド・カントリーファンド・インフラファンド': 'REIT_Fund'
        }
        return segment_mapping.get(segment, segment)

    def _is_valid_stock_code(self, code: str) -> bool:
        """銘柄コードの妥当性チェック"""
        if not code:
            return False
        # 4桁数字または4桁数字+英字1文字のパターンを許可
        return (len(code) == 4 and code.isdigit()) or \
               (len(code) == 5 and code[:4].isdigit() and code[4].isalpha())
```

### StockMasterUpdater クラス
```python
from typing import List, Dict, Tuple

class StockMasterUpdater:
    def __init__(self, db_connection):
        self.db = db_connection
        self.differ = StockDiffer()

    async def update_master(self, jpx_data: List[Dict]) -> Dict:
        """銘柄マスタ更新"""
        try:
            # 現在のマスタデータ取得
            current_master = await self._get_current_master()

            # 差分検出
            changes = self.differ.detect_changes(current_master, jpx_data)

            # データベース更新実行
            update_result = await self._execute_updates(changes)

            # 更新履歴記録
            await self._record_update_history(update_result)

            return update_result

        except Exception as e:
            logger.error(f"銘柄マスタ更新エラー: {e}")
            raise

    async def _execute_updates(self, changes: Dict) -> Dict:
        """データベース更新実行"""
        result = {
            'new_stocks': 0,
            'updated_stocks': 0,
            'delisted_stocks': 0,
            'total_stocks': 0
        }

        async with self.db.transaction():
            # 新規上場銘柄の追加
            for stock_data in changes['new_stocks']:
                await self._insert_new_stock(stock_data)
                result['new_stocks'] += 1

            # 既存銘柄の更新
            for stock_data in changes['updated_stocks']:
                await self._update_existing_stock(stock_data)
                result['updated_stocks'] += 1

            # 上場廃止銘柄の処理
            for stock_code in changes['delisted_stocks']:
                await self._mark_delisted(stock_code)
                result['delisted_stocks'] += 1

            # 総銘柄数更新
            result['total_stocks'] = await self._count_active_stocks()

        return result

    async def _insert_new_stock(self, stock_data: Dict):
        """新規銘柄追加"""
        query = """
        INSERT INTO stock_master (
            stock_code, stock_name, market_segment,
            industry_33_code, industry_33_category,
            industry_17_code, industry_17_category,
            scale_code, scale_category,
            jpx_base_date, jpx_last_updated
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, CURRENT_DATE)
        """
        await self.db.execute(query,
            stock_data['stock_code'],
            stock_data['stock_name'],
            stock_data['market_segment'],
            stock_data['industry_33_code'],
            stock_data['industry_33_category'],
            stock_data['industry_17_code'],
            stock_data['industry_17_category'],
            stock_data['scale_code'],
            stock_data['scale_category'],
            stock_data['base_date']
        )

        # 変更ログ記録
        await self._log_change('new', stock_data['stock_code'], None, stock_data)

    async def _mark_delisted(self, stock_code: str):
        """上場廃止銘柄マーク"""
        query = """
        UPDATE stock_master
        SET is_active = FALSE, delisting_date = CURRENT_DATE,
            updated_at = CURRENT_TIMESTAMP
        WHERE stock_code = $1 AND is_active = TRUE
        """
        await self.db.execute(query, stock_code)

        # 変更ログ記録
        await self._log_change('delisted', stock_code, None, {'is_active': False})
```

---

## 📈 定期実行・スケジューリング

### スケジューラー設定
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

class JPXScheduler:
    def __init__(self, jpx_service: JPXService):
        self.jpx_service = jpx_service
        self.scheduler = AsyncIOScheduler()

    def start_scheduler(self):
        """定期実行開始"""
        # 平日の朝9時に実行（JST）
        self.scheduler.add_job(
            func=self.jpx_service.update_stock_master,
            trigger=CronTrigger(
                hour=9,
                minute=0,
                day_of_week='mon-fri',
                timezone='Asia/Tokyo'
            ),
            id='jpx_daily_update',
            name='JPX銘柄マスタ日次更新',
            replace_existing=True
        )

        # 週次バックアップ（日曜の深夜2時）
        self.scheduler.add_job(
            func=self.jpx_service.backup_master_data,
            trigger=CronTrigger(
                hour=2,
                minute=0,
                day_of_week='sun',
                timezone='Asia/Tokyo'
            ),
            id='jpx_weekly_backup',
            name='JPX銘柄マスタ週次バックアップ'
        )

        self.scheduler.start()
```

---

## 🛡️ エラーハンドリング

### エラー分類と対応
```python
class JPXErrorHandler:
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 60  # 1分

    async def handle_download_error(self, error: Exception, attempt: int) -> bool:
        """ダウンロードエラー処理"""
        if attempt < self.max_retries:
            if isinstance(error, requests.exceptions.Timeout):
                logger.warning(f"ダウンロードタイムアウト（試行{attempt + 1}回目）")
                await asyncio.sleep(self.retry_delay * attempt)
                return True  # リトライ実行

            elif isinstance(error, requests.exceptions.ConnectionError):
                logger.warning(f"ネットワークエラー（試行{attempt + 1}回目）")
                await asyncio.sleep(self.retry_delay * attempt)
                return True  # リトライ実行

        logger.error(f"ダウンロード失敗（最大試行回数到達）: {error}")
        return False  # リトライ中止

    async def handle_parse_error(self, error: Exception, file_path: Path) -> bool:
        """解析エラー処理"""
        logger.error(f"ファイル解析エラー: {error}")

        # ファイルサイズチェック
        if file_path.stat().st_size < 1024:  # 1KB未満
            logger.error("ダウンロードファイルが不完全です")
            return False

        # ファイル形式チェック
        if not self._is_valid_excel_file(file_path):
            logger.error("無効なExcelファイル形式です")
            return False

        return True  # 他のエラーは継続処理
```

---

## 📊 監視・ログ

### ログ出力項目
```python
JPX_LOG_FORMAT = {
    "timestamp": "2024-01-15T09:00:00Z",
    "operation": "download|parse|update|schedule",
    "status": "start|success|failed|retry",
    "jpx_file_date": "2024-01-14",
    "total_stocks": 3800,
    "new_stocks": 5,
    "updated_stocks": 12,
    "delisted_stocks": 2,
    "processing_time_ms": 15000,
    "file_size_bytes": 524288,
    "error_message": null
}
```

### アラート条件
- **ダウンロード失敗**: 3回連続失敗時
- **解析エラー**: ファイル形式不正時
- **大幅な銘柄数変動**: 前回比±10%以上の変動
- **更新処理長時間**: 通常の3倍以上の処理時間

---

## 🔄 運用手順

### 日次運用フロー
1. **自動実行**: 平日朝9時に自動実行
2. **結果確認**: 更新結果をダッシュボードで確認
3. **異常検知**: アラート発生時の確認・対応
4. **データ検証**: 月次での全件データ整合性チェック

### 手動実行手順
```bash
# JPX銘柄マスタ更新の手動実行
python -m jpx_integration.main --update-master

# 特定日付のファイルで更新
python -m jpx_integration.main --update-master --date 2024-01-15

# バックアップ実行
python -m jpx_integration.main --backup
```

---

## 🎯 今後の拡張予定

### Phase 2: 高度な機能
- **データ品質チェック**: 銘柄名変更、市場区分変更の自動検出
- **履歴管理**: 銘柄情報の変更履歴詳細管理
- **API連携**: 他のデータソースとの突合・検証

### Phase 3: 分析機能
- **統計情報**: 新規上場・廃止の傾向分析
- **市場分析**: 市場区分別の銘柄数推移
- **レポート機能**: 月次・年次の変更サマリーレポート

---

この仕様により、JPXから確実に最新の銘柄情報を取得し、システムの銘柄マスタを常に最新状態に保つことができます。