# データベース設計書

## 概要

株価データ取得システムのデータベース設計仕様書です。  
プロジェクトの設計理念（**動作優先・シンプル設計・後から拡張**）に基づき、最小限の構成から開始し、必要に応じて拡張していく方針です。

## 目次

- [データベース設計書](#データベース設計書)
  - [概要](#概要)
  - [目次](#目次)
  - [基本情報](#基本情報)
  - [テーブル設計](#テーブル設計)
    - [1. stocks\_daily テーブル（日足データ）](#1-stocks_daily-テーブル日足データ)
      - [テーブル定義](#テーブル定義)
      - [カラム定義](#カラム定義)
      - [制約](#制約)
        - [主キー制約](#主キー制約)
        - [ユニーク制約](#ユニーク制約)
        - [チェック制約](#チェック制約)
  - [インデックス設計](#インデックス設計)
    - [1. 主キーインデックス（自動作成）](#1-主キーインデックス自動作成)
    - [2. ユニーク制約インデックス（自動作成）](#2-ユニーク制約インデックス自動作成)
    - [3. 検索用インデックス](#3-検索用インデックス)
      - [銘柄コード検索インデックス](#銘柄コード検索インデックス)
      - [日付検索インデックス](#日付検索インデックス)
      - [複合インデックス（銘柄+日付降順）](#複合インデックス銘柄日付降順)
  - [SQLAlchemy モデル定義](#sqlalchemy-モデル定義)
    - [Python実装例](#python実装例)
  - [データベース初期化](#データベース初期化)
    - [1. データベース作成](#1-データベース作成)
    - [2. テーブル作成](#2-テーブル作成)
  - [パフォーマンス考慮事項](#パフォーマンス考慮事項)
    - [MVP段階での方針](#mvp段階での方針)
    - [将来の拡張案（必要になってから検討）](#将来の拡張案必要になってから検討)
  - [データ容量見積もり](#データ容量見積もり)
    - [1銘柄あたりのデータ量](#1銘柄あたりのデータ量)
    - [100銘柄の場合](#100銘柄の場合)
  - [バックアップ・運用](#バックアップ運用)
    - [MVP段階での方針](#mvp段階での方針-1)
    - [将来の運用計画（必要になってから）](#将来の運用計画必要になってから)
  - [サンプルデータ](#サンプルデータ)
    - [テストデータ挿入例](#テストデータ挿入例)
  - [実装優先度](#実装優先度)
    - [優先度: 高（MVP必須）](#優先度-高mvp必須)
    - [優先度: 中（動作確認後）](#優先度-中動作確認後)
    - [優先度: 低（必要になってから）](#優先度-低必要になってから)
  - [複数時間軸対応（将来拡張）](#複数時間軸対応将来拡張)
    - [yfinanceで対応可能な時間軸](#yfinanceで対応可能な時間軸)
    - [将来のテーブル設計案](#将来のテーブル設計案)
      - [分足データテーブル（将来拡張）](#分足データテーブル将来拡張)
      - [週足・月足データテーブル（将来拡張）](#週足月足データテーブル将来拡張)
    - [設計方針](#設計方針)
      - [MVP段階（現在）](#mvp段階現在)
      - [将来拡張時](#将来拡張時)
    - [拡張時の考慮事項](#拡張時の考慮事項)
      - [データ量](#データ量)
      - [パフォーマンス](#パフォーマンス)
      - [API設計への影響](#api設計への影響)
  - [まとめ](#まとめ)
    - [🎯 **個人+AI開発でのシンプルDB設計**](#-個人ai開発でのシンプルdb設計)
      - [設計方針](#設計方針-1)
      - [避けるべき過度な設計](#避けるべき過度な設計)
      - [成功の指標](#成功の指標)

## 基本情報

- **DBMS**: PostgreSQL
- **文字コード**: UTF-8
- **タイムゾーン**: Asia/Tokyo (JST)
- **開発方針**: MVP最優先、シンプル構成

## テーブル設計

### 1. stocks_1d テーブル（日足データ）

日足株価データを格納するメインテーブルです。（旧stocks_dailyテーブルを統一命名規則でstocks_1dに変更）

#### テーブル定義

```sql
CREATE TABLE stocks_1d (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2. stocks_1m テーブル（1分足データ）

1分足株価データを格納するテーブルです。

#### テーブル定義

```sql
CREATE TABLE stocks_1m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3. stocks_5m テーブル（5分足データ）

```sql
CREATE TABLE stocks_5m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4. stocks_15m テーブル（15分足データ）

```sql
CREATE TABLE stocks_15m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 5. stocks_30m テーブル（30分足データ）

```sql
CREATE TABLE stocks_30m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 6. stocks_1h テーブル（1時間足データ）

```sql
CREATE TABLE stocks_1h (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 7. stocks_1wk テーブル（1週間足データ）

```sql
CREATE TABLE stocks_1wk (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 8. stocks_1mo テーブル（1ヶ月足データ）

```sql
CREATE TABLE stocks_1mo (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 共通カラム定義

**日足・週足・月足テーブル共通**

| カラム名     | データ型                 | NULL     | デフォルト        | 説明                     |
| ------------ | ------------------------ | -------- | ----------------- | ------------------------ |
| `id`         | SERIAL                   | NOT NULL | AUTO_INCREMENT    | 主キー、自動採番         |
| `symbol`     | VARCHAR(20)              | NOT NULL | -                 | 銘柄コード（例：7203.T） |
| `date`       | DATE                     | NOT NULL | -                 | 取引日（YYYY-MM-DD）     |
| `open`       | DECIMAL(10,2)            | NOT NULL | -                 | 始値                     |
| `high`       | DECIMAL(10,2)            | NOT NULL | -                 | 高値                     |
| `low`        | DECIMAL(10,2)            | NOT NULL | -                 | 安値                     |
| `close`      | DECIMAL(10,2)            | NOT NULL | -                 | 終値                     |
| `volume`     | BIGINT                   | NOT NULL | -                 | 出来高                   |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | レコード作成日時         |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | レコード更新日時         |

**分足・時間足テーブル共通**

| カラム名     | データ型                 | NULL     | デフォルト        | 説明                     |
| ------------ | ------------------------ | -------- | ----------------- | ------------------------ |
| `id`         | SERIAL                   | NOT NULL | AUTO_INCREMENT    | 主キー、自動採番         |
| `symbol`     | VARCHAR(20)              | NOT NULL | -                 | 銘柄コード（例：7203.T） |
| `datetime`   | TIMESTAMP WITH TIME ZONE | NOT NULL | -                 | 取引日時（精密な時刻）   |
| `open`       | DECIMAL(10,2)            | NOT NULL | -                 | 始値                     |
| `high`       | DECIMAL(10,2)            | NOT NULL | -                 | 高値                     |
| `low`        | DECIMAL(10,2)            | NOT NULL | -                 | 安値                     |
| `close`      | DECIMAL(10,2)            | NOT NULL | -                 | 終値                     |
| `volume`     | BIGINT                   | NOT NULL | -                 | 出来高                   |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | レコード作成日時         |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL | CURRENT_TIMESTAMP | レコード更新日時         |

#### 制約設計

##### 主キー制約（全テーブル共通）
```sql
CONSTRAINT pk_stocks_{interval} PRIMARY KEY (id)
```

##### ユニーク制約

**日足・週足・月足テーブル**
```sql
CONSTRAINT uk_stocks_{interval}_symbol_date UNIQUE (symbol, date)
```

**分足・時間足テーブル**
```sql
CONSTRAINT uk_stocks_{interval}_symbol_datetime UNIQUE (symbol, datetime)
```

##### チェック制約（全テーブル共通）
```sql
CONSTRAINT ck_stocks_{interval}_prices CHECK (
    open >= 0 AND high >= 0 AND low >= 0 AND close >= 0
),
CONSTRAINT ck_stocks_{interval}_volume CHECK (volume >= 0),
CONSTRAINT ck_stocks_{interval}_price_logic CHECK (
    high >= low AND
    high >= open AND
    high >= close AND
    low <= open AND
    low <= close
)
```

**制約例：stocks_1d テーブル**
```sql
-- 主キー制約
CONSTRAINT pk_stocks_1d PRIMARY KEY (id),
-- ユニーク制約
CONSTRAINT uk_stocks_1d_symbol_date UNIQUE (symbol, date),
-- チェック制約
CONSTRAINT ck_stocks_1d_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
CONSTRAINT ck_stocks_1d_volume CHECK (volume >= 0),
CONSTRAINT ck_stocks_1d_price_logic CHECK (
    high >= low AND high >= open AND high >= close AND low <= open AND low <= close
)
```

## インデックス設計

### 基本設計方針

各時間軸テーブルで統一されたインデックス命名規則を採用します。

### 1. 主キーインデックス（自動作成）
```sql
-- 全テーブル共通：自動作成されるため明示的な作成不要
-- CREATE UNIQUE INDEX idx_stocks_{interval}_pk ON stocks_{interval} (id);
```

### 2. ユニーク制約インデックス（自動作成）
```sql
-- 日足・週足・月足：自動作成
-- CREATE UNIQUE INDEX idx_stocks_{interval}_symbol_date ON stocks_{interval} (symbol, date);

-- 分足・時間足：自動作成
-- CREATE UNIQUE INDEX idx_stocks_{interval}_symbol_datetime ON stocks_{interval} (symbol, datetime);
```

### 3. 検索用インデックス設計

#### 銘柄コード検索インデックス（全テーブル共通）
```sql
CREATE INDEX idx_stocks_{interval}_symbol ON stocks_{interval} (symbol);
```

#### 時間検索インデックス

**日足・週足・月足テーブル**
```sql
CREATE INDEX idx_stocks_{interval}_date ON stocks_{interval} (date);
```

**分足・時間足テーブル**
```sql
CREATE INDEX idx_stocks_{interval}_datetime ON stocks_{interval} (datetime);
```

#### 複合インデックス（パフォーマンス最適化）

**日足・週足・月足テーブル**
```sql
CREATE INDEX idx_stocks_{interval}_symbol_date_desc ON stocks_{interval} (symbol, date DESC);
```

**分足・時間足テーブル**
```sql
CREATE INDEX idx_stocks_{interval}_symbol_datetime_desc ON stocks_{interval} (symbol, datetime DESC);
```

### 4. 各テーブルのインデックス例

#### stocks_1d テーブル
```sql
CREATE INDEX idx_stocks_1d_symbol ON stocks_1d (symbol);
CREATE INDEX idx_stocks_1d_date ON stocks_1d (date);
CREATE INDEX idx_stocks_1d_symbol_date_desc ON stocks_1d (symbol, date DESC);
```

#### stocks_1m テーブル
```sql
CREATE INDEX idx_stocks_1m_symbol ON stocks_1m (symbol);
CREATE INDEX idx_stocks_1m_datetime ON stocks_1m (datetime);
CREATE INDEX idx_stocks_1m_symbol_datetime_desc ON stocks_1m (symbol, datetime DESC);
```

#### stocks_5m テーブル
```sql
CREATE INDEX idx_stocks_5m_symbol ON stocks_5m (symbol);
CREATE INDEX idx_stocks_5m_datetime ON stocks_5m (datetime);
CREATE INDEX idx_stocks_5m_symbol_datetime_desc ON stocks_5m (symbol, datetime DESC);
```

#### stocks_15m テーブル
```sql
CREATE INDEX idx_stocks_15m_symbol ON stocks_15m (symbol);
CREATE INDEX idx_stocks_15m_datetime ON stocks_15m (datetime);
CREATE INDEX idx_stocks_15m_symbol_datetime_desc ON stocks_15m (symbol, datetime DESC);
```

#### stocks_30m テーブル
```sql
CREATE INDEX idx_stocks_30m_symbol ON stocks_30m (symbol);
CREATE INDEX idx_stocks_30m_datetime ON stocks_30m (datetime);
CREATE INDEX idx_stocks_30m_symbol_datetime_desc ON stocks_30m (symbol, datetime DESC);
```

#### stocks_1h テーブル
```sql
CREATE INDEX idx_stocks_1h_symbol ON stocks_1h (symbol);
CREATE INDEX idx_stocks_1h_datetime ON stocks_1h (datetime);
CREATE INDEX idx_stocks_1h_symbol_datetime_desc ON stocks_1h (symbol, datetime DESC);
```

#### stocks_1wk テーブル
```sql
CREATE INDEX idx_stocks_1wk_symbol ON stocks_1wk (symbol);
CREATE INDEX idx_stocks_1wk_date ON stocks_1wk (date);
CREATE INDEX idx_stocks_1wk_symbol_date_desc ON stocks_1wk (symbol, date DESC);
```

#### stocks_1mo テーブル
```sql
CREATE INDEX idx_stocks_1mo_symbol ON stocks_1mo (symbol);
CREATE INDEX idx_stocks_1mo_date ON stocks_1mo (date);
CREATE INDEX idx_stocks_1mo_symbol_date_desc ON stocks_1mo (symbol, date DESC);
```

### 5. インデックス利用想定クエリ

#### 特定銘柄のデータ検索
```sql
SELECT * FROM stocks_1d WHERE symbol = '7203.T';
```

#### 期間指定でのデータ検索
```sql
SELECT * FROM stocks_1d WHERE date >= '2024-01-01' AND date <= '2024-12-31';
```

#### 銘柄別最新データ取得
```sql
SELECT * FROM stocks_1d WHERE symbol = '7203.T' ORDER BY date DESC LIMIT 30;
```

#### 分足データでの時間範囲検索
```sql
SELECT * FROM stocks_1m WHERE symbol = '7203.T'
AND datetime >= '2024-01-01 09:00:00+09:00'
AND datetime <= '2024-01-01 15:00:00+09:00';
```

## SQLAlchemy モデル定義

### Python実装例

```python
from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, BigInteger, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

# 日足データモデル
class Stock1d(Base):
    __tablename__ = 'stocks_1d'

    # カラム定義
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 制約定義
    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1d_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1d_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1d_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1d_price_logic'),
        Index('idx_stocks_1d_symbol', 'symbol'),
        Index('idx_stocks_1d_date', 'date'),
        Index('idx_stocks_1d_symbol_date_desc', 'symbol', 'date', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock1d(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

# 1分足データモデル
class Stock1m(Base):
    __tablename__ = 'stocks_1m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1m_price_logic'),
        Index('idx_stocks_1m_symbol', 'symbol'),
        Index('idx_stocks_1m_datetime', 'datetime'),
        Index('idx_stocks_1m_symbol_datetime_desc', 'symbol', 'datetime', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock1m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 5分足データモデル
class Stock5m(Base):
    __tablename__ = 'stocks_5m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_5m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_5m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_5m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_5m_price_logic'),
        Index('idx_stocks_5m_symbol', 'symbol'),
        Index('idx_stocks_5m_datetime', 'datetime'),
        Index('idx_stocks_5m_symbol_datetime_desc', 'symbol', 'datetime', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock5m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 15分足データモデル
class Stock15m(Base):
    __tablename__ = 'stocks_15m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_15m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_15m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_15m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_15m_price_logic'),
        Index('idx_stocks_15m_symbol', 'symbol'),
        Index('idx_stocks_15m_datetime', 'datetime'),
        Index('idx_stocks_15m_symbol_datetime_desc', 'symbol', 'datetime', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock15m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 30分足データモデル
class Stock30m(Base):
    __tablename__ = 'stocks_30m'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_30m_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_30m_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_30m_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_30m_price_logic'),
        Index('idx_stocks_30m_symbol', 'symbol'),
        Index('idx_stocks_30m_datetime', 'datetime'),
        Index('idx_stocks_30m_symbol_datetime_desc', 'symbol', 'datetime', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock30m(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 1時間足データモデル
class Stock1h(Base):
    __tablename__ = 'stocks_1h'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'datetime', name='uk_stocks_1h_symbol_datetime'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1h_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1h_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1h_price_logic'),
        Index('idx_stocks_1h_symbol', 'symbol'),
        Index('idx_stocks_1h_datetime', 'datetime'),
        Index('idx_stocks_1h_symbol_datetime_desc', 'symbol', 'datetime', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock1h(symbol='{self.symbol}', datetime='{self.datetime}', close={self.close})>"

# 週足データモデル
class Stock1wk(Base):
    __tablename__ = 'stocks_1wk'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1wk_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1wk_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1wk_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1wk_price_logic'),
        Index('idx_stocks_1wk_symbol', 'symbol'),
        Index('idx_stocks_1wk_date', 'date'),
        Index('idx_stocks_1wk_symbol_date_desc', 'symbol', 'date', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock1wk(symbol='{self.symbol}', date='{self.date}', close={self.close})>"

# 月足データモデル
class Stock1mo(Base):
    __tablename__ = 'stocks_1mo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Numeric(10, 2), nullable=False)
    high = Column(Numeric(10, 2), nullable=False)
    low = Column(Numeric(10, 2), nullable=False)
    close = Column(Numeric(10, 2), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('symbol', 'date', name='uk_stocks_1mo_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_1mo_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_1mo_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_1mo_price_logic'),
        Index('idx_stocks_1mo_symbol', 'symbol'),
        Index('idx_stocks_1mo_date', 'date'),
        Index('idx_stocks_1mo_symbol_date_desc', 'symbol', 'date', postgresql_desc=True),
    )

    def __repr__(self):
        return f"<Stock1mo(symbol='{self.symbol}', date='{self.date}', close={self.close})>"
```

## データベース初期化

### 1. データベース作成

```sql
-- データベース作成
CREATE DATABASE stock_data_system;

-- ユーザー作成（開発用）
CREATE USER stock_user WITH PASSWORD 'stock_password';
GRANT ALL PRIVILEGES ON DATABASE stock_data_system TO stock_user;
```

### 2. 全テーブル作成スクリプト

```sql
-- ====================================
-- 日足データテーブル (stocks_1d)
-- ====================================
CREATE TABLE stocks_1d (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- 制約
    CONSTRAINT uk_stocks_1d_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_1d_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_1d_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1d_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

-- インデックス作成
CREATE INDEX idx_stocks_1d_symbol ON stocks_1d (symbol);
CREATE INDEX idx_stocks_1d_date ON stocks_1d (date);
CREATE INDEX idx_stocks_1d_symbol_date_desc ON stocks_1d (symbol, date DESC);

-- ====================================
-- 1分足データテーブル (stocks_1m)
-- ====================================
CREATE TABLE stocks_1m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_1m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_1m_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_1m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1m_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_1m_symbol ON stocks_1m (symbol);
CREATE INDEX idx_stocks_1m_datetime ON stocks_1m (datetime);
CREATE INDEX idx_stocks_1m_symbol_datetime_desc ON stocks_1m (symbol, datetime DESC);

-- ====================================
-- 5分足データテーブル (stocks_5m)
-- ====================================
CREATE TABLE stocks_5m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_5m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_5m_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_5m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_5m_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_5m_symbol ON stocks_5m (symbol);
CREATE INDEX idx_stocks_5m_datetime ON stocks_5m (datetime);
CREATE INDEX idx_stocks_5m_symbol_datetime_desc ON stocks_5m (symbol, datetime DESC);

-- ====================================
-- 15分足データテーブル (stocks_15m)
-- ====================================
CREATE TABLE stocks_15m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_15m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_15m_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_15m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_15m_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_15m_symbol ON stocks_15m (symbol);
CREATE INDEX idx_stocks_15m_datetime ON stocks_15m (datetime);
CREATE INDEX idx_stocks_15m_symbol_datetime_desc ON stocks_15m (symbol, datetime DESC);

-- ====================================
-- 30分足データテーブル (stocks_30m)
-- ====================================
CREATE TABLE stocks_30m (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_30m_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_30m_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_30m_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_30m_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_30m_symbol ON stocks_30m (symbol);
CREATE INDEX idx_stocks_30m_datetime ON stocks_30m (datetime);
CREATE INDEX idx_stocks_30m_symbol_datetime_desc ON stocks_30m (symbol, datetime DESC);

-- ====================================
-- 1時間足データテーブル (stocks_1h)
-- ====================================
CREATE TABLE stocks_1h (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_1h_symbol_datetime UNIQUE (symbol, datetime),
    CONSTRAINT ck_stocks_1h_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_1h_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1h_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_1h_symbol ON stocks_1h (symbol);
CREATE INDEX idx_stocks_1h_datetime ON stocks_1h (datetime);
CREATE INDEX idx_stocks_1h_symbol_datetime_desc ON stocks_1h (symbol, datetime DESC);

-- ====================================
-- 週足データテーブル (stocks_1wk)
-- ====================================
CREATE TABLE stocks_1wk (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_1wk_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_1wk_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_1wk_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1wk_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_1wk_symbol ON stocks_1wk (symbol);
CREATE INDEX idx_stocks_1wk_date ON stocks_1wk (date);
CREATE INDEX idx_stocks_1wk_symbol_date_desc ON stocks_1wk (symbol, date DESC);

-- ====================================
-- 月足データテーブル (stocks_1mo)
-- ====================================
CREATE TABLE stocks_1mo (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uk_stocks_1mo_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_1mo_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_1mo_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_1mo_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);

CREATE INDEX idx_stocks_1mo_symbol ON stocks_1mo (symbol);
CREATE INDEX idx_stocks_1mo_date ON stocks_1mo (date);
CREATE INDEX idx_stocks_1mo_symbol_date_desc ON stocks_1mo (symbol, date DESC);
```

### 3. データ移行（既存のstocks_dailyテーブルがある場合）

既存のstocks_dailyテーブルのデータをstocks_1dに移行する手順：

```sql
-- 既存データの移行
INSERT INTO stocks_1d (symbol, date, open, high, low, close, volume, created_at, updated_at)
SELECT symbol, date, open, high, low, close, volume, created_at, updated_at
FROM stocks_daily;

-- 移行確認後、既存テーブルを削除（バックアップ推奨）
-- DROP TABLE stocks_daily;
```

## パフォーマンス考慮事項

### MVP段階での方針

- **インデックス**: 必要最小限のみ作成
- **パーティション**: 現時点では不要（データ量が少ないため）
- **最適化**: 動作確認後に検討

### 将来の拡張案（必要になってから検討）

- **テーブルパーティション**: 日付別パーティション
- **読み取り専用レプリカ**: 分析用途
- **アーカイブ**: 古いデータの別テーブル移動

## データ容量見積もり

### 1銘柄あたりのデータ量

- 1日1レコード: 約 100 bytes
- 1年（約250営業日）: 25 KB
- 10年: 250 KB

### 100銘柄の場合

- 1年: 2.5 MB
- 10年: 25 MB

**結論**: MVP段階では容量を気にする必要なし

## バックアップ・運用

### MVP段階での方針

- **バックアップ**: 開発段階では最小限
- **監視**: 基本的なエラーログのみ
- **メンテナンス**: 必要になってから検討

### 将来の運用計画（必要になってから）

- 定期バックアップ
- パフォーマンス監視
- データベースメンテナンス

## サンプルデータ

### テストデータ挿入例

```sql
-- サンプルデータ挿入（日足データ）
INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume) VALUES
('7203.T', '2024-09-09', 2500.00, 2550.00, 2480.00, 2530.00, 1500000),
('7203.T', '2024-09-08', 2480.00, 2520.00, 2460.00, 2500.00, 1200000),
('7203.T', '2024-09-07', 2450.00, 2490.00, 2430.00, 2480.00, 1100000);

-- 6502.T（東芝）のサンプルデータ
INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume) VALUES
('6502.T', '2024-09-09', 4500.00, 4580.00, 4450.00, 4550.00, 800000),
('6502.T', '2024-09-08', 4480.00, 4520.00, 4460.00, 4500.00, 750000);
```

## 実装優先度

### 優先度: 高（MVP必須）

- ✅ stocks_daily テーブル作成
- ✅ 基本制約（ユニーク、チェック）
- ✅ 基本インデックス
- ✅ SQLAlchemyモデル

### 優先度: 中（動作確認後）

- パフォーマンス最適化
- 詳細なログ・監視
- バックアップ設定

### 優先度: 低（必要になってから）

- テーブルパーティション
- レプリケーション
- アーカイブ機能

## マイルストーン1対応：複数時間軸とmax期間対応

### yfinanceで対応可能な時間軸とテーブル対応表

| 時間軸   | yfinance interval | テーブル名   | 実装優先度        | 備考              |
| -------- | ----------------- | ------------ | ----------------- | ----------------- |
| 1分足    | 1m                | stocks_1m    | **高（M1必須）**  | 大容量注意        |
| 5分足    | 5m                | stocks_5m    | **高（M1必須）**  | 効率的分析        |
| 15分足   | 15m               | stocks_15m   | **高（M1必須）**  | スイング向け      |
| 30分足   | 30m               | stocks_30m   | **高（M1必須）**  | 中期分析          |
| 1時間足  | 1h                | stocks_1h    | **高（M1必須）**  | デイトレード      |
| 日足     | 1d                | stocks_1d    | **高（M1必須）**  | 既存からリネーム  |
| 週足     | 1wk               | stocks_1wk   | **高（M1必須）**  | 中長期分析        |
| 月足     | 1mo               | stocks_1mo   | **高（M1必須）**  | 長期投資          |

### yfinanceで対応可能な期間（period）

| period | 説明                 | 対応状況           | 備考                     |
| ------ | -------------------- | ------------------ | ------------------------ |
| 1d     | 過去1日              | ✅ 既存対応        | -                        |
| 5d     | 過去5日              | ✅ 既存対応        | -                        |
| 1mo    | 過去1ヶ月            | ✅ 既存対応        | -                        |
| 3mo    | 過去3ヶ月            | ✅ 既存対応        | -                        |
| 6mo    | 過去6ヶ月            | ✅ 既存対応        | -                        |
| 1y     | 過去1年              | ✅ 既存対応        | -                        |
| 2y     | 過去2年              | ✅ 既存対応        | -                        |
| 5y     | 過去5年              | ✅ 既存対応        | -                        |
| 10y    | 過去10年             | ✅ 既存対応        | -                        |
| ytd    | 年初来               | ✅ 既存対応        | -                        |
| **max** | **利用可能な全期間** | **🆕 M1で追加**   | **マイルストーン1必須** |

### period=maxの仕様

- **yfinanceのmaxパラメータ**：銘柄が上場してから現在までの全データを取得
- **データ量への影響**：銘柄によっては10年以上のデータとなり大容量
- **パフォーマンス考慮**：初回取得時間が長くなる可能性あり
- **実装上の注意**：タイムアウト設定とプログレス表示が必要

### 将来のテーブル設計案

#### 分足データテーブル（将来拡張）
```sql
CREATE TABLE stocks_minute (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    datetime TIMESTAMP WITH TIME ZONE NOT NULL,  -- 分足は日時が必要
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    interval_type VARCHAR(5) NOT NULL,  -- '1m', '5m', '15m', '30m'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- 制約
    CONSTRAINT uk_stocks_minute_symbol_datetime_interval UNIQUE (symbol, datetime, interval_type),
    CONSTRAINT ck_stocks_minute_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_minute_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_minute_price_logic CHECK (
        high >= low AND high >= open AND high >= close AND low <= open AND low <= close
    )
);
```

#### 週足・月足データテーブル（将来拡張）
```sql
CREATE TABLE stocks_weekly (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,  -- 週の開始日
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_stocks_weekly_symbol_date UNIQUE (symbol, date)
);

CREATE TABLE stocks_monthly (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,  -- 月の開始日
    open DECIMAL(10,2) NOT NULL,
    high DECIMAL(10,2) NOT NULL,
    low DECIMAL(10,2) NOT NULL,
    close DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_stocks_monthly_symbol_date UNIQUE (symbol, date)
);
```

### 設計方針

#### MVP段階（現在）
- **日足のみ実装**: stocks_daily テーブル
- **シンプル設計**: 複雑な統合は避ける
- **動作優先**: まず日足で動作確認

#### 将来拡張時
- **テーブル分離**: 時間軸ごとに独立したテーブル
- **共通スキーマ**: 基本構造は統一
- **段階的追加**: 必要になった時間軸から順次追加

### 拡張時の考慮事項

#### データ量
- **分足**: 大容量（パーティション必要）
- **日足**: 中容量（現在の設計で対応可能）
- **週足・月足**: 小容量（問題なし）

#### パフォーマンス
- **分足**: 専用インデックス・パーティション必要
- **日足**: 現在の設計で十分
- **週足・月足**: 現在の設計パターンで対応可能

#### API設計への影響
- **エンドポイント**: `/api/stocks/daily`, `/api/stocks/minute` など
- **パラメータ**: interval 指定の追加
- **レスポンス**: 時間軸に応じたフォーマット

---

## まとめ

### 🎯 **個人+AI開発でのシンプルDB設計**

#### 設計方針
1. **最小限で開始**: 1テーブルから始める
2. **動作優先**: 複雑な最適化より確実な動作
3. **段階的拡張**: 必要になってから機能追加

#### 避けるべき過度な設計
- 複雑なテーブル構造
- 過度な正規化
- 不要なインデックス
- 複雑な制約

#### 成功の指標
- データの確実な保存・取得
- 基本的なクエリの高速動作
- 簡潔で理解しやすいスキーマ

このデータベース設計により、**動作するシステムを素早く構築**し、**必要に応じて進化**させることができます。