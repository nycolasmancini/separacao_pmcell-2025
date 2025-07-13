"""Repository para operações com acessos aos pedidos."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order_access import OrderAccess
from app.repositories.base import BaseRepository


class OrderAccessRepository(BaseRepository[OrderAccess]):
    """
    Repository específico para acessos aos pedidos.
    
    Adiciona métodos específicos para controle de acesso.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repository com o modelo OrderAccess."""
        super().__init__(OrderAccess, session)
    
    async def get_active_access(
        self, 
        order_id: int, 
        user_id: int
    ) -> Optional[OrderAccess]:
        """
        Busca acesso ativo de um usuário a um pedido.
        
        Args:
            order_id: ID do pedido
            user_id: ID do usuário
            
        Returns:
            Optional[OrderAccess]: Acesso ativo ou None
        """
        query = (
            select(OrderAccess)
            .where(
                and_(
                    OrderAccess.order_id == order_id,
                    OrderAccess.user_id == user_id,
                    OrderAccess.left_at.is_(None)
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_accesses_by_order(self, order_id: int) -> List[OrderAccess]:
        """
        Busca todos os acessos ativos a um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[OrderAccess]: Lista de acessos ativos
        """
        query = (
            select(OrderAccess)
            .where(
                and_(
                    OrderAccess.order_id == order_id,
                    OrderAccess.left_at.is_(None)
                )
            )
            .options(selectinload(OrderAccess.user))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_active_accesses_by_user(self, user_id: int) -> List[OrderAccess]:
        """
        Busca todos os acessos ativos de um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[OrderAccess]: Lista de acessos ativos
        """
        query = (
            select(OrderAccess)
            .where(
                and_(
                    OrderAccess.user_id == user_id,
                    OrderAccess.left_at.is_(None)
                )
            )
            .options(selectinload(OrderAccess.order))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_access(self, order_id: int, user_id: int) -> OrderAccess:
        """
        Cria um novo acesso ao pedido.
        
        Args:
            order_id: ID do pedido
            user_id: ID do usuário
            
        Returns:
            OrderAccess: Acesso criado
        """
        # Verificar se já existe acesso ativo
        existing = await self.get_active_access(order_id, user_id)
        if existing:
            return existing
            
        # Criar novo acesso
        return await self.create(order_id=order_id, user_id=user_id)
    
    async def leave_order(self, order_id: int, user_id: int) -> bool:
        """
        Registra saída do usuário do pedido.
        
        Args:
            order_id: ID do pedido
            user_id: ID do usuário
            
        Returns:
            bool: True se sucesso, False se não havia acesso ativo
        """
        access = await self.get_active_access(order_id, user_id)
        if access:
            access.leave()
            await self.session.flush()
            return True
        return False
    
    async def leave_all_orders(self, user_id: int) -> int:
        """
        Registra saída do usuário de todos os pedidos.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            int: Número de pedidos que o usuário saiu
        """
        accesses = await self.get_active_accesses_by_user(user_id)
        for access in accesses:
            access.leave()
        await self.session.flush()
        return len(accesses)
    
    async def get_order_history(
        self, 
        order_id: int
    ) -> List[OrderAccess]:
        """
        Busca histórico completo de acessos a um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[OrderAccess]: Lista de todos os acessos
        """
        query = (
            select(OrderAccess)
            .where(OrderAccess.order_id == order_id)
            .options(selectinload(OrderAccess.user))
            .order_by(OrderAccess.accessed_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_separation_time_stats(
        self, 
        order_id: Optional[int] = None,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas de tempo de separação.
        
        Args:
            order_id: ID do pedido (opcional)
            user_id: ID do usuário (opcional)
            days: Número de dias para análise
            
        Returns:
            Dict[str, Any]: Estatísticas de tempo
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(OrderAccess)
            .where(
                and_(
                    OrderAccess.left_at.isnot(None),
                    OrderAccess.accessed_at >= since
                )
            )
        )
        
        if order_id:
            query = query.where(OrderAccess.order_id == order_id)
        if user_id:
            query = query.where(OrderAccess.user_id == user_id)
            
        result = await self.session.execute(query)
        accesses = result.scalars().all()
        
        if not accesses:
            return {
                "total_accesses": 0,
                "total_minutes": 0,
                "avg_minutes": 0,
                "min_minutes": 0,
                "max_minutes": 0
            }
        
        durations = [a.duration_minutes for a in accesses if a.duration_minutes]
        
        return {
            "total_accesses": len(accesses),
            "total_minutes": round(sum(durations), 2),
            "avg_minutes": round(sum(durations) / len(durations), 2) if durations else 0,
            "min_minutes": round(min(durations), 2) if durations else 0,
            "max_minutes": round(max(durations), 2) if durations else 0
        }