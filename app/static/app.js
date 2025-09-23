// Stock Data Management System - JavaScript
// Version: 1.0.0

// Global state management
const AppState = {
    currentPage: 0,
    currentLimit: 25,
    currentSymbol: '',
    totalRecords: 0,
    isLoading: false
};

// Utility functions
const Utils = {
    // Format number with thousands separator
    formatNumber: (num) => {
        return new Intl.NumberFormat('ja-JP').format(num);
    },

    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('ja-JP', {
            style: 'currency',
            currency: 'JPY',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    },

    // Format date
    formatDate: (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
    },

    // Escape HTML to prevent XSS
    escapeHtml: (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // Show loading state
    showLoading: (element, loadingText = 'Loading...') => {
        if (element) {
            element.innerHTML = `
                <div class="loading-text">
                    <span class="loading" aria-hidden="true"></span>
                    ${Utils.escapeHtml(loadingText)}
                </div>
            `;
        }
    },

    // Debounce function for search input
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// API service
const ApiService = {
    // Base API request handler
    request: async (url, options = {}) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // Fetch stock data from Yahoo Finance
    fetchStockData: async (symbol, period) => {
        return ApiService.request('/api/fetch-data', {
            method: 'POST',
            body: JSON.stringify({ symbol, period })
        });
    },

    // Get stocks with filters
    getStocks: async (filters = {}) => {
        const params = new URLSearchParams();

        Object.entries(filters).forEach(([key, value]) => {
            if (value !== null && value !== undefined && value !== '') {
                params.append(key, value);
            }
        });

        const url = `/api/stocks${params.toString() ? '?' + params.toString() : ''}`;
        return ApiService.request(url);
    },

    // Test database connection
    testConnection: async () => {
        return ApiService.request('/api/test-connection');
    },

    // Delete stock data
    deleteStock: async (stockId) => {
        return ApiService.request(`/api/stocks/${stockId}`, {
            method: 'DELETE'
        });
    }
};

// UI Components
const UIComponents = {
    // Create alert component
    createAlert: (type, title, message, autoHide = true) => {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type}`;
        alertElement.innerHTML = `
            <div class="alert-title">${Utils.escapeHtml(title)}</div>
            <div>${Utils.escapeHtml(message)}</div>
        `;

        if (autoHide) {
            setTimeout(() => {
                if (alertElement.parentNode) {
                    alertElement.remove();
                }
            }, 5000);
        }

        return alertElement;
    },

    // Show result in container
    showResult: (containerId, type, title, message, autoHide = true) => {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        const alert = UIComponents.createAlert(type, title, message, autoHide);
        container.appendChild(alert);
    },

    // Create table row for stock data
    createStockTableRow: (stock) => {
        return `
            <tr data-stock-id="${stock.id}">
                <td>${stock.id}</td>
                <td>${Utils.escapeHtml(stock.symbol)}</td>
                <td>${Utils.formatDate(stock.date)}</td>
                <td>${Utils.formatCurrency(stock.open)}</td>
                <td>${Utils.formatCurrency(stock.high)}</td>
                <td>${Utils.formatCurrency(stock.low)}</td>
                <td>${Utils.formatCurrency(stock.close)}</td>
                <td>${Utils.formatNumber(stock.volume)}</td>
                <td>
                    <button
                        type="button"
                        class="btn btn-danger btn-sm"
                        onclick="StockDataManager.deleteStock(${stock.id})"
                        aria-label="Delete stock data for ${Utils.escapeHtml(stock.symbol)} on ${Utils.formatDate(stock.date)}"
                    >
                        削除
                    </button>
                </td>
            </tr>
        `;
    },

    // Update pagination info and controls
    updatePagination: (current, total, limit, hasNext) => {
        const paginationElement = document.getElementById('pagination');
        const paginationText = document.getElementById('pagination-text');
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');

        if (!paginationElement || !paginationText) return;

        const start = current * limit + 1;
        const end = Math.min((current + 1) * limit, total);

        paginationText.textContent = `表示中: ${start}-${end} / 全 ${Utils.formatNumber(total)} 件`;

        if (prevBtn) {
            prevBtn.disabled = current === 0;
        }

        if (nextBtn) {
            nextBtn.disabled = !hasNext;
        }

        paginationElement.style.display = total > 0 ? 'flex' : 'none';
    }
};

// Stock Data Fetch Manager
const StockFetchManager = {
    init: () => {
        const form = document.getElementById('fetch-form');
        if (form) {
            form.addEventListener('submit', StockFetchManager.handleSubmit);
        }
    },

    handleSubmit: async (event) => {
        event.preventDefault();

        if (AppState.isLoading) return;

        const symbol = document.getElementById('symbol')?.value?.trim();
        const period = document.getElementById('period')?.value;

        if (!symbol) {
            UIComponents.showResult('result-container', 'error', 'エラー', '銘柄コードを入力してください');
            return;
        }

        try {
            AppState.isLoading = true;
            StockFetchManager.setLoadingState(true);

            const response = await ApiService.fetchStockData(symbol, period);

            if (response.success) {
                const { data } = response;
                UIComponents.showResult(
                    'result-container',
                    'success',
                    '取得成功',
                    `銘柄: ${data.symbol} | レコード数: ${Utils.formatNumber(data.records_count)} | 保存件数: ${Utils.formatNumber(data.saved_records)} | 期間: ${data.date_range.start} ～ ${data.date_range.end}`
                );

                // Refresh data table if visible
                if (document.getElementById('data-table-body').children.length > 1) {
                    StockDataManager.loadData();
                }
            } else {
                UIComponents.showResult(
                    'result-container',
                    'error',
                    'エラー',
                    `${response.error}: ${response.message}`
                );
            }
        } catch (error) {
            UIComponents.showResult(
                'result-container',
                'error',
                '通信エラー',
                `サーバーとの通信に失敗しました: ${error.message}`
            );
        } finally {
            AppState.isLoading = false;
            StockFetchManager.setLoadingState(false);
        }
    },

    setLoadingState: (loading) => {
        const btn = document.getElementById('fetch-btn');
        const btnText = btn?.querySelector('.btn-text');
        const spinner = document.getElementById('loading-spinner');

        if (btn && btnText && spinner) {
            btn.disabled = loading;
            btnText.textContent = loading ? 'データ取得中...' : 'データ取得';
            spinner.style.display = loading ? 'inline-block' : 'none';
        }
    }
};

// Stock Data Manager
const StockDataManager = {
    init: () => {
        const loadBtn = document.getElementById('load-data-btn');
        const prevBtn = document.getElementById('prev-page-btn');
        const nextBtn = document.getElementById('next-page-btn');

        if (loadBtn) {
            loadBtn.addEventListener('click', StockDataManager.loadData);
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => StockDataManager.changePage(-1));
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => StockDataManager.changePage(1));
        }

        // Auto-load data on filter change (debounced)
        const symbolFilter = document.getElementById('view-symbol');
        const limitFilter = document.getElementById('view-limit');

        if (symbolFilter) {
            symbolFilter.addEventListener('input', Utils.debounce(() => {
                AppState.currentPage = 0;
                StockDataManager.loadData();
            }, 500));
        }

        if (limitFilter) {
            limitFilter.addEventListener('change', () => {
                AppState.currentPage = 0;
                AppState.currentLimit = parseInt(limitFilter.value);
                StockDataManager.loadData();
            });
        }
    },

    loadData: async () => {
        if (AppState.isLoading) return;

        try {
            AppState.isLoading = true;
            const tableBody = document.getElementById('data-table-body');
            const symbolFilter = document.getElementById('view-symbol')?.value?.trim();
            const limit = parseInt(document.getElementById('view-limit')?.value) || 25;

            if (tableBody) {
                Utils.showLoading(tableBody, 'データを読み込み中...');
            }

            const filters = {
                symbol: symbolFilter || undefined,
                limit: limit,
                offset: AppState.currentPage * limit
            };

            const response = await ApiService.getStocks(filters);

            if (response.success) {
                AppState.currentSymbol = symbolFilter;
                AppState.currentLimit = limit;
                AppState.totalRecords = response.pagination.total;

                StockDataManager.renderTable(response.data);
                UIComponents.updatePagination(
                    AppState.currentPage,
                    response.pagination.total,
                    response.pagination.limit,
                    response.pagination.has_next
                );
            } else {
                if (tableBody) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="9" class="text-center error">
                                データの読み込みに失敗しました: ${Utils.escapeHtml(response.message)}
                            </td>
                        </tr>
                    `;
                }
            }
        } catch (error) {
            const tableBody = document.getElementById('data-table-body');
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" class="text-center error">
                            エラーが発生しました: ${Utils.escapeHtml(error.message)}
                        </td>
                    </tr>
                `;
            }
        } finally {
            AppState.isLoading = false;
        }
    },

    renderTable: (stocks) => {
        const tableBody = document.getElementById('data-table-body');
        if (!tableBody) return;

        if (stocks.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center loading-text">
                        データが見つかりませんでした
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = stocks.map(stock =>
            UIComponents.createStockTableRow(stock)
        ).join('');
    },

    changePage: (direction) => {
        const newPage = AppState.currentPage + direction;
        if (newPage < 0) return;

        AppState.currentPage = newPage;
        StockDataManager.loadData();
    },

    deleteStock: async (stockId) => {
        if (!confirm('このデータを削除してもよろしいですか？')) {
            return;
        }

        try {
            const response = await ApiService.deleteStock(stockId);

            if (response.success) {
                // Remove row from table
                const row = document.querySelector(`tr[data-stock-id="${stockId}"]`);
                if (row) {
                    row.remove();
                }

                UIComponents.showResult(
                    'result-container',
                    'success',
                    '削除完了',
                    response.message
                );

                // Reload data to update pagination
                StockDataManager.loadData();
            } else {
                UIComponents.showResult(
                    'result-container',
                    'error',
                    '削除エラー',
                    response.message
                );
            }
        } catch (error) {
            UIComponents.showResult(
                'result-container',
                'error',
                '削除エラー',
                `削除に失敗しました: ${error.message}`
            );
        }
    }
};

// System Status Manager
const SystemStatusManager = {
    init: () => {
        const testBtn = document.getElementById('test-connection-btn');
        if (testBtn) {
            testBtn.addEventListener('click', SystemStatusManager.testConnection);
        }
    },

    testConnection: async () => {
        const btn = document.getElementById('test-connection-btn');
        const resultContainer = document.getElementById('connection-result');

        if (!btn || !resultContainer) return;

        try {
            btn.disabled = true;
            btn.textContent = 'テスト実行中...';
            resultContainer.innerHTML = '';

            const response = await ApiService.testConnection();

            if (response.success) {
                const alert = UIComponents.createAlert(
                    'success',
                    '接続成功',
                    `${response.message} (データベース: ${response.database}, ユーザー: ${response.user})`
                );
                resultContainer.appendChild(alert);
            } else {
                const alert = UIComponents.createAlert(
                    'error',
                    '接続失敗',
                    response.message
                );
                resultContainer.appendChild(alert);
            }
        } catch (error) {
            const alert = UIComponents.createAlert(
                'error',
                '接続エラー',
                `接続テストに失敗しました: ${error.message}`
            );
            resultContainer.appendChild(alert);
        } finally {
            btn.disabled = false;
            btn.textContent = '接続テスト実行';
        }
    }
};

// Accessibility enhancements
const AccessibilityManager = {
    init: () => {
        // Add keyboard navigation for buttons
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' && event.target.classList.contains('btn')) {
                event.target.click();
            }
        });

        // Improve focus management
        document.addEventListener('focusin', (event) => {
            if (event.target.classList.contains('form-control')) {
                event.target.setAttribute('aria-expanded', 'false');
            }
        });

        // Add skip links functionality
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (event) => {
                event.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        }
    }
};

// Application initialization
const App = {
    init: () => {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', App.initializeApp);
        } else {
            App.initializeApp();
        }
    },

    initializeApp: () => {
        try {
            // Initialize all managers
            StockFetchManager.init();
            StockDataManager.init();
            SystemStatusManager.init();
            AccessibilityManager.init();

            console.log('Stock Data Management System initialized successfully');
        } catch (error) {
            console.error('Failed to initialize application:', error);
        }
    }
};

// Start the application
App.init();

// Global error handling
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    event.preventDefault();
});

// Export for potential testing or external access
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        AppState,
        Utils,
        ApiService,
        UIComponents,
        StockFetchManager,
        StockDataManager,
        SystemStatusManager
    };
}