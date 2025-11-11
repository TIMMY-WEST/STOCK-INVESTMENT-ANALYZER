---
category: task_tracking
type: issue_list
ai_context: critical
status: active
last_updated: 2025-01-09
related_docs:
  - ./refactoring/refactoring_plan.md
  - ../standards/git-workflow.md
---

# Issue管理

> **📋 ドキュメント種別**: Issue管理リスト
> **🎯 目的**: リファクタリング計画のIssue一覧と進捗管理
> **👥 対象読者**: 開発者、プロジェクトマネージャー
> **📅 最終更新**: 2025-01-09

---

## 📑 目次

- [Issue管理の方針](#issue管理の方針)
- [Phase 0: データアクセス層リファクタリング](#phase-0-データアクセス層リファクタリング)
- [Phase 1: サービス層リファクタリング](#phase-1-サービス層リファクタリング)
- [Phase 2: API層リファクタリング](#phase-2-api層リファクタリング)
- [Phase 3: プレゼンテーション層リファクタリング](#phase-3-プレゼンテーション層リファクタリング)
- [統合テスト・リリース](#統合テストリリース)
- [進捗サマリー](#進捗サマリー)

---

## Issue管理の方針

本Issueリストは [リファクタリング総合計画](./refactoring/refactoring_plan.md) に基づき、以下の方針で作成されています：

### 分割基準
- **1-3日で完了**: 各Issueは1-3日で完了できるサイズ
- **技術領域単位**: モデル分割、CRUD実装など明確な技術領域
- **テスト可能**: 各Issue完了時に動作確認が可能

### ラベル体系
- **Priority**: `priority:high`, `priority:medium`, `priority:low`
- **Type**: `feature`, `refactor`, `test`, `docs`
- **Layer**: `data-access`, `service`, `api`, `presentation`
- **Phase**: `phase-0`, `phase-1`, `phase-2`, `phase-3`

### Milestone
- `MS-R0: データアクセス層完了` (2025/3/23)
- `MS-R1: サービス層完了` (2025/4/27)
- `MS-R2: API層完了` (2025/5/11)
- `MS-R3: 全レイヤー完了` (2025/5/18)
- `MS-R4: 統合テスト完了` (2025/5/23)

---

## Phase 0: データアクセス層リファクタリング

**期間**: 2025/2/10 〜 2025/3/23（6週間）
**Milestone**: MS-R0
**詳細計画**: [data_access_layer_plan.md](./refactoring/data_access_layer_plan.md)

### Week 1: 型定義基盤の構築（2/10-2/16）

#### Issue #001: プロジェクト全体共通型定義の作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日

**実装内容**:
- `app/types.py` の作成
- 共通型の定義（`Interval`, `ProcessStatus`, `BatchStatus`, `PaginationParams`等）
- 型定義の配置戦略ドキュメント準拠確認

**完了条件**:
- [ ] `app/types.py` が作成され、以下の型が定義されている
  - `Interval` (Literal型)
  - `ProcessStatus` (Enum)
  - `BatchStatus` (Enum)
  - `PaginationParams` (TypedDict)
- [ ] mypyによる型チェックが通る
- [ ] 型定義配置戦略ドキュメントとの整合性確認

**PRレビュー重点観点**:
- [ ] 型定義が明確で一貫性があるか
- [ ] 命名規則が適切か
- [ ] 型定義配置戦略（`docs/architecture/type_definition_strategy.md`）に準拠しているか
- [ ] ドキュメンテーションが十分か

**テスト方法**:
- `mypy app/types.py` でエラーがないこと
- インポートテストの実施

**関連ドキュメント**:
- [型定義配置戦略](../architecture/type_definition_strategy.md)

---

#### Issue #002: モデル層固有型定義の作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #001

**実装内容**:
- `app/models/types.py` の作成
- モデル層固有型の定義（`ModelConfig`, `TablePrefix`, `CRUDResult`等）
- エラー型定義の整備

**完了条件**:
- [ ] `app/models/types.py` が作成され、以下の型が定義されている
  - `ModelConfig` (TypedDict)
  - `TablePrefix` (Literal型)
  - `CRUDResult` (Generic TypedDict)
- [ ] 既存の `app/types.py` から必要な型をインポート
- [ ] mypyによる型チェックが通る

**PRレビュー重点観点**:
- [ ] モデル層に必要な型が網羅されているか
- [ ] `app/types.py` との役割分担が明確か
- [ ] ジェネリック型の使い方が適切か
- [ ] データアクセス層仕様書（`docs/architecture/layers/data_access_layer.md`）と整合しているか

**テスト方法**:
- `mypy app/models/types.py` でエラーがないこと
- モデル層での型利用テスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #003: カスタム例外クラスの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #002

**実装内容**:
- `app/models/exceptions.py` の作成
- データアクセス層で使用する例外クラスの定義
- エラーハンドリング戦略の実装

**完了条件**:
- [ ] `app/models/exceptions.py` が作成され、以下の例外が定義されている
  - `ModelNotFoundError`
  - `DatabaseError`
  - `ValidationError`
  - `CRUDOperationError`
- [ ] 各例外クラスに適切なドキュメントが付与されている
- [ ] 例外の継承関係が適切に設計されている

**PRレビュー重点観点**:
- [ ] 例外の粒度が適切か
- [ ] エラーメッセージが分かりやすいか
- [ ] 例外の継承構造が適切か
- [ ] アーキテクチャ概要（`docs/architecture/architecture_overview.md`）のエラーハンドリング方針と整合しているか

**テスト方法**:
- 各例外クラスのインスタンス化テスト
- エラーメッセージの確認

**関連ドキュメント**:
- [アーキテクチャ概要](../architecture/architecture_overview.md)

---

### Week 2-3: モデルの分割（2/17-3/2）

#### Issue #004: ベースモデルとミックスインの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 2日
**Depends on**: #003

**実装内容**:
- `app/models/base.py` の作成（`BaseModel`クラス）
- `app/models/mixins.py` の作成（`TimestampMixin`, `SoftDeleteMixin`）
- 共通機能の抽出と実装

**完了条件**:
- [ ] `BaseModel` クラスが実装され、以下の機能を持つ
  - 共通カラム定義
  - 型ヒント完備
  - ドキュメント文字列
- [ ] `TimestampMixin` が実装され、`created_at`, `updated_at` を提供
- [ ] `SoftDeleteMixin` が実装され、論理削除機能を提供
- [ ] mypyによる型チェックが通る

**PRレビュー重点観点**:
- [ ] ミックスインの責務が明確か
- [ ] 型ヒントが適切に付与されているか
- [ ] 再利用性が高い設計になっているか
- [ ] SQLAlchemyのベストプラクティスに従っているか
- [ ] データアクセス層仕様書と整合しているか

**テスト方法**:
- ベースモデルのインスタンス化テスト
- ミックスインの機能テスト（タイムスタンプ、論理削除）

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #005: 株価データモデルの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 2日
**Depends on**: #004

**実装内容**:
- `app/models/stock_data.py` の作成
- 株価データ関連モデルの実装（`StockPrice1d`, `StockPrice1wk`, `StockPrice1mo`, `StockPrice1m`等）
- 既存 `models.py` からの移行

**完了条件**:
- [ ] `stock_data.py` に以下のモデルが実装されている
  - `StockPrice1d`
  - `StockPrice1wk`
  - `StockPrice1mo`
  - `StockPrice1m`
- [ ] 各モデルに型ヒントとドキュメントが付与されている
- [ ] `BaseModel` と `TimestampMixin` を継承
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] モデル設計が適切か（カラム定義、制約）
- [ ] インデックス設計が適切か
- [ ] 型ヒントが完全か
- [ ] 既存の `models.py` の該当部分が適切に移行されているか
- [ ] パフォーマンスへの影響がないか

**テスト方法**:
- モデルのCRUD操作テスト
- 既存機能のリグレッションテスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #006: マスターデータモデルの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #004

**実装内容**:
- `app/models/master.py` の作成
- マスターデータモデルの実装（`StockMaster`, `SymbolMapping`等）

**完了条件**:
- [ ] `master.py` に以下のモデルが実装されている
  - `StockMaster`
  - `SymbolMapping`
- [ ] 各モデルに型ヒントとドキュメントが付与されている
- [ ] `BaseModel` と `TimestampMixin` を継承
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] マスターデータの設計が適切か
- [ ] 一意性制約が適切に設定されているか
- [ ] 型ヒントが完全か
- [ ] データアクセス層仕様書と整合しているか

**テスト方法**:
- マスターデータのCRUD操作テスト
- 一意性制約のテスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #007: バッチ処理モデルの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #004

**実装内容**:
- `app/models/batch.py` の作成
- バッチ処理モデルの実装（`BatchJob`, `BatchExecutionHistory`等）

**完了条件**:
- [ ] `batch.py` に以下のモデルが実装されている
  - `BatchJob`
  - `BatchExecutionHistory`
- [ ] ステータス管理が適切に実装されている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] バッチジョブのステータス管理が適切か
- [ ] 履歴管理の設計が適切か
- [ ] 型ヒントが完全か

**テスト方法**:
- バッチジョブの作成・更新テスト
- 履歴記録のテスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #008: セッション管理モデルの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #004

**実装内容**:
- `app/models/session.py` の作成
- データベースセッション管理ユーティリティの実装

**完了条件**:
- [ ] `session.py` にセッション管理機能が実装されている
  - `get_db_session()` 関数
  - コンテキストマネージャー
- [ ] トランザクション管理が適切に実装されている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] セッション管理が安全か（リソースリーク防止）
- [ ] トランザクション境界が適切か
- [ ] 型ヒントが完全か

**テスト方法**:
- セッション取得・解放のテスト
- トランザクションのロールバックテスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

### Week 4-5: CRUD操作の汎用化（3/3-3/16）

#### Issue #009: 汎用CRUDベースクラスの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 2日
**Depends on**: #008

**実装内容**:
- `app/models/crud/base.py` の作成
- 汎用CRUDベースクラス `BaseCRUD` の実装
- ジェネリック型を活用した型安全な実装

**完了条件**:
- [ ] `BaseCRUD[T]` クラスが実装され、以下のメソッドを提供
  - `get(id)` - 単一レコード取得
  - `get_multi(skip, limit)` - 複数レコード取得
  - `create(obj)` - 新規作成
  - `update(id, obj)` - 更新
  - `delete(id)` - 削除
- [ ] すべてのメソッドに型ヒントとドキュメントが付与されている
- [ ] エラーハンドリングが適切に実装されている
- [ ] mypyによる型チェックが通る

**PRレビュー重点観点**:
- [ ] ジェネリック型の使い方が適切か
- [ ] CRUD操作の実装が安全か（SQLインジェクション対策等）
- [ ] エラーハンドリングが適切か
- [ ] 型安全性が保たれているか
- [ ] データアクセス層仕様書と整合しているか

**テスト方法**:
- 各CRUD操作の単体テスト
- エラーケースのテスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #010: 株価データ専用CRUDクラスの作成
**Labels**: `feature`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 2日
**Depends on**: #009

**実装内容**:
- `app/models/crud/stock.py` の作成
- 株価データ専用CRUDクラスの実装（各interval向け）
- 高度な検索機能の実装

**完了条件**:
- [ ] 以下のCRUDクラスが実装されている
  - `StockPrice1dCRUD`
  - `StockPrice1wkCRUD`
  - `StockPrice1moCRUD`
  - `StockPrice1mCRUD`
- [ ] 各クラスに以下のメソッドが実装されている
  - `get_by_symbol_and_date(symbol, date)` - シンボルと日付で取得
  - `get_by_symbol_range(symbol, start, end)` - 期間指定取得
  - `bulk_insert(records)` - 一括挿入
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] 株価データ特有の検索機能が適切に実装されているか
- [ ] 一括挿入のパフォーマンスが最適化されているか
- [ ] インデックスが効果的に利用されているか
- [ ] 既存機能との互換性が保たれているか

**テスト方法**:
- 各検索メソッドの単体テスト
- 一括挿入のパフォーマンステスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #011: マスターデータ・バッチ処理CRUD実装
**Labels**: `feature`, `data-access`, `phase-0`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #009

**実装内容**:
- マスターデータCRUDクラスの実装
- バッチ処理CRUDクラスの実装

**完了条件**:
- [ ] `StockMasterCRUD` が実装されている
- [ ] `BatchJobCRUD` が実装されている
- [ ] 各クラスに必要なメソッドが実装されている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] マスターデータの検索・更新が適切か
- [ ] バッチジョブの管理が適切か
- [ ] 型ヒントが完全か

**テスト方法**:
- CRUD操作の単体テスト

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

### Week 6: 既存コード更新とテスト（3/17-3/23）

#### Issue #012: 既存コードの型ヒント追加とリファクタリング
**Labels**: `refactor`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 2日
**Depends on**: #011

**実装内容**:
- 既存コードへの型ヒント追加
- 新しいCRUDクラスへの移行
- `models.py` の段階的廃止

**完了条件**:
- [ ] 主要な既存関数・クラスに型ヒントが追加されている
- [ ] 既存コードが新しいCRUDクラスを利用するように更新されている
- [ ] `models.py` の使用箇所が減少している
- [ ] mypyによる型チェックが通る（カバレッジ95%以上）
- [ ] 既存テストがすべて通る

**PRレビュー重点観点**:
- [ ] 型ヒントが正確か
- [ ] リファクタリングによる動作変更がないか
- [ ] 既存機能との互換性が保たれているか
- [ ] パフォーマンスへの影響がないか

**テスト方法**:
- 全テストの実行
- 型カバレッジの確認

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

#### Issue #013: データアクセス層統合テストとドキュメント整備
**Labels**: `test`, `docs`, `data-access`, `phase-0`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R0
**Estimated**: 1日
**Depends on**: #012

**実装内容**:
- 統合テストの作成
- ドキュメントの更新
- `models.py` の完全廃止確認

**完了条件**:
- [ ] データアクセス層の統合テストが作成され、通過している
- [ ] テストカバレッジが80%以上
- [ ] `models.py` が完全に廃止されている
- [ ] ドキュメントが最新の実装に合わせて更新されている
- [ ] マイグレーションガイドが作成されている

**PRレビュー重点観点**:
- [ ] 統合テストが包括的か
- [ ] ドキュメントが分かりやすいか
- [ ] `models.py` が完全に削除されているか
- [ ] マイグレーションガイドが実用的か

**テスト方法**:
- 全統合テストの実行
- カバレッジレポートの確認
- ドキュメントの査読

**関連ドキュメント**:
- [データアクセス層仕様書](../architecture/layers/data_access_layer.md)

---

## Phase 1: サービス層リファクタリング

**期間**: 2025/3/24 〜 2025/4/27（5週間）
**Milestone**: MS-R1
**詳細計画**: [service_layer_plan.md](./refactoring/service_layer_plan.md)

### Week 1: 依存性注入の導入（3/24-3/30）

#### Issue #014: サービス層への依存性注入（DI）導入
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 2日

**実装内容**:
- 主要サービスクラスへのDIパターン導入
- コンストラクタインジェクションの実装
- テスタビリティの向上

**完了条件**:
- [ ] `StockDataFetcher`, `StockDataSaver` にDIが導入されている
- [ ] コンストラクタで依存オブジェクトを受け取れる
- [ ] デフォルト値により既存コードとの互換性が保たれている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] DIパターンの実装が適切か
- [ ] 既存コードへの影響が最小限か
- [ ] テスト時のモック作成が容易になっているか
- [ ] サービス層仕様書（`docs/architecture/layers/service_layer.md`）と整合しているか

**テスト方法**:
- DIを利用したモックテスト
- 既存機能のリグレッションテスト

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)
- [アーキテクチャ概要](../architecture/architecture_overview.md)

---

#### Issue #015: サービス層のユニットテスト拡充
**Labels**: `test`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日
**Depends on**: #014

**実装内容**:
- DIを活用したユニットテストの作成
- モックオブジェクトを使用したテスト
- カバレッジの向上

**完了条件**:
- [ ] 各サービスクラスのユニットテストが作成されている
- [ ] モックを使用した独立したテストになっている
- [ ] テストカバレッジが70%以上
- [ ] すべてのテストが通る

**PRレビュー重点観点**:
- [ ] テストが網羅的か
- [ ] モックの使い方が適切か
- [ ] エッジケースがカバーされているか

**テスト方法**:
- `pytest` による全テスト実行
- カバレッジレポート確認

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

### Week 2: 型定義の追加（3/31-4/6）

#### Issue #016: サービス層固有型定義の作成
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日

**実装内容**:
- `app/services/types.py` の作成
- サービス層固有型の定義（`ServiceResult`, `FetchResult`, `SaveResult`等）

**完了条件**:
- [ ] `app/services/types.py` が作成され、以下の型が定義されている
  - `ServiceResult[T]` (Generic型)
  - `FetchResult` (TypedDict)
  - `SaveResult` (TypedDict)
  - `BulkFetchOptions` (TypedDict)
- [ ] 各型にドキュメントが付与されている
- [ ] mypyによる型チェックが通る

**PRレビュー重点観点**:
- [ ] 型定義が明確で使いやすいか
- [ ] ジェネリック型の使い方が適切か
- [ ] 型定義配置戦略に準拠しているか
- [ ] サービス層仕様書と整合しているか

**テスト方法**:
- 型チェックの実行
- 実際のサービスクラスでの利用確認

**関連ドキュメント**:
- [型定義配置戦略](../architecture/type_definition_strategy.md)
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #017: 既存サービスクラスへの型ヒント追加
**Labels**: `refactor`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日
**Depends on**: #016

**実装内容**:
- 既存サービスクラスへの型ヒント追加
- 型定義の活用
- 型カバレッジの向上

**完了条件**:
- [ ] 主要サービスクラスに型ヒントが追加されている
  - `StockDataFetcher`
  - `StockDataSaver`
  - `StockDataOrchestrator`
  - `BulkDataService`（一部）
- [ ] mypyによる型チェックが通る（カバレッジ90%以上）
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] 型ヒントが正確で完全か
- [ ] 戻り値の型が明確か
- [ ] 既存の動作に影響がないか

**テスト方法**:
- `mypy` による型チェック
- 全テストの実行

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

### Week 3-4: BulkDataServiceの分割（4/7-4/20）

#### Issue #018: BulkDataService分割計画の策定と準備
**Labels**: `refactor`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1日

**実装内容**:
- BulkDataService（910行）の分析
- 責務の特定と分割計画の策定
- インターフェース設計

**完了条件**:
- [ ] 分割計画ドキュメントが作成されている
- [ ] 4つのクラスへの分割方針が明確
  - `BulkFetchOrchestrator` - 全体オーケストレーション
  - `SymbolResolver` - シンボル解決
  - `DataFetchCoordinator` - データ取得調整
  - `BatchProgressTracker` - 進捗管理
- [ ] インターフェース設計が完了している

**PRレビュー重点観点**:
- [ ] 分割方針が適切か
- [ ] 責務の分離が明確か
- [ ] インターフェース設計が実用的か

**テスト方法**:
- 計画ドキュメントのレビュー

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #019: SymbolResolverクラスの実装
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日
**Depends on**: #018

**実装内容**:
- `app/services/bulk/symbol_resolver.py` の作成
- シンボル解決ロジックの実装
- JPXデータ取得機能の移行

**完了条件**:
- [ ] `SymbolResolver` クラスが実装されている
- [ ] 以下のメソッドが実装されている
  - `resolve_symbols(options)` - シンボル解決
  - `get_jpx_symbols(limit, offset)` - JPXシンボル取得
- [ ] 型ヒント完備
- [ ] ユニットテスト作成
- [ ] 既存機能との互換性確認

**PRレビュー重点観点**:
- [ ] シンボル解決ロジックが正確か
- [ ] エラーハンドリングが適切か
- [ ] 型安全性が保たれているか

**テスト方法**:
- ユニットテストの実行
- シンボル解決の動作確認

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #020: DataFetchCoordinatorクラスの実装
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 2日
**Depends on**: #019

**実装内容**:
- `app/services/bulk/data_fetch_coordinator.py` の作成
- データ取得調整ロジックの実装
- 並列処理・リトライ機能の実装

**完了条件**:
- [ ] `DataFetchCoordinator` クラスが実装されている
- [ ] 以下のメソッドが実装されている
  - `fetch_data(symbols, options)` - データ取得調整
  - `handle_retry(symbol, error)` - リトライ処理
- [ ] 並列処理が適切に実装されている
- [ ] ユニットテスト作成
- [ ] 既存機能との互換性確認

**PRレビュー重点観点**:
- [ ] 並列処理が安全か（スレッドセーフ）
- [ ] リトライロジックが適切か
- [ ] パフォーマンスが維持されているか

**テスト方法**:
- 並列処理のテスト
- リトライ機能のテスト
- パフォーマンステスト

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #021: BatchProgressTrackerクラスの実装
**Labels**: `feature`, `service`, `phase-1`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1日
**Depends on**: #018

**実装内容**:
- `app/services/bulk/progress_tracker.py` の作成
- 進捗管理ロジックの実装
- リアルタイム進捗通知機能

**完了条件**:
- [ ] `BatchProgressTracker` クラスが実装されている
- [ ] 以下のメソッドが実装されている
  - `update_progress(completed, total)` - 進捗更新
  - `get_progress()` - 進捗取得
  - `notify_completion()` - 完了通知
- [ ] ユニットテスト作成

**PRレビュー重点観点**:
- [ ] 進捗管理が正確か
- [ ] 通知機能が適切に動作するか
- [ ] スレッドセーフか

**テスト方法**:
- 進捗管理のテスト
- 通知機能のテスト

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #022: BulkFetchOrchestratorクラスの実装と統合
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 2日
**Depends on**: #019, #020, #021

**実装内容**:
- `app/services/bulk/orchestrator.py` の作成
- 各コンポーネントの統合
- 既存BulkDataServiceとの互換性確保

**完了条件**:
- [ ] `BulkFetchOrchestrator` クラスが実装されている
- [ ] 各コンポーネント（SymbolResolver、DataFetchCoordinator、BatchProgressTracker）が統合されている
- [ ] 既存の `BulkDataService` のインターフェースと互換性がある
- [ ] ユニットテスト・統合テスト作成
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] 統合が適切に行われているか
- [ ] 既存機能との互換性が保たれているか
- [ ] エラーハンドリングが一貫しているか
- [ ] パフォーマンスが維持されているか

**テスト方法**:
- 統合テストの実行
- 既存機能のリグレッションテスト
- パフォーマンステスト

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

### Week 5: エラーハンドリング統一（4/21-4/27）

#### Issue #023: エラーハンドリングデコレータの作成
**Labels**: `feature`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日

**実装内容**:
- `app/utils/decorators.py` の作成
- 共通エラーハンドリングデコレータの実装
- リトライデコレータの実装

**完了条件**:
- [ ] 以下のデコレータが実装されている
  - `@handle_service_error` - サービス層エラーハンドリング
  - `@retry_on_error` - リトライ機能
  - `@log_execution_time` - 実行時間ロギング
- [ ] 各デコレータにドキュメントと型ヒントが付与されている
- [ ] ユニットテスト作成

**PRレビュー重点観点**:
- [ ] デコレータの実装が適切か
- [ ] エラーメッセージが分かりやすいか
- [ ] ロギングが適切に行われているか

**テスト方法**:
- デコレータのユニットテスト
- 各種エラーケースのテスト

**関連ドキュメント**:
- [アーキテクチャ概要](../architecture/architecture_overview.md)

---

#### Issue #024: サービス層へのエラーハンドリングデコレータ適用
**Labels**: `refactor`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日
**Depends on**: #023

**実装内容**:
- 既存サービスクラスへのデコレータ適用
- 一貫したエラーハンドリングの実現
- 既存の例外処理の整理

**完了条件**:
- [ ] 主要サービスクラスにデコレータが適用されている
- [ ] エラーハンドリングが一貫している
- [ ] 既存の重複したエラーハンドリングコードが削除されている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] デコレータの適用が適切か
- [ ] エラーハンドリングの一貫性が保たれているか
- [ ] 既存の動作が維持されているか

**テスト方法**:
- 全テストの実行
- エラーケースのテスト

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

#### Issue #025: サービス層統合テストとドキュメント整備
**Labels**: `test`, `docs`, `service`, `phase-1`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R1
**Estimated**: 1-2日
**Depends on**: #024

**実装内容**:
- サービス層の統合テスト作成
- ドキュメントの更新
- マイグレーションガイドの作成

**完了条件**:
- [ ] サービス層の統合テストが作成され、通過している
- [ ] テストカバレッジが80%以上
- [ ] `BulkDataService` の旧実装が廃止されている
- [ ] ドキュメントが最新の実装に合わせて更新されている
- [ ] マイグレーションガイドが作成されている

**PRレビュー重点観点**:
- [ ] 統合テストが包括的か
- [ ] ドキュメントが分かりやすいか
- [ ] マイグレーションガイドが実用的か

**テスト方法**:
- 全統合テストの実行
- カバレッジレポートの確認
- ドキュメントの査読

**関連ドキュメント**:
- [サービス層仕様書](../architecture/layers/service_layer.md)

---

## Phase 2: API層リファクタリング

**期間**: 2025/4/28 〜 2025/5/11（2週間）
**Milestone**: MS-R2
**詳細計画**: [api_layer_plan.md](./refactoring/api_layer_plan.md)

### Week 1: 基盤整備と型定義（4/28-5/4）

#### Issue #026: API層固有型定義の作成
**Labels**: `feature`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 1日

**実装内容**:
- `app/api/types.py` の作成
- API層固有型の定義（`APIResponse`, `BulkFetchRequest`, `ErrorResponse`等）

**完了条件**:
- [ ] `app/api/types.py` が作成され、以下の型が定義されている
  - `APIResponse[T]` (Generic型)
  - `BulkFetchRequest` (TypedDict)
  - `ErrorResponse` (TypedDict)
  - `PaginatedResponse[T]` (Generic型)
- [ ] 各型にドキュメントが付与されている
- [ ] mypyによる型チェックが通る

**PRレビュー重点観点**:
- [ ] API仕様に適した型定義になっているか
- [ ] レスポンス型の一貫性が保たれているか
- [ ] 型定義配置戦略に準拠しているか
- [ ] API層仕様書（`docs/architecture/layers/api_layer.md`）と整合しているか

**テスト方法**:
- 型チェックの実行
- 実際のAPIエンドポイントでの利用確認

**関連ドキュメント**:
- [型定義配置戦略](../architecture/type_definition_strategy.md)
- [API層仕様書](../architecture/layers/api_layer.md)

---

#### Issue #027: API共通ユーティリティの作成
**Labels**: `feature`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 1-2日

**実装内容**:
- `app/api/utils/` ディレクトリの作成
- 共通レスポンス生成関数の実装
- エラーレスポンス生成関数の実装

**完了条件**:
- [ ] `app/api/utils/response.py` が作成され、以下の関数が実装されている
  - `success_response(data, message)` - 成功レスポンス生成
  - `error_response(error, status_code)` - エラーレスポンス生成
  - `paginated_response(items, total, page, per_page)` - ページネーションレスポンス生成
- [ ] 型ヒント完備
- [ ] ユニットテスト作成

**PRレビュー重点観点**:
- [ ] レスポンス形式が一貫しているか
- [ ] エラーメッセージが分かりやすいか
- [ ] 型安全性が保たれているか

**テスト方法**:
- ユニットテストの実行
- 各種レスポンス生成の確認

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

#### Issue #028: APIバリデーション機能の統一
**Labels**: `feature`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 1-2日

**実装内容**:
- `app/api/validators/` ディレクトリの作成
- 共通バリデーション関数の実装
- リクエストスキーマの定義

**完了条件**:
- [ ] `app/api/validators/common.py` が作成され、以下の関数が実装されている
  - `validate_symbol(symbol)` - シンボル検証
  - `validate_date_range(start, end)` - 日付範囲検証
  - `validate_interval(interval)` - インターバル検証
  - `validate_pagination(page, per_page)` - ページネーション検証
- [ ] 型ヒント完備
- [ ] ユニットテスト作成

**PRレビュー重点観点**:
- [ ] バリデーションロジックが適切か
- [ ] エラーメッセージが分かりやすいか
- [ ] セキュリティ面での問題がないか（インジェクション対策等）

**テスト方法**:
- ユニットテストの実行
- 各種バリデーションケースの確認

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

### Week 2: 構造改善（5/5-5/11）

#### Issue #029: ジョブ管理機能の分離
**Labels**: `feature`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 2日

**実装内容**:
- `app/api/jobs/` ディレクトリの作成
- ジョブ管理ロジックの `bulk_data.py` からの分離
- ジョブステータス管理の実装

**完了条件**:
- [ ] `app/api/jobs/manager.py` が作成され、以下の機能が実装されている
  - `create_job(job_config)` - ジョブ作成
  - `get_job_status(job_id)` - ジョブステータス取得
  - `update_job_progress(job_id, progress)` - 進捗更新
  - `complete_job(job_id, result)` - ジョブ完了
- [ ] 型ヒント完備
- [ ] ユニットテスト作成
- [ ] `bulk_data.py` からジョブ管理ロジックが削除されている

**PRレビュー重点観点**:
- [ ] ジョブ管理が適切に分離されているか
- [ ] ステータス管理が正確か
- [ ] 既存機能との互換性が保たれているか
- [ ] `bulk_data.py` の行数が削減されているか

**テスト方法**:
- ジョブ管理のユニットテスト
- 既存機能のリグレッションテスト

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

#### Issue #030: bulk_data.pyのリファクタリングと型ヒント追加
**Labels**: `refactor`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 2日
**Depends on**: #029

**実装内容**:
- `bulk_data.py` の残りロジックへの型ヒント追加
- 共通ユーティリティ・バリデーターの活用
- コードの整理と最適化

**完了条件**:
- [ ] `bulk_data.py` の全関数に型ヒントが追加されている
- [ ] 共通レスポンス生成関数が使用されている
- [ ] 共通バリデーション関数が使用されている
- [ ] `bulk_data.py` の行数が450行以下（70%削減）
- [ ] mypyによる型チェックが通る
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] 型ヒントが正確で完全か
- [ ] 共通ユーティリティが適切に活用されているか
- [ ] コードの可読性が向上しているか
- [ ] パフォーマンスへの影響がないか

**テスト方法**:
- `mypy` による型チェック
- 全テストの実行
- API動作確認

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

#### Issue #031: その他APIエンドポイントのリファクタリング
**Labels**: `refactor`, `api`, `phase-2`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 1-2日

**実装内容**:
- その他のAPIファイル（`stock_master.py`, `system_monitoring.py`等）へのリファクタリング適用
- 型ヒント追加
- 共通ユーティリティの活用

**完了条件**:
- [ ] 主要APIファイルに型ヒントが追加されている
- [ ] 共通レスポンス生成関数が使用されている
- [ ] 共通バリデーション関数が使用されている
- [ ] mypyによる型チェックが通る
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] 一貫性のあるAPI設計になっているか
- [ ] 型安全性が保たれているか
- [ ] 既存機能への影響がないか

**テスト方法**:
- 型チェックの実行
- 全テストの実行
- API動作確認

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

#### Issue #032: API層統合テストとドキュメント整備
**Labels**: `test`, `docs`, `api`, `phase-2`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R2
**Estimated**: 1日
**Depends on**: #030, #031

**実装内容**:
- API層の統合テスト作成
- OpenAPIドキュメントの更新
- マイグレーションガイドの作成

**完了条件**:
- [ ] API層の統合テストが作成され、通過している
- [ ] テストカバレッジが75%以上
- [ ] OpenAPI仕様書が最新の実装に合わせて更新されている
- [ ] マイグレーションガイドが作成されている

**PRレビュー重点観点**:
- [ ] 統合テストが包括的か
- [ ] OpenAPI仕様書が正確か
- [ ] マイグレーションガイドが実用的か

**テスト方法**:
- 全統合テストの実行
- カバレッジレポートの確認
- OpenAPI仕様書の検証

**関連ドキュメント**:
- [API層仕様書](../architecture/layers/api_layer.md)

---

## Phase 3: プレゼンテーション層リファクタリング

**期間**: 2025/5/12 〜 2025/5/18（1週間）
**Milestone**: MS-R3
**詳細計画**: [presentation_layer_plan.md](./refactoring/presentation_layer_plan.md)

### Week 1: Application Factory実装（5/12-5/18）

#### Issue #033: Application Factory パターンの実装
**Labels**: `feature`, `presentation`, `phase-3`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R3
**Estimated**: 2日

**実装内容**:
- `app/factory.py` の作成
- `create_app()` 関数の実装
- 環境別設定の分離

**完了条件**:
- [ ] `app/factory.py` が作成され、`create_app(config_name)` 関数が実装されている
- [ ] 以下の環境設定がサポートされている
  - `development`
  - `testing`
  - `production`
- [ ] 拡張機能の初期化が `create_app()` 内で行われている
- [ ] 型ヒント完備
- [ ] ユニットテスト作成

**PRレビュー重点観点**:
- [ ] Application Factoryパターンが適切に実装されているか
- [ ] 環境別設定の分離が明確か
- [ ] 拡張機能の初期化が適切か
- [ ] プレゼンテーション層仕様書（`docs/architecture/layers/presentation_layer.md`）と整合しているか

**テスト方法**:
- 各環境での `create_app()` テスト
- 拡張機能の初期化確認

**関連ドキュメント**:
- [プレゼンテーション層仕様書](../architecture/layers/presentation_layer.md)
- [アーキテクチャ概要](../architecture/architecture_overview.md)

---

#### Issue #034: 環境別設定ファイルの作成
**Labels**: `feature`, `presentation`, `phase-3`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R3
**Estimated**: 1日

**実装内容**:
- `app/config/` ディレクトリの作成
- 環境別設定クラスの実装

**完了条件**:
- [ ] `app/config/base.py` が作成され、基本設定クラスが実装されている
- [ ] `app/config/development.py` が作成されている
- [ ] `app/config/testing.py` が作成されている
- [ ] `app/config/production.py` が作成されている
- [ ] 型ヒント完備
- [ ] 設定値のバリデーション実装

**PRレビュー重点観点**:
- [ ] 設定値が適切に分離されているか
- [ ] セキュリティ面での問題がないか（シークレット管理等）
- [ ] デフォルト値が適切か

**テスト方法**:
- 各設定クラスのロードテスト
- 設定値のバリデーションテスト

**関連ドキュメント**:
- [プレゼンテーション層仕様書](../architecture/layers/presentation_layer.md)

---

#### Issue #035: ルート分離とBlueprint化
**Labels**: `refactor`, `presentation`, `phase-3`, `priority:medium`
**Assignee**: 開発者
**Milestone**: MS-R3
**Estimated**: 1-2日
**Depends on**: #033

**実装内容**:
- `app/routes/` ディレクトリの作成
- 各APIエンドポイントのBlueprint化
- `app.py` のシンプル化

**完了条件**:
- [ ] `app/routes/` ディレクトリが作成されている
- [ ] 以下のBlueprintが作成されている
  - `app/routes/stock.py` - 株価データAPI
  - `app/routes/bulk.py` - 一括取得API
  - `app/routes/master.py` - マスターデータAPI
  - `app/routes/monitoring.py` - モニタリングAPI
- [ ] `app.py` が100行以下にシンプル化されている
- [ ] 既存テストが通る

**PRレビュー重点観点**:
- [ ] Blueprintの分離が適切か
- [ ] ルーティングが正しく動作するか
- [ ] `app.py` がシンプルで理解しやすいか

**テスト方法**:
- 各Blueprintの動作確認
- 全テストの実行

**関連ドキュメント**:
- [プレゼンテーション層仕様書](../architecture/layers/presentation_layer.md)

---

#### Issue #036: プレゼンテーション層統合テストとドキュメント整備
**Labels**: `test`, `docs`, `presentation`, `phase-3`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R3
**Estimated**: 1日
**Depends on**: #035

**実装内容**:
- プレゼンテーション層の統合テスト作成
- ドキュメントの更新
- マイグレーションガイドの作成

**完了条件**:
- [ ] プレゼンテーション層の統合テストが作成され、通過している
- [ ] 各環境での動作確認が完了している
- [ ] ドキュメントが最新の実装に合わせて更新されている
- [ ] マイグレーションガイドが作成されている

**PRレビュー重点観点**:
- [ ] 統合テストが包括的か
- [ ] 各環境で正しく動作するか
- [ ] ドキュメントが分かりやすいか

**テスト方法**:
- 全統合テストの実行
- 各環境での起動確認

**関連ドキュメント**:
- [プレゼンテーション層仕様書](../architecture/layers/presentation_layer.md)

---

## 統合テスト・リリース

**期間**: 2025/5/19 〜 2025/5/23（5日間）
**Milestone**: MS-R4

#### Issue #037: 全レイヤー統合テストの実施
**Labels**: `test`, `integration`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R4
**Estimated**: 2日

**実装内容**:
- 全レイヤーを通した統合テストの作成
- E2Eテストの実施
- パフォーマンステストの実施

**完了条件**:
- [ ] 全レイヤーを通した統合テストが作成され、通過している
- [ ] E2Eテストが作成され、通過している
- [ ] パフォーマンステストが実施され、基準を満たしている
- [ ] テストカバレッジが80%以上
- [ ] すべての既存機能が正常動作している

**PRレビュー重点観点**:
- [ ] 統合テストが包括的か
- [ ] E2Eテストがユーザーシナリオを網羅しているか
- [ ] パフォーマンスが維持・向上しているか
- [ ] 既存機能に問題がないか

**テスト方法**:
- 全統合テストの実行
- E2Eテストの実行
- パフォーマンステストの実行
- カバレッジレポートの確認

**関連ドキュメント**:
- [リファクタリング総合計画](./refactoring/refactoring_plan.md)

---

#### Issue #038: ドキュメント最終整備とリリース準備
**Labels**: `docs`, `release`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R4
**Estimated**: 2日

**実装内容**:
- 全ドキュメントの最終レビューと更新
- リリースノートの作成
- マイグレーションガイドの完成

**完了条件**:
- [ ] 以下のドキュメントが最新化されている
  - アーキテクチャドキュメント
  - 各レイヤー仕様書
  - APIドキュメント
  - 開発ガイド
- [ ] リリースノートが作成されている
- [ ] マイグレーションガイドが完成している
- [ ] READMEが最新化されている

**PRレビュー重点観点**:
- [ ] ドキュメントが正確で分かりやすいか
- [ ] リリースノートが包括的か
- [ ] マイグレーションガイドが実用的か

**テスト方法**:
- ドキュメントの査読
- マイグレーション手順の検証

**関連ドキュメント**:
- [リファクタリング総合計画](./refactoring/refactoring_plan.md)

---

#### Issue #039: リリース判定とデプロイ
**Labels**: `release`, `priority:high`
**Assignee**: 開発者
**Milestone**: MS-R4
**Estimated**: 1日
**Depends on**: #037, #038

**実装内容**:
- リリース判定の実施
- 本番環境へのデプロイ準備
- リリース作業

**完了条件**:
- [ ] 以下の成功基準をすべて満たしている
  - ✅ テストカバレッジ80%以上達成
  - ✅ 循環的複雑度を平均3-5に改善
  - ✅ 型カバレッジ95%以上達成
  - ✅ すべての既存機能が正常動作
  - ✅ 包括的なテストスイートの完成
  - ✅ ドキュメントが完全に整備
- [ ] デプロイ準備が完了している
- [ ] リリースタグが作成されている

**PRレビュー重点観点**:
- [ ] すべての成功基準を満たしているか
- [ ] デプロイ手順が適切か
- [ ] ロールバック計画があるか

**テスト方法**:
- 成功基準の確認
- デプロイリハーサル

**関連ドキュメント**:
- [リファクタリング総合計画](./refactoring/refactoring_plan.md)

---

## 進捗サマリー

### Phase別進捗

| Phase | 期間 | Issue数 | 完了数 | 進捗率 | ステータス |
|-------|------|---------|--------|--------|-----------|
| **Phase 0: データアクセス層** | 2025/2/10-3/23 | 13 | 0 | 0% | 📋 計画中 |
| **Phase 1: サービス層** | 2025/3/24-4/27 | 12 | 0 | 0% | 📋 計画中 |
| **Phase 2: API層** | 2025/4/28-5/11 | 7 | 0 | 0% | 📋 計画中 |
| **Phase 3: プレゼンテーション層** | 2025/5/12-5/18 | 4 | 0 | 0% | 📋 計画中 |
| **統合テスト・リリース** | 2025/5/19-5/23 | 3 | 0 | 0% | 📋 計画中 |
| **合計** | - | **39** | **0** | **0%** | 📋 計画中 |

### Milestone進捗

| Milestone | 完了予定 | Issue数 | 完了数 | ステータス |
|-----------|---------|---------|--------|-----------|
| **MS-R0: データアクセス層完了** | 2025/3/23 | 13 | 0 | 📋 未着手 |
| **MS-R1: サービス層完了** | 2025/4/27 | 12 | 0 | 📋 未着手 |
| **MS-R2: API層完了** | 2025/5/11 | 7 | 0 | 📋 未着手 |
| **MS-R3: 全レイヤー完了** | 2025/5/18 | 4 | 0 | 📋 未着手 |
| **MS-R4: 統合テスト完了** | 2025/5/23 | 3 | 0 | 📋 未着手 |

### 優先度別Issue数

| 優先度 | Issue数 | 割合 |
|--------|---------|------|
| `priority:high` | 30 | 77% |
| `priority:medium` | 9 | 23% |
| `priority:low` | 0 | 0% |

### タイプ別Issue数

| タイプ | Issue数 | 割合 |
|--------|---------|------|
| `feature` | 24 | 62% |
| `refactor` | 9 | 23% |
| `test` | 4 | 10% |
| `docs` | 2 | 5% |

---

## 📚 関連ドキュメント

- [リファクタリング総合計画](./refactoring/refactoring_plan.md)
- [データアクセス層リファクタリング計画](./refactoring/data_access_layer_plan.md)
- [サービス層リファクタリング計画](./refactoring/service_layer_plan.md)
- [API層リファクタリング計画](./refactoring/api_layer_plan.md)
- [プレゼンテーション層リファクタリング計画](./refactoring/presentation_layer_plan.md)
- [Git運用ワークフロー](../standards/git-workflow.md)
- [アーキテクチャ概要](../architecture/architecture_overview.md)

---

**最終更新**: 2025-01-09
**ドキュメント管理者**: 開発者
**更新サイクル**: Issue作成・完了時に随時更新
