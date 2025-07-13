from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database import get_async_session
from ..core.security import verify_token
from ..services.auth import AuthService
from ..models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> User:
    """Dependency para obter usuário atual autenticado"""
    token = credentials.credentials
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(int(user_id))
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency para usuário ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency para acesso de admin"""
    if current_user.role.value != "admin":  # Use .value para acessar o valor do enum
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: apenas administradores"
        )
    return current_user