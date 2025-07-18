"""Repository para operações com usuários."""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Repository específico para usuários.
    
    Adiciona métodos específicos para operações com usuários.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repository com o modelo User."""
        super().__init__(User, session)
    
    async def get_all_users(self) -> List[User]:
        """
        Busca todos os usuários para verificação de PIN.
        
        Returns:
            List[User]: Lista de usuários
        """
        return await self.get_all()
    
    async def get_by_role(self, role: UserRole) -> List[User]:
        """
        Busca todos os usuários com determinado papel.
        
        Args:
            role: Papel do usuário
            
        Returns:
            List[User]: Lista de usuários
        """
        return await self.get_all(role=role)
    
    async def get_active_users(self) -> List[User]:
        """
        Busca todos os usuários ativos.
        
        Returns:
            List[User]: Lista de usuários ativos
        """
        return await self.get_all(is_active=True)
    
    async def get_by_pin(self, pin: str) -> Optional[User]:
        """
        Busca usuário pelo PIN (usando pin_unique).
        
        Args:
            pin: PIN do usuário
            
        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        query = select(User).where(User.pin_unique == pin)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def is_pin_unique(self, pin: str, exclude_id: Optional[int] = None) -> bool:
        """
        Verifica se o PIN é único.
        
        Args:
            pin: PIN para verificar
            exclude_id: ID do usuário para excluir da verificação (para updates)
            
        Returns:
            bool: True se o PIN é único
        """
        query = select(User).where(User.pin_unique == pin)
        
        if exclude_id:
            query = query.where(User.id != exclude_id)
            
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is None
    
    async def authenticate(self, pin: str) -> Optional[User]:
        """
        Autentica usuário pelo PIN.
        
        Args:
            pin: PIN do usuário
            
        Returns:
            Optional[User]: Usuário se autenticado e ativo, None caso contrário
        """
        user = await self.get_by_pin(pin)
        
        if user and user.is_active:
            return user
            
        return None