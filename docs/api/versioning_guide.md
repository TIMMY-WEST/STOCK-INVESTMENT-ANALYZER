# APIバージョニングガイド

## 概要

STOCK-INVESTMENT-ANALYZERでは、APIの後方互換性を保ちながら新機能を追加するために、APIバージョニング機能を導入しています。

## バージョニング方式

### URL パスベースバージョニング

APIバージョンはURLパスに含めて指定します：

```
/api/v{version}/{endpoint}
```

例：
- `/api/v1/system/health-check`
- `/api/v1/bulk-data/jobs`
- `/api/v1/stock-master/stocks`

### 後方互換性

既存のAPIエンドポイント（バージョン指定なし）は引き続き利用可能です：

```
/api/{endpoint}
```

例：
- `/api/system/health-check`
- `/api/bulk-data/jobs`
- `/api/stock-master/stocks`

## サポートされているバージョン

### 現在のバージョン

- **v1**: 初期バージョン（デフォルト）

### デフォルトバージョン

バージョンが指定されていないリクエストは、デフォルトでv1として処理されます。

## APIエンドポイント

### システム監視API

#### ヘルスチェック
- **既存**: `GET /api/system/health-check`
- **v1**: `GET /api/v1/system/health-check`

#### データベース接続テスト
- **既存**: `GET /api/system/database/connection`
- **v1**: `GET /api/v1/system/database/connection`

#### 外部API接続テスト
- **既存**: `GET /api/system/external-api/connection`
- **v1**: `GET /api/v1/system/external-api/connection`

### バルクデータAPI

#### ジョブ管理
- **既存**: `GET /api/bulk-data/jobs`
- **v1**: `GET /api/v1/bulk-data/jobs`

- **既存**: `POST /api/bulk-data/jobs`
- **v1**: `POST /api/v1/bulk-data/jobs`

#### ジョブステータス確認
- **既存**: `GET /api/bulk-data/jobs/{job_id}/status`
- **v1**: `GET /api/v1/bulk-data/jobs/{job_id}/status`

#### ジョブキャンセル
- **既存**: `POST /api/bulk-data/jobs/{job_id}/cancel`
- **v1**: `POST /api/v1/bulk-data/jobs/{job_id}/cancel`

#### ジョブログ取得
- **既存**: `GET /api/bulk-data/jobs/{job_id}/logs`
- **v1**: `GET /api/v1/bulk-data/jobs/{job_id}/logs`

### 株式マスタAPI

#### 株式マスタ更新
- **既存**: `POST /api/stock-master/`
- **v1**: `POST /api/v1/stock-master/`

#### 株式リスト取得
- **既存**: `GET /api/stock-master/stocks`
- **v1**: `GET /api/v1/stock-master/stocks`

## 使用例

### cURLでの使用例

```bash
# 既存のエンドポイント（バージョンなし）
curl -X GET "http://localhost:8000/api/system/health-check"

# バージョン付きエンドポイント
curl -X GET "http://localhost:8000/api/v1/system/health-check"

# 認証が必要なエンドポイント
curl -X GET "http://localhost:8000/api/v1/stock-master/stocks" \
     -H "X-API-Key: your-api-key"
```

### JavaScriptでの使用例

```javascript
// 既存のエンドポイント
fetch('/api/system/health-check')
  .then(response => response.json())
  .then(data => console.log(data));

// バージョン付きエンドポイント
fetch('/api/v1/system/health-check')
  .then(response => response.json())
  .then(data => console.log(data));

// 認証が必要なエンドポイント
fetch('/api/v1/stock-master/stocks', {
  headers: {
    'X-API-Key': 'your-api-key'
  }
})
  .then(response => response.json())
  .then(data => console.log(data));
```

### Pythonでの使用例

```python
import requests


# 既存のエンドポイント
response = requests.get('http://localhost:8000/api/system/health-check')
print(response.json())

# バージョン付きエンドポイント
response = requests.get('http://localhost:8000/api/v1/system/health-check')
print(response.json())

# 認証が必要なエンドポイント
headers = {'X-API-Key': 'your-api-key'}
response = requests.get('http://localhost:8000/api/v1/stock-master/stocks', headers=headers)
print(response.json())
```

## レスポンス形式

バージョンに関係なく、レスポンス形式は同じです：

### 成功レスポンス

```json
{
  "status": "success",
  "data": {
    // レスポンスデータ
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### エラーレスポンス

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 認証

APIキー認証が必要なエンドポイントでは、バージョンに関係なく同じ認証方式を使用します：

```
X-API-Key: your-api-key
```

## エラーハンドリング

### 存在しないバージョン

存在しないバージョンを指定した場合、404エラーが返されます：

```bash
curl -X GET "http://localhost:8000/api/v999/system/health-check"
# 404 Not Found
```

### 存在しないエンドポイント

存在しないエンドポイントにアクセスした場合、404エラーが返されます：

```bash
curl -X GET "http://localhost:8000/api/v1/nonexistent"
# 404 Not Found
```

## 移行ガイド

### 既存のクライアントアプリケーション

既存のクライアントアプリケーションは変更なしで動作し続けます。バージョンなしのエンドポイントは引き続きサポートされます。

### 新しいクライアントアプリケーション

新しいクライアントアプリケーションでは、明示的にバージョンを指定することを推奨します：

```javascript
// 推奨
fetch('/api/v1/system/health-check')

// 非推奨（動作はするが、将来的に変更される可能性がある）
fetch('/api/system/health-check')
```

### 段階的移行

1. **Phase 1**: 既存のエンドポイントとバージョン付きエンドポイントの両方をサポート
2. **Phase 2**: 新機能はバージョン付きエンドポイントでのみ提供
3. **Phase 3**: 既存のエンドポイントの廃止予告
4. **Phase 4**: 既存のエンドポイントの廃止

## 設定

### アプリケーション設定

```python
# app.py
app.config['API_DEFAULT_VERSION'] = 'v1'
app.config['API_SUPPORTED_VERSIONS'] = ['v1']
```

### 新しいバージョンの追加

新しいバージョンを追加する場合：

1. `API_SUPPORTED_VERSIONS`に新しいバージョンを追加
2. 新しいバージョン用のBlueprintを作成
3. 必要に応じて`API_DEFAULT_VERSION`を更新

```python
app.config['API_DEFAULT_VERSION'] = 'v2'
app.config['API_SUPPORTED_VERSIONS'] = ['v1', 'v2']
```

## ベストプラクティス

### クライアント側

1. **明示的なバージョン指定**: 常にバージョンを明示的に指定する
2. **エラーハンドリング**: バージョン関連のエラーを適切に処理する
3. **バージョン管理**: 使用するAPIバージョンを設定で管理する

### サーバー側

1. **後方互換性**: 既存のバージョンの動作を変更しない
2. **段階的廃止**: 古いバージョンは段階的に廃止する
3. **ドキュメント更新**: バージョン変更時はドキュメントを更新する

## トラブルシューティング

### よくある問題

#### 404エラーが発生する

- URLパスが正しいか確認
- バージョン番号が正しいか確認
- エンドポイントが存在するか確認

#### 認証エラーが発生する

- APIキーが正しく設定されているか確認
- ヘッダー名が正しいか確認（`X-API-Key`）

#### レスポンスが期待と異なる

- 使用しているバージョンが正しいか確認
- APIドキュメントで仕様を確認

### デバッグ方法

1. **ログ確認**: アプリケーションログでリクエストの詳細を確認
2. **ネットワーク監視**: ブラウザの開発者ツールでリクエスト/レスポンスを確認
3. **テストツール**: Postmanやcurlでリクエストをテスト

## 今後の予定

### 予定されている機能

- **v2**: 新しいデータ形式のサポート
- **v3**: GraphQL APIの導入
- **認証方式の拡張**: OAuth2.0のサポート

### 廃止予定

現在のところ、廃止予定のバージョンはありません。v1は長期間サポートされる予定です。
