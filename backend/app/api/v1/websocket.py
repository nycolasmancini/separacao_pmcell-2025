"""
Endpoints WebSocket para atualizações em tempo real.
"""
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.deps import get_async_session
from app.repositories.user import UserRepository
from app.services.websocket import connection_manager
from app.schemas.orders import WebSocketMessage

logger = logging.getLogger("app.api.websocket")
router = APIRouter()
security = HTTPBearer()


async def get_user_from_token(token: str):
    """
    Extrai usuário do token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        User: Usuário autenticado
        
    Raises:
        HTTPException: Se token inválido
    """
    try:
        logger.debug(f"Decoding JWT token: {token[:20]}...")
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        logger.debug(f"JWT decoded successfully, user_id: {user_id}")
        
        if user_id is None:
            logger.warning("JWT token missing 'sub' claim")
            raise HTTPException(status_code=401, detail="Invalid token - missing user ID")
    except JWTError as jwt_error:
        logger.warning(f"JWT decode error: {str(jwt_error)}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(jwt_error)}")
    
    # Buscar usuário no banco
    from app.core.database import get_session_maker
    async with get_session_maker()() as session:
        user_repo = UserRepository(session)
        logger.debug(f"Looking up user {user_id} in database")
        user = await user_repo.get(int(user_id))
        if user is None:
            logger.warning(f"User {user_id} not found in database")
            raise HTTPException(status_code=401, detail="User not found")
        logger.debug(f"User found: {user.name} (role: {user.role})")
        return user


@router.websocket("/orders")
async def websocket_orders(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint para atualizações de pedidos em tempo real.
    
    Args:
        websocket: Conexão WebSocket
        token: Token JWT para autenticação
    """
    logger.info(f"WebSocket connection attempt from {websocket.client.host}:{websocket.client.port}")
    
    if not token:
        logger.warning("WebSocket connection rejected: No token provided")
        await websocket.close(code=1008, reason="Token required")
        return
    
    try:
        # Autenticar usuário
        logger.info(f"Authenticating WebSocket with token: {token[:20]}...")
        user = await get_user_from_token(token)
        logger.info(f"WebSocket authenticated successfully for user {user.id} ({user.name})")
        
        # Conectar usuário
        await connection_manager.connect(websocket, user.id, user.name)
        logger.info(f"WebSocket connection established for user {user.id}")
        
        try:
            while True:
                # Aguardar mensagens do cliente
                data = await websocket.receive_text()
                
                try:
                    # Parse da mensagem
                    import json
                    message_data = json.loads(data)
                    logger.debug(f"WebSocket message from user {user.id}: {message_data}")
                    
                    # Processar diferentes tipos de mensagem
                    if "type" in message_data:
                        await handle_client_message(
                            user.id, 
                            message_data["type"], 
                            message_data.get("data", {})
                        )
                    else:
                        logger.warning(f"WebSocket message without type from user {user.id}: {message_data}")
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from user {user.id}: {data}")
                except Exception as e:
                    logger.error(f"Error processing message from user {user.id}: {str(e)}")
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user {user.id}")
        except Exception as e:
            logger.error(f"WebSocket error for user {user.id}: {str(e)}")
        finally:
            await connection_manager.disconnect(user.id)
            
    except Exception as e:
        logger.error(f"WebSocket authentication error: {str(e)}", exc_info=True)
        try:
            await websocket.close(code=1008, reason="Authentication failed")
        except Exception as close_error:
            logger.error(f"Error closing WebSocket after auth failure: {str(close_error)}")


async def handle_client_message(user_id: int, message_type: str, data: dict):
    """
    Processa mensagens do cliente.
    
    Args:
        user_id: ID do usuário
        message_type: Tipo da mensagem
        data: Dados da mensagem
    """
    try:
        logger.info(f"Processing WebSocket message: user={user_id}, type={message_type}, data={data}")
        
        if message_type == "join_order":
            order_id = data.get("order_id")
            if order_id:
                logger.info(f"User {user_id} joining order {order_id}")
                await connection_manager.join_order(user_id, order_id)
            else:
                logger.warning(f"join_order message missing order_id from user {user_id}")
        
        elif message_type == "leave_order":
            order_id = data.get("order_id")
            if order_id:
                logger.info(f"User {user_id} leaving order {order_id}")
                await connection_manager.leave_order(user_id, order_id)
            else:
                logger.warning(f"leave_order message missing order_id from user {user_id}")
        
        elif message_type == "ping":
            # Responder pong para keep-alive
            await connection_manager.send_personal_message(
                WebSocketMessage(
                    type="pong",
                    data={"timestamp": data.get("timestamp")}
                ),
                user_id
            )
        
        else:
            logger.warning(f"Unknown message type from user {user_id}: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling message {message_type} from user {user_id}: {str(e)}")


# Funções helper para enviar notificações
async def notify_item_separated(order_id: int, item_id: int, progress_percentage: float):
    """
    Notifica que um item foi separado.
    
    Args:
        order_id: ID do pedido
        item_id: ID do item
        progress_percentage: Nova porcentagem de progresso
    """
    message = WebSocketMessage(
        type="item_separated",
        data={
            "order_id": order_id,
            "item_id": item_id,
            "progress_percentage": progress_percentage
        }
    )
    await connection_manager.broadcast_to_order(order_id, message)


async def notify_item_sent_to_purchase(order_id: int, item_id: int):
    """
    Notifica que um item foi enviado para compras.
    
    Args:
        order_id: ID do pedido
        item_id: ID do item
    """
    message = WebSocketMessage(
        type="item_sent_to_purchase",
        data={
            "order_id": order_id,
            "item_id": item_id
        }
    )
    await connection_manager.broadcast_to_order(order_id, message)


async def notify_order_completed(order_id: int):
    """
    Notifica que um pedido foi completado.
    
    Args:
        order_id: ID do pedido
    """
    message = WebSocketMessage(
        type="order_completed",
        data={
            "order_id": order_id
        }
    )
    await connection_manager.broadcast_message(message)


async def notify_new_order(order_id: int, order_number: str, client_name: str):
    """
    Notifica sobre um novo pedido.
    
    Args:
        order_id: ID do pedido
        order_number: Número do pedido
        client_name: Nome do cliente
    """
    message = WebSocketMessage(
        type="new_order",
        data={
            "order_id": order_id,
            "order_number": order_number,
            "client_name": client_name
        }
    )
    await connection_manager.broadcast_message(message)


async def notify_order_updated(order_id: int, progress_percentage: float):
    """
    Notifica atualização geral do pedido.
    
    Args:
        order_id: ID do pedido
        progress_percentage: Nova porcentagem de progresso
    """
    message = WebSocketMessage(
        type="order_updated",
        data={
            "order_id": order_id,
            "progress_percentage": progress_percentage
        }
    )
    await connection_manager.broadcast_message(message)