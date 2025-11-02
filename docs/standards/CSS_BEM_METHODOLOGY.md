# CSS BEM Methodology Implementation

## 概要

このドキュメントでは、STOCK-INVESTMENT-ANALYZERプロジェクトにおけるBEM（Block Element Modifier）命名規則の実装について説明します。

## BEM命名規則とは

BEMは以下の3つの要素から構成されるCSS命名規則です：

- **Block（ブロック）**: 独立したコンポーネント（例：`button`, `form`, `status`）
- **Element（要素）**: ブロック内の構成要素（例：`button__text`, `form__input`, `status__detail`）
- **Modifier（修飾子）**: ブロックや要素の状態や変種（例：`button--primary`, `status--error`）

### 命名パターン

```css
.block {}
.block__element {}
.block--modifier {}
.block__element--modifier {}
```

## 実装されたBEMクラス

### 1. ステータスコンポーネント

#### 旧クラス名
```css
.test-detail
.test-detail.error
```

#### 新BEMクラス名
```css
.status__detail
.status__detail--error
```

#### 使用例
```html
<!-- 正常状態 -->
<div class="status__detail">接続成功</div>

<!-- エラー状態 -->
<div class="status__detail status__detail--error">接続失敗</div>
```

### 2. ボタンコンポーネント

#### 旧クラス名
```css
.btn-danger
.btn-primary
.btn-secondary
```

#### 新BEMクラス名
```css
.btn--danger
.btn--primary
.btn--secondary
```

#### 使用例
```html
<button class="btn btn--danger">削除</button>
<button class="btn btn--primary">保存</button>
```

### 3. フォームコンポーネント

#### BEMクラス構造
```css
.form {}
.form__group {}
.form__label {}
.form__input {}
.form__input--error {}
.form__help-text {}
```

## JavaScript実装

動的なクラス操作もBEM命名規則に対応しています：

```javascript
// 旧実装
element.className = 'test-detail error';

// 新BEM実装
element.className = 'status__detail status__detail--error';
```

## ファイル構造

### 影響を受けたファイル

1. **CSS**
   - `app/static/style.css` - BEMクラス定義

2. **JavaScript**
   - `app/static/script.js` - 動的クラス操作

3. **HTMLテンプレート**
   - `app/templates/base.html`
   - `app/templates/index.html`
   - `app/templates/partials/header.html`
   - `app/templates/partials/footer.html`

## 利点

### 1. 保守性の向上
- クラス名から構造が明確に理解できる
- コンポーネント間の依存関係が明確

### 2. 再利用性の向上
- ブロック単位でのコンポーネント再利用が容易
- 修飾子による状態管理が統一

### 3. 命名衝突の回避
- 明確な命名規則により、クラス名の衝突を防止

## 開発ガイドライン

### 新しいコンポーネントの作成

1. **ブロックの定義**
   ```css
   .component-name {}
   ```

2. **要素の追加**
   ```css
   .component-name__element {}
   ```

3. **修飾子の追加**
   ```css
   .component-name--modifier {}
   .component-name__element--modifier {}
   ```

### 命名規則

- ブロック名：機能を表す名詞（例：`button`, `form`, `modal`）
- 要素名：ブロック内での役割（例：`title`, `content`, `icon`）
- 修飾子名：状態や変種（例：`active`, `disabled`, `large`）

## 移行状況

### 完了済み
- ✅ ステータス表示コンポーネント
- ✅ 基本ボタンコンポーネント
- ✅ システムモニタリング関連

### 今後の予定
- フォームコンポーネントの完全移行
- テーブルコンポーネントの移行
- モーダル・アラートコンポーネントの移行

## 参考資料

- [BEM公式ドキュメント](https://bem.info/)
- [CSS Guidelines](https://cssguidelin.es/#bem-like-naming)

## 更新履歴

- 2025-10-26: 初回実装（Issue #176対応）
  - ステータスコンポーネントのBEM化
  - 基本ボタンコンポーネントのBEM化
  - JavaScript動的クラス操作の対応
