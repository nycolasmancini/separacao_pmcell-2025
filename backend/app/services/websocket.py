"""
WebSocket service para atualizações em tempo real.
"""
import json
import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
from app.schemas.orders import WebSocketMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gerenciador de conexões WebSocket.
    
    Mantém conexões ativas e permite broadcast de mensagens.
    """
    
    def __init__(self):
        """Inicializa o gerenciador."""
        # Conexões ativas por ID de usuário
        self.active_connections: Dict[int, WebSocket] = {}
        
        # Usuários por pedido (para tracking de presença)
        self.users_in_orders: Dict[int, Set[int]] = {}
        
        # Metadados de conexão
        self.connection_metadata: Dict[int, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, user_name: str):
        """
        Conecta um usuário ao WebSocket.
        
        Args:
            websocket: Conexão WebSocket
            user_id: ID do usuário
            user_name: Nome do usuário
        """
        await websocket.accept()
        
        # Se usuário já tinha conexão, desconectar a anterior
        if user_id in self.active_connections:
            await self.disconnect(user_id)
        
        self.active_connections[user_id] = websocket
        self.connection_metadata[user_id] = {
            "user_name": user_name,
            "connected_at": datetime.now(),
            "current_order": None
        }
        
        logger.info(f"User {user_id} ({user_name}) connected to WebSocket")
        
        # Notificar outros usuários sobre nova conexão
        await self.broadcast_message(WebSocketMessage(
            type="user_joined",
            data={
                "user_id": user_id,
                "user_name": user_name
            }
        ), exclude_user=user_id)
    
    async def disconnect(self, user_id: int):
        """
        Desconecta um usuário.
        
        Args:
            user_id: ID do usuário
        """
        if user_id not in self.active_connections:
            return
        
        user_name = self.connection_metadata.get(user_id, {}).get("user_name", "Unknown")
        current_order = self.connection_metadata.get(user_id, {}).get("current_order")
        
        # Remover de pedidos ativos
        if current_order:
            await self.leave_order(user_id, current_order)
        
        # Remover conexão
        del self.active_connections[user_id]
        if user_id in self.connection_metadata:
            del self.connection_metadata[user_id]
        
        logger.info(f"User {user_id} ({user_name}) disconnected from WebSocket")
        
        # Notificar outros usuários sobre desconexão
        await self.broadcast_message(WebSocketMessage(
            type="user_left",
            data={
                "user_id": user_id,
                "user_name": user_name
            }
        ), exclude_user=user_id)
    
    async def join_order(self, user_id: int, order_id: int):
        """
        Marca usuário como presente em um pedido.
        
        Args:
            user_id: ID do usuário
            order_id: ID do pedido
        """
        if user_id not in self.active_connections:
            return
        
        # Remover de pedido anterior se existir
        current_order = self.connection_metadata.get(user_id, {}).get("current_order")
        if current_order and current_order != order_id:
            await self.leave_order(user_id, current_order)
        
        # Adicionar ao novo pedido
        if order_id not in self.users_in_orders:
            self.users_in_orders[order_id] = set()
        
        self.users_in_orders[order_id].add(user_id)
        self.connection_metadata[user_id]["current_order"] = order_id
        
        user_name = self.connection_metadata[user_id]["user_name"]
        logger.info(f"User {user_id} ({user_name}) joined order {order_id}")
        
        # Notificar outros usuários no mesmo pedido
        await self.broadcast_to_order(order_id, WebSocketMessage(
            type="user_joined",
            data={
                "order_id": order_id,
                "user_id": user_id,
                "user_name": user_name
            }
        ), exclude_user=user_id)
    
    async def leave_order(self, user_id: int, order_id: int):
        """
        Remove usuário de um pedido.
        
        Args:
            user_id: ID do usuário
            order_id: ID do pedido
        """
        if order_id in self.users_in_orders:
            self.users_in_orders[order_id].discard(user_id)
            
            # Limpar pedido vazio
            if not self.users_in_orders[order_id]:
                del self.users_in_orders[order_id]
        
        if user_id in self.connection_metadata:
            self.connection_metadata[user_id]["current_order"] = None
        
        user_name = self.connection_metadata.get(user_id, {}).get("user_name", "Unknown")
        logger.info(f"User {user_id} ({user_name}) left order {order_id}")
        
        # Notificar outros usuários no pedido
        await self.broadcast_to_order(order_id, WebSocketMessage(
            type="user_left",
            data={
                "order_id": order_id,
                "user_id": user_id,
                "user_name": user_name
            }
        ), exclude_user=user_id)
    
    async def send_personal_message(self, message: WebSocketMessage, user_id: int):
        """
        Envia mensagem para usuário específico.
        
        Args:
            message: Mensagem a ser enviada
            user_id: ID do usuário
        """
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message.model_dump_json())
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                # Remover conexão com problema
                await self.disconnect(user_id)
    
    async def broadcast_message(
        self, 
        message: WebSocketMessage, 
        exclude_user: Optional[int] = None
    ):
        """
        Faz broadcast de mensagem para todos os usuários conectados.
        
        Args:
            message: Mensagem a ser enviada
            exclude_user: ID do usuário a ser excluído (opcional)
        """
        disconnected_users = []
        
        for user_id, connection in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await connection.send_text(message.model_dump_json())
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                disconnected_users.append(user_id)
        
        # Limpar conexões com problema
        for user_id in disconnected_users:
            await self.disconnect(user_id)
    
    async def broadcast_to_order(
        self, 
        order_id: int, 
        message: WebSocketMessage,
        exclude_user: Optional[int] = None
    ):
        """
        Faz broadcast de mensagem para usuários em um pedido específico.
        
        Args:
            order_id: ID do pedido
            message: Mensagem a ser enviada
            exclude_user: ID do usuário a ser excluído (opcional)
        """
        if order_id not in self.users_in_orders:
            return
        
        disconnected_users = []
        
        for user_id in self.users_in_orders[order_id]:
            if exclude_user and user_id == exclude_user:
                continue
            
            if user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(message.model_dump_json())
                except Exception as e:
                    logger.error(f"Error broadcasting to user {user_id} in order {order_id}: {str(e)}")
                    disconnected_users.append(user_id)
        
        # Limpar conexões com problema
        for user_id in disconnected_users:
            await self.disconnect(user_id)
    
    def get_users_in_order(self, order_id: int) -> List[Dict[str, Any]]:
        """
        Retorna lista de usuários ativos em um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[Dict[str, Any]]: Lista de usuários com metadados
        """
        if order_id not in self.users_in_orders:
            return []
        
        users = []
        for user_id in self.users_in_orders[order_id]:
            if user_id in self.connection_metadata:
                metadata = self.connection_metadata[user_id]
                users.append({
                    "user_id": user_id,
                    "user_name": metadata["user_name"],
                    "connected_at": metadata["connected_at"].isoformat()
                })
        
        return users
    
    def get_connection_count(self) -> int:
        """
        Retorna número de conexões ativas.
        
        Returns:
            int: Número de conexões ativas
        """
        return len(self.active_connections)
    
    def get_order_count(self) -> int:
        """
        Retorna número de pedidos com usuários ativos.
        
        Returns:
            int: Número de pedidos ativos
        """
        return len(self.users_in_orders)


# Instância global do gerenciador
connection_manager = ConnectionManager()