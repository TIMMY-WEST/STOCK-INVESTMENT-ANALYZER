# プロジェクト概要

## プロジェクト名
STOCK-INVESTMENT-ANALYZER

## プロジェクトの目的
Yahoo Financeから日本企業の株価データを取得し、PostgreSQLに保存するWebアプリケーション。
FlaskベースのMVP優先設計で、シンプルな構成から段階的に機能拡張できる株価データ収集・分析システム。

## 技術スタック
- **バックエンド**: Flask 3.0.0, SQLAlchemy 2.0.23
- **データベース**: PostgreSQL (psycopg2-binary 2.9.9)
- **データ取得**: yfinance 0.2.66 (Yahoo Finance API)
- **環境管理**: python-dotenv 1.0.0
- **フロントエンド**: HTML/CSS/JavaScript (Vanilla)
- **テスト**: pytest

## プロジェクトの特徴
- MVP優先設計による段階的機能拡張
- 日本株式市場特化（東証対応）
- PostgreSQLを使用した高性能なデータ保存
- レスポンシブデザイン対応
- アクセシビリティ配慮（ARIA属性、セマンティックHTML）