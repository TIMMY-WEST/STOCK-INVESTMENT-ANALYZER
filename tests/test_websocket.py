"""
WebSocket進捗配信機能のテスト
"""
import pytest
from flask_socketio import SocketIOTestClient
import time


@pytest.fixture
def app_instance():
    """Flaskアプリインスタンスを作成"""
    from app.app import app, socketio
    app.config['TESTING'] = True
    return app, socketio


@pytest.fixture
def client(app_instance):
    """Flask-SocketIOテストクライアントを作成"""
    app, socketio = app_instance
    return app.test_client()


@pytest.fixture
def socketio_client(app_instance):
    """SocketIOテストクライアントを作成"""
    app, socketio = app_instance
    return socketio.test_client(app)


def test_websocket_connection(socketio_client):
    """WebSocket接続のテスト"""
    # 接続確認
    assert socketio_client.is_connected()


def test_websocket_disconnect(socketio_client):
    """WebSocket切断のテスト"""
    # 接続確認
    assert socketio_client.is_connected()

    # 切断
    socketio_client.disconnect()

    # 切断確認
    assert not socketio_client.is_connected()


def test_bulk_progress_event(socketio_client, client, app_instance):
    """進捗イベントの送信テスト"""
    app, socketio = app_instance

    # WebSocket接続
    assert socketio_client.is_connected()

    job_id = "test-job-123"

    # 進捗データ
    progress_data = {
        'total': 3,
        'processed': 1,
        'successful': 1,
        'failed': 0,
        'progress_percentage': 33.3
    }

    # WebSocketイベントを手動で発火
    socketio.emit('bulk_progress', {
        'job_id': job_id,
        'progress': progress_data
    })

    # イベント受信確認
    received = socketio_client.get_received()

    # イベントが受信されたことを確認
    progress_events = [msg for msg in received if msg.get('name') == 'bulk_progress']
    assert len(progress_events) > 0


def test_bulk_complete_event(socketio_client, app_instance):
    """完了イベントの送信テスト"""
    app, socketio = app_instance

    # WebSocket接続
    assert socketio_client.is_connected()

    job_id = "test-job-456"
    summary_data = {
        'total_symbols': 3,
        'successful': 3,
        'failed': 0,
        'duration_seconds': 5.2
    }

    # 完了イベントを発火
    socketio.emit('bulk_complete', {
        'job_id': job_id,
        'summary': summary_data
    })

    # イベント受信確認
    received = socketio_client.get_received()

    # イベントが受信されたことを確認
    complete_events = [msg for msg in received if msg.get('name') == 'bulk_complete']
    assert len(complete_events) > 0


def test_websocket_test_page(client):
    """WebSocketテストページへのアクセステスト"""
    response = client.get('/websocket-test')
    assert response.status_code == 200
    assert b'WebSocket' in response.data


def test_multiple_clients_connection(app_instance):
    """複数クライアントの接続テスト"""
    app, socketio = app_instance

    # 複数のクライアントを作成
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)
    client3 = socketio.test_client(app)

    # すべてのクライアントが接続されていることを確認
    assert client1.is_connected()
    assert client2.is_connected()
    assert client3.is_connected()

    # クライアントを切断
    client1.disconnect()
    client2.disconnect()
    client3.disconnect()

    # すべてのクライアントが切断されていることを確認
    assert not client1.is_connected()
    assert not client2.is_connected()
    assert not client3.is_connected()


def test_progress_broadcast_to_multiple_clients(app_instance):
    """複数クライアントへの進捗ブロードキャストテスト"""
    app, socketio = app_instance

    # 複数のクライアントを作成
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)

    job_id = "test-broadcast-job"
    progress_data = {
        'total': 5,
        'processed': 2,
        'successful': 2,
        'failed': 0,
        'progress_percentage': 40.0
    }

    # 進捗イベントをブロードキャスト
    socketio.emit('bulk_progress', {
        'job_id': job_id,
        'progress': progress_data
    })

    # 両方のクライアントがイベントを受信したことを確認
    received1 = client1.get_received()
    received2 = client2.get_received()

    progress_events1 = [msg for msg in received1 if msg.get('name') == 'bulk_progress']
    progress_events2 = [msg for msg in received2 if msg.get('name') == 'bulk_progress']

    assert len(progress_events1) > 0
    assert len(progress_events2) > 0

    # クリーンアップ
    client1.disconnect()
    client2.disconnect()
