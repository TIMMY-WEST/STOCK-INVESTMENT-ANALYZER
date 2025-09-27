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
        const resetBtn = document.getElementById('reset-btn');

        if (form) {
            form.addEventListener('submit', StockFetchManager.handleSubmit);
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', StockFetchManager.handleReset);
        }
    },

    handleSubmit: async (event) => {
        event.preventDefault();

        if (AppState.isLoading) return;

        const symbol = document.getElementById('symbol')?.value?.trim();
        const period = document.getElementById('period')?.value;

        // Enhanced client-side validation
        const validationResult = StockFetchManager.validateForm(symbol, period);
        if (!validationResult.isValid) {
            StockFetchManager.showValidationErrors(validationResult.errors);
            return;
        }

        try {
            AppState.isLoading = true;
            StockFetchManager.setLoadingState(true);

            const response = await ApiService.fetchStockData(symbol, period);

            if (response.success) {
                const { data } = response;

                // Complete progress bar
                const progressBar = document.getElementById('fetch-progress');
                if (progressBar) {
                    progressBar.style.width = '100%';
                }

                // Show enhanced success message
                setTimeout(() => {
                    StockFetchManager.showSuccessMessage(data);

                    // Refresh data table if visible
                    if (document.getElementById('data-table-body').children.length > 1) {
                        StockDataManager.loadData();
                    }
                }, 500);
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
        const resetBtn = document.getElementById('reset-btn');
        const resultContainer = document.getElementById('result-container');

        if (btn && btnText && spinner) {
            btn.disabled = loading;
            btnText.textContent = loading ? 'データ取得中...' : 'データ取得';
            spinner.style.display = loading ? 'inline-block' : 'none';

            // Enhanced button loading animation
            if (loading) {
                btn.classList.add('loading');
            } else {
                btn.classList.remove('loading');
            }
        }

        if (resetBtn) {
            resetBtn.disabled = loading;
        }

        // Show progress container during loading
        if (loading) {
            StockFetchManager.showProgressBar(resultContainer);
        } else {
            StockFetchManager.hideProgressBar();
        }
    },

    showProgressBar: (container) => {
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-info">
                <div class="alert-title">
                    <span class="loading" aria-hidden="true"></span>
                    データ取得中
                </div>
                <div>Yahoo Finance APIからデータを取得しています...</div>
                <div class="progress-container mt-2">
                    <div class="progress-bar" id="fetch-progress"></div>
                </div>
            </div>
        `;

        // Simulate progress
        const progressBar = document.getElementById('fetch-progress');
        if (progressBar) {
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15;
                if (progress > 85) progress = 85; // Don't go to 100% until actual completion
                progressBar.style.width = progress + '%';
            }, 300);

            // Store interval ID for cleanup
            container.dataset.progressInterval = interval;
        }
    },

    hideProgressBar: () => {
        const container = document.getElementById('result-container');
        if (container && container.dataset.progressInterval) {
            clearInterval(container.dataset.progressInterval);
            delete container.dataset.progressInterval;
        }
    },

    handleReset: () => {
        const form = document.getElementById('fetch-form');
        const resultContainer = document.getElementById('result-container');

        if (form) {
            // Reset form to default values
            document.getElementById('symbol').value = '7203.T';
            document.getElementById('period').value = '1mo';

            // Clear any validation errors
            StockFetchManager.clearValidationErrors();
        }

        if (resultContainer) {
            resultContainer.innerHTML = '';
        }
    },

    validateForm: (symbol, period) => {
        const errors = [];

        // Validate symbol
        if (!symbol) {
            errors.push({
                field: 'symbol',
                message: '銘柄コードを入力してください'
            });
        } else if (!symbol.match(/^[0-9]{4}\.T$/)) {
            errors.push({
                field: 'symbol',
                message: '正しい銘柄コード形式で入力してください（例: 7203.T）'
            });
        }

        // Validate period
        const validPeriods = ['5d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'];
        if (!validPeriods.includes(period)) {
            errors.push({
                field: 'period',
                message: '有効な期間を選択してください'
            });
        }

        return {
            isValid: errors.length === 0,
            errors: errors
        };
    },

    showValidationErrors: (errors) => {
        // Clear previous errors
        StockFetchManager.clearValidationErrors();

        errors.forEach(error => {
            const field = document.getElementById(error.field);
            if (field) {
                field.classList.add('form-control-error');

                // Create error element if it doesn't exist
                let errorElement = field.parentNode.querySelector('.field-error');
                if (!errorElement) {
                    errorElement = document.createElement('div');
                    errorElement.className = 'field-error text-danger mt-1';
                    field.parentNode.appendChild(errorElement);
                }

                errorElement.textContent = error.message;
                errorElement.style.display = 'block';
            }
        });

        // Show summary error in result container
        const summaryMessage = errors.map(e => e.message).join(', ');
        UIComponents.showResult('result-container', 'error', 'バリデーションエラー', summaryMessage);
    },

    clearValidationErrors: () => {
        // Remove error classes from form controls
        document.querySelectorAll('.form-control-error').forEach(element => {
            element.classList.remove('form-control-error');
        });

        // Hide error messages
        document.querySelectorAll('.field-error').forEach(element => {
            element.style.display = 'none';
        });
    },

    showSuccessMessage: (data) => {
        const container = document.getElementById('result-container');
        if (!container) return;

        container.innerHTML = `
            <div class="alert alert-success">
                <div class="alert-title">
                    ✅ データ取得完了
                </div>
                <div class="success-details mt-2">
                    <div class="row">
                        <div class="col">
                            <strong>銘柄:</strong> ${Utils.escapeHtml(data.symbol)}
                        </div>
                        <div class="col">
                            <strong>取得レコード数:</strong> ${Utils.formatNumber(data.records_count)}
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col">
                            <strong>保存件数:</strong> ${Utils.formatNumber(data.saved_records)}
                        </div>
                        <div class="col">
                            <strong>取得期間:</strong> ${data.date_range.start} ～ ${data.date_range.end}
                        </div>
                    </div>
                </div>
                <div class="success-actions mt-3">
                    <button type="button" class="btn btn-sm btn-secondary" onclick="StockDataManager.loadData()">
                        データテーブルを更新
                    </button>
                </div>
            </div>
        `;

        // Add confetti animation for success
        StockFetchManager.showSuccessAnimation();
    },

    showSuccessAnimation: () => {
        // Simple confetti-like animation
        const container = document.getElementById('result-container');
        if (!container) return;

        const colors = ['#28a745', '#007bff', '#ffc107', '#17a2b8'];

        for (let i = 0; i < 15; i++) {
            setTimeout(() => {
                const confetti = document.createElement('div');
                confetti.style.cssText = `
                    position: absolute;
                    width: 8px;
                    height: 8px;
                    background: ${colors[Math.floor(Math.random() * colors.length)]};
                    border-radius: 50%;
                    pointer-events: none;
                    z-index: 1000;
                    left: ${Math.random() * 100}%;
                    top: 0;
                    opacity: 0.8;
                    animation: confettiFall 2s ease-out forwards;
                `;

                // Add confetti CSS animation if not exists
                if (!document.getElementById('confetti-styles')) {
                    const style = document.createElement('style');
                    style.id = 'confetti-styles';
                    style.textContent = `
                        @keyframes confettiFall {
                            to {
                                transform: translateY(100vh) rotate(360deg);
                                opacity: 0;
                            }
                        }
                    `;
                    document.head.appendChild(style);
                }

                container.style.position = 'relative';
                container.appendChild(confetti);

                // Remove confetti after animation
                setTimeout(() => {
                    if (confetti.parentNode) {
                        confetti.parentNode.removeChild(confetti);
                    }
                }, 2000);
            }, i * 100);
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
                page: AppState.currentPage,
                limit: limit
            };

            if (symbolFilter) {
                filters.symbol = symbolFilter;
                AppState.currentSymbol = symbolFilter;
            }

            const response = await ApiService.getStocks(filters);

            if (response.success) {
                const { data, pagination } = response;
                AppState.totalRecords = pagination.total;

                StockDataManager.renderTable(data);
                UIComponents.updatePagination(
                    pagination.page,
                    pagination.total,
                    pagination.limit,
                    pagination.has_next
                );
            } else {
                if (tableBody) {
                    tableBody.innerHTML = `
                        <tr>
                            <td colspan="9" class="text-center text-danger">
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
                        <td colspan="9" class="text-center text-danger">
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
                    <td colspan="9" class="text-center text-muted">
                        データが見つかりませんでした
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = stocks.map(stock => UIComponents.createStockTableRow(stock)).join('');
    },

    changePage: (direction) => {
        AppState.currentPage = Math.max(0, AppState.currentPage + direction);
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

                // Show success message
                UIComponents.showResult(
                    'result-container',
                    'success',
                    '削除完了',
                    'データが正常に削除されました'
                );

                // Reload data to update pagination
                setTimeout(() => {
                    StockDataManager.loadData();
                }, 1000);
            } else {
                UIComponents.showResult(
                    'result-container',
                    'error',
                    '削除エラー',
                    `削除に失敗しました: ${response.message}`
                );
            }
        } catch (error) {
            UIComponents.showResult(
                'result-container',
                'error',
                '削除エラー',
                `削除処理中にエラーが発生しました: ${error.message}`
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
        const statusContainer = document.getElementById('connection-status');

        if (!btn || !statusContainer) return;

        try {
            btn.disabled = true;
            btn.textContent = 'テスト中...';

            const response = await ApiService.testConnection();

            if (response.success) {
                statusContainer.innerHTML = `
                    <div class="alert alert-success">
                        <div class="alert-title">✅ 接続成功</div>
                        <div>データベースへの接続が正常に確立されました</div>
                        <div class="mt-2">
                            <small>
                                <strong>データベース:</strong> ${Utils.escapeHtml(response.database_info.name)}<br>
                                <strong>テーブル数:</strong> ${response.database_info.tables}<br>
                                <strong>レコード数:</strong> ${Utils.formatNumber(response.database_info.total_records)}
                            </small>
                        </div>
                    </div>
                `;
            } else {
                statusContainer.innerHTML = `
                    <div class="alert alert-error">
                        <div class="alert-title">❌ 接続失敗</div>
                        <div>${Utils.escapeHtml(response.message)}</div>
                    </div>
                `;
            }
        } catch (error) {
            statusContainer.innerHTML = `
                <div class="alert alert-error">
                    <div class="alert-title">❌ 接続エラー</div>
                    <div>サーバーとの通信に失敗しました: ${Utils.escapeHtml(error.message)}</div>
                </div>
            `;
        } finally {
            btn.disabled = false;
            btn.textContent = '接続テスト';
        }
    }
};

// Accessibility Manager
const AccessibilityManager = {
    init: () => {
        // Add keyboard navigation support
        document.addEventListener('keydown', AccessibilityManager.handleKeydown);

        // Add focus management for modals and alerts
        AccessibilityManager.setupFocusManagement();

        // Add ARIA live regions for dynamic content
        AccessibilityManager.setupLiveRegions();
    },

    handleKeydown: (event) => {
        // ESC key to close alerts
        if (event.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => {
                if (alert.style.display !== 'none') {
                    alert.remove();
                }
            });
        }
    },

    setupFocusManagement: () => {
        // Ensure proper focus management for dynamic content
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('alert')) {
                            // Focus on new alerts for screen readers
                            node.setAttribute('tabindex', '-1');
                            node.focus();
                        }
                    });
                }
            });
        });

        observer.observe(document.body, { childList: true, subtree: true });
    },

    setupLiveRegions: () => {
        // Create ARIA live region for status updates
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'live-region';
        document.body.appendChild(liveRegion);
    }
};

// Main App Initialization
const App = {
    init: () => {
        // Wait for DOM to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', App.initializeApp);
        } else {
            App.initializeApp();
        }
    },

    initializeApp: () => {
        // Initialize all managers
        StockFetchManager.init();
        StockDataManager.init();
        SystemStatusManager.init();
        AccessibilityManager.init();

        console.log('Stock Investment Analyzer - Application initialized successfully');
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

// Export for testing (if in Node.js environment)
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