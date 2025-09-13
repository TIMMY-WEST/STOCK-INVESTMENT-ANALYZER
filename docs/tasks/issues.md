# 株価データ取得システム - Issue管理

## 📋 Issue一覧

以下のIssueは [`milestones.md`](./milestones.md) のマイルストンから分解されたタスクです。GitHub Issue管理の基本方針（[`github_workflow.md`](../github_workflow.md) 2.1節）に従って作成されています。

---

## 🏗️ マイルストン 1: 環境構築・基盤整備 関連Issue

### Issue #1: Python環境とプロジェクト構造のセットアップ
**Labels**: `feature`, `infrastructure`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🏗️ マイルストン 1: 環境構築・基盤整備 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
Python 3.12.8環境のセットアップとプロジェクトディレクトリ構成の作成

#### 完了条件
- [ ] Python 3.12.8仮想環境作成
- [ ] 依存関係インストール（yfinance, psycopg2-binary, SQLAlchemy, Flask等）
- [ ] プロジェクトディレクトリ構成作成（app/, docs/, tests/ 等）
- [ ] requirements.txt作成
- [ ] 基本的なプロジェクト構成の動作確認

#### PRレビュー重点観点
- [ ] 仮想環境が正しく作成されているか
- [ ] 必要な依存関係が全て含まれているか
- [ ] ディレクトリ構成が仕様書と一致しているか
- [ ] requirements.txtにバージョン固定が適切に設定されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 仮想環境でのパッケージインポート確認
- プロジェクト構成が [`project_architecture.md`](../project_architecture.md) と一致していることを確認

#### 参考仕様書
- [`setup_guide.md`](../setup_guide.md)
- [`project_architecture.md`](../project_architecture.md)

---

### Issue #2: PostgreSQL環境構築とデータベース接続設定
**Labels**: `feature`, `database`, `infrastructure`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🏗️ マイルストン 1: 環境構築・基盤整備 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
PostgreSQLのローカル環境構築とアプリケーションからの接続設定

#### 完了条件
- [ ] PostgreSQLローカルインストールと起動確認
- [ ] データベース・ユーザー作成
- [ ] .env環境変数ファイル作成
- [ ] SQLAlchemyでの基本接続設定
- [ ] 基本的な接続テスト成功

#### PRレビュー重点観点
- [ ] PostgreSQLの設定が適切か（ポート、認証等）
- [ ] .envファイルでの機密情報管理が適切か
- [ ] SQLAlchemy接続設定が正しいか
- [ ] セキュリティ面での問題がないか（認証情報の扱い）
- [ ] エラーハンドリングが適切に実装されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- PostgreSQL接続テスト
- 環境変数の読み込み確認
- SQLAlchemyでの基本操作確認

#### 参考仕様書
- [`setup_guide.md`](../setup_guide.md)
- [`database_design.md`](../database_design.md)

---

## 💾 マイルストン 2: データベース実装 関連Issue

### Issue #3: PostgreSQL データベース・テーブル作成スクリプト実装
**Labels**: `feature`, `database`, `infrastructure`, `priority:high`
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `💾 マイルストン 2: データベース実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
PostgreSQLデータベースとstocks_dailyテーブルを作成するSQLスクリプトの実装

#### 完了条件
- [ ] データベース作成スクリプト（`scripts/create_database.sql`）作成
- [ ] テーブル作成スクリプト（`scripts/create_tables.sql`）作成
- [ ] セットアップ用のシェルスクリプト（`scripts/setup_db.sh` or `scripts/setup_db.bat`）作成
- [ ] スクリプト実行手順の文書化
- [ ] PostgreSQL接続確認とテーブル作成の動作確認
- [ ] 初期データ投入スクリプト（サンプルデータ）作成

#### PRレビュー重点観点
- [ ] SQLスクリプトの構文が正しいか
- [ ] データベース・テーブル設計が仕様書と一致しているか
- [ ] セットアップスクリプトが適切に動作するか
- [ ] 実行手順が明確で再現可能か
- [ ] エラー処理が適切に実装されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 新しいPostgreSQLインスタンスでのスクリプト実行確認
- 作成されたデータベース・テーブル構造の確認
- 初期データ投入の確認
- セットアップ手順の再現性確認

#### 参考仕様書
- [`database_design.md`](../database_design.md)
- [`setup_guide.md`](../setup_guide.md)

---

### Issue #4: stocks_dailyテーブル作成と制約設定
**Labels**: `feature`, `database`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `💾 マイルストン 2: データベース実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
株価データ格納用のstocks_dailyテーブル作成と必要な制約・インデックスの設定

#### 完了条件
- [ ] stocks_dailyテーブルのCREATE文実装
- [ ] 主キー設定（symbol, date複合キー）
- [ ] NOT NULL制約設定
- [ ] チェック制約設定（価格 > 0等）
- [ ] インデックス設定（銘柄、日付、複合）
- [ ] テーブル構造の動作確認

#### PRレビュー重点観点
- [ ] テーブル設計が仕様書と一致しているか
- [ ] 制約設定が適切か（データ整合性確保）
- [ ] インデックス設定が効率的か
- [ ] カラムのデータ型が適切か
- [ ] 将来的な拡張性が考慮されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- テーブル作成の確認
- 制約違反データでのエラー確認
- インデックス使用状況の確認

#### 参考仕様書
- [`database_design.md`](../database_design.md)

---

### Issue #5: SQLAlchemyモデル実装とCRUD操作
**Labels**: `feature`, `backend`, `database`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `💾 マイルストン 2: データベース実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
SQLAlchemyを使用したStockDailyモデルの実装と基本的なCRUD操作の実装

#### 完了条件
- [ ] `app/models.py`にStockDailyモデル実装
- [ ] SQLAlchemyでのテーブル定義
- [ ] 基本的なCRUD操作メソッド実装
- [ ] データベースセッション管理実装
- [ ] サンプルデータでの動作確認
- [ ] 基本的なエラーハンドリング実装

#### PRレビュー重点観点
- [ ] SQLAlchemyモデルの定義が適切か
- [ ] CRUDメソッドの実装が正しいか
- [ ] セッション管理が適切か（リソース管理）
- [ ] エラーハンドリングが十分か
- [ ] コードの可読性・保守性が保たれているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- サンプルデータの挿入・取得・更新・削除テスト
- 制約違反データでのエラーハンドリング確認
- 複数レコードでの操作確認

#### 参考仕様書
- [`database_design.md`](../database_design.md)

---

## ⚙️ マイルストン 3: バックエンドAPI実装 関連Issue

### Issue #6: Flaskアプリケーション基盤とデータベース接続設定
**Labels**: `feature`, `backend`, `infrastructure`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `⚙️ マイルストン 3: バックエンドAPI実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
Flaskアプリケーションの基盤となる`app.py`の作成とデータベース接続の設定

#### 完了条件
- [ ] `app/app.py`にFlaskアプリケーション作成
- [ ] データベース接続設定
- [ ] 環境変数の読み込み設定
- [ ] 基本的なルーティング設定
- [ ] エラーハンドラー実装
- [ ] アプリケーション起動確認

#### PRレビュー重点観点
- [ ] Flaskアプリケーションの構成が適切か
- [ ] データベース接続設定が正しいか
- [ ] 環境変数の管理が適切か
- [ ] エラーハンドリングが実装されているか
- [ ] セキュリティ面での基本設定が適切か
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- Flaskアプリケーションの起動確認
- データベース接続テスト
- 基本ルートでのレスポンス確認

#### 参考仕様書
- [`api_specification.md`](../api_specification.md)

---

### Issue #7: 株価データ取得API実装（POST /api/fetch-data）
**Labels**: `feature`, `backend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `⚙️ マイルストン 3: バックエンドAPI実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
Yahoo Finance（yfinance）から株価データを取得してデータベースに保存するAPIエンドポイント

#### 完了条件
- [ ] `POST /api/fetch-data`エンドポイント実装
- [ ] yfinanceライブラリでの株価データ取得処理
- [ ] リクエストパラメータのバリデーション（銘柄コード、期間）
- [ ] データベース保存処理
- [ ] 重複データのハンドリング
- [ ] エラーレスポンス実装（API仕様準拠）
- [ ] 成功レスポンス実装

#### PRレビュー重点観点
- [ ] yfinanceライブラリの使用方法が適切か
- [ ] リクエストデータのバリデーションが十分か
- [ ] データベース保存処理が正しいか
- [ ] エラーハンドリングが適切に実装されているか
- [ ] APIレスポンス形式が仕様書通りか
- [ ] 重複データの処理が適切か
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- PostmanまたはcurlでのAPI動作確認
- トヨタ自動車（7203.T）での正常系テスト
- 存在しない銘柄コードでの異常系テスト
- 各種エラーケースでのレスポンス確認

#### 参考仕様書
- [`api_specification.md`](../api_specification.md)

---

### Issue #8: 保存済み株価データ取得API実装（GET /api/stocks）
**Labels**: `feature`, `backend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `⚙️ マイルストン 3: バックエンドAPI実装 関連Issue`  
**Assignees**: 自分をアサイン

#### 実装内容
データベースに保存された株価データを取得するAPIエンドポイント（ページネーション・フィルタリング対応）

#### 完了条件
- [ ] `GET /api/stocks`エンドポイント実装
- [ ] データベースからのデータ取得処理
- [ ] ページネーション機能実装（limit, offset）
- [ ] 銘柄フィルタリング機能実装
- [ ] 日付範囲フィルタリング機能実装
- [ ] レスポンス形式の統一（API仕様準拠）
- [ ] エラーハンドリング実装

#### PRレビュー重点観点
- [ ] データ取得クエリが効率的か
- [ ] ページネーションの実装が適切か
- [ ] フィルタリング機能が正しく動作するか
- [ ] APIレスポンス形式が仕様書通りか
- [ ] エラーハンドリングが適切に実装されているか
- [ ] パフォーマンス面での配慮があるか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 保存済みデータの取得確認
- ページネーション動作確認
- 各種フィルタリング機能の確認
- 大量データでのパフォーマンス確認

#### 参考仕様書
- [`api_specification.md`](../api_specification.md)

---

## 🎨 マイルストン 4: フロントエンド実装 関連Issue

### Issue #9: HTMLテンプレートとCSS基盤実装
**Labels**: `feature`, `frontend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🎨 マイルストン 4: フロントエンド実装 関連Issue`   
**Assignees**: 自分をアサイン

#### 実装内容
株価データ管理画面のHTMLテンプレート作成と基本的なCSS実装

#### 完了条件
- [ ] `app/templates/index.html`作成
- [ ] `app/static/style.css`作成
- [ ] レスポンシブデザインの基本実装
- [ ] フォーム・テーブルの基本レイアウト
- [ ] ナビゲーション・ヘッダー実装
- [ ] エラー・成功メッセージ表示エリア実装
- [ ] 基本的なUI/UX設計

#### PRレビュー重点観点
- [ ] HTMLの構造が適切か（セマンティック要素の使用）
- [ ] CSSの設計が保守しやすいか
- [ ] レスポンシブデザインが適切に実装されているか
- [ ] アクセシビリティの基本配慮があるか
- [ ] ブラウザ間互換性が考慮されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 各種デバイスサイズでの表示確認
- 主要ブラウザでの表示確認
- 基本的なアクセシビリティチェック

#### 参考仕様書
- [`frontend_design.md`](../frontend_design.md)

---

### Issue #10: データ取得フォーム機能実装
**Labels**: `feature`, `frontend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🎨 マイルストン 4: フロントエンド実装 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
銘柄コード・期間指定による株価データ取得フォームの実装

#### 完了条件
- [ ] 銘柄コード入力フィールド実装
- [ ] 期間選択プルダウン実装（1週間、1ヶ月、3ヶ月等）
- [ ] 送信ボタン・リセットボタン実装
- [ ] フォームバリデーション実装（クライアントサイド）
- [ ] 送信中の状態表示（ローディング）
- [ ] エラーメッセージ表示機能
- [ ] 成功時のフィードバック表示

#### PRレビュー重点観点
- [ ] フォームの入力項目が仕様通りか
- [ ] バリデーション処理が適切か
- [ ] ユーザビリティが配慮されているか
- [ ] エラーハンドリングが適切に実装されているか
- [ ] UI/UXが直感的か
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 各入力項目の動作確認
- バリデーション機能の確認
- エラーケースでの表示確認

#### 参考仕様書
- [`frontend_design.md`](../frontend_design.md)

---

### Issue #11: JavaScript実装とAPI連携機能
**Labels**: `feature`, `frontend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🎨 マイルストン 4: フロントエンド実装 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
フォームからAPIへのリクエスト送信とレスポンス処理のJavaScript実装

#### 完了条件
- [ ] `app/static/script.js`作成
- [ ] フォーム送信時のAPI呼び出し実装
- [ ] `POST /api/fetch-data`への非同期リクエスト
- [ ] `GET /api/stocks`への非同期リクエスト
- [ ] レスポンスデータの処理・表示
- [ ] エラーレスポンスのハンドリング
- [ ] ローディング状態の管理

#### PRレビュー重点観点
- [ ] 非同期処理の実装が適切か
- [ ] エラーハンドリングが十分か
- [ ] APIレスポンスの処理が正しいか
- [ ] ユーザーフィードバックが適切か
- [ ] コードの可読性・保守性が保たれているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- フォーム送信からAPI呼び出しまでの一連の動作確認
- 正常系・異常系での処理確認
- ネットワークエラー時の挙動確認

#### 参考仕様書
- [`frontend_design.md`](../frontend_design.md)
- [`api_specification.md`](../api_specification.md)

---

### Issue #12: 株価データテーブル表示機能実装
**Labels**: `feature`, `frontend`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🎨 マイルストン 4: フロントエンド実装 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
取得した株価データをテーブル形式で表示する機能の実装

#### 完了条件
- [ ] 株価データテーブルの動的生成
- [ ] データフォーマット実装（価格・日付・出来高の表示形式）
- [ ] テーブルソート機能実装（日付順等）
- [ ] データが存在しない場合のメッセージ表示
- [ ] レスポンシブテーブルの実装
- [ ] 大量データ対応（ページネーション表示）

#### PRレビュー重点観点
- [ ] テーブル表示の実装が適切か
- [ ] データフォーマットが見やすいか
- [ ] ソート機能が正しく動作するか
- [ ] レスポンシブ対応が適切か
- [ ] パフォーマンス面での配慮があるか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 様々なデータ量でのテーブル表示確認
- ソート機能の動作確認
- レスポンシブデザインの確認

#### 参考仕様書
- [`frontend_design.md`](../frontend_design.md)

---

## 🧪 マイルストン 5: 統合テスト・動作確認 関連Issue

### Issue #13: エンドツーエンド動作確認テスト
**Labels**: `feature`, `testing`, `priority:high`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🧪 マイルストン 5: 統合テスト・動作確認 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
ブラウザからの株価データ取得フローの完全な動作確認テスト

#### 完了条件
- [ ] ブラウザからの株価データ取得フロー確認
- [ ] トヨタ自動車（7203.T）での正常系テスト実行
- [ ] 複数銘柄での動作確認（少なくとも3銘柄）
- [ ] 異なる期間設定での動作確認
- [ ] データの永続化確認（ページリロード後も表示される）
- [ ] テスト結果の詳細記録

#### PRレビュー重点観点
- [ ] テストケースが網羅的か
- [ ] 実際の本番環境想定でのテストか
- [ ] テスト結果の記録が適切か
- [ ] 発見された問題が適切に記録されているか
- [ ] 次のフェーズへの準備が整っているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- ブラウザでの実際の操作による手動テスト
- 異なるシナリオでのテスト実行
- テスト結果の詳細記録

#### 参考仕様書
- 全仕様書を参照

---

### Issue #14: エラーケース・例外処理テスト
**Labels**: `feature`, `testing`, `priority:medium`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🧪 マイルストン 5: 統合テスト・動作確認 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
各種エラーケースでの適切なエラーハンドリングと表示の確認テスト

#### 完了条件
- [ ] 存在しない銘柄コードでのエラーテスト
- [ ] ネットワークエラー時の動作確認
- [ ] データベース接続エラー時の動作確認
- [ ] 不正な入力値でのバリデーションテスト
- [ ] APIサーバーエラー時のフロントエンド表示確認
- [ ] エラー時の適切なメッセージ表示確認

#### PRレビュー重点観点
- [ ] エラーケースが網羅的にテストされているか
- [ ] エラーメッセージがユーザーフレンドリーか
- [ ] システムの堅牢性が確保されているか
- [ ] エラー時のユーザー体験が配慮されているか
- [ ] セキュリティ面での問題がないか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 意図的にエラーを発生させるテストケース実行
- 各種異常系での動作確認
- エラーメッセージの表示内容確認

#### 参考仕様書
- 全仕様書を参照

---

### Issue #15: ブラウザ互換性・レスポンシブデザイン確認
**Labels**: `feature`, `testing`, `frontend`, `priority:medium`  
**Projects**: `@TIMMY-WEST's STOCK-INVESTMENT-ANALYZER`  
**Milestone**: `🧪 マイルストン 5: 統合テスト・動作確認 関連Issue` 
**Assignees**: 自分をアサイン

#### 実装内容
主要ブラウザとデバイスでの互換性とレスポンシブデザインの確認

#### 完了条件
- [ ] Chrome、Firefox、Safari、Edgeでの動作確認
- [ ] スマートフォンでの表示・操作確認
- [ ] タブレットでの表示・操作確認
- [ ] 異なる画面サイズでの表示確認
- [ ] 基本的なアクセシビリティ確認
- [ ] 互換性問題があれば修正対応

#### PRレビュー重点観点
- [ ] 主要ブラウザで動作するか
- [ ] レスポンシブデザインが適切に機能するか
- [ ] アクセシビリティの基本配慮があるか
- [ ] パフォーマンスに問題がないか
- [ ] 実用的なユーザビリティが確保されているか
- [ ] 実装内容が既存の仕様書・ドキュメントと乖離していないか

#### テスト方法
- 異なるブラウザでの手動テスト
- デベロッパーツールでの表示確認
- 実際のデバイスでの動作確認

#### 参考仕様書
- [`frontend_design.md`](../frontend_design.md)

---

## 📊 Issue管理の進め方

### 🔄 推奨開発フロー
```
Issue作成 → ブランチ作成 → 実装 → PR作成 → レビュー → マージ → Issue完了
```

### ⚠️ 重要なポイント
- **各Issueは順番に実装**する（特にマイルストン1→2→3→4→5の順序）
- **前のIssueが完了してから次に進む**
- **各Issue完了時に動作確認**を行う
- **問題があれば前のIssueに戻る**
- **PRマージ時に `Closes #<Issue番号>` でIssueを自動クローズ**

### 📈 進捗管理
- 各IssueをGitHub Issue として作成
- ラベル・マイルストン・アサインの設定
- プロジェクトボードでのカンバン管理
- 完了条件のチェックボックスで進捗管理

---

## 📚 参考仕様書

各Issue実装時は以下の仕様書を参照：

- **プロジェクト全体設計**: [`project_architecture.md`](../project_architecture.md)
- **環境構築手順**: [`setup_guide.md`](../setup_guide.md)
- **API仕様**: [`api_specification.md`](../api_specification.md)
- **データベース設計**: [`database_design.md`](../database_design.md)
- **フロントエンド設計**: [`frontend_design.md`](../frontend_design.md)
- **GitHub運用ワークフロー**: [`github_workflow.md`](../github_workflow.md)

このIssue分解により、MVP開発を段階的かつ確実に進めることができます。