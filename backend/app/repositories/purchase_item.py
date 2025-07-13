"""Repository para operações com itens em compras."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.purchase_item import PurchaseItem
from app.models.order_item import OrderItem  
from app.models.order import Order
from app.repositories.base import BaseRepository


class PurchaseItemRepository(BaseRepository[PurchaseItem]):
    """
    Repository específico para itens em compras.
    
    Adiciona métodos específicos para operações com compras.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repository com o modelo PurchaseItem."""
        super().__init__(PurchaseItem, session)
    
    async def get_pending_items(self) -> List[PurchaseItem]:
        """
        Busca todos os itens pendentes de compra.
        
        Returns:
            List[PurchaseItem]: Lista de itens pendentes
        """
        query = (
            select(PurchaseItem)
            .where(PurchaseItem.is_completed == False)
            .options(
                selectinload(PurchaseItem.order_item).selectinload(OrderItem.order)
            )
            .order_by(PurchaseItem.requested_at)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_by_order(self, order_id: int) -> List[PurchaseItem]:
        """
        Busca itens em compras de um pedido específico.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[PurchaseItem]: Lista de itens em compras do pedido
        """
        query = (
            select(PurchaseItem)
            .join(PurchaseItem.order_item)
            .where(PurchaseItem.order_item.has(order_id=order_id))
            .options(selectinload(PurchaseItem.order_item))
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def complete_purchase(
        self, 
        purchase_id: int, 
        user_id: int,
        notes: Optional[str] = None
    ) -> Optional[PurchaseItem]:
        """
        Marca um item como comprado.
        
        Args:
            purchase_id: ID do item de compra
            user_id: ID do usuário que completou
            notes: Observações sobre a compra
            
        Returns:
            Optional[PurchaseItem]: Item atualizado ou None
        """
        item = await self.get(purchase_id)
        if item and not item.is_completed:
            item.complete(user_id, notes)
            await self.session.flush()
        return item
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas de compras.
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Dict[str, Any]: Estatísticas de compras
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total de itens
        total_query = select(func.count(PurchaseItem.id))
        total_result = await self.session.execute(total_query)
        total_items = total_result.scalar() or 0
        
        # Itens pendentes
        pending_query = (
            select(func.count(PurchaseItem.id))
            .where(PurchaseItem.is_completed == False)
        )
        pending_result = await self.session.execute(pending_query)
        pending_items = pending_result.scalar() or 0
        
        # Tempo médio de compra (em horas)
        avg_time_query = (
            select(
                func.avg(
                    func.julianday(PurchaseItem.completed_at) - 
                    func.julianday(PurchaseItem.requested_at)
                ) * 24
            )
            .where(
                and_(
                    PurchaseItem.is_completed == True,
                    PurchaseItem.requested_at >= since
                )
            )
        )
        avg_time_result = await self.session.execute(avg_time_query)
        avg_time_hours = avg_time_result.scalar() or 0.0
        
        return {
            "total_items": total_items,
            "pending_items": pending_items,
            "completed_items": total_items - pending_items,
            "avg_completion_hours": round(avg_time_hours, 2),
            "period_days": days
        }
    
    async def get_items_by_user(
        self, 
        user_id: int,
        completed: Optional[bool] = None
    ) -> List[PurchaseItem]:
        """
        Busca itens de compra por usuário.
        
        Args:
            user_id: ID do usuário
            completed: Filtrar por status (None para todos)
            
        Returns:
            List[PurchaseItem]: Lista de itens
        """
        query = (
            select(PurchaseItem)
            .where(PurchaseItem.requested_by_id == user_id)
        )
        
        if completed is not None:
            query = query.where(PurchaseItem.is_completed == completed)
            
        result = await self.session.execute(query)
        return result.scalars().all()