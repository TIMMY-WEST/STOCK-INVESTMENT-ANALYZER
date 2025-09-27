# 推奨コマンド

## 開発環境
- **OS**: Windows
- **Python**: 仮想環境 (venv)

## 基本コマンド
```bash
# 仮想環境の有効化 (Windows)
venv\Scripts\activate.bat

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション起動
python app/app.py

# データベースセットアップ (Windows)
scripts\setup_db.bat
```

## テスト実行
```bash
# 全テスト実行
pytest

# 特定のテストファイル実行
pytest tests/test_app.py
pytest tests/test_models.py

# 詳細出力でテスト実行
pytest -v

# カバレッジ付きテスト実行
pytest --cov=app
```

## データベース操作
```bash
# データベース接続テスト
python app/simple_test.py

# データベース初期化
python scripts/db/create_database.py

# 接続テスト
python scripts/db/create_database.py --test-connection
```

## ユーティリティコマンド (Windows)
```bash
# ディレクトリ一覧
dir

# ファイル内容表示
type filename.txt

# ファイル検索
where filename

# プロセス一覧
tasklist

# ネットワーク接続確認
ping hostname
```