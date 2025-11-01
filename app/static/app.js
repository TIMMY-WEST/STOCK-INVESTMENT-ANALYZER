/**
 * 株価データ取得システム - 共通ユーティリティとサービス
 * ES6 Module版
 */

// 新しい状態管理システムをインポート
import { AppState as NewAppState, AppStateManager, appStateManager } from './state-manager.js';

// 後方互換性のために既存のAppStateクラスを維持（非推奨）
export class AppState extends NewAppState {
    constructor() {
        super();
    }
}

// 新しい状態管理システムをエクスポート
export { AppStateManager, appStateManager };

// 期間と足の組み合わせ検証ルール
export const INTERVAL_PERIOD_RULES = {
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

// ユーティリティ関数群
export class Utils {
    // 数値を3桁区切りでフォーマット
    static formatNumber(num) {
        if (num === null || num === undefined || num === '') return '-';
        return new Intl.NumberFormat('ja-JP').format(num);
    }

    // 通貨フォーマット
    static formatCurrency(amount) {
        if (amount === null || amount === undefined || amount === '') return '-';
        return new Intl.NumberFormat('ja-JP', {
            style: 'currency',
            currency: 'JPY',
            minimumFractionDigits: 0,
            maximumFractionDigits: 2
        }).format(amount);
    }

    // 日付フォーマット
    static formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('ja-JP', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
    }

    // 日時フォーマット（日付と日時の両方に対応）
    static formatDateTime(dateTimeString) {
        if (!dateTimeString) return '-';

        const date = new Date(dateTimeString);

        // 日付のみの場合（長さが10文字またはT00:00:00を含む）
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

    // HTMLエスケープ
    static escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ローディング表示制御
    static showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'block';
            element.innerHTML = '<div class="loading-spinner">読み込み中...</div>';
        }
    }

    static hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
        }
    }

    // デバウンス関数
    static debounce(func, wait) {
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

    // 期間オプションの更新
    static updatePeriodOptions(intervalValue) {
        const periodSelect = document.getElementById('period');
        if (!periodSelect) return;

        const allowedPeriods = INTERVAL_PERIOD_RULES[intervalValue] || [];
        const options = periodSelect.querySelectorAll('option');

        options.forEach(option => {
            if (option.value === '') {
                option.style.display = 'block';
                return;
            }

            if (allowedPeriods.includes(option.value)) {
                option.style.display = 'block';
                option.disabled = false;
            } else {
                option.style.display = 'none';
                option.disabled = true;
            }
        });

        // 現在選択されている期間が無効な場合はリセット
        if (periodSelect.value && !allowedPeriods.includes(periodSelect.value)) {
            periodSelect.value = '';
        }
    }

    // 時間軸と期間の組み合わせ検証
    static validateIntervalPeriod(interval, period) {
        if (!interval || !period) return true;
        const allowedPeriods = INTERVAL_PERIOD_RULES[interval];
        return allowedPeriods ? allowedPeriods.includes(period) : false;
    }
}

// APIサービスクラス
export class ApiService {
    // APIリクエストのベースハンドラ
    static async request(url, options = {}) {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    // Yahoo Financeから株価データを取得
    static async fetchStockData(symbol, period, interval) {
        const params = new URLSearchParams({
            symbol: symbol,
            period: period,
            interval: interval
        });

        return await this.request(`/api/fetch?${params}`);
    }

    // フィルタリングされた株価データを取得
    static async getFilteredStockData(params) {
        const queryParams = new URLSearchParams(params);
        return await this.request(`/api/data?${queryParams}`);
    }

    // データベース接続テスト
    static async testDatabaseConnection() {
        return await this.request('/api/test/db');
    }

    // Yahoo Finance API接続テスト
    static async testYahooFinanceApi() {
        return await this.request('/api/test/yahoo');
    }

    // 統合ヘルスチェック
    static async healthCheck() {
        return await this.request('/api/health');
    }
}

// UIコンポーネント管理クラス
export class UIComponents {
    // エラーメッセージの表示
    static showError(message, containerId = 'error-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <strong>エラー:</strong> ${Utils.escapeHtml(message)}
                </div>
            `;
            container.style.display = 'block';
        }
    }

    // 成功メッセージの表示
    static showSuccess(message, containerId = 'success-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-success" role="alert">
                    ${Utils.escapeHtml(message)}
                </div>
            `;
            container.style.display = 'block';
        }
    }

    // メッセージをクリア
    static clearMessages() {
        const container = document.getElementById('result-container');

        if (container) {
            container.style.display = 'none';
            container.innerHTML = '';
        }
    }

    // エラーメッセージの表示（script.js互換）
    static showErrorMessage(message) {
        const container = document.getElementById('result-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    ${Utils.escapeHtml(message)}
                </div>
            `;
            container.style.display = 'block';
        }
    }

    // 成功メッセージの表示（script.js互換）
    static showSuccessMessage(message) {
        const container = document.getElementById('result-container');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-success" role="alert">
                    ${Utils.escapeHtml(message)}
                </div>
            `;
            container.style.display = 'block';
        }
    }

    // 詳細な成功メッセージの表示
    static showDetailedSuccessMessage(message, data) {
        const container = document.getElementById('result-container');
        if (container) {
            let detailsHtml = '';

            if (data) {
                detailsHtml = '<div class="mt-2">';

                if (data.records_count !== undefined) {
                    detailsHtml += `<p><strong>取得レコード数:</strong> ${data.records_count}</p>`;
                }

                if (data.saved_records !== undefined) {
                    detailsHtml += `<p><strong>保存レコード数:</strong> ${data.saved_records}</p>`;
                }

                if (data.period) {
                    detailsHtml += `<p><strong>期間:</strong> ${data.period}</p>`;
                }

                if (data.interval) {
                    detailsHtml += `<p><strong>足:</strong> ${data.interval}</p>`;
                }

                if (data.date_range) {
                    detailsHtml += `<p><strong>データ期間:</strong> ${data.date_range.start} ～ ${data.date_range.end}</p>`;
                }

                detailsHtml += '</div>';
            }

            container.innerHTML = `
                <div class="alert alert-success" role="alert">
                    ${Utils.escapeHtml(message)}
                    ${detailsHtml}
                </div>
            `;
            container.style.display = 'block';
        }
    }

    // テーブルの作成
    static createTable(data, columns, containerId) {
        const container = document.getElementById(containerId);
        if (!container || !data || data.length === 0) return;

        let tableHtml = '<table class="table table-striped table-hover">';

        // ヘッダー
        tableHtml += '<thead><tr>';
        columns.forEach(col => {
            tableHtml += `<th>${Utils.escapeHtml(col.label)}</th>`;
        });
        tableHtml += '</tr></thead>';

        // ボディ
        tableHtml += '<tbody>';
        data.forEach(row => {
            tableHtml += '<tr>';
            columns.forEach(col => {
                const value = row[col.key];
                const formattedValue = col.formatter ? col.formatter(value) : value;
                tableHtml += `<td>${Utils.escapeHtml(formattedValue)}</td>`;
            });
            tableHtml += '</tr>';
        });
        tableHtml += '</tbody></table>';

        container.innerHTML = tableHtml;
    }
}

// フォームバリデーションクラス
export class FormValidator {
    static validateRequired(value, fieldName) {
        if (!value || value.trim() === '') {
            return `${fieldName}は必須項目です。`;
        }
        return null;
    }

    static validateSymbol(symbol) {
        if (!symbol) return '銘柄コードは必須です。';

        // 基本的な銘柄コード形式チェック
        const symbolPattern = /^[A-Z0-9]+(\.[A-Z]+)?$/i;
        if (!symbolPattern.test(symbol)) {
            return '銘柄コードの形式が正しくありません。';
        }

        return null;
    }

    static validateIntervalPeriod(interval, period) {
        if (!interval || !period) return null;

        if (!Utils.validateIntervalPeriod(interval, period)) {
            return `選択された時間軸（${interval}）と期間（${period}）の組み合わせは無効です。`;
        }

        return null;
    }

    // インスタンスメソッドとしてvalidateStockFormを追加
    validateStockForm(formData) {
        const errors = {};

        // 銘柄コードの検証
        const symbolError = FormValidator.validateSymbol(formData.symbol);
        if (symbolError) {
            errors.symbol = symbolError;
        }

        // 期間の検証
        const periodError = FormValidator.validateRequired(formData.period, '期間');
        if (periodError) {
            errors.period = periodError;
        }

        // 足の検証
        const intervalError = FormValidator.validateRequired(formData.interval, '足');
        if (intervalError) {
            errors.interval = intervalError;
        }

        // 期間と足の組み合わせ検証
        if (!periodError && !intervalError) {
            const combinationError = FormValidator.validateIntervalPeriod(formData.interval, formData.period);
            if (combinationError) {
                errors.combination = combinationError;
            }
        }

        return {
            isValid: Object.keys(errors).length === 0,
            errors: errors
        };
    }
}
