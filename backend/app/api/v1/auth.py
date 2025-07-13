from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.database import get_async_session
from ...schemas.auth import LoginRequest, TokenResponse, UserResponse
from ...services.auth import AuthService
from ...core.deps import get_current_active_user
from ...models.user import User

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
        created_at=current_user.created_at
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout (no backend só confirmamos que o usuário está autenticado)"""
    return {"message": "Logout realizado com sucesso"}