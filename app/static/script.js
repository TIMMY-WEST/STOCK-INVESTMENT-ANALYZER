// 株価データ取得システム - JavaScript API連携機能
// Issue #19: JavaScript実装とAPI連携機能

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

        // POST /api/fetch-data への非同期リクエスト
        const response = await fetch('/api/fetch-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symbol, period })
        });

        const result = await response.json();

        if (result.success) {
            showSuccess('データを取得しました', result.data);
            // データテーブル更新
            await loadStockData();
        } else {
            showError(result.message || 'データ取得に失敗しました');
        }

    } catch (error) {
        console.error('データ取得エラー:', error);
        showError('ネットワークエラーが発生しました: ' + error.message);
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
    if (!field) return;

    field.classList.add('form-control-error');

    // エラーメッセージ要素を作成または更新
    let errorElement = field.parentNode.querySelector('.field-error');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'field-error';
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
    document.querySelectorAll('.form-control-error').forEach(el => {
        el.classList.remove('form-control-error');
    });

    // エラーメッセージを非表示
    document.querySelectorAll('.field-error').forEach(el => {
        el.style.display = 'none';
    });
}

// ローディング状態管理
function showLoading() {
    const fetchButton = document.getElementById('fetch-btn');
    const buttonText = fetchButton.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');

    if (fetchButton) {
        fetchButton.disabled = true;
    }

    if (buttonText) {
        buttonText.textContent = 'データ取得中...';
    }

    if (spinner) {
        spinner.style.display = 'inline-block';
    }

    // ローディングメッセージを表示
    if (resultContainer) {
        resultContainer.innerHTML = `
            <div class="alert alert-info">
                <div class="alert-content">
                    <span class="status-icon">📊</span>
                    <span>Yahoo Finance APIからデータを取得中...</span>
                </div>
            </div>
        `;
    }
}

function hideLoading() {
    const fetchButton = document.getElementById('fetch-btn');
    const buttonText = fetchButton.querySelector('.btn-text');
    const spinner = document.getElementById('loading-spinner');

    if (fetchButton) {
        fetchButton.disabled = false;
    }

    if (buttonText) {
        buttonText.textContent = 'データ取得';
    }

    if (spinner) {
        spinner.style.display = 'none';
    }
}

// ステータス表示関数
function showSuccess(message, data) {
    const resultContainer = document.getElementById('result-container');
    if (!resultContainer) return;

    resultContainer.innerHTML = `
        <div class="alert alert-success">
            <div class="alert-title">✅ ${escapeHtml(message)}</div>
            <div class="success-details">
                <div><strong>銘柄:</strong> ${escapeHtml(data.symbol)}</div>
                <div><strong>取得レコード数:</strong> ${formatNumber(data.records_count)}</div>
                <div><strong>保存レコード数:</strong> ${formatNumber(data.saved_records)}</div>
                <div><strong>取得期間:</strong> ${data.date_range.start} ～ ${data.date_range.end}</div>
            </div>
        </div>
    `;

    // 2秒後に自動非表示
    setTimeout(() => {
        if (resultContainer.innerHTML.includes('alert-success')) {
            resultContainer.innerHTML = '';
        }
    }, 5000);
}

function showError(message) {
    const resultContainer = document.getElementById('result-container');
    if (!resultContainer) return;

    resultContainer.innerHTML = `
        <div class="alert alert-error">
            <div class="alert-title">❌ エラー</div>
            <div>${escapeHtml(message)}</div>
        </div>
    `;

    // 5秒後に自動非表示
    setTimeout(() => {
        if (resultContainer.innerHTML.includes('alert-error')) {
            resultContainer.innerHTML = '';
        }
    }, 5000);
}

// 株価データ読み込み (GET /api/stocks への非同期リクエスト)
async function loadStockData(page = null) {
    try {
        const tableBody = document.getElementById('data-table-body');
        const symbolFilter = document.getElementById('view-symbol')?.value?.trim();
        const limit = parseInt(document.getElementById('view-limit')?.value) || 25;

        // ページが指定されている場合は使用、そうでなければ現在のページを使用
        if (page !== null) {
            currentPage = page;
        }
        currentLimit = limit;

        if (tableBody) {
            showLoadingInTable(tableBody);
        }

        // URLパラメータ構築
        const params = new URLSearchParams({
            limit: currentLimit,
            offset: currentPage * currentLimit
        });

        if (symbolFilter) {
            params.append('symbol', symbolFilter);
        }

        const response = await fetch(`/api/stocks?${params.toString()}`);
        const result = await response.json();

        if (result.success) {
            totalRecords = result.pagination.total;
            updateDataTable(result.data);
            updatePagination();
            updateDataSummary(symbolFilter, result.data.length, totalRecords);
        } else {
            showErrorInTable(tableBody, result.message || 'データの読み込みに失敗しました');
        }

    } catch (error) {
        console.error('データ読み込みエラー:', error);
        const tableBody = document.getElementById('data-table-body');
        if (tableBody) {
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
    currentStockData = [...stockData];

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
            <td data-label="日付">${formatDate(stock.date)}</td>
            <td data-label="始値" class="text-right">${formatCurrency(stock.open)}</td>
            <td data-label="高値" class="text-right">${formatCurrency(stock.high)}</td>
            <td data-label="安値" class="text-right">${formatCurrency(stock.low)}</td>
            <td data-label="終値" class="text-right">${formatCurrency(stock.close)}</td>
            <td data-label="出来高" class="text-right">${formatNumber(stock.volume)}</td>
            <td data-label="操作">
                <button type="button" class="btn btn-danger btn-sm" onclick="deleteStock(${stock.id})">
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

// ユーティリティ関数

// HTMLエスケープ
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
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

// テーブルソート機能
let currentStockData = [];
let currentSortColumn = null;
let currentSortDirection = 'asc';

// ページネーション機能
let currentPage = 0;
let currentLimit = 25;
let totalRecords = 0;

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
    if (currentStockData.length === 0) return;

    // ソート方向を決定
    if (currentSortColumn === column) {
        currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        currentSortDirection = 'asc';
        currentSortColumn = column;
    }

    // データをソート
    const sortedData = [...currentStockData].sort((a, b) => {
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
            return currentSortDirection === 'asc' ? -1 : 1;
        }
        if (aValue > bValue) {
            return currentSortDirection === 'asc' ? 1 : -1;
        }
        return 0;
    });

    // ソートされたデータでテーブルを更新
    updateDataTable(sortedData);
    updateSortIcons(column, currentSortDirection);
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
            if (currentPage > 0) {
                loadStockData(currentPage - 1);
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const totalPages = Math.ceil(totalRecords / currentLimit);
            if (currentPage < totalPages - 1) {
                loadStockData(currentPage + 1);
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

    const totalPages = Math.ceil(totalRecords / currentLimit);
    const startRecord = currentPage * currentLimit + 1;
    const endRecord = Math.min((currentPage + 1) * currentLimit, totalRecords);

    // ページネーション情報テキストを更新
    paginationText.textContent = `表示中: ${startRecord}-${endRecord} / 全 ${totalRecords} 件`;

    // ボタンの有効/無効を設定
    prevBtn.disabled = currentPage === 0;
    nextBtn.disabled = currentPage >= totalPages - 1;

    // ページネーションコンテナの表示/非表示
    if (totalRecords > currentLimit) {
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
    }
}