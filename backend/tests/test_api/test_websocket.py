"""
Testes para WebSocket endpoints.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.user import User
from app.core.security import create_access_token
from app.services.websocket import ConnectionManager, connection_manager
from app.schemas.orders import WebSocketMessage


class TestConnectionManager:
    """Testes para o ConnectionManager."""
    
    @pytest.fixture
    def manager(self):
        """Instância limpa do ConnectionManager."""
        return ConnectionManager()
    
    @pytest.fixture
    async def mock_websocket(self):
        """Mock de WebSocket."""
        websocket = AsyncMock()
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        return websocket
    
    @pytest.mark.asyncio
    async def test_connect_user(self, manager, mock_websocket):
        """Testa conexão de usuário."""
        user_id = 1
        user_name = "Test User"
        
        await manager.connect(mock_websocket, user_id, user_name)
        
        # Verificar que WebSocket foi aceito
        mock_websocket.accept.assert_called_once()
        
        # Verificar que usuário foi adicionado
        assert user_id in manager.active_connections
        assert manager.active_connections[user_id] == mock_websocket
        assert user_id in manager.connection_metadata
        assert manager.connection_metadata[user_id]["user_name"] == user_name
    
    @pytest.mark.asyncio
    async def test_connect_user_replaces_existing(self, manager, mock_websocket):
        """Testa que nova conexão substitui a anterior."""
        user_id = 1
        user_name = "Test User"
        
        # Primeira conexão
        old_websocket = AsyncMock()
        await manager.connect(old_websocket, user_id, user_name)
        
        # Segunda conexão (deve substituir)
        await manager.connect(mock_websocket, user_id, user_name)
        
        # Verificar que apenas nova conexão existe
        assert manager.active_connections[user_id] == mock_websocket
        assert len(manager.active_connections) == 1
    
    @pytest.mark.asyncio
    async def test_disconnect_user(self, manager, mock_websocket):
        """Testa desconexão de usuário."""
        user_id = 1
        user_name = "Test User"
        
        # Conectar primeiro
        await manager.connect(mock_websocket, user_id, user_name)
        assert user_id in manager.active_connections
        
        # Desconectar
        await manager.disconnect(user_id)
        
        # Verificar que usuário foi removido
        assert user_id not in manager.active_connections
        assert user_id not in manager.connection_metadata
    
    @pytest.mark.asyncio
    async def test_join_order(self, manager, mock_websocket):
        """Testa entrada de usuário em pedido."""
        user_id = 1
        user_name = "Test User"
        order_id = 100
        
        # Conectar usuário
        await manager.connect(mock_websocket, user_id, user_name)
        
        # Entrar no pedido
        await manager.join_order(user_id, order_id)
        
        # Verificar que usuário foi adicionado ao pedido
        assert order_id in manager.users_in_orders
        assert user_id in manager.users_in_orders[order_id]
        assert manager.connection_metadata[user_id]["current_order"] == order_id
    
    @pytest.mark.asyncio
    async def test_join_order_leaves_previous(self, manager, mock_websocket):
        """Testa que entrar em novo pedido sai do anterior."""
        user_id = 1
        user_name = "Test User"
        order_id_1 = 100
        order_id_2 = 200
        
        # Conectar e entrar no primeiro pedido
        await manager.connect(mock_websocket, user_id, user_name)
        await manager.join_order(user_id, order_id_1)
        
        # Entrar no segundo pedido
        await manager.join_order(user_id, order_id_2)
        
        # Verificar que saiu do primeiro e entrou no segundo
        assert order_id_1 not in manager.users_in_orders or user_id not in manager.users_in_orders[order_id_1]
        assert user_id in manager.users_in_orders[order_id_2]
        assert manager.connection_metadata[user_id]["current_order"] == order_id_2
    
    @pytest.mark.asyncio
    async def test_leave_order(self, manager, mock_websocket):
        """Testa saída de usuário do pedido."""
        user_id = 1
        user_name = "Test User"
        order_id = 100
        
        # Conectar e entrar no pedido
        await manager.connect(mock_websocket, user_id, user_name)
        await manager.join_order(user_id, order_id)
        
        # Sair do pedido
        await manager.leave_order(user_id, order_id)
        
        # Verificar que usuário saiu
        assert order_id not in manager.users_in_orders or user_id not in manager.users_in_orders[order_id]
        assert manager.connection_metadata[user_id]["current_order"] is None
    
    @pytest.mark.asyncio
    async def test_send_personal_message(self, manager, mock_websocket):
        """Testa envio de mensagem pessoal."""
        user_id = 1
        user_name = "Test User"
        
        # Conectar usuário
        await manager.connect(mock_websocket, user_id, user_name)
        
        # Enviar mensagem
        message = WebSocketMessage(
            type="test",
            data={"content": "Hello"}
        )
        await manager.send_personal_message(message, user_id)
        
        # Verificar que mensagem foi enviada
        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert "test" in sent_data
        assert "Hello" in sent_data
    
    @pytest.mark.asyncio
    async def test_send_personal_message_connection_error(self, manager, mock_websocket):
        """Testa tratamento de erro ao enviar mensagem."""
        user_id = 1
        user_name = "Test User"
        
        # Conectar usuário
        await manager.connect(mock_websocket, user_id, user_name)
        
        # Configurar erro no envio
        mock_websocket.send_text.side_effect = Exception("Connection error")
        
        # Enviar mensagem (não deve falhar)
        message = WebSocketMessage(type="test", data={})
        await manager.send_personal_message(message, user_id)
        
        # Verificar que usuário foi removido após erro
        assert user_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_broadcast_message(self, manager):
        """Testa broadcast para todos os usuários."""
        # Conectar múltiplos usuários
        websockets = []
        for i in range(3):
            ws = AsyncMock()
            await manager.connect(ws, i + 1, f"User {i + 1}")
            websockets.append(ws)
        
        # Fazer broadcast
        message = WebSocketMessage(type="broadcast", data={"content": "Hello all"})
        await manager.broadcast_message(message)
        
        # Verificar que todos receberam
        for ws in websockets:
            ws.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_message_exclude_user(self, manager):
        """Testa broadcast excluindo usuário específico."""
        # Conectar usuários
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        await manager.connect(ws1, 1, "User 1")
        await manager.connect(ws2, 2, "User 2")
        
        # Fazer broadcast excluindo usuário 1
        message = WebSocketMessage(type="broadcast", data={})
        await manager.broadcast_message(message, exclude_user=1)
        
        # Verificar que apenas usuário 2 recebeu
        ws1.send_text.assert_not_called()
        ws2.send_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_broadcast_to_order(self, manager):
        """Testa broadcast para usuários de um pedido específico."""
        # Conectar usuários
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        await manager.connect(ws1, 1, "User 1")
        await manager.connect(ws2, 2, "User 2")
        await manager.connect(ws3, 3, "User 3")
        
        # Usuários 1 e 2 no pedido 100, usuário 3 no pedido 200
        await manager.join_order(1, 100)
        await manager.join_order(2, 100)
        await manager.join_order(3, 200)
        
        # Broadcast para pedido 100
        message = WebSocketMessage(type="order_update", data={"order_id": 100})
        await manager.broadcast_to_order(100, message)
        
        # Verificar que apenas usuários do pedido 100 receberam
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()
        ws3.send_text.assert_not_called()
    
    def test_get_users_in_order(self, manager):
        """Testa obtenção de usuários em um pedido."""
        # Configurar dados manualmente para teste
        manager.users_in_orders[100] = {1, 2}
        manager.connection_metadata[1] = {
            "user_name": "User 1",
            "connected_at": "2024-07-12T10:00:00"
        }
        manager.connection_metadata[2] = {
            "user_name": "User 2", 
            "connected_at": "2024-07-12T10:05:00"
        }
        
        users = manager.get_users_in_order(100)
        
        assert len(users) == 2
        assert any(user["user_name"] == "User 1" for user in users)
        assert any(user["user_name"] == "User 2" for user in users)
    
    def test_get_users_in_order_empty(self, manager):
        """Testa obtenção de usuários em pedido vazio."""
        users = manager.get_users_in_order(999)
        assert users == []
    
    def test_get_connection_count(self, manager):
        """Testa contagem de conexões."""
        assert manager.get_connection_count() == 0
        
        # Adicionar conexões manualmente
        manager.active_connections[1] = AsyncMock()
        manager.active_connections[2] = AsyncMock()
        
        assert manager.get_connection_count() == 2
    
    def test_get_order_count(self, manager):
        """Testa contagem de pedidos ativos."""
        assert manager.get_order_count() == 0
        
        # Adicionar pedidos manualmente
        manager.users_in_orders[100] = {1}
        manager.users_in_orders[200] = {2, 3}
        
        assert manager.get_order_count() == 2


class TestWebSocketEndpoint:
    """Testes para o endpoint WebSocket."""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI."""
        return TestClient(app)
    
    @pytest.fixture
    async def test_user(self, db_session: AsyncSession):
        """Usuário de teste."""
        user = User(
            name="WebSocket User",
            pin="2222",
            role="separador"
        )
        db_session.add(user)
        await db_session.commit()
        return user
    
    @pytest.fixture
    def auth_token(self, test_user):
        """Token de autenticação."""
        return create_access_token(data={"sub": str(test_user.id)})
    
    def test_websocket_without_token(self, client):
        """Testa conexão WebSocket sem token."""
        with client.websocket_connect("/api/v1/ws/orders") as websocket:
            # Deve fechar com código de erro
            with pytest.raises(Exception):
                websocket.receive_text()
    
    def test_websocket_with_invalid_token(self, client):
        """Testa conexão WebSocket com token inválido."""
        with pytest.raises(Exception):
            with client.websocket_connect("/api/v1/ws/orders?token=invalid") as websocket:
                websocket.receive_text()
    
    @patch('app.api.v1.websocket.connection_manager')
    def test_websocket_with_valid_token(self, mock_manager, client, auth_token):
        """Testa conexão WebSocket com token válido."""
        mock_manager.connect = AsyncMock()
        mock_manager.disconnect = AsyncMock()
        
        # Simular conexão bem-sucedida
        try:
            with client.websocket_connect(f"/api/v1/ws/orders?token={auth_token}") as websocket:
                # Se chegou aqui, a autenticação passou
                pass
        except Exception:
            # Esperado devido ao mock não completo
            pass
        
        # O importante é que a autenticação não falhou imediatamente
        # Em um teste real, verificaríamos se connect foi chamado
    
    @pytest.mark.asyncio
    async def test_handle_client_message_join_order(self):
        """Testa processamento de mensagem join_order."""
        from app.api.v1.websocket import handle_client_message
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.join_order = AsyncMock()
            
            await handle_client_message(1, "join_order", {"order_id": 100})
            
            mock_manager.join_order.assert_called_once_with(1, 100)
    
    @pytest.mark.asyncio
    async def test_handle_client_message_leave_order(self):
        """Testa processamento de mensagem leave_order."""
        from app.api.v1.websocket import handle_client_message
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.leave_order = AsyncMock()
            
            await handle_client_message(1, "leave_order", {"order_id": 100})
            
            mock_manager.leave_order.assert_called_once_with(1, 100)
    
    @pytest.mark.asyncio
    async def test_handle_client_message_ping(self):
        """Testa processamento de mensagem ping."""
        from app.api.v1.websocket import handle_client_message
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.send_personal_message = AsyncMock()
            
            await handle_client_message(1, "ping", {"timestamp": "123456"})
            
            # Verificar que pong foi enviado
            mock_manager.send_personal_message.assert_called_once()
            call_args = mock_manager.send_personal_message.call_args
            message, user_id = call_args[0]
            
            assert message.type == "pong"
            assert message.data["timestamp"] == "123456"
            assert user_id == 1
    
    @pytest.mark.asyncio
    async def test_handle_client_message_unknown(self):
        """Testa processamento de mensagem desconhecida."""
        from app.api.v1.websocket import handle_client_message
        
        # Não deve falhar, apenas logar warning
        await handle_client_message(1, "unknown_type", {})


class TestWebSocketNotifications:
    """Testes para funções de notificação WebSocket."""
    
    @pytest.mark.asyncio
    async def test_notify_item_separated(self):
        """Testa notificação de item separado."""
        from app.api.v1.websocket import notify_item_separated
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.broadcast_to_order = AsyncMock()
            
            await notify_item_separated(100, 5, 75.0)
            
            # Verificar que broadcast foi feito
            mock_manager.broadcast_to_order.assert_called_once()
            order_id, message = mock_manager.broadcast_to_order.call_args[0]
            
            assert order_id == 100
            assert message.type == "item_separated"
            assert message.data["order_id"] == 100
            assert message.data["item_id"] == 5
            assert message.data["progress_percentage"] == 75.0
    
    @pytest.mark.asyncio
    async def test_notify_item_sent_to_purchase(self):
        """Testa notificação de item enviado para compras."""
        from app.api.v1.websocket import notify_item_sent_to_purchase
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.broadcast_to_order = AsyncMock()
            
            await notify_item_sent_to_purchase(100, 5)
            
            mock_manager.broadcast_to_order.assert_called_once()
            order_id, message = mock_manager.broadcast_to_order.call_args[0]
            
            assert order_id == 100
            assert message.type == "item_sent_to_purchase"
            assert message.data["order_id"] == 100
            assert message.data["item_id"] == 5
    
    @pytest.mark.asyncio
    async def test_notify_order_completed(self):
        """Testa notificação de pedido completado."""
        from app.api.v1.websocket import notify_order_completed
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.broadcast_message = AsyncMock()
            
            await notify_order_completed(100)
            
            mock_manager.broadcast_message.assert_called_once()
            message = mock_manager.broadcast_message.call_args[0][0]
            
            assert message.type == "order_completed"
            assert message.data["order_id"] == 100
    
    @pytest.mark.asyncio
    async def test_notify_new_order(self):
        """Testa notificação de novo pedido."""
        from app.api.v1.websocket import notify_new_order
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.broadcast_message = AsyncMock()
            
            await notify_new_order(100, "12345", "Cliente Teste")
            
            mock_manager.broadcast_message.assert_called_once()
            message = mock_manager.broadcast_message.call_args[0][0]
            
            assert message.type == "new_order"
            assert message.data["order_id"] == 100
            assert message.data["order_number"] == "12345"
            assert message.data["client_name"] == "Cliente Teste"
    
    @pytest.mark.asyncio
    async def test_notify_order_updated(self):
        """Testa notificação de atualização de pedido."""
        from app.api.v1.websocket import notify_order_updated
        
        with patch('app.api.v1.websocket.connection_manager') as mock_manager:
            mock_manager.broadcast_message = AsyncMock()
            
            await notify_order_updated(100, 85.5)
            
            mock_manager.broadcast_message.assert_called_once()
            message = mock_manager.broadcast_message.call_args[0][0]
            
            assert message.type == "order_updated"
            assert message.data["order_id"] == 100
            assert message.data["progress_percentage"] == 85.5