# End-to-End (E2E) テストガイド

## 概要

このプロジェクトには、実際のアプリケーション起動とブラウザ操作を含むE2Eテストが含まれています。これらのテストは、ユーザーの実際の操作をシミュレートして、アプリケーション全体の動作を検証します。

## 必要な依存関係

E2Eテストを実行するには、以下の依存関係が必要です：

```bash
pip install -r requirements.txt
```

主要な依存関係：
- `selenium==4.15.2` - ブラウザ自動化
- `webdriver-manager==4.0.1` - ChromeDriverの自動管理
- `pytest==7.4.3` - テストフレームワーク

## セットアップ

### 1. Google Chromeのインストール

E2EテストはGoogle Chromeブラウザを使用します。システムにGoogle Chromeがインストールされていることを確認してください。

### 2. 環境変数の設定

テスト用の環境変数を設定してください：

```bash
# .env ファイルまたは環境変数として設定
FLASK_ENV=testing
FLASK_PORT=8001
```

### 3. データベースの準備

テスト実行前に、データベースが適切に設定されていることを確認してください。

## テストの実行

### 全てのE2Eテストを実行

```bash
pytest tests/test_e2e_application.py -v
```

### 特定のテストを実行

```bash
# アプリケーション起動テストのみ
pytest tests/test_e2e_application.py::TestE2EApplication::test_application_startup_and_homepage_load -v

# フォーム操作テストのみ
pytest tests/test_e2e_application.py::TestE2EApplication::test_stock_data_fetch_form_interaction -v
```

### ヘッドレスモードを無効にして実行（デバッグ用）

テストファイル内の `chrome_options.add_argument("--headless")` をコメントアウトして実行すると、ブラウザの動作を視覚的に確認できます。

## テスト内容

### 1. アプリケーション起動テスト
- Flaskアプリケーションの自動起動
- ホームページの正常な読み込み確認
- ページタイトルとヘッダーの確認

### 2. フォーム操作テスト
- 株価データ取得フォームの要素確認
- 入力フィールドの操作
- セレクトボックスの選択
- デフォルト値の確認

### 3. データ取得機能テスト
- 有効な銘柄コードでのデータ取得
- 結果表示の確認
- 処理時間の妥当性確認

### 4. エラーハンドリングテスト
- 無効な銘柄コードの処理
- エラーメッセージの表示確認
- ユーザーフレンドリーなエラー表示

### 5. UI機能テスト
- リセットボタンの動作確認
- ナビゲーションリンクの存在確認
- アクセシビリティ機能の確認

### 6. レスポンシブデザインテスト
- 異なる画面サイズでの表示確認
- モバイル、タブレット、デスクトップ対応

### 7. API エンドポイントテスト
- データベース接続テストAPI
- レスポンス形式の確認

## トラブルシューティング

### ChromeDriverの問題

```bash
# ChromeDriverを手動で更新
pip install --upgrade webdriver-manager
```

### ポートの競合

テスト用ポート（8001）が使用中の場合：

```bash
# 使用中のプロセスを確認
netstat -ano | findstr :8001

# プロセスを終了（Windows）
taskkill /PID <プロセスID> /F
```

### タイムアウトエラー

ネットワークが遅い環境では、テストファイル内の待機時間を調整してください：

```python
# WebDriverWaitのタイムアウト時間を延長
WebDriverWait(driver, 30)  # デフォルト: 10秒
```

## CI/CD での実行

継続的インテグレーション環境でE2Eテストを実行する場合：

```yaml
# GitHub Actions の例
- name: Run E2E Tests
  run: |
    sudo apt-get update
    sudo apt-get install -y google-chrome-stable
    pytest tests/test_e2e_application.py -v
```

## 注意事項

1. **リソース使用量**: E2Eテストはブラウザを起動するため、通常のユニットテストより多くのリソースを消費します。

2. **実行時間**: ネットワーク接続やシステム性能により、実行時間が変動する可能性があります。

3. **環境依存**: ブラウザのバージョンやシステム環境により、テスト結果が影響を受ける場合があります。

4. **データベース状態**: テスト実行前にデータベースの状態を確認し、必要に応じてリセットしてください。

## 今後の拡張

- より多くのブラウザ（Firefox、Safari）でのテスト
- パフォーマンステストの追加
- ビジュアルリグレッションテストの導入
- モバイルデバイスでのテスト
