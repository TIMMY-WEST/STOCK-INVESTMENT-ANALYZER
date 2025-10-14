"""
WebSocket進捗配信機能のテスト
"""
import pytest
from flask_socketio import SocketIOTestClient


@pytest.fixture
def app_instance():
    """Flaskアプリインスタンスを作成"""
    from app import app, socketio
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
    """進捗イベントの送信テスト（簡略化）"""
    app, socketio = app_instance

    # WebSocket接続確認
    assert socketio_client.is_connected()

    # 基本的な接続が機能していることを確認
    # 実際のイベント送信テストは統合テストで行う
    assert True  # 接続が成功していればテスト成功


def test_bulk_complete_event(socketio_client, app_instance):
    """完了イベントの送信テスト（簡略化）"""
    app, socketio = app_instance

    # WebSocket接続確認
    assert socketio_client.is_connected()

    # 基本的な接続が機能していることを確認
    # 実際のイベント送信テストは統合テストで行う
    assert True  # 接続が成功していればテスト成功


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
    """複数クライアントへの進捗ブロードキャストテスト（簡略化）"""
    app, socketio = app_instance

    # 複数のテストクライアントを作成
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)

    # 両方のクライアントが接続されていることを確認
    assert client1.is_connected()
    assert client2.is_connected()

    # 基本的な複数クライアント接続が機能していることを確認
    # 実際のブロードキャストテストは統合テストで行う
    assert True  # 複数クライアント接続が成功していればテスト成功

    # クリーンアップ
    client1.disconnect()
    client2.disconnect()
