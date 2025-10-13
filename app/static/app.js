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
    fetchStockData: async (symbol, period, interval = '1d') => {
        return ApiService.request('/api/fetch-data', {
            method: 'POST',
            body: JSON.stringify({ symbol, period, interval })
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
        const interval = document.getElementById('interval')?.value || '1d';

        // Enhanced client-side validation
        const validationResult = StockFetchManager.validateForm(symbol, period);
        if (!validationResult.isValid) {
            StockFetchManager.showValidationErrors(validationResult.errors);
            return;
        }

        try {
            AppState.isLoading = true;
            StockFetchManager.setLoadingState(true);

            const response = await ApiService.fetchStockData(symbol, period, interval);

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
        const validPeriods = ['5d', '1wk', '1mo', '3mo', '6mo', '1y', '2y', '5y'];
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

// Bulk Data Fetch Manager
const BulkDataFetchManager = {
    currentJobId: null,
    pollInterval: null,
    socket: null,

    init: () => {
        const startBtn = document.getElementById('bulk-start-btn');
        const stopBtn = document.getElementById('bulk-stop-btn');
        const resetBtn = document.getElementById('bulk-reset-btn');
        const symbolsInput = document.getElementById('bulk-symbols');

        if (startBtn) {
            startBtn.addEventListener('click', BulkDataFetchManager.startBulkFetch);
        }

        if (stopBtn) {
            stopBtn.addEventListener('click', BulkDataFetchManager.stopBulkFetch);
        }

        if (resetBtn) {
            resetBtn.addEventListener('click', BulkDataFetchManager.resetBulkFetch);
        }

        if (symbolsInput) {
            symbolsInput.addEventListener('input', BulkDataFetchManager.updateSymbolCount);
        }

        // Initialize WebSocket if available
        BulkDataFetchManager.initWebSocket();
    },

    initWebSocket: () => {
        // WebSocket接続（Socket.IOが利用可能な場合）
        if (typeof io !== 'undefined') {
            try {
                BulkDataFetchManager.socket = io();

                BulkDataFetchManager.socket.on('bulk_progress', (data) => {
                    if (data.job_id === BulkDataFetchManager.currentJobId) {
                        BulkDataFetchManager.updateProgress(data.progress);
                    }
                });

                BulkDataFetchManager.socket.on('bulk_complete', (data) => {
                    if (data.job_id === BulkDataFetchManager.currentJobId) {
                        BulkDataFetchManager.showResult(data.summary);
                    }
                });
            } catch (error) {
                console.warn('WebSocket not available, using polling instead:', error);
            }
        }
    },

    updateSymbolCount: () => {
        const symbolsInput = document.getElementById('bulk-symbols');
        const countDisplay = document.getElementById('bulk-symbols-count');

        if (!symbolsInput || !countDisplay) return;

        const symbols = BulkDataFetchManager.getSymbolsFromInput();
        countDisplay.innerHTML = `<small>選択銘柄数: ${symbols.length}</small>`;
    },

    getSymbolsFromInput: () => {
        const symbolsInput = document.getElementById('bulk-symbols');
        if (!symbolsInput) return [];

        const text = symbolsInput.value.trim();
        if (!text) return [];

        return text.split('\n')
            .map(s => s.trim())
            .filter(s => s.length > 0);
    },

    startBulkFetch: async () => {
        const symbols = BulkDataFetchManager.getSymbolsFromInput();
        const interval = document.getElementById('bulk-interval')?.value || '1d';
        const period = document.getElementById('bulk-period')?.value || '1mo';

        // Validation
        if (symbols.length === 0) {
            UIComponents.showResult(
                'bulk-result-container',
                'error',
                '入力エラー',
                '銘柄コードを入力してください'
            );
            document.getElementById('bulk-result-section').style.display = 'block';
            return;
        }

        if (symbols.length > 100) {
            UIComponents.showResult(
                'bulk-result-container',
                'error',
                '入力エラー',
                '銘柄数は100以下にしてください'
            );
            document.getElementById('bulk-result-section').style.display = 'block';
            return;
        }

        if (!interval) {
            UIComponents.showResult(
                'bulk-result-container',
                'error',
                '入力エラー',
                '時間軸を選択してください'
            );
            document.getElementById('bulk-result-section').style.display = 'block';
            return;
        }

        try {
            // UI状態を取得中に変更
            BulkDataFetchManager.setFetchingState(true);

            // ジョブ開始API呼び出し
            const response = await fetch('/api/bulk/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': localStorage.getItem('api_key') || ''
                },
                body: JSON.stringify({
                    symbols: symbols,
                    interval: interval,
                    period: period || undefined
                })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                BulkDataFetchManager.currentJobId = data.job_id;

                // 進捗表示セクションを表示
                document.getElementById('bulk-progress-section').style.display = 'block';
                document.getElementById('bulk-total').textContent = symbols.length;

                // WebSocketがない場合はポーリング開始
                if (!BulkDataFetchManager.socket) {
                    BulkDataFetchManager.startPolling();
                }
            } else {
                throw new Error(data.message || 'ジョブの開始に失敗しました');
            }
        } catch (error) {
            BulkDataFetchManager.setFetchingState(false);
            BulkDataFetchManager.showError('一括取得開始エラー', error.message);
        }
    },

    startPolling: () => {
        if (BulkDataFetchManager.pollInterval) {
            clearInterval(BulkDataFetchManager.pollInterval);
        }

        BulkDataFetchManager.pollInterval = setInterval(async () => {
            if (!BulkDataFetchManager.currentJobId) {
                clearInterval(BulkDataFetchManager.pollInterval);
                return;
            }

            try {
                const response = await fetch(`/api/bulk/status/${BulkDataFetchManager.currentJobId}`, {
                    headers: {
                        'X-API-KEY': localStorage.getItem('api_key') || ''
                    }
                });

                const data = await response.json();

                if (data.success && data.job) {
                    const job = data.job;

                    if (job.progress) {
                        BulkDataFetchManager.updateProgress(job.progress);
                    }

                    if (job.status === 'completed') {
                        clearInterval(BulkDataFetchManager.pollInterval);
                        BulkDataFetchManager.showResult(job.summary);
                    } else if (job.status === 'failed') {
                        clearInterval(BulkDataFetchManager.pollInterval);
                        BulkDataFetchManager.showError('一括取得失敗', job.error || '不明なエラー');
                    }
                }
            } catch (error) {
                console.error('Status polling error:', error);
            }
        }, 1000); // 1秒ごとにポーリング
    },

    updateProgress: (progress) => {
        const progressBar = document.getElementById('bulk-progress-bar');
        const progressText = document.getElementById('bulk-progress-text');
        const processed = document.getElementById('bulk-processed');
        const successful = document.getElementById('bulk-successful');
        const failed = document.getElementById('bulk-failed');
        const currentSymbol = document.getElementById('bulk-current-symbol');

        if (progressBar && progressText) {
            const percentage = Math.round(progress.progress_percentage || 0);
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
            progressText.textContent = percentage + '%';
        }

        if (processed) {
            processed.textContent = progress.processed || 0;
        }

        if (successful) {
            successful.textContent = progress.successful || 0;
        }

        if (failed) {
            failed.textContent = progress.failed || 0;
        }

        if (currentSymbol && progress.current_symbol) {
            currentSymbol.textContent = progress.current_symbol;
        }
    },

    showResult: (summary) => {
        BulkDataFetchManager.setFetchingState(false);

        const resultSection = document.getElementById('bulk-result-section');
        const resultContainer = document.getElementById('bulk-result-container');

        if (!resultSection || !resultContainer) return;

        resultSection.style.display = 'block';

        const alert = document.createElement('div');
        alert.className = summary.failed === 0 ? 'alert alert-success' : 'alert alert-warning';
        alert.innerHTML = `
            <div class="alert-title">✅ 一括取得完了</div>
            <div class="mt-2">
                <div class="row">
                    <div class="col">
                        <strong>総銘柄数:</strong> ${Utils.formatNumber(summary.total || 0)}
                    </div>
                    <div class="col">
                        <strong>成功:</strong> <span class="stat-success">${Utils.formatNumber(summary.successful || 0)}</span>
                    </div>
                    <div class="col">
                        <strong>失敗:</strong> <span class="stat-error">${Utils.formatNumber(summary.failed || 0)}</span>
                    </div>
                </div>
                <div class="row mt-1">
                    <div class="col">
                        <strong>ダウンロード件数:</strong> ${Utils.formatNumber(summary.total_downloaded || 0)}
                    </div>
                    <div class="col">
                        <strong>DB格納件数:</strong> ${Utils.formatNumber(summary.total_saved || 0)}
                    </div>
                    <div class="col">
                        <strong>スキップ件数:</strong> ${Utils.formatNumber(summary.total_skipped || 0)}
                    </div>
                </div>
            </div>
        `;

        resultContainer.innerHTML = '';
        resultContainer.appendChild(alert);

        // 自動的にデータテーブルを更新
        if (typeof loadStockData === 'function') {
            console.log('一括取得完了: データテーブルを自動更新中...');
            loadStockData();
        } else {
            console.warn('loadStockData関数が見つかりません');
        }

        // エラー詳細がある場合は表示
        if (summary.errors && summary.errors.length > 0) {
            const errorSection = document.getElementById('bulk-error-section');
            const errorContainer = document.getElementById('bulk-error-container');

            if (errorSection && errorContainer) {
                errorSection.style.display = 'block';

                const errorList = document.createElement('div');
                errorList.className = 'alert alert-danger';
                errorList.innerHTML = `
                    <div class="alert-title">エラー詳細 (${summary.errors.length}件)</div>
                    <ul class="mt-2 mb-0">
                        ${summary.errors.slice(0, 10).map(err =>
                            `<li><strong>${Utils.escapeHtml(err.symbol)}:</strong> ${Utils.escapeHtml(err.error)}</li>`
                        ).join('')}
                        ${summary.errors.length > 10 ? `<li>...他${summary.errors.length - 10}件</li>` : ''}
                    </ul>
                `;

                errorContainer.innerHTML = '';
                errorContainer.appendChild(errorList);
            }
        }
    },

    showError: (title, message) => {
        BulkDataFetchManager.setFetchingState(false);

        const errorSection = document.getElementById('bulk-error-section');
        const errorContainer = document.getElementById('bulk-error-container');

        if (errorSection && errorContainer) {
            errorSection.style.display = 'block';
            const alert = UIComponents.createAlert('error', title, message, false);
            errorContainer.innerHTML = '';
            errorContainer.appendChild(alert);
        }
    },

    stopBulkFetch: async () => {
        if (!BulkDataFetchManager.currentJobId) return;

        try {
            const response = await fetch(`/api/bulk/stop/${BulkDataFetchManager.currentJobId}`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': localStorage.getItem('api_key') || ''
                }
            });

            const data = await response.json();

            if (data.success) {
                BulkDataFetchManager.setFetchingState(false);
                UIComponents.showResult(
                    'bulk-result-container',
                    'warning',
                    'キャンセル',
                    'ジョブのキャンセルをリクエストしました'
                );
                document.getElementById('bulk-result-section').style.display = 'block';
            }
        } catch (error) {
            BulkDataFetchManager.showError('停止エラー', error.message);
        }
    },

    resetBulkFetch: () => {
        // ポーリング停止
        if (BulkDataFetchManager.pollInterval) {
            clearInterval(BulkDataFetchManager.pollInterval);
            BulkDataFetchManager.pollInterval = null;
        }

        // 状態リセット
        BulkDataFetchManager.currentJobId = null;
        BulkDataFetchManager.setFetchingState(false);

        // UI リセット
        document.getElementById('bulk-symbols').value = '';
        document.getElementById('bulk-interval').value = '1d';
        document.getElementById('bulk-period').value = '1mo';
        document.getElementById('bulk-progress-section').style.display = 'none';
        document.getElementById('bulk-result-section').style.display = 'none';
        document.getElementById('bulk-error-section').style.display = 'none';

        BulkDataFetchManager.updateSymbolCount();
    },

    setFetchingState: (isFetching) => {
        const startBtn = document.getElementById('bulk-start-btn');
        const stopBtn = document.getElementById('bulk-stop-btn');
        const resetBtn = document.getElementById('bulk-reset-btn');
        const symbolsInput = document.getElementById('bulk-symbols');
        const intervalSelect = document.getElementById('bulk-interval');
        const periodSelect = document.getElementById('bulk-period');

        if (startBtn) {
            startBtn.disabled = isFetching;
            startBtn.style.display = isFetching ? 'none' : 'inline-block';
        }

        if (stopBtn) {
            stopBtn.disabled = !isFetching;
            stopBtn.style.display = isFetching ? 'inline-block' : 'none';
        }

        if (resetBtn) {
            resetBtn.disabled = isFetching;
        }

        if (symbolsInput) {
            symbolsInput.disabled = isFetching;
        }

        if (intervalSelect) {
            intervalSelect.disabled = isFetching;
        }

        if (periodSelect) {
            periodSelect.disabled = isFetching;
        }
    }
};

// JPX Stock Automation Manager
const JPXAutomationManager = {
    currentJobId: null,
    socket: null,
    pollInterval: null,

    init: () => {
        try {
            // Get UI elements
            const startBtn = document.getElementById('jpx-start-btn');
            const stopBtn = document.getElementById('jpx-stop-btn');
            const intervalInput = document.getElementById('jpx-interval');
            const periodInput = document.getElementById('jpx-period');

            if (startBtn) {
                startBtn.addEventListener('click', JPXAutomationManager.startJPXAutomation);
            }
            if (stopBtn) {
                stopBtn.addEventListener('click', JPXAutomationManager.stopJPXAutomation);
            }

            // Initialize WebSocket for real-time updates
            JPXAutomationManager.initWebSocket();

            console.log('JPX Automation Manager initialized');
        } catch (error) {
            console.error('JPX Automation Manager initialization error:', error);
        }
    },

    initWebSocket: () => {
        try {
            if (typeof io !== 'undefined') {
                JPXAutomationManager.socket = io();

                JPXAutomationManager.socket.on('bulk_progress', (data) => {
                    if (data.job_id === JPXAutomationManager.currentJobId) {
                        JPXAutomationManager.updateProgress(data.progress);
                    }
                });

                JPXAutomationManager.socket.on('bulk_complete', (data) => {
                    if (data.job_id === JPXAutomationManager.currentJobId) {
                        JPXAutomationManager.showResult(data.summary);
                    }
                });

                console.log('JPX WebSocket initialized');
            }
        } catch (error) {
            console.warn('JPX WebSocket initialization failed:', error);
        }
    },

    startJPXAutomation: async () => {
        try {
            const intervalInput = document.getElementById('jpx-interval');
            const periodInput = document.getElementById('jpx-period');
            const interval = intervalInput.value;
            const period = periodInput.value;

            // Validation
            if (!interval) {
                JPXAutomationManager.showError('入力エラー', '時間軸を選択してください');
                return;
            }

            JPXAutomationManager.setProcessingState(true);
            JPXAutomationManager.showStatus('JPX銘柄リストをダウンロード中...');

            // Step 1: Update stock master from JPX
            const updateResponse = await fetch('/api/stock-master/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': localStorage.getItem('api_key') || ''
                },
                body: JSON.stringify({
                    update_type: 'manual'
                })
            });

            if (!updateResponse.ok) {
                const errorData = await updateResponse.json();
                throw new Error(errorData.message || 'JPX銘柄リスト更新エラー');
            }

            const updateResult = await updateResponse.json();
            console.log('JPX update result:', updateResult);

            const stockCount = updateResult.data.total_stocks;
            JPXAutomationManager.updateStockCount(stockCount);
            JPXAutomationManager.showStatus(`JPX銘柄リスト取得完了（${stockCount}銘柄）。株価データ取得を開始します...`);

            // Step 2: Get stock list (with pagination)
            const symbols = [];
            const limit = 1000; // API limit per request
            let offset = 0;
            let hasMore = true;

            while (hasMore) {
                const listResponse = await fetch(`/api/stock-master/list?limit=${limit}&offset=${offset}`, {
                    method: 'GET',
                    headers: {
                        'X-API-KEY': localStorage.getItem('api_key') || ''
                    }
                });

                if (!listResponse.ok) {
                    throw new Error('銘柄リスト取得エラー');
                }

                const listResult = await listResponse.json();
                const batchSymbols = listResult.data.stocks.map(stock => stock.stock_code);
                symbols.push(...batchSymbols);

                // Check if there are more records
                if (batchSymbols.length < limit) {
                    hasMore = false;
                } else {
                    offset += limit;
                    JPXAutomationManager.showStatus(`銘柄リスト取得中... (${symbols.length}/${stockCount})`);
                }
            }

            console.log(`Starting bulk fetch for ${symbols.length} symbols`);

            // Step 3: Start bulk fetch
            console.log('[JPXAutomationManager] 一括取得APIリクエスト開始');
            console.log('[JPXAutomationManager] リクエストパラメータ:', {
                symbolsCount: symbols.length,
                interval: interval,
                period: period,
                apiKey: localStorage.getItem('api_key') ? '設定済み' : '未設定'
            });

            const bulkResponse = await fetch('/api/bulk/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': localStorage.getItem('api_key') || ''
                },
                body: JSON.stringify({
                    symbols: symbols,
                    interval: interval,
                    period: period || undefined
                })
            });

            console.log('[JPXAutomationManager] APIレスポンス受信:', {
                status: bulkResponse.status,
                statusText: bulkResponse.statusText,
                ok: bulkResponse.ok
            });

            if (!bulkResponse.ok) {
                let errorMessage = '一括取得開始エラー';
                try {
                    const errorData = await bulkResponse.json();
                    console.error('[JPXAutomationManager] APIエラーレスポンス:', errorData);
                    errorMessage = errorData.message || errorMessage;
                } catch (parseError) {
                    console.error('[JPXAutomationManager] エラーレスポンスのパースに失敗:', parseError);
                    errorMessage = `HTTP ${bulkResponse.status}: ${bulkResponse.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const bulkResult = await bulkResponse.json();
            console.log('[JPXAutomationManager] 一括取得開始成功:', bulkResult);
            
            JPXAutomationManager.currentJobId = bulkResult.job_id;

            JPXAutomationManager.showProgressSection();
            JPXAutomationManager.showStatus('株価データ取得中...');

            // Start polling if WebSocket is not available
            if (!JPXAutomationManager.socket) {
                console.log('[JPXAutomationManager] WebSocket未接続のため、ポーリング開始');
                JPXAutomationManager.startPolling();
            } else {
                console.log('[JPXAutomationManager] WebSocket接続済み、リアルタイム進捗受信待機');
            }

        } catch (error) {
            console.error('JPX automation error:', error);
            JPXAutomationManager.setProcessingState(false);
            JPXAutomationManager.showError('JPX自動取得エラー', error.message);
        }
    },

    startPolling: () => {
        console.log('[JPXAutomationManager] ポーリング開始');
        JPXAutomationManager.pollInterval = setInterval(async () => {
            if (!JPXAutomationManager.currentJobId) {
                console.log('[JPXAutomationManager] ジョブIDが無いためポーリング停止');
                clearInterval(JPXAutomationManager.pollInterval);
                return;
            }

            try {
                console.log(`[JPXAutomationManager] ステータス取得開始: job_id=${JPXAutomationManager.currentJobId}`);
                const response = await fetch(`/api/bulk/status/${JPXAutomationManager.currentJobId}`, {
                    headers: {
                        'X-API-KEY': localStorage.getItem('api_key') || ''
                    }
                });

                console.log(`[JPXAutomationManager] ステータスレスポンス: status=${response.status}, ok=${response.ok}`);

                if (response.ok) {
                    const data = await response.json();
                    console.log('[JPXAutomationManager] ステータスデータ:', data);
                    
                    if (data.success && data.job) {
                        const job = data.job;
                        console.log(`[JPXAutomationManager] ジョブステータス: ${job.status}, 進捗: ${job.progress?.progress_percentage || 0}%`);

                        JPXAutomationManager.updateProgress(job.progress);

                        if (job.status === 'completed') {
                            console.log('[JPXAutomationManager] ジョブ完了、ポーリング停止');
                            clearInterval(JPXAutomationManager.pollInterval);
                            JPXAutomationManager.showResult(job.summary);
                        } else if (job.status === 'failed') {
                            console.log('[JPXAutomationManager] ジョブ失敗、ポーリング停止');
                            clearInterval(JPXAutomationManager.pollInterval);
                            JPXAutomationManager.showError('一括取得失敗', job.error || '不明なエラー');
                        }
                    } else {
                        console.error('[JPXAutomationManager] ステータスレスポンスが無効:', data);
                    }
                } else {
                    console.error(`[JPXAutomationManager] ステータス取得エラー: ${response.status} ${response.statusText}`);
                    try {
                        const errorData = await response.json();
                        console.error('[JPXAutomationManager] エラーレスポンス:', errorData);
                    } catch (parseError) {
                        console.error('[JPXAutomationManager] エラーレスポンスのパースに失敗:', parseError);
                    }
                }
            } catch (error) {
                console.error('[JPXAutomationManager] ポーリングエラー:', error);
            }
        }, 2000);
    },

    updateProgress: (progress) => {
        const progressBar = document.getElementById('jpx-progress-bar');
        const progressText = document.getElementById('jpx-progress-text');
        const processedEl = document.getElementById('jpx-processed');
        const totalEl = document.getElementById('jpx-total');
        const successfulEl = document.getElementById('jpx-successful');
        const failedEl = document.getElementById('jpx-failed');
        const currentSymbolEl = document.getElementById('jpx-current-symbol');

        if (progressBar && progressText) {
            const percentage = progress.progress_percentage || 0;
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
            progressText.textContent = `${Math.round(percentage)}%`;
        }

        if (processedEl) processedEl.textContent = progress.processed || 0;
        if (totalEl) totalEl.textContent = progress.total || 0;
        if (successfulEl) successfulEl.textContent = progress.successful || 0;
        if (failedEl) failedEl.textContent = progress.failed || 0;
        if (currentSymbolEl && progress.current_symbol) {
            currentSymbolEl.textContent = progress.current_symbol;
        }
    },

    showProgressSection: () => {
        const progressSection = document.getElementById('jpx-progress-section');
        if (progressSection) {
            progressSection.style.display = 'block';
        }
    },

    showStatus: (message) => {
        const statusSection = document.getElementById('jpx-status-section');
        const statusEl = document.getElementById('jpx-status');

        if (statusSection) {
            statusSection.style.display = 'block';
        }
        if (statusEl) {
            statusEl.textContent = message;
        }
    },

    updateStockCount: (count) => {
        const stockCountEl = document.getElementById('jpx-stock-count');
        if (stockCountEl) {
            stockCountEl.textContent = count;
        }
    },

    showResult: (summary) => {
        JPXAutomationManager.setProcessingState(false);

        const resultSection = document.getElementById('jpx-result-section');
        const resultContainer = document.getElementById('jpx-result-container');

        if (resultContainer) {
            resultContainer.innerHTML = `
                <div class="alert alert-success">
                    <h4>取得完了</h4>
                    <p>全銘柄の株価データ取得が完了しました。</p>
                    <ul>
                        <li>合計銘柄数: ${summary.total_symbols}</li>
                        <li>成功: ${summary.successful}</li>
                        <li>失敗: ${summary.failed}</li>
                        <li>処理時間: ${summary.duration_seconds ? summary.duration_seconds.toFixed(2) + '秒' : 'N/A'}</li>
                    </ul>
                </div>
            `;
        }

        if (resultSection) {
            resultSection.style.display = 'block';
        }

        JPXAutomationManager.showStatus('完了');
    },

    showError: (title, message) => {
        const errorSection = document.getElementById('jpx-error-section');
        const errorContainer = document.getElementById('jpx-error-container');

        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h4>${Utils.escapeHtml(title)}</h4>
                    <p>${Utils.escapeHtml(message)}</p>
                </div>
            `;
        }

        if (errorSection) {
            errorSection.style.display = 'block';
        }
    },

    stopJPXAutomation: async () => {
        if (!JPXAutomationManager.currentJobId) return;

        try {
            const response = await fetch(`/api/bulk/stop/${JPXAutomationManager.currentJobId}`, {
                method: 'POST',
                headers: {
                    'X-API-KEY': localStorage.getItem('api_key') || ''
                }
            });

            if (response.ok) {
                JPXAutomationManager.setProcessingState(false);
                JPXAutomationManager.showStatus('停止しました');
            }
        } catch (error) {
            console.error('Stop error:', error);
            JPXAutomationManager.showError('停止エラー', error.message);
        }
    },

    setProcessingState: (isProcessing) => {
        const startBtn = document.getElementById('jpx-start-btn');
        const stopBtn = document.getElementById('jpx-stop-btn');
        const intervalInput = document.getElementById('jpx-interval');
        const periodInput = document.getElementById('jpx-period');

        if (startBtn) {
            startBtn.disabled = isProcessing;
            startBtn.style.display = isProcessing ? 'none' : 'inline-block';
        }

        if (stopBtn) {
            stopBtn.disabled = !isProcessing;
            stopBtn.style.display = isProcessing ? 'inline-block' : 'none';
        }

        if (intervalInput) intervalInput.disabled = isProcessing;
        if (periodInput) periodInput.disabled = isProcessing;

        if (!isProcessing) {
            if (JPXAutomationManager.pollInterval) {
                clearInterval(JPXAutomationManager.pollInterval);
                JPXAutomationManager.pollInterval = null;
            }
            JPXAutomationManager.currentJobId = null;
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
            BulkDataFetchManager.init();
            JPXAutomationManager.init();

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