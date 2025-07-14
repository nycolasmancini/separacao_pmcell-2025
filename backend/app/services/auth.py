from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..repositories.user import UserRepository
from ..repositories.order import OrderRepository
from ..repositories.order_access import OrderAccessRepository
from ..core.security import verify_password, create_access_token
from ..schemas.auth import LoginRequest, TokenResponse, OrderAccessRequest, OrderAccessResponse, UserResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.order_repo = OrderRepository(db)
        self.order_access_repo = OrderAccessRepository(db)
    
    async def login(self, login_data: LoginRequest) -> TokenResponse:
        """Autentica usuário com PIN e retorna token"""
        # Busca todos os usuários e verifica PIN
        users = await self.user_repo.get_all_users()
        
        user = None
        for u in users:
            if verify_password(login_data.pin, u.pin_hash):
                user = u
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="PIN incorreto"
            )
        
        # Cria token JWT
        access_token = create_access_token(subject=user.id)
        
        return TokenResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "photo_url": user.photo_url,
                "created_at": user.created_at
            }
        )
    
    async def get_current_user(self, user_id: int):
        """Retorna usuário atual pelo ID do token"""
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        # Verificar se o usuário está ativo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        return user

    async def authenticate_order_access(self, access_data: OrderAccessRequest) -> OrderAccessResponse:
        """Autentica usuário para acesso a um pedido específico"""
        # Verificar se o pedido existe
        order = await self.order_repo.get(access_data.order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pedido não encontrado"
            )
        
        # Buscar usuário por PIN
        users = await self.user_repo.get_all_users()
        user = None
        for u in users:
            if verify_password(access_data.pin, u.pin_hash):
                user = u
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="PIN incorreto"
            )
        
        # Verificar se o usuário está ativo
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo"
            )
        
        # Criar ou atualizar acesso ao pedido
        await self.order_access_repo.create_access(order.id, user.id)
        
        return OrderAccessResponse(
            success=True,
            user=UserResponse(
                id=user.id,
                name=user.name,
                role=user.role,
                photo_url=user.photo_url,
                created_at=user.created_at
            ),
            order_id=order.id,
            message="Acesso ao pedido autorizado"
        )