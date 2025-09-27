# コードベース構造

## ディレクトリ構成
```
STOCK-INVESTMENT-ANALYZER/
├── app/                    # メインアプリケーション
│   ├── app.py             # Flaskアプリケーション本体
│   ├── models.py          # データベースモデル
│   ├── static/            # 静的ファイル
│   │   ├── style.css      # CSS
│   │   ├── script.js      # JavaScript
│   │   └── app.js         # 追加JavaScript
│   └── templates/         # HTMLテンプレート
│       └── index.html     # メインページ
├── docs/                  # ドキュメント
│   ├── tasks/            # タスク・マイルストン管理
│   │   └── milestones.md # v2.0.0マイルストン
│   ├── frontend_design.md
│   ├── system_monitoring_design.md
│   └── (その他設計書)
├── scripts/              # データベースセットアップスクリプト
│   ├── create_database.sql
│   ├── create_tables.sql
│   ├── insert_sample_data.sql
│   ├── setup_db.bat      # Windows用セットアップ
│   └── setup_db.sh       # Unix用セットアップ
├── tests/                # テストコード
│   ├── test_app.py
│   ├── test_models.py
│   ├── test_error_handling.py
│   └── conftest.py       # pytest設定
└── venv/                 # Python仮想環境
```

## 主要コンポーネント
- **app.py**: Flask routes, API endpoints
- **models.py**: SQLAlchemy models, database operations
- **index.html**: Single-page application UI
- **script.js**: Frontend interactions, AJAX calls
- **style.css**: Responsive design, accessibility styling