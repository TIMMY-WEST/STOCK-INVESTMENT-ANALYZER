---
category: guide
ai_context: high
last_updated: 2025-10-18
related_docs:
  - ../guides/DATABASE_SETUP.md
  - ../architecture/project_architecture.md
  - ../development/github_workflow.md
---

# 環境構築・セットアップ手順書

## 概要

株価データ取得システムの開発環境セットアップ手順書です。  
プロジェクトの設計理念（**動作優先・シンプル設計・後から拡張**）に基づき、最小限の構成で素早く動作する環境を構築します。

## 目次

- [環境構築・セットアップ手順書](#環境構築セットアップ手順書)
  - [概要](#概要)
  - [目次](#目次)
  - [前提条件](#前提条件)
  - [1. 開発環境の準備](#1-開発環境の準備)
    - [1.1 Python環境のセットアップ](#11-python環境のセットアップ)
    - [1.2 プロジェクトディレクトリの準備](#12-プロジェクトディレクトリの準備)
    - [1.3 Python仮想環境の作成](#13-python仮想環境の作成)
    - [1.4 依存関係のインストール](#14-依存関係のインストール)
  - [2. PostgreSQL セットアップ](#2-postgresql-セットアップ)
    - [2.1 PostgreSQLのインストール](#21-postgresqlのインストール)
      - [Windows](#windows)
      - [macOS](#macos)
      - [Ubuntu/Linux](#ubuntulinux)
    - [2.2 データベースの作成](#22-データベースの作成)
    - [2.3 テーブルの作成](#23-テーブルの作成)
    - [2.4 接続確認](#24-接続確認)
  - [3. アプリケーションの初期セットアップ](#3-アプリケーションの初期セットアップ)
    - [3.1 環境変数の設定](#31-環境変数の設定)
    - [3.2 最小限のアプリケーション作成](#32-最小限のアプリケーション作成)
    - [3.3 データベースモデルの作成](#33-データベースモデルの作成)
  - [4. 初回起動手順](#4-初回起動手順)
    - [4.1 データベーステーブル作成](#41-データベーステーブル作成)
    - [4.2 アプリケーション起動](#42-アプリケーション起動)
    - [4.3 動作確認](#43-動作確認)
  - [5. トラブルシューティング](#5-トラブルシューティング)
    - [5.1 よくある問題と解決方法](#51-よくある問題と解決方法)
    - [5.2 動作確認チェックリスト](#52-動作確認チェックリスト)
  - [6. 開発時の作業フロー](#6-開発時の作業フロー)
    - [6.1 日常の開発開始手順](#61-日常の開発開始手順)
    - [6.2 開発終了時の手順](#62-開発終了時の手順)
  - [付録](#付録)
    - [A. 必要なファイルの作成](#a-必要なファイルの作成)
    - [B. 環境変数一覧](#b-環境変数一覧)
    - [C. ポート番号一覧](#c-ポート番号一覧)

## 前提条件

- Windows 10/11, macOS, またはLinux
- インターネット接続環境
- 管理者権限（インストール時のみ）

## 1. 開発環境の準備

### 1.1 Python環境のセットアップ

**Python 3.12.8 のインストール**

```bash
# バージョン確認
python --version
# または
python3 --version
```

Python 3.12.8 がインストールされていない場合：
- **Windows**: [Python.org](https://www.python.org/downloads/) からダウンロード
- **macOS**: `brew install python@3.12` または Python.orgからダウンロード
- **Linux**: `sudo apt install python3.12` または各ディストリビューションの方法

### 1.2 プロジェクトディレクトリの準備

```bash
# プロジェクトディレクトリに移動
cd F:\TAKUMI\GitHub\STOCK-INVESTMENT-ANALYZER

# ディレクトリ構造の確認
ls -la
```

### 1.3 Python仮想環境の作成

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 仮想環境が有効化されていることを確認
which python
```

### 1.4 依存関係のインストール

**requirements.txt の作成**

```bash
# requirements.txt ファイルを作成
cat > requirements.txt << EOF
Flask==3.0.0
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
yfinance==0.2.28
python-dotenv==1.0.0
EOF
```

**パッケージのインストール**

```bash
# 依存関係のインストール
pip install -r requirements.txt

# インストール確認
pip list
```

## 2. PostgreSQL セットアップ

### 2.1 PostgreSQLのインストール

#### Windows
```bash
# Chocolatey経由（推奨）
choco install postgresql

# または公式インストーラーを使用
# https://www.postgresql.org/download/windows/
```

#### macOS
```bash
# Homebrew経由（推奨）
brew install postgresql

# サービス開始
brew services start postgresql
```

#### Ubuntu/Linux
```bash
# パッケージ更新
sudo apt update

# PostgreSQLインストール
sudo apt install postgresql postgresql-contrib

# サービス開始
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2.2 データベースの作成

```bash
# PostgreSQLに接続（初回）
sudo -u postgres psql

# または Windows/macOSの場合
psql -U postgres
```

**データベースとユーザーの作成**

```sql
-- データベース作成
CREATE DATABASE stock_data_system;

-- 開発用ユーザー作成
CREATE USER stock_user WITH PASSWORD 'stock_password';

-- 権限付与
GRANT ALL PRIVILEGES ON DATABASE stock_data_system TO stock_user;

-- 接続テスト用に追加権限
ALTER USER stock_user CREATEDB;

-- 終了
\q
```

### 2.3 テーブルの作成

**新しいターミナルでデータベースに接続**

```bash
# 作成したデータベースに接続
psql -U stock_user -d stock_data_system -h localhost
```

**テーブル作成SQL**

```sql
-- stocks_daily テーブル作成
CREATE TABLE stocks_daily (
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
    CONSTRAINT uk_stocks_daily_symbol_date UNIQUE (symbol, date),
    CONSTRAINT ck_stocks_daily_prices CHECK (open >= 0 AND high >= 0 AND low >= 0 AND close >= 0),
    CONSTRAINT ck_stocks_daily_volume CHECK (volume >= 0),
    CONSTRAINT ck_stocks_daily_price_logic CHECK (
        high >= low AND 
        high >= open AND 
        high >= close AND 
        low <= open AND 
        low <= close
    )
);

-- インデックス作成
CREATE INDEX idx_stocks_daily_symbol ON stocks_daily (symbol);
CREATE INDEX idx_stocks_daily_date ON stocks_daily (date);
CREATE INDEX idx_stocks_daily_symbol_date_desc ON stocks_daily (symbol, date DESC);
```

### 2.4 接続確認

```sql
-- テーブル作成確認
\dt

-- テーブル構造確認
\d stocks_daily

-- サンプルデータ挿入
INSERT INTO stocks_daily (symbol, date, open, high, low, close, volume) VALUES
('7203.T', '2024-09-09', 2500.00, 2550.00, 2480.00, 2530.00, 1500000);

-- データ確認
SELECT * FROM stocks_daily;

-- 終了
\q
```

## 3. アプリケーションの初期セットアップ

### 3.1 環境変数の設定

**.env ファイルの作成**

```bash
# .env ファイル作成
cat > .env << EOF
# データベース設定
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_data_system
DB_USER=stock_user
DB_PASSWORD=stock_password

# アプリケーション設定
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=8000
EOF
```

### 3.2 最小限のアプリケーション作成

**appディレクトリの作成**

```bash
# appディレクトリ作成
mkdir -p app/templates app/static
```

**app/app.py の作成**

```python
from flask import Flask, render_template, request, jsonify
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import yfinance as yf

# 環境変数読み込み
load_dotenv()

app = Flask(__name__)

# データベース接続設定
DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/fetch-data', methods=['POST'])
def fetch_data():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '7203.T')
        period = data.get('period', '1mo')
        
        # Yahoo Financeからデータ取得
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return jsonify({
                "success": False,
                "error": "INVALID_SYMBOL",
                "message": "指定された銘柄コードのデータが取得できません"
            }), 400
        
        return jsonify({
            "success": True,
            "message": "データを正常に取得しました",
            "data": {
                "symbol": symbol,
                "records_count": len(hist),
                "date_range": {
                    "start": hist.index[0].strftime('%Y-%m-%d'),
                    "end": hist.index[-1].strftime('%Y-%m-%d')
                }
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "EXTERNAL_API_ERROR",
            "message": f"データ取得に失敗しました: {str(e)}"
        }), 502

if __name__ == '__main__':
    app.run(
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        port=int(os.getenv('FLASK_PORT', 8000)),
        host='0.0.0.0'
    )
```

### 3.3 データベースモデルの作成

**app/models.py の作成**

```python
from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, UniqueConstraint, CheckConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class StockDaily(Base):
    __tablename__ = 'stocks_daily'
    
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
        UniqueConstraint('symbol', 'date', name='uk_stocks_daily_symbol_date'),
        CheckConstraint('open >= 0 AND high >= 0 AND low >= 0 AND close >= 0', name='ck_stocks_daily_prices'),
        CheckConstraint('volume >= 0', name='ck_stocks_daily_volume'),
        CheckConstraint('high >= low AND high >= open AND high >= close AND low <= open AND low <= close', name='ck_stocks_daily_price_logic'),
        Index('idx_stocks_daily_symbol', 'symbol'),
        Index('idx_stocks_daily_date', 'date'),
        Index('idx_stocks_daily_symbol_date_desc', 'symbol', 'date'),
    )
    
    def __repr__(self):
        return f"<StockDaily(symbol='{self.symbol}', date='{self.date}', close={self.close})>"
```

**app/templates/index.html の作成**

```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>株価データ取得システム</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
        .success { background-color: #d4edda; border-color: #c3e6cb; }
        .error { background-color: #f8d7da; border-color: #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>株価データ取得システム</h1>
        
        <div>
            <label>銘柄コード:</label>
            <input type="text" id="symbol" value="7203.T" placeholder="例: 7203.T">
            
            <label>期間:</label>
            <select id="period">
                <option value="1mo">1ヶ月</option>
                <option value="3mo">3ヶ月</option>
                <option value="6mo">6ヶ月</option>
                <option value="1y">1年</option>
            </select>
            
            <button onclick="fetchData()">データ取得</button>
        </div>
        
        <div id="result"></div>
    </div>

    <script>
        async function fetchData() {
            const symbol = document.getElementById('symbol').value;
            const period = document.getElementById('period').value;
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = '<p>データ取得中...</p>';
            
            try {
                const response = await fetch('/api/fetch-data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ symbol, period })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    resultDiv.className = 'result success';
                    resultDiv.innerHTML = `
                        <h3>取得成功</h3>
                        <p><strong>銘柄:</strong> ${data.data.symbol}</p>
                        <p><strong>レコード数:</strong> ${data.data.records_count}</p>
                        <p><strong>期間:</strong> ${data.data.date_range.start} ～ ${data.data.date_range.end}</p>
                    `;
                } else {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>エラー</h3>
                        <p><strong>エラーコード:</strong> ${data.error}</p>
                        <p><strong>メッセージ:</strong> ${data.message}</p>
                    `;
                }
            } catch (error) {
                resultDiv.className = 'result error';
                resultDiv.innerHTML = `
                    <h3>通信エラー</h3>
                    <p>サーバーとの通信に失敗しました: ${error.message}</p>
                `;
            }
        }
    </script>
</body>
</html>
```

## 4. 初回起動手順

### 4.1 データベーステーブル作成

```bash
# 仮想環境が有効化されていることを確認
which python

# テーブル作成の確認（前の手順で完了している場合はスキップ）
psql -U stock_user -d stock_data_system -h localhost -c "\dt"
```

### 4.2 アプリケーション起動

```bash
# アプリケーションディレクトリに移動
cd app

# Flask アプリケーション起動
python app.py
```

**期待される出力:**
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://[::1]:8000
```

### 4.3 動作確認

**ブラウザで確認**
1. ブラウザで `http://localhost:8000` にアクセス
2. 銘柄コード「7203.T」（トヨタ）でデータ取得テスト
3. 正常にデータが取得されることを確認

**API直接テスト**
```bash
# 別ターミナルで API テスト
curl -X POST http://localhost:8000/api/fetch-data \
  -H "Content-Type: application/json" \
  -d '{"symbol":"7203.T","period":"1mo"}'
```

## 5. トラブルシューティング

### 5.1 よくある問題と解決方法

**問題: PostgreSQL接続エラー**
```bash
# PostgreSQLサービス状態確認
# Windows
net start postgresql

# macOS
brew services list | grep postgresql

# Linux
sudo systemctl status postgresql
```

**問題: Python パッケージエラー**
```bash
# 仮想環境の再作成
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**問題: ポート使用中エラー**
```bash
# ポート8000の使用状況確認
# Windows
netstat -ano | findstr :8000

# macOS/Linux
lsof -i :8000

# 異なるポートで起動
FLASK_PORT=8001 python app.py
```

### 5.2 動作確認チェックリスト

- [ ] Python 3.12.8 がインストールされている
- [ ] 仮想環境が作成・有効化されている
- [ ] 必要なパッケージがインストールされている
- [ ] PostgreSQLサービスが起動している
- [ ] データベース `stock_data_system` が作成されている
- [ ] テーブル `stocks_daily` が作成されている
- [ ] `.env` ファイルが正しく設定されている
- [ ] Flask アプリケーションが起動する
- [ ] ブラウザで画面が表示される
- [ ] API経由でデータ取得ができる

## 6. 開発時の作業フロー

### 6.1 日常の開発開始手順

```bash
# 1. プロジェクトディレクトリに移動
cd F:\TAKUMI\GitHub\STOCK-INVESTMENT-ANALYZER

# 2. 仮想環境の有効化
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. PostgreSQLサービス確認
# Windows: services.msc で postgresql サービス確認
# macOS: brew services list | grep postgresql
# Linux: sudo systemctl status postgresql

# 4. アプリケーション起動
cd app
python app.py
```

### 6.2 開発終了時の手順

```bash
# 1. アプリケーション停止（Ctrl+C）

# 2. 仮想環境の無効化
deactivate

# 3. PostgreSQLサービス停止（必要に応じて）
# Windows: net stop postgresql
# macOS: brew services stop postgresql
# Linux: sudo systemctl stop postgresql
```

## 付録

### A. 必要なファイルの作成

**作成する必要があるファイル一覧:**
- `requirements.txt` - Python依存関係
- `.env` - 環境変数設定
- `app/app.py` - メインアプリケーション
- `app/models.py` - データベースモデル
- `app/templates/index.html` - HTMLテンプレート

### B. 環境変数一覧

| 変数名        | 説明                   | デフォルト値      |
| ------------- | ---------------------- | ----------------- |
| `DB_HOST`     | データベースホスト     | localhost         |
| `DB_PORT`     | データベースポート     | 5432              |
| `DB_NAME`     | データベース名         | stock_data_system |
| `DB_USER`     | データベースユーザー   | stock_user        |
| `DB_PASSWORD` | データベースパスワード | stock_password    |
| `FLASK_ENV`   | Flask環境              | development       |
| `FLASK_DEBUG` | デバッグモード         | True              |
| `FLASK_PORT`  | アプリケーションポート | 8000              |

### C. ポート番号一覧

| サービス   | ポート | 説明                |
| ---------- | ------ | ------------------- |
| Flask App  | 8000   | Webアプリケーション |
| PostgreSQL | 5432   | データベース        |

---

このセットアップ手順により、**動作優先・シンプル設計**の理念に基づいた開発環境を素早く構築し、株価データ取得システムの開発を開始できます。