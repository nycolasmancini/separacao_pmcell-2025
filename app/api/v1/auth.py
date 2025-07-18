from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_async_session
from ...schemas.auth import LoginRequest, TokenResponse, UserResponse, OrderAccessRequest, OrderAccessResponse
from ...services.auth import AuthService
from ...services.websocket import connection_manager
from ...core.deps import get_current_active_user
from ...models.user import User
from typing import List, Dict, Any

router = APIRouter(prefix="/auth", tags=["autenticacao"])

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Login com PIN"""
    auth_service = AuthService(db)
    return await auth_service.login(login_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Informações do usuário atual"""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        role=current_user.role,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout (no backend só confirmamos que o usuário está autenticado)"""
    return {"message": "Logout realizado com sucesso"}

@router.post("/order-access", response_model=OrderAccessResponse)
async def order_access(
    access_data: OrderAccessRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Autenticação para acesso a um pedido específico"""
    import logging
    logger = logging.getLogger("app.api.auth")
    
    try:
        logger.info(f"Order access request: order_id={access_data.order_id}, pin length={len(access_data.pin)}")
        
        auth_service = AuthService(db)
        result = await auth_service.authenticate_order_access(access_data)
        
        # Notificar via WebSocket sobre o acesso
        user_info = {
            "id": result.user.id,
            "name": result.user.name,
            "role": result.user.role,
            "photo_url": result.user.photo_url
        }
        await connection_manager.notify_order_access(result.order_id, user_info)
        
        logger.info(f"Order access successful: user={result.user.name}, order_id={result.order_id}")
        return result
        
    except HTTPException as e:
        logger.warning(f"Order access failed: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in order access: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor"
        )

@router.get("/orders/{order_id}/active-users")
async def get_order_active_users(
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Obter usuários ativos em um pedido"""
    active_users = connection_manager.get_users_in_order(order_id)
    return active_users