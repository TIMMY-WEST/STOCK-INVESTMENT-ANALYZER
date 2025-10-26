/**
 * 株価データ取得システム - JavaScript API連携機能
 * ES6 Module版
 */

// 共通ユーティリティとサービスをインポート
import { AppState, Utils, ApiService, UIComponents, FormValidator, INTERVAL_PERIOD_RULES } from './app.js';

// アプリケーション状態管理インスタンス
const appState = new AppState();

// アプリケーション初期化
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

// アプリケーション初期化関数
function initApp() {
    console.log('株価データ取得システムを初期化中...');

    // フォームイベントリスナー設定
    const fetchForm = document.getElementById('fetch-form');
    if (fetchForm) {
        fetchForm.addEventListener('submit', handleFetchSubmit);
    }

    // データ読み込みボタンイベントリスナー設定
    const loadDataBtn = document.getElementById('load-data-btn');
    if (loadDataBtn) {
        loadDataBtn.addEventListener('click', loadStockData);
    }

    // テーブルソート機能設定
    initTableSorting();

    // ページネーション機能設定
    initPagination();

    // 初期状態のページネーション表示を設定
    updatePagination();

    // Issue #67: 時間軸選択UI機能初期化
    initTimeframeSelector();

    // Issue #67: 足選択UI機能初期化
    initIntervalSelector();

    // 初期データ読み込み
    loadExistingData();
}

// データ取得フォーム送信ハンドラ
async function handleFetchSubmit(event) {
    event.preventDefault();
    console.log('[handleFetchSubmit] フォーム送信開始');

    // ローディング状態開始
    showLoading();
    console.log('[handleFetchSubmit] showLoading() 呼び出し完了');

    const formData = new FormData(event.target);
    const symbol = formData.get('symbol');
    const period = formData.get('period');
    const interval = formData.get('interval');
    console.log('[handleFetchSubmit] パラメータ:', { symbol, period, interval });

    // バリデーション
    const errors = validateForm(formData);
    if (Object.keys(errors).length > 0) {
        console.log('[handleFetchSubmit] バリデーションエラー、hideLoading() 呼び出し');
        hideLoading(); // バリデーションエラー時にローディング状態を解除
        showValidationErrors(errors);
        return;
    }

    // バリデーションエラーをクリア
    clearFieldErrors();

    try {
        console.log('[handleFetchSubmit] APIリクエスト送信開始');

        // POST /api/fetch-data への非同期リクエスト
        const response = await fetch('/api/fetch-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol, period, interval })
        });

        console.log('[handleFetchSubmit] レスポンス受信:', response.status, response.ok);
        const result = await response.json();
        console.log('[handleFetchSubmit] JSON パース完了:', result);

        // ローディング状態を先に解除
        console.log('[handleFetchSubmit] hideLoading() 呼び出し開始');
        hideLoading();
        console.log('[handleFetchSubmit] hideLoading() 呼び出し完了');

        if (result.success) {
            console.log('[handleFetchSubmit] 成功: showSuccess() 呼び出し');
            showSuccess('データを取得しました', result.data);
            console.log('[handleFetchSubmit] showSuccess() 完了');
            // データテーブル更新
            await loadStockData();
        } else {
            console.log('[handleFetchSubmit] 失敗: showError() 呼び出し');
            showError(result.message || 'データ取得に失敗しました');
        }

    } catch (error) {
        console.error('[handleFetchSubmit] エラー発生:', error);
        console.error('[handleFetchSubmit] エラースタック:', error.stack);
        hideLoading();
        showError('ネットワークエラーが発生しました: ' + error.message);
    }
}

// フォームバリデーション（FormValidatorクラスを使用）
function validateForm(formData) {
    const validator = new FormValidator();

    // FormDataをプレーンオブジェクトに変換
    const data = {
        symbol: formData.get('symbol'),
        period: formData.get('period'),
        interval: formData.get('interval')
    };

    const result = validator.validateStockForm(data);

    // バリデーション結果のerrorsオブジェクトのみを返す
    return result.errors;
}

// バリデーションエラー表示
function showValidationErrors(errors) {
    Object.entries(errors).forEach(([field, message]) => {
        showFieldError(field, message);
    });
}

function showFieldError(fieldName, message) {
    // 時間軸選択と足選択のエラーは専用関数で処理
    if (fieldName === 'period') {
        showTimeframeError(message);
        const timeframeSelector = document.getElementById('period');
        if (timeframeSelector) {
            setTimeframeSelectorState(timeframeSelector, 'invalid');
        }
        return;
    } else if (fieldName === 'interval') {
        showIntervalError(message);
        const intervalSelector = document.getElementById('interval');
        if (intervalSelector) {
            setIntervalSelectorState(intervalSelector, 'invalid');
        }
        return;
    }

    // 通常のフィールドエラー処理
    const field = document.getElementById(fieldName);
    if (!field) return;

    field.classList.add('form__control--error');

    // エラーメッセージ要素を作成または更新
    let errorElement = field.parentNode.querySelector('.form__error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'form__error';
        errorElement.style.color = '#dc3545';
        errorElement.style.fontSize = '0.875rem';
        errorElement.style.marginTop = '0.25rem';
        field.parentNode.appendChild(errorElement);
    }

    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

function clearFieldErrors() {
    // エラークラスを削除
    document.querySelectorAll('.form__control--error').forEach(el => {
        el.classList.remove('form__control--error');
    });

    // エラーメッセージを非表示
    document.querySelectorAll('.form__error').forEach(el => {
        el.style.display = 'none';
    });

    // 時間軸選択と足選択のエラーもクリア
    clearTimeframeError();
    clearIntervalError();

    const timeframeSelector = document.getElementById('period');
    if (timeframeSelector) {
        setTimeframeSelectorState(timeframeSelector, 'neutral');
    }

    const intervalSelector = document.getElementById('interval');
    if (intervalSelector) {
        setIntervalSelectorState(intervalSelector, 'neutral');
    }
}

// ローディング状態管理（Utilsクラスを使用）
function showLoading() {
    Utils.showLoading();
}

function hideLoading() {
    Utils.hideLoading();
}

// ステータス表示関数（UIComponentsクラスを使用）
function showSuccess(message, data) {
    console.log('[showSuccess] 開始:', message, data);

    // データが渡された場合は詳細表示、そうでなければシンプル表示
    if (data && typeof data === 'object') {
        UIComponents.showDetailedSuccessMessage(message, data);
    } else {
        UIComponents.showSuccessMessage(message);
    }

    console.log('[showSuccess] 完了');
}

function showError(message) {
    UIComponents.showErrorMessage(message);
}

// 株価データ読み込み (GET /api/stocks への非同期リクエスト)
async function loadStockData(page = null) {
    try {
        const tableBody = document.getElementById('data-table-body');
        const symbolFilter = document.getElementById('view-symbol')?.value?.trim();
        const intervalFilter = document.getElementById('view-interval')?.value || '1d';
        const limit = parseInt(document.getElementById('view-limit')?.value) || 25;

        // ページが指定されている場合は使用、そうでなければ現在のページを使用
        if (page !== null) {
            appState.currentPage = page;
        }
        appState.currentLimit = limit;

        if (tableBody) {
            showLoadingInTable(tableBody);
        }

        // URLパラメータ構築
        const params = new URLSearchParams({
            limit: appState.currentLimit,
            offset: appState.currentPage * appState.currentLimit,
            interval: intervalFilter
        });

        if (symbolFilter) {
            params.append('symbol', symbolFilter);
        }

        const response = await fetch(`/api/stocks?${params.toString()}`);

        // レスポンステキストを取得してJSONパースを安全に実行
        const responseText = await response.text();
        let result;

        try {
            result = JSON.parse(responseText);
        } catch (jsonError) {
            console.error('JSONパースエラー:', jsonError);
            console.error('レスポンステキスト:', responseText.substring(0, 500) + '...');

            // NaN値が含まれている場合の対処
            if (responseText.includes('NaN')) {
                console.warn('レスポンスにNaN値が含まれています。サーバー側の修正が必要です。');
                throw new Error('サーバーから無効なデータが返されました。管理者にお問い合わせください。');
            }

            throw new Error('サーバーレスポンスの解析に失敗しました: ' + jsonError.message);
        }

        if (result.success) {
            appState.totalRecords = result.pagination.total;
            updateDataTable(result.data);
            updatePagination();
            updateDataSummary(symbolFilter, result.data.length, appState.totalRecords);
        } else {
            // エラーの場合もページネーションを更新（totalRecordsは0のまま）
            updatePagination();
            showErrorInTable(tableBody, result.message || 'データの読み込みに失敗しました');
        }

    } catch (error) {
        console.error('データ読み込みエラー:', error);
        const tableBody = document.getElementById('data-table-body');
        if (tableBody) {
            // ネットワークエラーの場合もページネーションを更新
            updatePagination();
            showErrorInTable(tableBody, 'ネットワークエラーが発生しました: ' + error.message);
        }
    }
}

// テーブルにローディング表示
function showLoadingInTable(tableBody) {
    tableBody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center">
                <div class="loading-content">
                    <span class="loading-spinner">🔄</span>
                    データを読み込み中...
                </div>
            </td>
        </tr>
    `;
}

// テーブルにエラー表示
function showErrorInTable(tableBody, message) {
    tableBody.innerHTML = `
        <tr>
            <td colspan="9" class="text-center error">
                <div class="error-content">
                    <span class="error-icon">❌</span>
                    ${escapeHtml(message)}
                </div>
            </td>
        </tr>
    `;
}

// データテーブル更新
function updateDataTable(stockData) {
    const tableBody = document.getElementById('data-table-body');
    if (!tableBody) return;

    // 現在のストックデータを保存（ソート機能で使用）
    appState.currentStockData = [...stockData];

    if (stockData.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center">
                    <div class="no-data-content">
                        <span class="no-data-icon">📊</span>
                        データが見つかりませんでした
                    </div>
                </td>
            </tr>
        `;
        return;
    }

    const rows = stockData.map(stock => `
        <tr>
            <td data-label="ID">${stock.id}</td>
            <td data-label="銘柄コード">${escapeHtml(stock.symbol)}</td>
            <td data-label="日付">${formatDateTime(stock.datetime || stock.date)}</td>
            <td data-label="始値" class="text-right">${formatCurrency(stock.open)}</td>
            <td data-label="高値" class="text-right">${formatCurrency(stock.high)}</td>
            <td data-label="安値" class="text-right">${formatCurrency(stock.low)}</td>
            <td data-label="終値" class="text-right">${formatCurrency(stock.close)}</td>
            <td data-label="出来高" class="text-right">${formatNumber(stock.volume)}</td>
            <td data-label="操作">
                <button type="button" class="btn btn--danger btn--sm" onclick="deleteStock(${stock.id})">
                    削除
                </button>
            </td>
        </tr>
    `).join('');

    tableBody.innerHTML = rows;
}

// データサマリー更新
function updateDataSummary(symbol, displayCount, totalCount) {
    // 現在の実装では、データサマリー表示エリアがHTMLに存在しないため、
    // 将来的な拡張に備えてコメントアウト
    /*
    const currentSymbolEl = document.getElementById('current-symbol');
    const dataCountEl = document.getElementById('data-count');

    if (currentSymbolEl && symbol) {
        currentSymbolEl.textContent = symbol;
    }

    if (dataCountEl) {
        dataCountEl.textContent = totalCount;
    }
    */
}

// 既存データ読み込み
function loadExistingData() {
    // ページ読み込み時に既存データを自動表示
    loadStockData();
}

// 株価データ削除機能
async function deleteStock(stockId) {
    if (!confirm('このデータを削除してもよろしいですか？')) {
        return;
    }

    try {
        const response = await fetch(`/api/stocks/${stockId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showSuccess('データを削除しました', { symbol: '', records_count: 0, saved_records: 0, date_range: { start: '', end: '' } });
            // テーブル再読み込み
            await loadStockData();
        } else {
            showError(result.message || 'データの削除に失敗しました');
        }

    } catch (error) {
        console.error('削除エラー:', error);
        showError('ネットワークエラーが発生しました: ' + error.message);
    }
}

// ユーティリティ関数（Utilsクラスを使用）

// HTMLエスケープ
function escapeHtml(text) {
    return Utils.escapeHtml(text);
}

// 数値フォーマット
function formatNumber(num) {
    return new Intl.NumberFormat('ja-JP').format(num);
}

// 通貨フォーマット
function formatCurrency(amount) {
    return new Intl.NumberFormat('ja-JP', {
        style: 'currency',
        currency: 'JPY',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

// 日付フォーマット
function formatDate(dateString) {
    const date = new Date(dateString + 'T00:00:00');
    return new Intl.DateTimeFormat('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(date);
}

// 日付・日時フォーマット（datetime または date フィールドに対応）
function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '-';

    const date = new Date(dateTimeString);

    // 日付のみの場合（時刻が00:00:00の場合）
    if (dateTimeString.length === 10 || dateTimeString.indexOf('T00:00:00') > 0) {
        return new Intl.DateTimeFormat('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
    }

    // 日時の場合
    return new Intl.DateTimeFormat('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).format(date);
}

// グローバルエラーハンドリング
window.addEventListener('error', (event) => {
    console.error('JavaScript Error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection:', event.reason);
    event.preventDefault();
});

// グローバル関数として削除機能を公開
window.deleteStock = deleteStock;

// モジュール内状態管理はインポートしたappStateインスタンスを使用

// テーブルソート機能初期化
function initTableSorting() {
    const table = document.getElementById('data-table');
    if (!table) return;

    // ソート可能なヘッダーにクリックイベントを追加
    const sortableHeaders = table.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortColumn = this.dataset.sort;
            sortTable(sortColumn);
        });
    });
}

// テーブルソート実行
function sortTable(column) {
    if (appState.currentStockData.length === 0) return;

    // ソート方向を決定
    if (appState.currentSortColumn === column) {
        appState.currentSortDirection = appState.currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        appState.currentSortDirection = 'asc';
        appState.currentSortColumn = column;
    }

    // データをソート
    const sortedData = [...appState.currentStockData].sort((a, b) => {
        let aValue = a[column];
        let bValue = b[column];

        // 日付の場合は Date オブジェクトに変換
        if (column === 'date') {
            aValue = new Date(aValue);
            bValue = new Date(bValue);
        }
        // 数値の場合は数値に変換
        else if (['open', 'high', 'low', 'close', 'volume'].includes(column)) {
            aValue = parseFloat(aValue) || 0;
            bValue = parseFloat(bValue) || 0;
        }
        // 文字列の場合は小文字で比較
        else if (typeof aValue === 'string') {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
        }

        if (aValue < bValue) {
            return appState.currentSortDirection === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
            return appState.currentSortDirection === 'asc' ? 1 : -1;
        }
        return 0;
    });

    // ソートされたデータでテーブルを更新
    updateDataTable(sortedData);
    updateSortIcons(column, appState.currentSortDirection);
}

// ソートアイコンを更新
function updateSortIcons(activeColumn, direction) {
    const table = document.getElementById('data-table');
    if (!table) return;

    // 全てのソートアイコンをリセット
    const sortableHeaders = table.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.classList.remove('sort-asc', 'sort-desc');
    });

    // アクティブなカラムにソート方向を設定
    const activeHeader = table.querySelector(`[data-sort="${activeColumn}"]`);
    if (activeHeader) {
        activeHeader.classList.add(`sort-${direction}`);
    }
}

// ページネーション機能初期化
function initPagination() {
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            if (appState.currentPage > 0) {
                loadStockData(appState.currentPage - 1);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(appState.totalRecords / appState.currentLimit);
            if (appState.currentPage < totalPages - 1) {
                loadStockData(appState.currentPage + 1);
            }
        });
    }
}

// ページネーション情報を更新
function updatePagination() {
    const paginationContainer = document.getElementById('pagination');
    const paginationText = document.getElementById('pagination-text');
    const prevBtn = document.getElementById('prev-page-btn');
    const nextBtn = document.getElementById('next-page-btn');

    if (!paginationContainer || !paginationText || !prevBtn || !nextBtn) return;

    // 変数の安全性チェック
    const safeTotalRecords = isNaN(appState.totalRecords) || appState.totalRecords < 0 ? 0 : appState.totalRecords;
    const safeCurrentPage = isNaN(appState.currentPage) || appState.currentPage < 0 ? 0 : appState.currentPage;
    const safeCurrentLimit = isNaN(appState.currentLimit) || appState.currentLimit <= 0 ? 25 : appState.currentLimit;

    // データが存在しない場合の処理
    if (safeTotalRecords === 0) {
        paginationText.textContent = '表示中: 0-0 / 全 0 件';
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        paginationContainer.style.display = 'none';
        return;
    }

    const totalPages = Math.ceil(safeTotalRecords / safeCurrentLimit);
    const startRecord = safeCurrentPage * safeCurrentLimit + 1;
    const endRecord = Math.min((safeCurrentPage + 1) * safeCurrentLimit, safeTotalRecords);



    // ページネーション情報テキストを更新
    paginationText.textContent = `表示中: ${startRecord}-${endRecord} / 全 ${safeTotalRecords} 件`;

    // ボタンの有効/無効を設定
    prevBtn.disabled = appState.currentPage === 0;
    nextBtn.disabled = appState.currentPage >= totalPages - 1;

    // ページネーションコンテナの表示/非表示
    if (appState.totalRecords > appState.currentLimit) {
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
    }
}

// Issue #67: 時間軸選択UI実装 - Enhanced Timeframe Selector Functions

/**
 * 時間軸選択機能の初期化
 */
function initTimeframeSelector() {
    console.log('時間軸選択UI機能を初期化中...');

    const timeframeSelector = document.getElementById('period');
    const timeframeIndicator = document.getElementById('timeframe-indicator');

    if (!timeframeSelector || !timeframeIndicator) {
        console.warn('時間軸選択要素が見つかりません');
        return;
    }

    // 初期状態の設定
    updateTimeframeIndicator(timeframeSelector.value);

    // イベントリスナーの設定
    timeframeSelector.addEventListener('change', handleTimeframeChange);
    timeframeSelector.addEventListener('blur', validateTimeframeSelection);

    // フォーカス時のアクセシビリティ向上
    timeframeSelector.addEventListener('focus', handleTimeframeFocus);

    console.log('時間軸選択UI機能の初期化が完了しました');
}

/**
 * 時間軸選択変更時のハンドラ
 * @param {Event} event - 変更イベント
 */
function handleTimeframeChange(event) {
    const selectedValue = event.target.value;

    // バリデーション実行
    const isValid = validateTimeframeSelection(event);

    if (isValid) {
        // インジケーター更新
        updateTimeframeIndicator(selectedValue);

        // フォームの状態を有効に設定
        setTimeframeSelectorState(event.target, 'valid');

        // アクセシビリティ: 選択内容をアナウンス
        announceTimeframeSelection(selectedValue);
    }
}

/**
 * 時間軸選択のバリデーション
 * @param {Event} event - イベントオブジェクト
 * @returns {boolean} バリデーション結果
 */
function validateTimeframeSelection(event) {
    const timeframeSelector = event.target;
    const selectedValue = timeframeSelector.value;
    const errorElement = document.getElementById('period-error');

    // エラーメッセージをクリア
    clearTimeframeError();

    // 必須チェック
    if (!selectedValue || selectedValue.trim() === '') {
        showTimeframeError('期間を選択してください');
        setTimeframeSelectorState(timeframeSelector, 'invalid');
        return false;
    }

    // 有効な期間値のチェック
    const validPeriods = ['5d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'];
    if (!validPeriods.includes(selectedValue)) {
        showTimeframeError('無効な期間が選択されています');
        setTimeframeSelectorState(timeframeSelector, 'invalid');
        return false;
    }

    // バリデーション成功
    setTimeframeSelectorState(timeframeSelector, 'valid');
    return true;
}

/**
 * 時間軸インジケーターの更新
 * @param {string} selectedValue - 選択された期間値
 */
function updateTimeframeIndicator(selectedValue) {
    const indicator = document.getElementById('timeframe-indicator');
    const indicatorText = indicator.querySelector('.form__indicator-text');

    if (!indicator || !indicatorText) {
        return;
    }

    // 既存のクラスをクリア
    indicator.className = 'form__timeframe-indicator';

    // 期間に応じたメッセージとスタイルを設定
    const timeframeConfig = getTimeframeConfig(selectedValue);

    indicatorText.textContent = timeframeConfig.message;
    indicator.classList.add(timeframeConfig.className);

    // アニメーション効果
    indicator.style.transform = 'scale(0.95)';
    setTimeout(() => {
        indicator.style.transform = 'scale(1)';
    }, 150);
}

/**
 * 期間設定の取得
 * @param {string} value - 期間値
 * @returns {Object} 期間設定オブジェクト
 */
function getTimeframeConfig(value) {
    const configs = {
        '5d': {
            message: '5日間のデータを取得します（短期分析向け）',
            className: 'short-term'
        },
        '1wk': {
            message: '1週間のデータを取得します（短期分析向け）',
            className: 'short-term'
        },
        '1mo': {
            message: '1ヶ月のデータを取得します（中期分析向け）',
            className: 'medium-term'
        },
        '3mo': {
            message: '3ヶ月のデータを取得します（中期分析向け）',
            className: 'medium-term'
        },
        '6mo': {
            message: '6ヶ月のデータを取得します（中期分析向け）',
            className: 'medium-term'
        },
        '1y': {
            message: '1年間のデータを取得します（長期分析向け）',
            className: 'long-term'
        },
        '2y': {
            message: '2年間のデータを取得します（長期分析向け）',
            className: 'long-term'
        },
        '5y': {
            message: '5年間のデータを取得します（長期分析向け）',
            className: 'long-term'
        },
        'max': {
            message: '利用可能な全期間のデータを取得します（包括的分析向け）',
            className: 'max-term'
        }
    };

    return configs[value] || {
        message: '期間を選択してください',
        className: 'medium-term'
    };
}

/**
 * 時間軸選択器の状態設定
 * @param {HTMLElement} element - 選択器要素
 * @param {string} state - 状態 ('valid', 'invalid', 'neutral')
 */
function setTimeframeSelectorState(element, state) {
    // 既存の状態クラスをクリア
    element.classList.remove('is-valid', 'is-invalid');

    // 新しい状態クラスを追加
    if (state === 'valid') {
        element.classList.add('is-valid');
    } else if (state === 'invalid') {
        element.classList.add('is-invalid');
    }
}

/**
 * 時間軸選択エラーの表示
 * @param {string} message - エラーメッセージ
 */
function showTimeframeError(message) {
    const errorElement = document.getElementById('period-error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');

        // アクセシビリティ: エラーをアナウンス
        errorElement.setAttribute('aria-live', 'assertive');
    }
}

/**
 * 時間軸選択エラーのクリア
 */
function clearTimeframeError() {
    const errorElement = document.getElementById('period-error');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
        errorElement.setAttribute('aria-live', 'polite');
    }
}

/**
 * フォーカス時のハンドラ
 * @param {Event} event - フォーカスイベント
 */
function handleTimeframeFocus(event) {
    // フォーカス時にエラーをクリア
    clearTimeframeError();
    setTimeframeSelectorState(event.target, 'neutral');
}

/**
 * 選択内容のアナウンス（アクセシビリティ向上）
 * @param {string} selectedValue - 選択された値
 */
function announceTimeframeSelection(selectedValue) {
    const config = getTimeframeConfig(selectedValue);

    // スクリーンリーダー用の一時的な要素を作成
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';

    announcement.textContent = `期間が選択されました: ${config.message}`;

    document.body.appendChild(announcement);

    // 短時間後に要素を削除
    setTimeout(() => {
        if (announcement.parentNode) {
            announcement.parentNode.removeChild(announcement);
        }
    }, 1000);
}


// ========================================
// Issue #67: 足選択UI機能実装
// ========================================

/**
 * 足選択UI機能の初期化
 */
function initIntervalSelector() {
    console.log('足選択UI機能を初期化中...');

    const intervalSelector = document.getElementById('interval');
    const intervalIndicator = document.getElementById('interval-indicator');

    if (!intervalSelector || !intervalIndicator) {
        console.warn('足選択要素が見つかりません');
        return;
    }

    // 初期状態の設定
    updateIntervalIndicator(intervalSelector.value);

    // イベントリスナーの設定
    intervalSelector.addEventListener('change', handleIntervalChange);
    intervalSelector.addEventListener('blur', validateIntervalSelection);

    // フォーカス時のアクセシビリティ向上
    intervalSelector.addEventListener('focus', handleIntervalFocus);

    console.log('足選択UI機能の初期化が完了しました');
}

/**
 * 足選択変更時のハンドラ
 * @param {Event} event - 変更イベント
 */
function handleIntervalChange(event) {
    const selectedValue = event.target.value;

    // バリデーション実行
    const isValid = validateIntervalSelection(event);

    if (isValid) {
        // インジケーター更新
        updateIntervalIndicator(selectedValue);

        // 期間選択肢を制限
        updatePeriodOptions(selectedValue);

        // フォームの状態を有効に設定
        setIntervalSelectorState(event.target, 'valid');

        // アクセシビリティ: 選択内容をアナウンス
        announceIntervalSelection(selectedValue);
    }
}

/**
 * 時間軸に応じて期間の選択肢を制限
 * @param {string} interval - 選択された時間軸
 */
function updatePeriodOptions(interval) {
    const periodSelector = document.getElementById('period');
    if (!periodSelector) return;

    // 時間軸ごとの利用可能期間マッピング
    const allowedPeriods = {
        '1m': ['1d', '5d', '7d'],
        '2m': ['1d', '5d', '60d'],
        '5m': ['1d', '5d', '1mo', '60d'],
        '15m': ['1d', '5d', '1mo', '60d'],
        '30m': ['1d', '5d', '1mo', '60d'],
        '60m': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '730d'],
        '90m': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '730d'],
        '1h': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '730d'],
        '1d': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        '5d': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        '1wk': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        '1mo': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'],
        '3mo': ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    };

    const allowed = allowedPeriods[interval] || Object.keys(allowedPeriods['1d']);
    const currentValue = periodSelector.value;

    // 全optionを走査して無効化/有効化
    Array.from(periodSelector.options).forEach(option => {
        if (option.value === '') return; // プレースホルダーはスキップ

        if (allowed.includes(option.value)) {
            option.disabled = false;
            option.style.display = '';
        } else {
            option.disabled = true;
            option.style.display = 'none';
        }
    });

    // 現在の選択が無効になった場合、デフォルト値にリセット
    if (currentValue && !allowed.includes(currentValue)) {
        // 1分足なら7d、5-60分足なら60d、それ以外は1mo
        if (interval === '1m') {
            periodSelector.value = '7d';
        } else if (['2m', '5m', '15m', '30m'].includes(interval)) {
            periodSelector.value = '60d';
        } else if (['60m', '90m', '1h'].includes(interval)) {
            periodSelector.value = '730d';
        } else {
            periodSelector.value = '1mo';
        }

        // 期間インジケーターを更新
        const timeframeIndicator = document.getElementById('timeframe-indicator');
        if (timeframeIndicator) {
            const indicatorText = timeframeIndicator.querySelector('.indicator-text');
            if (indicatorText) {
                const periodMap = {
                    '1d': '1日分',
                    '5d': '5日分',
                    '7d': '7日分',
                    '1mo': '1ヶ月分',
                    '60d': '60日分',
                    '3mo': '3ヶ月分',
                    '6mo': '6ヶ月分',
                    '1y': '1年分',
                    '2y': '2年分',
                    '5y': '5年分',
                    '10y': '10年分',
                    '730d': '2年分(730日)',
                    'ytd': '年初来',
                    'max': '全期間'
                };
                const periodText = periodMap[periodSelector.value] || periodSelector.value;
                indicatorText.textContent = `${periodText}のデータを取得します`;
            }
        }
    }
}

/**
 * 足選択のバリデーション
 * @param {Event} event - イベントオブジェクト
 * @returns {boolean} バリデーション結果
 */
function validateIntervalSelection(event) {
    const intervalSelector = event.target;
    const selectedValue = intervalSelector.value;

    // エラーメッセージをクリア
    clearIntervalError();

    // 必須チェック
    if (!selectedValue || selectedValue.trim() === '') {
        showIntervalError('足を選択してください');
        setIntervalSelectorState(intervalSelector, 'invalid');
        return false;
    }

    // 有効な足値のチェック
    const validIntervals = [
        '1m', '5m', '15m', '30m',
        '1h',
        '1d', '1wk', '1mo'
    ];
    if (!validIntervals.includes(selectedValue)) {
        showIntervalError('無効な足が選択されています');
        setIntervalSelectorState(intervalSelector, 'invalid');
        return false;
    }

    // バリデーション成功
    setIntervalSelectorState(intervalSelector, 'valid');
    return true;
}

/**
 * 足インジケーターの更新
 * @param {string} selectedValue - 選択された足値
 */
function updateIntervalIndicator(selectedValue) {
    const indicator = document.getElementById('interval-indicator');
    const indicatorText = indicator.querySelector('.form__indicator-text');

    if (!indicator || !indicatorText) {
        return;
    }

    // 既存のクラスをクリア
    indicator.className = 'form__interval-indicator';

    // 足に応じたメッセージとスタイルを設定
    const intervalConfig = getIntervalConfig(selectedValue);

    indicatorText.textContent = intervalConfig.message;
    indicator.classList.add(intervalConfig.className);

    // アニメーション効果
    indicator.style.transform = 'scale(0.95)';
    setTimeout(() => {
        indicator.style.transform = 'scale(1)';
    }, 150);
}

/**
 * 足設定の取得
 * @param {string} value - 足値
 * @returns {Object} 足設定オブジェクト
 */
function getIntervalConfig(value) {
    const configs = {
        // 分足（短期取引）
        '1m': {
            message: '1分足 - 超短期スキャルピング取引向け',
            className: 'minute-interval'
        },
        '5m': {
            message: '5分足 - 短期デイトレード向け',
            className: 'minute-interval'
        },
        '15m': {
            message: '15分足 - 短期デイトレード向け',
            className: 'minute-interval'
        },
        '30m': {
            message: '30分足 - 短期〜中期デイトレード向け',
            className: 'minute-interval'
        },

        // 時間足（中期取引）
        '1h': {
            message: '1時間足 - 中期スイングトレード向け',
            className: 'hour-interval'
        },

        // 日足・週足・月足（長期取引）
        '1d': {
            message: '日足 - 長期投資・ポジショントレード向け',
            className: 'day-interval'
        },
        '1wk': {
            message: '週足 - 長期投資・トレンド分析向け',
            className: 'week-interval'
        },
        '1mo': {
            message: '月足 - 超長期投資・マクロ分析向け',
            className: 'month-interval'
        }
    };

    return configs[value] || {
        message: '足を選択してください',
        className: 'day-interval'
    };
}

/**
 * 足選択器の状態設定
 * @param {HTMLElement} element - 選択器要素
 * @param {string} state - 状態 ('valid', 'invalid', 'neutral')
 */
function setIntervalSelectorState(element, state) {
    // 既存の状態クラスをクリア
    element.classList.remove('is-valid', 'is-invalid');

    // 新しい状態クラスを追加
    if (state === 'valid') {
        element.classList.add('is-valid');
    } else if (state === 'invalid') {
        element.classList.add('is-invalid');
    }
}

/**
 * 足選択エラーの表示
 * @param {string} message - エラーメッセージ
 */
function showIntervalError(message) {
    const errorElement = document.getElementById('interval-error');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');

        // アクセシビリティ: エラーをアナウンス
        errorElement.setAttribute('aria-live', 'assertive');
    }
}

/**
 * 足選択エラーのクリア
 */
function clearIntervalError() {
    const errorElement = document.getElementById('interval-error');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
        errorElement.setAttribute('aria-live', 'polite');
    }
}

/**
 * フォーカス時のハンドラ
 * @param {Event} event - フォーカスイベント
 */
function handleIntervalFocus(event) {
    // フォーカス時にエラーをクリア
    clearIntervalError();
    setIntervalSelectorState(event.target, 'neutral');
}

/**
 * 選択内容のアナウンス（アクセシビリティ向上）
 * @param {string} selectedValue - 選択された値
 */
function announceIntervalSelection(selectedValue) {
    const config = getIntervalConfig(selectedValue);

    // スクリーンリーダー用の一時的な要素を作成
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';

    announcement.textContent = `足が選択されました: ${config.message}`;

    document.body.appendChild(announcement);

    // 短時間後に要素を削除
    setTimeout(() => {
        if (announcement.parentNode) {
            announcement.parentNode.removeChild(announcement);
        }
    }, 1000);
}

// システム状態管理
const SystemStatusManager = {
    /**
     * 初期化
     */
    init: function() {
        const checkBtn = document.getElementById('system-check-btn');
        if (checkBtn) {
            checkBtn.addEventListener('click', this.runSystemCheck.bind(this));
            console.log('[SystemStatusManager] システム状態確認ボタンのイベントリスナーを設定しました');
        } else {
            console.warn('[SystemStatusManager] system-check-btn要素が見つかりません');
        }
    },

    /**
     * システム状態チェックの実行
     */
    runSystemCheck: async function() {
        const btn = document.getElementById('system-check-btn');
        const resultsContainer = document.getElementById('monitoring-results');

        if (!btn || !resultsContainer) {
            console.error('[SystemStatusManager] 必要な要素が見つかりません');
            return;
        }

        try {
            console.log('[SystemStatusManager] システム状態チェック開始');

            // ボタンを無効化し、テキストを変更
            btn.disabled = true;
            btn.textContent = 'チェック実行中...';

            // 結果コンテナを表示
            resultsContainer.style.display = 'block';

            // 3つのテストを順次実行
            await this.runDatabaseTest();
            await this.runApiTest();
            await this.runHealthCheck();

            console.log('[SystemStatusManager] システム状態チェック完了');

        } catch (error) {
            console.error('[SystemStatusManager] システム状態チェック中にエラーが発生:', error);
            this.showError('システム状態チェック中にエラーが発生しました: ' + error.message);
        } finally {
            // ボタンを元に戻す
            btn.disabled = false;
            btn.textContent = 'システム状態の確認';
        }
    },

    /**
     * データベース接続テスト
     */
    runDatabaseTest: async function() {
        console.log('[SystemStatusManager] データベース接続テスト開始');

        const statusElement = document.getElementById('db-test-status');
        const detailsElement = document.getElementById('db-test-details');
        const resultContainer = document.getElementById('db-test-result');

        if (resultContainer) {
            resultContainer.style.display = 'block';
        }

        if (statusElement) {
            statusElement.textContent = 'テスト中...';
            statusElement.className = 'status status--testing';
        }

        try {
            const response = await fetch('/api/system/db-connection-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            const data = await response.json();
            console.log('[SystemStatusManager] データベース接続テスト結果:', data);

            if (statusElement) {
                if (data.success) {
                    statusElement.textContent = '✅ 正常';
                    statusElement.className = 'status status--success';
                } else {
                    statusElement.textContent = '❌ エラー';
                    statusElement.className = 'status status--error';
                }
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail">
                        <strong>結果:</strong> ${data.success ? '接続成功' : '接続失敗'}
                    </div>
                    <div class="status__detail">
                        <strong>メッセージ:</strong> ${data.message || 'なし'}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return data;
        } catch (error) {
            console.error('[SystemStatusManager] データベース接続テストエラー:', error);

            if (statusElement) {
                statusElement.textContent = '❌ エラー';
                statusElement.className = 'status status--error';
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail status__detail--error">
                        <strong>エラー:</strong> ${error.message}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return { success: false, message: error.message };
        }
    },

    /**
     * API接続テスト
     */
    runApiTest: async function() {
        console.log('[SystemStatusManager] API接続テスト開始');

        const statusElement = document.getElementById('api-test-status');
        const detailsElement = document.getElementById('api-test-details');
        const resultContainer = document.getElementById('api-test-result');

        if (resultContainer) {
            resultContainer.style.display = 'block';
        }

        if (statusElement) {
            statusElement.textContent = 'テスト中...';
            statusElement.className = 'status status--testing';
        }

        try {
            const response = await fetch('/api/system/api-connection-test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol: '7203.T' })
            });

            const data = await response.json();
            console.log('[SystemStatusManager] API接続テスト結果:', data);

            if (statusElement) {
                if (data.success) {
                    statusElement.textContent = '✅ 正常';
                    statusElement.className = 'status status--success';
                } else {
                    statusElement.textContent = '❌ エラー';
                    statusElement.className = 'status status--error';
                }
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail">
                        <strong>結果:</strong> ${data.success ? 'API接続成功' : 'API接続失敗'}
                    </div>
                    <div class="status__detail">
                        <strong>メッセージ:</strong> ${data.message || 'なし'}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return data;
        } catch (error) {
            console.error('[SystemStatusManager] API接続テストエラー:', error);

            if (statusElement) {
                statusElement.textContent = '❌ エラー';
                statusElement.className = 'status status--error';
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail status__detail--error">
                        <strong>エラー:</strong> ${error.message}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return { success: false, message: error.message };
        }
    },

    /**
     * ヘルスチェック
     */
    runHealthCheck: async function() {
        console.log('[SystemStatusManager] ヘルスチェック開始');

        const statusElement = document.getElementById('health-check-status');
        const detailsElement = document.getElementById('health-check-details');
        const resultContainer = document.getElementById('health-check-result');

        if (resultContainer) {
            resultContainer.style.display = 'block';
        }

        if (statusElement) {
            statusElement.textContent = 'チェック中...';
            statusElement.className = 'status status--testing';
        }

        try {
            const response = await fetch('/api/system/health-check');
            const data = await response.json();
            console.log('[SystemStatusManager] ヘルスチェック結果:', data);

            if (statusElement) {
                if (data.status === 'healthy') {
                    statusElement.textContent = '✅ 正常';
                    statusElement.className = 'status status--success';
                } else {
                    statusElement.textContent = '❌ 異常';
                    statusElement.className = 'status status--error';
                }
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail">
                        <strong>ステータス:</strong> ${data.status || '不明'}
                    </div>
                    <div class="status__detail">
                        <strong>メッセージ:</strong> ${data.message || 'なし'}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return data;
        } catch (error) {
            console.error('[SystemStatusManager] ヘルスチェックエラー:', error);

            if (statusElement) {
                statusElement.textContent = '❌ エラー';
                statusElement.className = 'status status--error';
            }

            if (detailsElement) {
                detailsElement.innerHTML = `
                    <div class="status__detail status__detail--error">
                        <strong>エラー:</strong> ${error.message}
                    </div>
                    <div class="status__detail">
                        <strong>実行時刻:</strong> ${new Date().toLocaleString('ja-JP')}
                    </div>
                `;
            }

            return { success: false, message: error.message };
        }
    },

    /**
     * エラー表示
     */
    showError: function(message) {
        const resultsContainer = document.getElementById('monitoring-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            resultsContainer.innerHTML = `
                <div class="alert alert-danger">
                    <strong>エラー:</strong> ${message}
                </div>
            `;
        }
    }
};

// DOMContentLoadedイベントでSystemStatusManagerを初期化
document.addEventListener('DOMContentLoaded', function() {
    SystemStatusManager.init();
});
