# コードスタイル・規約

## Python (Flask/SQLAlchemy)
- **命名規則**: snake_case (関数、変数)、PascalCase (クラス)
- **インデント**: 4スペース
- **文字列**: シングルクォート優先
- **型ヒント**: 使用推奨 (新規コード)
- **docstring**: 主要関数・クラスに記述

## HTMLテンプレート
- **言語**: 日本語 (lang="ja")
- **アクセシビリティ**: ARIA属性必須
- **セマンティック**: 適切なHTMLタグ使用
- **レスポンシブ**: モバイルファースト

## CSS
- **命名**: BEM記法風 (.card, .card-header, .card-body)
- **カスタムプロパティ**: CSS変数活用
- **レスポンシブ**: フレキシブルデザイン
- **アクセシビリティ**: 色彩コントラスト配慮

## JavaScript
- **ES6+**: モダンJavaScript記法
- **非同期**: async/await使用
- **エラーハンドリング**: try-catch必須
- **DOM操作**: querySelector系使用

## データベース
- **テーブル名**: stocks_daily (snake_case)
- **カラム名**: snake_case
- **インデックス**: パフォーマンス重視
- **制約**: 適切な外部キー・NOT NULL設定

## ファイル構成
- **設定ファイル**: .env (環境変数)
- **ドキュメント**: markdown形式
- **スクリプト**: scripts/ ディレクトリ
- **テスト**: tests/ ディレクトリ、pytest準拠