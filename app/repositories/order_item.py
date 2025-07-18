"""Repository para operações com itens de pedido."""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order_item import OrderItem
from app.models.purchase_item import PurchaseItem
from app.repositories.base import BaseRepository


class OrderItemRepository(BaseRepository[OrderItem]):
    """
    Repository específico para itens de pedido.
    
    Adiciona métodos específicos para operações com itens.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repository com o modelo OrderItem."""
        super().__init__(OrderItem, session)
    
    async def get_by_order(self, order_id: int) -> List[OrderItem]:
        """
        Busca todos os itens de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[OrderItem]: Lista de itens do pedido
        """
        query = (
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
            .order_by(OrderItem.product_name)  # Ordem alfabética
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_unseparated_items(self, order_id: int) -> List[OrderItem]:
        """
        Busca itens não separados de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            List[OrderItem]: Lista de itens não separados
        """
        query = (
            select(OrderItem)
            .where(
                and_(
                    OrderItem.order_id == order_id,
                    OrderItem.is_separated == False
                )
            )
            .order_by(OrderItem.product_name)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_items_in_purchase(self, order_id: Optional[int] = None) -> List[OrderItem]:
        """
        Busca itens enviados para compras.
        
        Args:
            order_id: ID do pedido (opcional, None para todos)
            
        Returns:
            List[OrderItem]: Lista de itens em compras
        """
        query = (
            select(OrderItem)
            .where(OrderItem.sent_to_purchase == True)
            .options(selectinload(OrderItem.purchase_item))
        )
        
        if order_id:
            query = query.where(OrderItem.order_id == order_id)
            
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def mark_separated(self, item_id: int, user_id: int) -> Optional[OrderItem]:
        """
        Marca um item como separado.
        
        Args:
            item_id: ID do item
            user_id: ID do usuário que separou
            
        Returns:
            Optional[OrderItem]: Item atualizado ou None
        """
        item = await self.get(item_id)
        if item:
            item.mark_as_separated(user_id)
            await self.session.flush()
        return item
    
    async def send_to_purchase(self, item_id: int, user_id: int) -> Optional[PurchaseItem]:
        """
        Envia item para compras.
        
        Args:
            item_id: ID do item
            user_id: ID do usuário
            
        Returns:
            Optional[PurchaseItem]: Item de compra criado ou None
        """
        item = await self.get(item_id)
        if not item or item.sent_to_purchase:
            return None
            
        # Marcar como enviado para compras
        item.send_to_purchase(user_id)
        
        # Criar registro de compra
        purchase_item = PurchaseItem(
            order_item_id=item_id,
            requested_by_id=user_id
        )
        self.session.add(purchase_item)
        
        await self.session.flush()
        return purchase_item
    
    async def remove_from_purchase(self, item_id: int, user_id: int) -> Optional[OrderItem]:
        """
        Remove item das compras.
        
        Args:
            item_id: ID do item
            user_id: ID do usuário
            
        Returns:
            Optional[OrderItem]: Item atualizado ou None
        """
        item = await self.get(item_id)
        if not item or not item.sent_to_purchase:
            return None
            
        # Remover da compras
        item.sent_to_purchase = False
        item.sent_to_purchase_at = None
        item.sent_to_purchase_by_id = None
        
        # Remover registro de compra se existir
        from app.models.purchase_item import PurchaseItem
        purchase_query = select(PurchaseItem).where(PurchaseItem.order_item_id == item_id)
        result = await self.session.execute(purchase_query)
        purchase_item = result.scalar_one_or_none()
        
        if purchase_item:
            await self.session.delete(purchase_item)
        
        await self.session.flush()
        return item

    async def mark_not_sent(
        self, 
        item_id: int, 
        user_id: int, 
        reason: Optional[str] = None
    ) -> Optional[OrderItem]:
        """
        Marca item como não enviado.
        
        Args:
            item_id: ID do item
            user_id: ID do usuário
            reason: Motivo
            
        Returns:
            Optional[OrderItem]: Item atualizado ou None
        """
        item = await self.get(item_id)
        if item:
            item.mark_as_not_sent(user_id, reason)
            await self.session.flush()
        return item
    
    async def bulk_separate(
        self, 
        item_ids: List[int], 
        user_id: int
    ) -> List[OrderItem]:
        """
        Marca múltiplos itens como separados.
        
        Args:
            item_ids: Lista de IDs dos itens
            user_id: ID do usuário
            
        Returns:
            List[OrderItem]: Lista de itens atualizados
        """
        query = select(OrderItem).where(OrderItem.id.in_(item_ids))
        result = await self.session.execute(query)
        items = result.scalars().all()
        
        for item in items:
            item.mark_as_separated(user_id)
            
        await self.session.flush()
        return items
    
    async def count_all(self) -> int:
        """
        Conta o total de itens.
        
        Returns:
            int: Total de itens
        """
        from sqlalchemy import func, select
        from app.models.order_item import OrderItem
        
        query = select(func.count(OrderItem.id))
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def count_separated(self) -> int:
        """
        Conta itens separados.
        
        Returns:
            int: Total de itens separados
        """
        from sqlalchemy import func, select
        from app.models.order_item import OrderItem
        
        query = select(func.count(OrderItem.id)).where(OrderItem.is_separated == True)
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def count_in_purchase(self) -> int:
        """
        Conta itens em compras.
        
        Returns:
            int: Total de itens em compras
        """
        from sqlalchemy import func, select
        from app.models.order_item import OrderItem
        
        query = select(func.count(OrderItem.id)).where(OrderItem.sent_to_purchase == True)
        result = await self.session.execute(query)
        return result.scalar() or 0