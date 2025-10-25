/**
 * JPX全銘柄8種類順次自動取得機能のJavaScript
 */

// ES6モジュールインポート
import { Utils, UIComponents } from './app.js';

// モジュール内状態管理
const JpxSequentialState = {
    jobId: null,
    checkInterval: null,
    intervalResults: []
};

// ページ読み込み時の初期化
document.addEventListener('DOMContentLoaded', function() {
    // 開始ボタンのイベントリスナー
    const startBtn = document.getElementById('jpx-seq-start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', handleJpxSequentialStart);
    }

    // 停止ボタンのイベントリスナー
    const stopBtn = document.getElementById('jpx-seq-stop-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', handleJpxSequentialStop);
    }

    // 銘柄マスタ更新ボタンのイベントリスナー
    const updateMasterBtn = document.getElementById('jpx-seq-update-master-btn');
    if (updateMasterBtn) {
        updateMasterBtn.addEventListener('click', handleJpxStockMasterUpdate);
    }
});

/**
 * JPX全銘柄順次取得を開始
 */
async function handleJpxSequentialStart() {
    console.log('[JPX Sequential] 開始ボタンがクリックされました');

    // 設定値を取得
    const limit = document.getElementById('jpx-seq-limit').value;
    const marketCategory = document.getElementById('jpx-seq-market').value;

    // UI初期化
    resetJpxSequentialUI();

    // ボタン状態変更
    const startBtn = document.getElementById('jpx-seq-start-btn');
    const stopBtn = document.getElementById('jpx-seq-stop-btn');
    startBtn.disabled = true;
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';

    // ステータスセクション表示
    const statusSection = document.getElementById('jpx-seq-status-section');
    statusSection.style.display = 'block';

    try {
        // 1. JPX銘柄一覧を取得
        console.log('[JPX Sequential] 銘柄一覧取得開始');
        const symbolsResponse = await fetch(
            `/api/bulk/jpx-sequential/get-symbols?limit=${limit}${marketCategory ? '&market_category=' + encodeURIComponent(marketCategory) : ''}`
        );

        if (!symbolsResponse.ok) {
            throw new Error(`銘柄一覧取得エラー: ${symbolsResponse.status}`);
        }

        const symbolsData = await symbolsResponse.json();

        if (!symbolsData.success) {
            throw new Error(symbolsData.message || '銘柄一覧の取得に失敗しました');
        }

        const symbols = symbolsData.symbols;
        console.log(`[JPX Sequential] 銘柄一覧取得成功: ${symbols.length}銘柄`);

        // 銘柄が0件の場合はエラー
        if (!symbols || symbols.length === 0) {
            throw new Error(
                'JPX銘柄マスタにデータがありません。\n\n' +
                '対処方法:\n' +
                '1. 下の「📥 JPX銘柄マスタを更新」ボタンをクリックして銘柄マスタを更新してください。\n' +
                '2. または、「JPX全銘柄自動取得（単一時間軸）」セクションの「JPX銘柄リスト取得 & 全銘柄データ取得開始」ボタンを実行してください。'
            );
        }

        // 対象銘柄数を表示
        document.getElementById('jpx-seq-stock-count').textContent = symbols.length;

        // 2. 順次取得ジョブを開始
        console.log('[JPX Sequential] ジョブ開始リクエスト送信');
        const startResponse = await fetch('/api/bulk/jpx-sequential/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ symbols: symbols })
        });

        if (!startResponse.ok) {
            throw new Error(`ジョブ開始エラー: ${startResponse.status}`);
        }

        const startData = await startResponse.json();

        if (!startData.success) {
            throw new Error(startData.message || 'ジョブの開始に失敗しました');
        }

        JpxSequentialState.jobId = startData.job_id;
        console.log(`[JPX Sequential] ジョブ開始成功: ${JpxSequentialState.jobId}`);

        // 結果セクション表示
        const intervalsSection = document.getElementById('jpx-seq-intervals-section');
        intervalsSection.style.display = 'block';

        // 3. ジョブの進捗を監視
        startJpxSequentialMonitoring();

    } catch (error) {
        console.error('[JPX Sequential] エラー:', error);
        showJpxSequentialError(error.message);

        // ボタン状態を元に戻す
        startBtn.disabled = false;
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
    }
}

/**
 * JPX全銘柄順次取得を停止
 */
async function handleJpxSequentialStop() {
    console.log('[JPX Sequential] 停止ボタンがクリックされました');

    if (!JpxSequentialState.jobId) {
        return;
    }

    try {
        const response = await fetch(`/api/bulk/stop/${JpxSequentialState.jobId}`, {
            method: 'POST'
        });

        if (response.ok) {
            console.log('[JPX Sequential] ジョブ停止リクエスト成功');
            stopJpxSequentialMonitoring();
        }
    } catch (error) {
        console.error('[JPX Sequential] 停止エラー:', error);
    }
}

/**
 * ジョブの進捗監視を開始
 */
function startJpxSequentialMonitoring() {
    console.log('[JPX Sequential] 進捗監視開始');

    // 即座に1回チェック
    checkJpxSequentialStatus();

    // 5秒ごとにステータスをチェック
    JpxSequentialState.checkInterval = setInterval(checkJpxSequentialStatus, 5000);
}

/**
 * ジョブの進捗監視を停止
 */
function stopJpxSequentialMonitoring() {
    console.log('[JPX Sequential] 進捗監視停止');

    if (JpxSequentialState.checkInterval) {
        clearInterval(JpxSequentialState.checkInterval);
        JpxSequentialState.checkInterval = null;
    }

    // ボタン状態を元に戻す
    const startBtn = document.getElementById('jpx-seq-start-btn');
    const stopBtn = document.getElementById('jpx-seq-stop-btn');
    startBtn.disabled = false;
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
}

/**
 * ジョブステータスをチェック
 */
async function checkJpxSequentialStatus() {
    if (!JpxSequentialState.jobId) {
        return;
    }

    try {
        const response = await fetch(`/api/bulk/status/${JpxSequentialState.jobId}`);

        if (!response.ok) {
            throw new Error(`ステータス取得エラー: ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.message || 'ステータスの取得に失敗しました');
        }

        const job = data.job;

        // UI更新
        updateJpxSequentialUI(job);

        // ジョブが完了または失敗した場合は監視を停止
        if (job.status === 'completed' || job.status === 'failed') {
            console.log(`[JPX Sequential] ジョブ終了: ${job.status}`);
            stopJpxSequentialMonitoring();

            if (job.status === 'completed') {
                showJpxSequentialResult(job);
            } else {
                showJpxSequentialError(job.error || 'ジョブが失敗しました');
            }
        }

    } catch (error) {
        console.error('[JPX Sequential] ステータスチェックエラー:', error);
    }
}

/**
 * UIを更新
 */
function updateJpxSequentialUI(job) {
    // 進捗情報を更新
    const completedIntervals = job.completed_intervals || 0;
    const totalIntervals = job.total_intervals || 8;
    const currentInterval = job.current_interval || '-';

    document.getElementById('jpx-seq-interval-progress').textContent = `${completedIntervals} / ${totalIntervals}`;
    document.getElementById('jpx-seq-current-interval').textContent = currentInterval;

    // 時間軸の結果を表示
    if (job.interval_results && job.interval_results.length > 0) {
        displayJpxSequentialIntervalResults(job.interval_results);
    }
}

/**
 * 各時間軸の結果を表示
 */
function displayJpxSequentialIntervalResults(results) {
    const container = document.getElementById('jpx-seq-intervals-container');

    // コンテナをクリア（初回のみ）
    if (JpxSequentialState.intervalResults.length === 0) {
        container.innerHTML = '';
    }

    // 新しい結果のみ表示
    const newResults = results.slice(JpxSequentialState.intervalResults.length);

    newResults.forEach((result, index) => {
        const actualIndex = JpxSequentialState.intervalResults.length + index + 1;

        const resultCard = document.createElement('div');
        resultCard.className = 'interval-result-card mb-3';
        resultCard.style.border = '1px solid #ddd';
        resultCard.style.borderRadius = '8px';
        resultCard.style.padding = '15px';
        resultCard.style.backgroundColor = result.success ? '#f0f8ff' : '#fff5f5';

        if (result.success) {
            const summary = result.summary || {};
            resultCard.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: #28a745;">
                        ✅ ${actualIndex}. ${result.name}
                    </h4>
                    <span style="color: #666; font-size: 14px;">
                        処理時間: ${summary.duration_seconds || 0}秒
                    </span>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div>
                        <strong>成功:</strong> ${summary.successful || 0} / ${summary.total_symbols || 0} 銘柄
                    </div>
                    <div>
                        <strong>失敗:</strong> ${summary.failed || 0} 銘柄
                    </div>
                    <div>
                        <strong>ダウンロード:</strong> ${summary.total_downloaded || 0} 件
                    </div>
                    <div>
                        <strong>保存:</strong> ${summary.total_saved || 0} 件
                    </div>
                </div>
            `;
        } else {
            resultCard.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin: 0; color: #dc3545;">
                        ❌ ${actualIndex}. ${result.name}
                    </h4>
                </div>
                <div style="margin-top: 10px; color: #dc3545;">
                    <strong>エラー:</strong> ${result.error || '不明なエラー'}
                </div>
            `;
        }

        container.appendChild(resultCard);
    });

    // 処理済みの結果を記録
    JpxSequentialState.intervalResults = results;
}

/**
 * 最終結果を表示
 */
function showJpxSequentialResult(job) {
    const resultSection = document.getElementById('jpx-seq-result-section');
    const resultContainer = document.getElementById('jpx-seq-result-container');

    const summary = job.summary || {};

    // interval_resultsから成功・失敗を計算
    const intervalResults = summary.interval_results || job.interval_results || [];
    const totalIntervals = intervalResults.length || summary.total_intervals || 8;
    const completedIntervals = intervalResults.length || summary.completed_intervals || 0;
    const successfulIntervals = intervalResults.filter(r => r.success === true).length || summary.successful_intervals || 0;
    const failedIntervals = intervalResults.filter(r => r.success === false).length || summary.failed_intervals || 0;

    console.log('[JPX Sequential] 最終結果サマリー:', {
        totalIntervals,
        completedIntervals,
        successfulIntervals,
        failedIntervals,
        intervalResults: intervalResults.length,
        summary
    });

    resultContainer.innerHTML = `
        <div class="alert alert-success">
            <h4>✅ 全時間軸のデータ取得が完了しました！</h4>
            <div style="margin-top: 15px;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div>
                        <strong>総時間軸数:</strong> ${totalIntervals}
                    </div>
                    <div>
                        <strong>完了:</strong> ${completedIntervals}
                    </div>
                    <div style="color: #28a745;">
                        <strong>成功:</strong> ${successfulIntervals}
                    </div>
                    <div style="color: #dc3545;">
                        <strong>失敗:</strong> ${failedIntervals}
                    </div>
                </div>
            </div>
        </div>
    `;

    resultSection.style.display = 'block';
}

/**
 * エラーを表示
 */
function showJpxSequentialError(errorMessage) {
    const errorSection = document.getElementById('jpx-seq-error-section');
    const errorContainer = document.getElementById('jpx-seq-error-container');

    errorContainer.innerHTML = `
        <div class="alert alert-danger">
            <strong>❌ エラーが発生しました</strong>
            <p style="margin-top: 10px;">${errorMessage}</p>
        </div>
    `;

    errorSection.style.display = 'block';
}

/**
 * UIをリセット
 */
function resetJpxSequentialUI() {
    console.log('[JPX Sequential] UI状態をリセット');

    // 状態をリセット
    JpxSequentialState.jobId = null;
    JpxSequentialState.intervalResults = [];

    // 監視を停止
    stopJpxSequentialMonitoring();

    // ステータスセクションを非表示
    document.getElementById('jpx-seq-status-section').style.display = 'none';

    // 結果セクションを非表示
    document.getElementById('jpx-seq-intervals-section').style.display = 'none';
    document.getElementById('jpx-seq-result-section').style.display = 'none';
    document.getElementById('jpx-seq-error-section').style.display = 'none';

    // コンテナをクリア
    document.getElementById('jpx-seq-intervals-container').innerHTML = '';
    document.getElementById('jpx-seq-result-container').innerHTML = '';
    document.getElementById('jpx-seq-error-container').innerHTML = '';

    // ステータス値をリセット
    document.getElementById('jpx-seq-stock-count').textContent = '-';
    document.getElementById('jpx-seq-interval-progress').textContent = '0 / 8';
    document.getElementById('jpx-seq-current-interval').textContent = '-';
}

/**
 * JPX銘柄マスタを更新
 */
async function handleJpxStockMasterUpdate() {
    console.log('[JPX Master Update] 銘柄マスタ更新ボタンがクリックされました');

    const updateBtn = document.getElementById('jpx-seq-update-master-btn');
    const statusDiv = document.getElementById('jpx-seq-master-status');
    const statusText = document.getElementById('jpx-seq-master-status-text');

    // ボタンを無効化
    updateBtn.disabled = true;
    updateBtn.textContent = '更新中...';

    // ステータス表示
    statusDiv.style.display = 'block';
    statusText.textContent = 'JPX公式サイトから銘柄一覧をダウンロードしています...';

    // ローディング表示
    Utils.showLoading(statusDiv);

    try {
        const response = await fetch('/api/stock-master/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ update_type: 'manual' })
        });

        if (!response.ok) {
            throw new Error(`銘柄マスタ更新エラー: ${response.status}`);
        }

        const data = await response.json();

        if (data.status !== 'success') {
            throw new Error(data.message || '銘柄マスタの更新に失敗しました');
        }

        // 成功メッセージを表示
        const result = data.data;
        statusDiv.className = 'alert alert-success';
        statusText.innerHTML = `
            <strong>✅ 銘柄マスタの更新が完了しました！</strong><br>
            <div style="margin-top: 10px;">
                総銘柄数: ${result.total_stocks}件<br>
                新規追加: ${result.added_stocks}件<br>
                更新: ${result.updated_stocks}件<br>
                削除: ${result.removed_stocks}件
            </div>
            <div style="margin-top: 10px;">
                これで「🚀 8種類データ順次自動取得 開始」ボタンが使用できます。
            </div>
        `;

        UIComponents.showSuccess(`銘柄マスタ更新完了: ${result.total_stocks}銘柄`);
        console.log('[JPX Master Update] 更新成功:', result);

        // 5秒後にメッセージを非表示
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 10000);

    } catch (error) {
        console.error('[JPX Master Update] エラー:', error);

        // エラーメッセージを表示
        statusDiv.className = 'alert alert-danger';
        statusText.innerHTML = `
            <strong>❌ エラーが発生しました</strong><br>
            <div style="margin-top: 10px;">
                ${error.message}
            </div>
            <div style="margin-top: 10px;">
                JPX公式サイトが一時的に利用できない可能性があります。<br>
                しばらく待ってから再度お試しください。
            </div>
        `;
        UIComponents.showError(`エラー: ${error.message}`);
    } finally {
        // ボタンを有効化
        updateBtn.disabled = false;
        updateBtn.innerHTML = '<span class="btn-text">📥 JPX銘柄マスタを更新</span>';
    }
}
