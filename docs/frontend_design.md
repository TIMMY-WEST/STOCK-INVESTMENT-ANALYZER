# フロントエンド設計書

## 概要

株価データ取得システムのフロントエンド設計仕様書です。  
プロジェクトの設計理念（**動作優先・シンプル設計・後から拡張**）に基づき、最小限の機能から開始し、必要に応じて拡張していく方針です。

## 目次

- [フロントエンド設計書](#フロントエンド設計書)
  - [概要](#概要)
  - [目次](#目次)
  - [1. 基本方針](#1-基本方針)
    - [1.1 設計理念](#11-設計理念)
    - [1.2 開発アプローチ](#12-開発アプローチ)
  - [2. 技術スタック](#2-技術スタック)
    - [2.1 MVP段階の技術スタック](#21-mvp段階の技術スタック)
    - [2.2 将来検討する技術（必要になってから）](#22-将来検討する技術必要になってから)
  - [3. 画面構成とUI要素](#3-画面構成とui要素)
    - [3.1 MVP画面構成](#31-mvp画面構成)
    - [3.2 メインページ（/）](#32-メインページ)
      - [3.2.1 レイアウト構成](#321-レイアウト構成)
      - [3.2.2 UI要素詳細](#322-ui要素詳細)
        - [データ取得セクション](#データ取得セクション)
        - [データ表示セクション](#データ表示セクション)
        - [ステータス表示セクション](#ステータス表示セクション)
    - [3.3 レスポンシブ対応](#33-レスポンシブ対応)
  - [4. ユーザー操作フロー](#4-ユーザー操作フロー)
    - [4.1 基本操作フロー](#41-基本操作フロー)
    - [4.2 データ取得フロー](#42-データ取得フロー)
    - [4.3 データ表示フロー](#43-データ表示フロー)
    - [4.4 エラー処理フロー](#44-エラー処理フロー)
  - [5. 状態管理方式](#5-状態管理方式)
    - [5.1 MVP段階の状態管理](#51-mvp段階の状態管理)
    - [5.2 状態の種類](#52-状態の種類)
      - [5.2.1 アプリケーション状態](#521-アプリケーション状態)
      - [5.2.2 UI状態](#522-ui状態)
    - [5.3 状態管理パターン](#53-状態管理パターン)
  - [6. コンポーネント設計](#6-コンポーネント設計)
    - [6.1 HTMLテンプレート構造](#61-htmlテンプレート構造)
    - [6.2 CSS設計方針](#62-css設計方針)
      - [6.2.1 基本方針](#621-基本方針)
      - [6.2.2 色彩設計](#622-色彩設計)
      - [6.2.3 レイアウト設計](#623-レイアウト設計)
    - [6.3 JavaScript設計方針](#63-javascript設計方針)
  - [7. データ表示設計](#7-データ表示設計)
    - [7.1 株価データテーブル](#71-株価データテーブル)
    - [7.2 データフォーマット](#72-データフォーマット)
    - [7.3 ページネーション](#73-ページネーション)
  - [8. フォーム設計](#8-フォーム設計)
    - [8.1 データ取得フォーム](#81-データ取得フォーム)
    - [8.2 バリデーション](#82-バリデーション)
    - [8.3 エラー表示](#83-エラー表示)
  - [9. パフォーマンス考慮事項](#9-パフォーマンス考慮事項)
    - [9.1 MVP段階での方針](#91-mvp段階での方針)
    - [9.2 将来の最適化案](#92-将来の最適化案)
  - [10. 実装例](#10-実装例)
    - [10.1 HTMLテンプレート例](#101-htmlテンプレート例)
    - [10.2 CSS例](#102-css例)
    - [10.3 JavaScript例](#103-javascript例)
  - [11. 実装優先度](#11-実装優先度)
    - [11.1 優先度: 高（MVP必須）](#111-優先度-高mvp必須)
    - [11.2 優先度: 中（動作確認後）](#112-優先度-中動作確認後)
    - [11.3 優先度: 低（必要になってから）](#113-優先度-低必要になってから)
  - [12. 将来拡張計画](#12-将来拡張計画)
    - [12.1 UI改善案](#121-ui改善案)
    - [12.2 機能拡張案](#122-機能拡張案)
    - [12.3 技術的拡張案](#123-技術的拡張案)
  - [まとめ](#まとめ)

## 1. 基本方針

### 1.1 設計理念

- **動作優先**: まず動くUIを作る
- **シンプル設計**: 複雑なコンポーネント設計は避ける
- **後から拡張**: 必要になってからUI改善・機能追加

### 1.2 開発アプローチ

1. **最小限のHTML**: 基本的なフォームとテーブル表示
2. **段階的改善**: 動作確認後にスタイル改善
3. **ユーザビリティ重視**: 操作しやすさを優先

## 2. 技術スタック

### 2.1 MVP段階の技術スタック

| 技術 | 用途 | 理由 |
|------|------|------|
| **HTML5** | ページ構造 | 基本かつ確実 |
| **CSS3** | スタイリング | シンプルで十分 |
| **Vanilla JavaScript** | 基本的なインタラクション | 軽量、依存関係なし |
| **Flask Jinja2** | テンプレートエンジン | Flaskと統合済み |

### 2.2 将来検討する技術（必要になってから）

- **Alpine.js**: 軽量なJavaScriptフレームワーク
- **Tailwind CSS**: ユーティリティファーストCSS
- **Chart.js**: データ可視化
- **HTMX**: 動的なページ更新

## 3. 画面構成とUI要素

### 3.1 MVP画面構成

```
┌─────────────────────────────────────┐
│              Header                 │
│        株価データ取得システム          │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│          データ取得セクション          │
│  ┌─────────────┐  ┌──────────────┐    │
│  │ 銘柄コード    │  │ 取得ボタン     │    │
│  │ [7203.T  ]  │  │ [データ取得]   │    │
│  └─────────────┘  └──────────────┘    │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         ステータス表示セクション        │
│  📊 データ取得中... (50%)             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│          データ表示セクション          │
│ ┌─────────────────────────────────┐   │
│ │ 日付     │始値   │高値   │終値   │   │
│ │ 2024-09-09│2500 │2550  │2530  │   │
│ │ 2024-09-08│2480 │2520  │2500  │   │
│ └─────────────────────────────────┘   │
└─────────────────────────────────────┘
```

### 3.2 メインページ（/）

#### 3.2.1 レイアウト構成

- **ヘッダー**: アプリケーションタイトル
- **コントロールエリア**: データ取得フォーム
- **ステータスエリア**: 処理状況表示
- **データエリア**: 株価データテーブル

#### 3.2.2 UI要素詳細

##### データ取得セクション

```html
<section class="data-fetch-section">
  <h2>株価データ取得</h2>
  <form id="fetch-form">
    <div class="form-group">
      <label for="symbol">銘柄コード:</label>
      <input type="text" id="symbol" name="symbol" 
             placeholder="7203.T" value="7203.T">
      <small>例: 7203.T（トヨタ自動車）</small>
    </div>
    
    <div class="form-group">
      <label for="period">取得期間:</label>
      <select id="period" name="period">
        <option value="1mo" selected>1ヶ月</option>
        <option value="3mo">3ヶ月</option>
        <option value="1y">1年</option>
      </select>
    </div>
    
    <button type="submit" id="fetch-button" class="btn-primary">
      データ取得
    </button>
  </form>
</section>
```

##### データ表示セクション

```html
<section class="data-display-section">
  <h2>株価データ</h2>
  <div class="data-summary">
    <span class="symbol-info">銘柄: <strong id="current-symbol">-</strong></span>
    <span class="data-count">データ件数: <strong id="data-count">0</strong>件</span>
  </div>
  
  <div class="table-container">
    <table id="stock-table" class="stock-data-table">
      <thead>
        <tr>
          <th>日付</th>
          <th>始値</th>
          <th>高値</th>
          <th>安値</th>
          <th>終値</th>
          <th>出来高</th>
        </tr>
      </thead>
      <tbody id="stock-table-body">
        <!-- データが挿入されます -->
      </tbody>
    </table>
  </div>
</section>
```

##### ステータス表示セクション

```html
<section class="status-section" id="status-section" style="display: none;">
  <div class="status-message">
    <span class="status-icon">📊</span>
    <span id="status-text">待機中</span>
  </div>
  <div class="progress-bar" id="progress-bar" style="display: none;">
    <div class="progress-fill" id="progress-fill"></div>
  </div>
</section>
```

### 3.3 レスポンシブ対応

MVP段階では基本的なレスポンシブ対応のみ実装：

- **デスクトップ**: 標準レイアウト
- **タブレット**: テーブルの横スクロール対応
- **スマートフォン**: 必要最小限の調整

## 4. ユーザー操作フロー

### 4.1 基本操作フロー

```
ページ読み込み
    ↓
既存データ表示（あれば）
    ↓
銘柄コード入力
    ↓
取得期間選択（オプション）
    ↓
「データ取得」ボタンクリック
    ↓
データ取得処理実行
    ↓
結果表示・エラー処理
```

### 4.2 データ取得フロー

1. **フォーム入力**
   - 銘柄コード入力（必須）
   - 取得期間選択（デフォルト: 1ヶ月）

2. **送信処理**
   - フォームバリデーション
   - ローディング状態表示
   - API呼び出し

3. **結果処理**
   - 成功: データテーブル更新
   - エラー: エラーメッセージ表示

### 4.3 データ表示フロー

1. **初期表示**
   - ページ読み込み時に既存データを表示

2. **動的更新**
   - 新しいデータ取得後にテーブルを更新
   - ページネーション（将来実装）

3. **フィルタリング**
   - 銘柄別表示（将来実装）
   - 期間別表示（将来実装）

### 4.4 エラー処理フロー

1. **バリデーションエラー**
   - 入力フィールドのハイライト
   - インラインエラーメッセージ

2. **APIエラー**
   - ステータスセクションでエラー表示
   - 再試行ボタン表示

3. **ネットワークエラー**
   - 接続エラーメッセージ
   - 自動再試行（将来実装）

## 5. 状態管理方式

### 5.1 MVP段階の状態管理

**シンプルなDOMベースの状態管理**を採用：

- **状態の保存**: DOM要素の属性・テキスト
- **状態の更新**: JavaScript で直接DOM操作
- **永続化**: サーバーサイドで管理（セッションなし）

### 5.2 状態の種類

#### 5.2.1 アプリケーション状態

| 状態 | 格納場所 | 説明 |
|------|----------|------|
| `currentSymbol` | `#current-symbol` テキスト | 現在表示中の銘柄 |
| `dataCount` | `#data-count` テキスト | データ件数 |
| `stockData` | `#stock-table-body` HTML | 表示中の株価データ |

#### 5.2.2 UI状態

| 状態 | 格納場所 | 説明 |
|------|----------|------|
| `isLoading` | `#fetch-button` disabled属性 | データ取得中フラグ |
| `statusVisible` | `#status-section` display | ステータス表示状態 |
| `errorMessage` | `#status-text` テキスト | エラーメッセージ |

### 5.3 状態管理パターン

```javascript
// シンプルな状態管理例
const AppState = {
  // 状態更新
  updateSymbol: function(symbol) {
    document.getElementById('current-symbol').textContent = symbol;
  },
  
  updateDataCount: function(count) {
    document.getElementById('data-count').textContent = count;
  },
  
  showLoading: function() {
    document.getElementById('fetch-button').disabled = true;
    document.getElementById('status-section').style.display = 'block';
    document.getElementById('status-text').textContent = 'データ取得中...';
  },
  
  hideLoading: function() {
    document.getElementById('fetch-button').disabled = false;
    document.getElementById('status-section').style.display = 'none';
  }
};
```

## 6. コンポーネント設計

### 6.1 HTMLテンプレート構造

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>株価データ取得システム</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <header class="header">
    <h1>株価データ取得システム</h1>
  </header>
  
  <main class="main-container">
    <!-- データ取得セクション -->
    {% include 'components/fetch_form.html' %}
    
    <!-- ステータスセクション -->
    {% include 'components/status_display.html' %}
    
    <!-- データ表示セクション -->
    {% include 'components/data_table.html' %}
  </main>
  
  <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
```

### 6.2 CSS設計方針

#### 6.2.1 基本方針

- **BEM記法**: `.block__element--modifier`
- **モバイルファースト**: 基本スタイルはモバイル向け
- **シンプルなレイアウト**: Flexbox中心

#### 6.2.2 色彩設計

```css
:root {
  /* カラーパレット */
  --primary-color: #2563eb;      /* プライマリブルー */
  --success-color: #10b981;      /* 成功グリーン */
  --error-color: #ef4444;        /* エラーレッド */
  --warning-color: #f59e0b;      /* 警告オレンジ */
  
  /* 基本色 */
  --text-primary: #1f2937;       /* メインテキスト */
  --text-secondary: #6b7280;     /* サブテキスト */
  --background: #ffffff;         /* 背景色 */
  --border-color: #d1d5db;       /* ボーダー色 */
}
```

#### 6.2.3 レイアウト設計

```css
/* レスポンシブコンテナ */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

/* カード風デザイン */
.section-card {
  background: var(--background);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
```

### 6.3 JavaScript設計方針

**バニラJavaScript**でシンプルに実装：

```javascript
// アプリケーション初期化
document.addEventListener('DOMContentLoaded', function() {
  initApp();
});

function initApp() {
  // フォーム初期化
  initFetchForm();
  
  // 既存データ読み込み
  loadExistingData();
}
```

## 7. データ表示設計

### 7.1 株価データテーブル

| カラム | 表示名 | 幅 | データ型 | フォーマット |
|--------|--------|----|---------|-----------| 
| date | 日付 | 120px | Date | YYYY-MM-DD |
| open | 始値 | 80px | Number | #,##0.00 |
| high | 高値 | 80px | Number | #,##0.00 |
| low | 安値 | 80px | Number | #,##0.00 |
| close | 終値 | 80px | Number | #,##0.00 |
| volume | 出来高 | 120px | Number | #,##0 |

### 7.2 データフォーマット

```javascript
// データフォーマット関数
function formatPrice(price) {
  return new Intl.NumberFormat('ja-JP', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price);
}

function formatVolume(volume) {
  return new Intl.NumberFormat('ja-JP').format(volume);
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('ja-JP');
}
```

### 7.3 ページネーション

MVP段階では実装せず、将来的に以下を検討：

```html
<!-- 将来のページネーション例 -->
<div class="pagination">
  <button class="pagination__prev">前へ</button>
  <span class="pagination__info">1-30 / 100件</span>
  <button class="pagination__next">次へ</button>
</div>
```

## 8. フォーム設計

### 8.1 データ取得フォーム

```html
<form class="fetch-form" id="fetch-form">
  <div class="form-group">
    <label class="form-label" for="symbol">銘柄コード</label>
    <input 
      type="text" 
      id="symbol" 
      name="symbol" 
      class="form-input"
      placeholder="7203.T"
      pattern="[0-9]{4}\.T"
      required>
    <span class="form-help">例: 7203.T（トヨタ自動車）</span>
  </div>
  
  <div class="form-group">
    <label class="form-label" for="period">取得期間</label>
    <select id="period" name="period" class="form-select">
      <option value="1mo">1ヶ月</option>
      <option value="3mo">3ヶ月</option>
      <option value="1y">1年</option>
    </select>
  </div>
  
  <button type="submit" class="btn btn--primary">
    <span class="btn-text">データ取得</span>
    <span class="btn-loading" style="display: none;">取得中...</span>
  </button>
</form>
```

### 8.2 バリデーション

```javascript
function validateForm(formData) {
  const errors = {};
  
  // 銘柄コード検証
  const symbol = formData.get('symbol');
  if (!symbol) {
    errors.symbol = '銘柄コードは必須です';
  } else if (!symbol.match(/^[0-9]{4}\.T$/)) {
    errors.symbol = '正しい銘柄コード形式で入力してください（例: 7203.T）';
  }
  
  return errors;
}
```

### 8.3 エラー表示

```javascript
function showFieldError(fieldName, message) {
  const field = document.getElementById(fieldName);
  const errorElement = field.parentNode.querySelector('.field-error');
  
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
  
  field.classList.add('form-input--error');
}

function clearFieldErrors() {
  document.querySelectorAll('.field-error').forEach(el => {
    el.style.display = 'none';
  });
  
  document.querySelectorAll('.form-input--error').forEach(el => {
    el.classList.remove('form-input--error');
  });
}
```

## 9. パフォーマンス考慮事項

### 9.1 MVP段階での方針

- **最適化は後回し**: 基本動作を優先
- **軽量化**: 外部ライブラリの最小限使用
- **ブラウザサポート**: モダンブラウザに限定

### 9.2 将来の最適化案

- 画像の遅延読み込み
- JavaScriptの分割読み込み
- CSSの最適化
- キャッシュ戦略

## 10. 実装例

### 10.1 HTMLテンプレート例

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>株価データ取得システム</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
  <div class="app">
    <header class="app-header">
      <h1 class="app-title">株価データ取得システム</h1>
    </header>
    
    <main class="app-main">
      <!-- データ取得フォーム -->
      <section class="section-card">
        <h2 class="section-title">データ取得</h2>
        <form class="fetch-form" id="fetch-form">
          <div class="form-row">
            <div class="form-group">
              <label for="symbol" class="form-label">銘柄コード</label>
              <input 
                type="text" 
                id="symbol" 
                name="symbol" 
                class="form-input"
                placeholder="7203.T"
                value="{{ default_symbol or '7203.T' }}">
              <div class="field-error" style="display: none;"></div>
            </div>
            
            <div class="form-group">
              <label for="period" class="form-label">取得期間</label>
              <select id="period" name="period" class="form-select">
                <option value="1mo">1ヶ月</option>
                <option value="3mo">3ヶ月</option>
                <option value="1y">1年</option>
              </select>
            </div>
            
            <div class="form-group">
              <button type="submit" class="btn btn--primary" id="fetch-button">
                データ取得
              </button>
            </div>
          </div>
        </form>
      </section>
      
      <!-- ステータス表示 -->
      <section class="section-card status-section" id="status-section" style="display: none;">
        <div class="status-content">
          <span class="status-icon">📊</span>
          <span id="status-text">準備中...</span>
        </div>
      </section>
      
      <!-- データ表示 -->
      <section class="section-card">
        <div class="section-header">
          <h2 class="section-title">株価データ</h2>
          <div class="data-summary">
            <span class="data-info">銘柄: <strong id="current-symbol">{{ current_symbol or '-' }}</strong></span>
            <span class="data-info">データ件数: <strong id="data-count">{{ data_count or 0 }}</strong>件</span>
          </div>
        </div>
        
        <div class="table-container">
          <table class="data-table" id="stock-table">
            <thead>
              <tr>
                <th>日付</th>
                <th>始値</th>
                <th>高値</th>
                <th>安値</th>
                <th>終値</th>
                <th>出来高</th>
              </tr>
            </thead>
            <tbody id="stock-table-body">
              {% if stock_data %}
                {% for row in stock_data %}
                <tr>
                  <td>{{ row.date.strftime('%Y-%m-%d') }}</td>
                  <td class="text-right">{{ "%.2f"|format(row.open) }}</td>
                  <td class="text-right">{{ "%.2f"|format(row.high) }}</td>
                  <td class="text-right">{{ "%.2f"|format(row.low) }}</td>
                  <td class="text-right">{{ "%.2f"|format(row.close) }}</td>
                  <td class="text-right">{{ "{:,}".format(row.volume) }}</td>
                </tr>
                {% endfor %}
              {% else %}
                <tr>
                  <td colspan="6" class="text-center text-muted">
                    データがありません。銘柄コードを入力してデータを取得してください。
                  </td>
                </tr>
              {% endif %}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  </div>
  
  <script src="{{ url_for('static', filename='script.js') }}"></script>
</body>
</html>
```

### 10.2 CSS例

```css
/* static/style.css */

/* リセット & 基本設定 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --primary-color: #2563eb;
  --success-color: #10b981;
  --error-color: #ef4444;
  --text-primary: #1f2937;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --background: #ffffff;
  --background-secondary: #f9fafb;
  --border-color: #e5e7eb;
}

body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.5;
  color: var(--text-primary);
  background-color: var(--background-secondary);
}

/* レイアウト */
.app {
  min-height: 100vh;
}

.app-header {
  background: var(--background);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem;
}

.app-title {
  text-align: center;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* セクションカード */
.section-card {
  background: var(--background);
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.data-summary {
  display: flex;
  gap: 1rem;
}

.data-info {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

/* フォーム */
.fetch-form .form-row {
  display: flex;
  gap: 1rem;
  align-items: end;
}

.form-group {
  flex: 1;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 1rem;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: var(--primary-color);
}

.form-input--error {
  border-color: var(--error-color);
}

.field-error {
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: var(--error-color);
}

/* ボタン */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn--primary {
  background-color: var(--primary-color);
  color: white;
}

.btn--primary:hover {
  background-color: #1d4ed8;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ステータス表示 */
.status-section {
  background-color: #fef3c7;
  border-left: 4px solid var(--warning-color);
}

.status-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-icon {
  font-size: 1.25rem;
}

/* データテーブル */
.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  background-color: var(--background-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.text-muted {
  color: var(--text-muted);
}

/* レスポンシブ対応 */
@media (max-width: 768px) {
  .app-main {
    padding: 1rem 0.5rem;
  }
  
  .section-card {
    padding: 1rem;
  }
  
  .fetch-form .form-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .data-summary {
    margin-top: 0.5rem;
    flex-direction: column;
    gap: 0.25rem;
  }
}
```

### 10.3 JavaScript例

```javascript
// static/script.js

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', function() {
  initApp();
});

function initApp() {
  console.log('アプリケーションを初期化中...');
  
  // フォームイベントリスナー設定
  const fetchForm = document.getElementById('fetch-form');
  if (fetchForm) {
    fetchForm.addEventListener('submit', handleFetchSubmit);
  }
  
  // 初期データ読み込み
  loadExistingData();
}

// データ取得フォーム送信ハンドラ
async function handleFetchSubmit(event) {
  event.preventDefault();
  
  const formData = new FormData(event.target);
  const symbol = formData.get('symbol');
  const period = formData.get('period');
  
  // バリデーション
  const errors = validateForm(formData);
  if (Object.keys(errors).length > 0) {
    showValidationErrors(errors);
    return;
  }
  
  // バリデーションエラーをクリア
  clearFieldErrors();
  
  try {
    // ローディング状態開始
    showLoading();
    
    // APIリクエスト
    const response = await fetch('/api/fetch-data', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ symbol, period })
    });
    
    const result = await response.json();
    
    if (result.success) {
      showSuccess('データを取得しました');
      // データテーブル更新
      await loadStockData(symbol);
    } else {
      showError(result.message || 'データ取得に失敗しました');
    }
    
  } catch (error) {
    console.error('データ取得エラー:', error);
    showError('ネットワークエラーが発生しました');
  } finally {
    hideLoading();
  }
}

// フォームバリデーション
function validateForm(formData) {
  const errors = {};
  
  const symbol = formData.get('symbol');
  if (!symbol) {
    errors.symbol = '銘柄コードは必須です';
  } else if (!symbol.match(/^[0-9]{4}\.T$/)) {
    errors.symbol = '正しい銘柄コード形式で入力してください（例: 7203.T）';
  }
  
  return errors;
}

// バリデーションエラー表示
function showValidationErrors(errors) {
  Object.entries(errors).forEach(([field, message]) => {
    showFieldError(field, message);
  });
}

function showFieldError(fieldName, message) {
  const field = document.getElementById(fieldName);
  const errorElement = field.parentNode.querySelector('.field-error');
  
  if (errorElement) {
    errorElement.textContent = message;
    errorElement.style.display = 'block';
  }
  
  field.classList.add('form-input--error');
}

function clearFieldErrors() {
  document.querySelectorAll('.field-error').forEach(el => {
    el.style.display = 'none';
  });
  
  document.querySelectorAll('.form-input--error').forEach(el => {
    el.classList.remove('form-input--error');
  });
}

// ローディング状態管理
function showLoading() {
  const fetchButton = document.getElementById('fetch-button');
  const statusSection = document.getElementById('status-section');
  const statusText = document.getElementById('status-text');
  
  fetchButton.disabled = true;
  fetchButton.textContent = 'データ取得中...';
  
  statusSection.style.display = 'block';
  statusText.textContent = 'Yahoo Financeからデータを取得中...';
}

function hideLoading() {
  const fetchButton = document.getElementById('fetch-button');
  const statusSection = document.getElementById('status-section');
  
  fetchButton.disabled = false;
  fetchButton.textContent = 'データ取得';
  
  setTimeout(() => {
    statusSection.style.display = 'none';
  }, 2000);
}

// ステータス表示
function showSuccess(message) {
  const statusSection = document.getElementById('status-section');
  const statusText = document.getElementById('status-text');
  
  statusSection.style.display = 'block';
  statusSection.style.backgroundColor = '#dcfce7';
  statusSection.style.borderLeftColor = '#10b981';
  statusText.textContent = message;
}

function showError(message) {
  const statusSection = document.getElementById('status-section');
  const statusText = document.getElementById('status-text');
  
  statusSection.style.display = 'block';
  statusSection.style.backgroundColor = '#fee2e2';
  statusSection.style.borderLeftColor = '#ef4444';
  statusText.textContent = message;
}

// 株価データ読み込み
async function loadStockData(symbol = null) {
  try {
    const url = symbol ? `/api/stocks?symbol=${symbol}&limit=30` : '/api/stocks?limit=30';
    const response = await fetch(url);
    const result = await response.json();
    
    if (result.success) {
      updateDataTable(result.data, symbol);
      updateDataSummary(symbol, result.data.length);
    }
  } catch (error) {
    console.error('データ読み込みエラー:', error);
  }
}

// データテーブル更新
function updateDataTable(stockData, symbol) {
  const tableBody = document.getElementById('stock-table-body');
  
  if (stockData.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="6" class="text-center text-muted">
          データがありません。
        </td>
      </tr>
    `;
    return;
  }
  
  const rows = stockData.map(row => `
    <tr>
      <td>${formatDate(row.date)}</td>
      <td class="text-right">${formatPrice(row.open)}</td>
      <td class="text-right">${formatPrice(row.high)}</td>
      <td class="text-right">${formatPrice(row.low)}</td>
      <td class="text-right">${formatPrice(row.close)}</td>
      <td class="text-right">${formatVolume(row.volume)}</td>
    </tr>
  `).join('');
  
  tableBody.innerHTML = rows;
}

// データサマリー更新
function updateDataSummary(symbol, count) {
  const currentSymbolEl = document.getElementById('current-symbol');
  const dataCountEl = document.getElementById('data-count');
  
  if (currentSymbolEl && symbol) {
    currentSymbolEl.textContent = symbol;
  }
  
  if (dataCountEl) {
    dataCountEl.textContent = count;
  }
}

// 既存データ読み込み
function loadExistingData() {
  loadStockData();
}

// データフォーマット関数
function formatPrice(price) {
  return new Intl.NumberFormat('ja-JP', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price);
}

function formatVolume(volume) {
  return new Intl.NumberFormat('ja-JP').format(volume);
}

function formatDate(dateString) {
  const date = new Date(dateString + 'T00:00:00');
  return date.toLocaleDateString('ja-JP');
}
```

## 11. 実装優先度

### 11.1 優先度: 高（MVP必須）

- ✅ 基本HTMLレイアウト（ヘッダー、フォーム、テーブル）
- ✅ データ取得フォーム（銘柄コード、期間選択）
- ✅ 株価データテーブル表示
- ✅ 基本的なCSS（レイアウト、フォント、色）
- ✅ JavaScript（フォーム送信、データ表示）
- ✅ エラーハンドリング（基本的なもの）

### 11.2 優先度: 中（動作確認後）

- レスポンシブデザイン改善
- ローディングアニメーション
- より詳細なエラーメッセージ
- データフォーマット改善
- UIアニメーション

### 11.3 優先度: 低（必要になってから）

- ページネーション
- データソート機能
- データエクスポート機能
- チャート表示
- ダークモード
- PWA対応

## 12. 将来拡張計画

### 12.1 UI改善案

- **チャート表示**: Chart.jsで株価チャート
- **データ比較**: 複数銘柄の比較表示
- **フィルタリング**: 期間・銘柄での絞り込み
- **ソート機能**: カラムクリックでソート

### 12.2 機能拡張案

- **お気に入り**: よく使用する銘柄の保存
- **アラート**: 価格変動通知
- **自動更新**: リアルタイムデータ更新
- **データエクスポート**: CSV/Excel出力

### 12.3 技術的拡張案

- **Alpine.js導入**: より洗練された状態管理
- **Tailwind CSS**: ユーティリティファーストCSS
- **Progressive Web App**: オフライン対応
- **WebSocket**: リアルタイム通信

---

## まとめ

この設計書に基づいて、**動作優先・シンプル設計・後から拡張**の理念で以下を実現します：

### 🎯 **個人+AI開発での実装戦略**

1. **MVP段階**: HTML + CSS + バニラJSで基本機能
2. **改善段階**: UI/UX改善、エラーハンドリング強化  
3. **拡張段階**: 必要になった機能から順次追加

### ✅ **成功の指標**

- **3日以内**: 基本UIと株価データ表示が動作
- **1週間以内**: 完全なデータ取得・表示フローが完成
- **理解しやすいコード**: 後から改修・拡張が容易

このアプローチにより、**確実に動作するUI**を素早く構築し、**ユーザーのフィードバックに基づいて進化**させることができます。