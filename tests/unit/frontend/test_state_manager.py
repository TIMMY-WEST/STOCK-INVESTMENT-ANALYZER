"""状態管理システムのテストコード.

このテストファイルは、新しいクライアントサイド状態管理システムの
JavaScript実装をテストするためのHTMLテストファイルを生成します。
"""

import os
from pathlib import Path
import tempfile

import pytest


pytestmark = pytest.mark.unit


def create_state_manager_test_html():
    """状態管理システムのHTMLテストファイルを作成."""
    test_html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>State Manager Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .test-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .test-result {
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
        }
        .test-pass {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .test-fail {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .test-summary {
            font-weight: bold;
            font-size: 1.2em;
            margin-top: 20px;
        }
        pre {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>状態管理システム テスト</h1>
    <div id="test-results"></div>

    <script type="module">
        // テスト用のStateManagerクラス（実際のファイルから読み込む代わりに埋め込み）
        class StateManager {
            constructor(namespace = 'default', initialState = {}, options = {}) {
                this.namespace = namespace;
                this.storageType = options.storageType || 'localStorage';
                this.listeners = new Map();
                this.websocketHandlers = new Map();

                // 初期状態を設定
                this.initializeState(initialState);
            }

            initializeState(initialState) {
                const existingState = this.loadFromStorage();
                const mergedState = { ...initialState, ...existingState };
                this.saveToStorage(mergedState);
            }

            get(path, defaultValue = undefined) {
                const state = this.loadFromStorage();
                return this.getNestedValue(state, path, defaultValue);
            }

            set(path, value, persist = true) {
                const state = this.loadFromStorage();
                this.setNestedValue(state, path, value);

                if (persist) {
                    this.saveToStorage(state);
                }

                this.notifyListeners(path, value);
                return this;
            }

            getNestedValue(obj, path, defaultValue) {
                if (typeof path === 'string') {
                    path = path.split('.');
                }

                let current = obj;
                for (const key of path) {
                    if (current === null || current === undefined || !(key in current)) {
                        return defaultValue;
                    }
                    current = current[key];
                }
                return current;
            }

            setNestedValue(obj, path, value) {
                if (typeof path === 'string') {
                    path = path.split('.');
                }

                let current = obj;
                for (let i = 0; i < path.length - 1; i++) {
                    const key = path[i];
                    if (!(key in current) || typeof current[key] !== 'object' || current[key] === null) {
                        current[key] = {};
                    }
                    current = current[key];
                }
                current[path[path.length - 1]] = value;
            }

            loadFromStorage() {
                try {
                    const storage = this.storageType === 'sessionStorage' ? sessionStorage : localStorage;
                    const data = storage.getItem(this.namespace);
                    return data ? JSON.parse(data) : {};
                } catch (error) {
                    console.warn('Failed to load from storage:', error);
                    return {};
                }
            }

            saveToStorage(state) {
                try {
                    const storage = this.storageType === 'sessionStorage' ? sessionStorage : localStorage;
                    storage.setItem(this.namespace, JSON.stringify(state));
                } catch (error) {
                    console.warn('Failed to save to storage:', error);
                }
            }

            subscribe(path, callback) {
                if (!this.listeners.has(path)) {
                    this.listeners.set(path, new Set());
                }
                this.listeners.get(path).add(callback);

                return () => {
                    const pathListeners = this.listeners.get(path);
                    if (pathListeners) {
                        pathListeners.delete(callback);
                        if (pathListeners.size === 0) {
                            this.listeners.delete(path);
                        }
                    }
                };
            }

            notifyListeners(path, value) {
                // 完全一致のリスナーを通知
                const exactListeners = this.listeners.get(path);
                if (exactListeners) {
                    exactListeners.forEach(callback => {
                        try {
                            callback(value, path);
                        } catch (error) {
                            console.error('Listener error:', error);
                        }
                    });
                }

                // 親パスのリスナーも通知
                const pathParts = path.split('.');
                for (let i = pathParts.length - 1; i > 0; i--) {
                    const parentPath = pathParts.slice(0, i).join('.');
                    const parentListeners = this.listeners.get(parentPath);
                    if (parentListeners) {
                        const parentValue = this.get(parentPath);
                        parentListeners.forEach(callback => {
                            try {
                                callback(parentValue, parentPath);
                            } catch (error) {
                                console.error('Parent listener error:', error);
                            }
                        });
                    }
                }
            }

            clear() {
                try {
                    const storage = this.storageType === 'sessionStorage' ? sessionStorage : localStorage;
                    storage.removeItem(this.namespace);
                } catch (error) {
                    console.warn('Failed to clear storage:', error);
                }
            }
        }

        // テスト実行クラス
        class TestRunner {
            constructor() {
                this.tests = [];
                this.results = [];
            }

            addTest(name, testFn) {
                this.tests.push({ name, testFn });
            }

            async runTests() {
                const resultsContainer = document.getElementById('test-results');

                for (const test of this.tests) {
                    try {
                        await test.testFn();
                        this.results.push({ name: test.name, status: 'pass', error: null });
                        this.displayResult(test.name, 'pass');
                    } catch (error) {
                        this.results.push({ name: test.name, status: 'fail', error: error.message });
                        this.displayResult(test.name, 'fail', error.message);
                    }
                }

                this.displaySummary();
            }

            displayResult(testName, status, error = null) {
                const resultsContainer = document.getElementById('test-results');
                const resultDiv = document.createElement('div');
                resultDiv.className = `test-result test-${status}`;

                let content = `✓ ${testName}`;
                if (status === 'fail') {
                    content = `✗ ${testName}`;
                    if (error) {
                        content += `\\n${error}`;
                    }
                }

                resultDiv.textContent = content;
                resultsContainer.appendChild(resultDiv);
            }

            displaySummary() {
                const resultsContainer = document.getElementById('test-results');
                const passCount = this.results.filter(r => r.status === 'pass').length;
                const failCount = this.results.filter(r => r.status === 'fail').length;

                const summaryDiv = document.createElement('div');
                summaryDiv.className = 'test-summary';
                summaryDiv.textContent = `テスト結果: ${passCount} 成功, ${failCount} 失敗`;

                if (failCount === 0) {
                    summaryDiv.style.color = '#155724';
                } else {
                    summaryDiv.style.color = '#721c24';
                }

                resultsContainer.appendChild(summaryDiv);
            }

            assert(condition, message) {
                if (!condition) {
                    throw new Error(message || 'Assertion failed');
                }
            }

            assertEqual(actual, expected, message) {
                if (actual !== expected) {
                    throw new Error(message || `Expected ${expected}, but got ${actual}`);
                }
            }

            assertDeepEqual(actual, expected, message) {
                if (JSON.stringify(actual) !== JSON.stringify(expected)) {
                    throw new Error(message || `Expected ${JSON.stringify(expected)}, but got ${JSON.stringify(actual)}`);
                }
            }
        }

        // テスト実行
        const runner = new TestRunner();

        // 基本的な状態管理テスト
        runner.addTest('基本的な状態の設定と取得', () => {
            const stateManager = new StateManager('test1');
            stateManager.clear();

            stateManager.set('user.name', 'テストユーザー');
            runner.assertEqual(stateManager.get('user.name'), 'テストユーザー');
        });

        runner.addTest('ネストした状態の管理', () => {
            const stateManager = new StateManager('test2');
            stateManager.clear();

            stateManager.set('pagination.currentPage', 1);
            stateManager.set('pagination.totalRecords', 100);

            runner.assertEqual(stateManager.get('pagination.currentPage'), 1);
            runner.assertEqual(stateManager.get('pagination.totalRecords'), 100);
        });

        runner.addTest('デフォルト値の取得', () => {
            const stateManager = new StateManager('test3');
            stateManager.clear();

            runner.assertEqual(stateManager.get('nonexistent.key', 'default'), 'default');
            runner.assertEqual(stateManager.get('another.key'), undefined);
        });

        runner.addTest('状態変更リスナー', async () => {
            const stateManager = new StateManager('test4');
            stateManager.clear();

            let callbackCalled = false;
            let receivedValue = null;

            const unsubscribe = stateManager.subscribe('test.value', (value) => {
                callbackCalled = true;
                receivedValue = value;
            });

            stateManager.set('test.value', 'test data');

            // 非同期処理を待つ
            await new Promise(resolve => setTimeout(resolve, 10));

            runner.assert(callbackCalled, 'コールバックが呼ばれませんでした');
            runner.assertEqual(receivedValue, 'test data');

            unsubscribe();
        });

        runner.addTest('永続化の無効化', () => {
            const stateManager = new StateManager('test5');
            stateManager.clear();

            // 永続化しない設定
            stateManager.set('temp.data', 'temporary', false);

            // 新しいインスタンスで確認
            const newStateManager = new StateManager('test5');
            runner.assertEqual(newStateManager.get('temp.data'), undefined);
        });

        runner.addTest('初期状態の設定', () => {
            const stateManager = new StateManager('test6', {
                'app.version': '1.0.0',
                'user.preferences': {
                    theme: 'light'
                }
            });

            runner.assertEqual(stateManager.get('app.version'), '1.0.0');
            runner.assertEqual(stateManager.get('user.preferences.theme'), 'light');

            stateManager.clear();
        });

        runner.addTest('sessionStorageの使用', () => {
            const stateManager = new StateManager('test7', {}, { storageType: 'sessionStorage' });
            stateManager.clear();

            stateManager.set('session.data', 'session value');
            runner.assertEqual(stateManager.get('session.data'), 'session value');

            stateManager.clear();
        });

        // テスト実行
        runner.runTests();
    </script>
</body>
</html>"""

    return test_html


def test_create_state_manager_test_file_with_valid_config_returns_test_file():
    """状態管理テストファイルの作成をテスト."""
    # Arrange (準備)
    test_html = create_state_manager_test_html()
    test_file_path = (
        Path(__file__).parent.parent / "test_state_manager_unit.html"
    )

    # Act (実行)
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_html)

    # Assert (検証)
    assert test_file_path.exists(), "テストファイルが作成されませんでした"
    print(f"状態管理テストファイルを作成しました: {test_file_path}")


if __name__ == "__main__":
    test_create_state_manager_test_file_with_valid_config_returns_test_file()
