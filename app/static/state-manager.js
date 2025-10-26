/**
 * クライアントサイド状態管理システム
 * Issue #177: クライアントサイド状態管理の改善
 */

/**
 * 状態管理の基底クラス
 * localStorage/sessionStorageを活用した永続化機能を提供
 */
export class StateManager {
    constructor(namespace = 'stock-analyzer', useSessionStorage = false) {
        this.namespace = namespace;
        this.storage = useSessionStorage ? sessionStorage : localStorage;
        this.state = {};
        this.listeners = new Map();
        this.websocketCallbacks = new Map();

        // 初期化時に永続化された状態を復元
        this.loadPersistedState();

        // WebSocketイベントリスナーの設定
        this.setupWebSocketListeners();
    }

    /**
     * 状態の取得
     * @param {string} key - 状態のキー
     * @param {*} defaultValue - デフォルト値
     * @returns {*} 状態の値
     */
    get(key, defaultValue = null) {
        return this.state[key] !== undefined ? this.state[key] : defaultValue;
    }

    /**
     * 状態の設定
     * @param {string} key - 状態のキー
     * @param {*} value - 設定する値
     * @param {boolean} persist - 永続化するかどうか
     */
    set(key, value, persist = true) {
        const oldValue = this.state[key];
        this.state[key] = value;

        // 永続化
        if (persist) {
            this.persistState(key, value);
        }

        // リスナーに変更を通知
        this.notifyListeners(key, value, oldValue);
    }

    /**
     * 複数の状態を一括設定
     * @param {Object} updates - 更新する状態のオブジェクト
     * @param {boolean} persist - 永続化するかどうか
     */
    setMultiple(updates, persist = true) {
        const changes = [];

        Object.entries(updates).forEach(([key, value]) => {
            const oldValue = this.state[key];
            this.state[key] = value;
            changes.push({ key, value, oldValue });

            if (persist) {
                this.persistState(key, value);
            }
        });

        // 一括でリスナーに通知
        changes.forEach(({ key, value, oldValue }) => {
            this.notifyListeners(key, value, oldValue);
        });
    }

    /**
     * 状態の削除
     * @param {string} key - 削除する状態のキー
     */
    remove(key) {
        const oldValue = this.state[key];
        delete this.state[key];

        // 永続化ストレージからも削除
        this.storage.removeItem(`${this.namespace}.${key}`);

        // リスナーに削除を通知
        this.notifyListeners(key, undefined, oldValue);
    }

    /**
     * 状態変更のリスナーを追加
     * @param {string} key - 監視する状態のキー
     * @param {Function} callback - コールバック関数
     */
    addListener(key, callback) {
        if (!this.listeners.has(key)) {
            this.listeners.set(key, new Set());
        }
        this.listeners.get(key).add(callback);
    }

    /**
     * 状態変更のリスナーを削除
     * @param {string} key - 監視する状態のキー
     * @param {Function} callback - コールバック関数
     */
    removeListener(key, callback) {
        if (this.listeners.has(key)) {
            this.listeners.get(key).delete(callback);
        }
    }

    /**
     * WebSocketイベントとの同期設定
     * @param {string} eventName - WebSocketイベント名
     * @param {string} stateKey - 対応する状態のキー
     * @param {Function} transformer - データ変換関数（オプション）
     */
    syncWithWebSocket(eventName, stateKey, transformer = null) {
        this.websocketCallbacks.set(eventName, { stateKey, transformer });
    }

    /**
     * 永続化された状態を読み込み
     */
    loadPersistedState() {
        try {
            // 名前空間に基づいて保存された状態を復元
            for (let i = 0; i < this.storage.length; i++) {
                const key = this.storage.key(i);
                if (key && key.startsWith(`${this.namespace}.`)) {
                    const stateKey = key.replace(`${this.namespace}.`, '');
                    const value = JSON.parse(this.storage.getItem(key));
                    this.state[stateKey] = value;
                }
            }
        } catch (error) {
            console.error('Failed to load persisted state:', error);
        }
    }

    /**
     * 状態を永続化
     * @param {string} key - 状態のキー
     * @param {*} value - 永続化する値
     */
    persistState(key, value) {
        try {
            const storageKey = `${this.namespace}.${key}`;
            this.storage.setItem(storageKey, JSON.stringify(value));
        } catch (error) {
            console.error(`Failed to persist state for key ${key}:`, error);
        }
    }

    /**
     * リスナーに変更を通知
     * @param {string} key - 変更された状態のキー
     * @param {*} newValue - 新しい値
     * @param {*} oldValue - 古い値
     */
    notifyListeners(key, newValue, oldValue) {
        if (this.listeners.has(key)) {
            this.listeners.get(key).forEach(callback => {
                try {
                    callback(newValue, oldValue, key);
                } catch (error) {
                    console.error(`Error in state listener for key ${key}:`, error);
                }
            });
        }
    }

    /**
     * WebSocketリスナーの設定
     */
    setupWebSocketListeners() {
        // グローバルなWebSocketインスタンスが利用可能な場合のみ設定
        if (typeof window !== 'undefined' && window.io) {
            const socket = window.io();

            socket.on('connect', () => {
                this.set('websocket.connected', true, false);
            });

            socket.on('disconnect', () => {
                this.set('websocket.connected', false, false);
            });

            // 登録されたWebSocketイベントの処理
            this.websocketCallbacks.forEach(({ stateKey, transformer }, eventName) => {
                socket.on(eventName, (data) => {
                    const value = transformer ? transformer(data) : data;
                    this.set(stateKey, value, false); // WebSocketデータは永続化しない
                });
            });
        }
    }

    /**
     * 状態の完全なリセット
     */
    reset() {
        // メモリ上の状態をクリア
        this.state = {};

        // 永続化ストレージからも削除
        const keysToRemove = [];
        for (let i = 0; i < this.storage.length; i++) {
            const key = this.storage.key(i);
            if (key && key.startsWith(`${this.namespace}.`)) {
                keysToRemove.push(key);
            }
        }

        keysToRemove.forEach(key => this.storage.removeItem(key));

        // リスナーをクリア
        this.listeners.clear();
    }

    /**
     * デバッグ用：現在の状態を出力
     */
    debug() {
        console.log('Current State:', this.state);
        console.log('Listeners:', this.listeners);
        console.log('WebSocket Callbacks:', this.websocketCallbacks);
    }
}

/**
 * アプリケーション固有の状態管理クラス
 * 株価データ管理システム用の状態を管理
 */
export class AppStateManager extends StateManager {
    constructor() {
        super('stock-analyzer-app', false); // localStorageを使用

        // デフォルト状態の設定
        this.initializeDefaultState();

        // アプリケーション固有のWebSocketイベント同期設定
        this.setupAppSpecificWebSocketSync();
    }

    /**
     * デフォルト状態の初期化
     */
    initializeDefaultState() {
        const defaults = {
            'pagination.currentPage': 0,
            'pagination.currentLimit': 25,
            'pagination.totalRecords': 0,
            'ui.isLoading': false,
            'table.sortColumn': null,
            'table.sortDirection': 'asc',
            'filters.symbol': '',
            'filters.period': '1mo',
            'filters.interval': '1d',
            'websocket.connected': false
        };

        Object.entries(defaults).forEach(([key, value]) => {
            if (this.get(key) === null) {
                this.set(key, value, true);
            }
        });
    }

    /**
     * アプリケーション固有のWebSocketイベント同期設定
     */
    setupAppSpecificWebSocketSync() {
        // バルク処理の進捗同期
        this.syncWithWebSocket('bulk_progress', 'bulk.progress');
        this.syncWithWebSocket('bulk_complete', 'bulk.complete');

        // JPX順次取得の進捗同期
        this.syncWithWebSocket('jpx_progress', 'jpx.progress');
        this.syncWithWebSocket('jpx_complete', 'jpx.complete');
    }

    /**
     * ページネーション状態の更新
     * @param {number} page - ページ番号
     * @param {number} limit - 1ページあたりの件数
     * @param {number} total - 総件数
     */
    updatePagination(page, limit, total) {
        this.setMultiple({
            'pagination.currentPage': page,
            'pagination.currentLimit': limit,
            'pagination.totalRecords': total
        });
    }

    /**
     * テーブルソート状態の更新
     * @param {string} column - ソート対象カラム
     * @param {string} direction - ソート方向 ('asc' | 'desc')
     */
    updateTableSort(column, direction) {
        this.setMultiple({
            'table.sortColumn': column,
            'table.sortDirection': direction
        });
    }

    /**
     * フィルター状態の更新
     * @param {Object} filters - フィルター設定
     */
    updateFilters(filters) {
        const updates = {};
        Object.entries(filters).forEach(([key, value]) => {
            updates[`filters.${key}`] = value;
        });
        this.setMultiple(updates);
    }

    /**
     * ローディング状態の設定
     * @param {boolean} isLoading - ローディング状態
     */
    setLoading(isLoading) {
        this.set('ui.isLoading', isLoading, false); // ローディング状態は永続化しない
    }
}

// グローバルなアプリケーション状態管理インスタンス
export const appStateManager = new AppStateManager();

// 後方互換性のための既存AppStateクラスのラッパー
export class AppState {
    constructor() {
        console.warn('AppState is deprecated. Use AppStateManager instead.');
        this.stateManager = appStateManager;
    }

    get currentPage() {
        return this.stateManager.get('pagination.currentPage', 0);
    }

    set currentPage(value) {
        this.stateManager.set('pagination.currentPage', value);
    }

    get currentLimit() {
        return this.stateManager.get('pagination.currentLimit', 25);
    }

    set currentLimit(value) {
        this.stateManager.set('pagination.currentLimit', value);
    }

    get totalRecords() {
        return this.stateManager.get('pagination.totalRecords', 0);
    }

    set totalRecords(value) {
        this.stateManager.set('pagination.totalRecords', value);
    }

    get isLoading() {
        return this.stateManager.get('ui.isLoading', false);
    }

    set isLoading(value) {
        this.stateManager.setLoading(value);
    }

    get currentSortColumn() {
        return this.stateManager.get('table.sortColumn', null);
    }

    set currentSortColumn(value) {
        this.stateManager.set('table.sortColumn', value);
    }

    get currentSortDirection() {
        return this.stateManager.get('table.sortDirection', 'asc');
    }

    set currentSortDirection(value) {
        this.stateManager.set('table.sortDirection', value);
    }

    get currentStockData() {
        return this.stateManager.get('data.stockData', []);
    }

    set currentStockData(value) {
        this.stateManager.set('data.stockData', value, false); // 大量データは永続化しない
    }
}
