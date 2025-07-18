"""Repository para operações com pedidos."""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.order_access import OrderAccess
from app.repositories.base import BaseRepository
from app.schemas.pdf import PDFExtractedData


class OrderRepository(BaseRepository[Order]):
    """
    Repository específico para pedidos.
    
    Adiciona métodos específicos para operações com pedidos.
    """
    
    def __init__(self, session: AsyncSession):
        """Inicializa o repository com o modelo Order."""
        super().__init__(Order, session)
    
    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Busca pedido pelo número.
        
        Args:
            order_number: Número do pedido
            
        Returns:
            Optional[Order]: Pedido encontrado ou None
        """
        return await self.get_by(order_number=order_number)
    
    async def get_with_items(self, id: int) -> Optional[Order]:
        """
        Busca pedido com seus itens.
        
        Args:
            id: ID do pedido
            
        Returns:
            Optional[Order]: Pedido com itens ou None
        """
        return await self.get_with_relations(id, ["items"])
    
    async def get_with_full_details(self, id: int) -> Optional[Order]:
        """
        Busca pedido com todos os relacionamentos.
        
        Args:
            id: ID do pedido
            
        Returns:
            Optional[Order]: Pedido completo ou None
        """
        query = (
            select(Order)
            .where(Order.id == id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.separated_by),
                selectinload(Order.items).selectinload(OrderItem.purchase_item),
                selectinload(Order.accesses).selectinload(OrderAccess.user)
            )
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_active_orders(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        """
        Busca pedidos ativos (não completados ou cancelados).
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            
        Returns:
            List[Order]: Lista de pedidos ativos
        """
        query = (
            select(Order)
            .where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.IN_PROGRESS])
            )
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_orders_by_seller(
        self, 
        seller_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Busca pedidos de um vendedor específico.
        
        Args:
            seller_name: Nome do vendedor
            skip: Número de registros para pular
            limit: Número máximo de registros
            
        Returns:
            List[Order]: Lista de pedidos do vendedor
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            seller_name=seller_name
        )
    
    async def get_orders_by_status(
        self,
        status: OrderStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Busca pedidos por status.
        
        Args:
            status: Status do pedido
            skip: Número de registros para pular
            limit: Número máximo de registros
            
        Returns:
            List[Order]: Lista de pedidos com o status
        """
        return await self.get_multi(
            skip=skip,
            limit=limit,
            status=status
        )
    
    async def update_progress(self, order_id: int) -> Optional[Order]:
        """
        Atualiza contadores de progresso do pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Optional[Order]: Pedido atualizado ou None
        """
        order = await self.get_with_items(order_id)
        if not order:
            return None
            
        # Contar itens
        items_separated = sum(1 for item in order.items if item.is_separated)
        items_in_purchase = sum(1 for item in order.items if item.sent_to_purchase)
        items_not_sent = sum(1 for item in order.items if item.not_sent)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 update_progress Debug for order {order_id}: "
                   f"items_separated={items_separated}, items_in_purchase={items_in_purchase}, "
                   f"items_not_sent={items_not_sent}, items_count={order.items_count}")
        
        # Atualizar contadores
        order.items_separated = items_separated
        order.items_in_purchase = items_in_purchase
        order.items_not_sent = items_not_sent
        
        # Atualizar status se necessário
        # Verificar se está completo sem usar a propriedade is_complete (evita lazy loading)
        # Itens separados E não enviados contam como "completados" (alinhado com o frontend)
        processed_items = items_separated + items_not_sent
        is_complete = processed_items == order.items_count and order.items_count > 0
        
        logger.info(f"🔍 update_progress Complete check for order {order_id}: "
                   f"processed_items={processed_items}, items_count={order.items_count}, "
                   f"is_complete={is_complete}, progress_percentage={order.progress_percentage}")
        
        if is_complete:
            order.status = OrderStatus.COMPLETED
            order.completed_at = datetime.utcnow()
        elif items_separated > 0 or items_in_purchase > 0 or items_not_sent > 0:
            order.status = OrderStatus.IN_PROGRESS
            
        await self.session.flush()
        return order
    
    async def get_orders_with_active_access(self, user_id: int) -> List[Order]:
        """
        Busca pedidos que o usuário está acessando atualmente.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            List[Order]: Lista de pedidos sendo acessados
        """
        query = (
            select(Order)
            .join(Order.accesses)
            .where(
                and_(
                    OrderAccess.user_id == user_id,
                    OrderAccess.left_at.is_(None)
                )
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Obtém estatísticas dos pedidos.
        
        Args:
            days: Número de dias para análise
            
        Returns:
            Dict[str, Any]: Estatísticas dos pedidos
        """
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total de pedidos
        total_query = select(func.count(Order.id))
        total_result = await self.session.execute(total_query)
        total_orders = total_result.scalar() or 0
        
        # Pedidos por status
        status_query = (
            select(Order.status, func.count(Order.id))
            .where(Order.created_at >= since)
            .group_by(Order.status)
        )
        status_result = await self.session.execute(status_query)
        orders_by_status = dict(status_result.all())
        
        # Valor total
        value_query = select(func.sum(Order.total_value))
        value_result = await self.session.execute(value_query)
        total_value = value_result.scalar() or 0.0
        
        return {
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "total_value": total_value,
            "period_days": days
        }
    
    async def create_from_pdf_data(
        self,
        pdf_data: PDFExtractedData,
        logistics_type: Optional[str] = None,
        package_type: Optional[str] = None,
        observations: Optional[str] = None
    ) -> Order:
        """
        Cria um pedido a partir dos dados extraídos do PDF.
        
        Args:
            pdf_data: Dados extraídos do PDF
            logistics_type: Tipo de logística
            package_type: Tipo de embalagem
            observations: Observações
            
        Returns:
            Order: Pedido criado
        """
        # Criar o pedido
        order = Order(
            order_number=pdf_data.order_number,
            client_name=pdf_data.client_name,
            seller_name=pdf_data.seller_name,
            order_date=pdf_data.order_date,
            total_value=pdf_data.total_value,
            logistics_type=logistics_type,
            package_type=package_type,
            observations=observations,
            items_count=pdf_data.items_count,
            status=OrderStatus.PENDING
        )
        
        self.session.add(order)
        await self.session.flush()  # Para ter o ID do pedido
        
        # Criar os itens
        for item_data in pdf_data.items:
            item = OrderItem(
                order_id=order.id,
                product_code=item_data.product_code,
                product_reference=item_data.product_reference,
                product_name=item_data.product_name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                total_price=item_data.total_price
            )
            self.session.add(item)
        
        await self.session.commit()
        return order
    
    async def list_paginated(
        self,
        offset: int = 0,
        limit: int = 20,
        status_filter: Optional[str] = None
    ) -> List[Order]:
        """
        Lista pedidos com paginação e filtros.
        
        Args:
            offset: Offset para paginação
            limit: Limite de resultados
            status_filter: Filtro por status
            
        Returns:
            List[Order]: Lista de pedidos
        """
        try:
            from sqlalchemy.orm import selectinload
            
            query = (
                select(Order)
                .options(selectinload(Order.items))  # Eagerly load items relationship
                .order_by(Order.created_at.desc())
            )
            
            # Aplicar filtro por status se fornecido
            if status_filter:
                try:
                    status_enum = OrderStatus(status_filter)
                    query = query.where(Order.status == status_enum)
                except ValueError:
                    # Ignora filtro inválido
                    pass
            
            query = query.offset(offset).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in list_paginated: {str(e)}")
            raise
    
    async def recalculate_progress(self, order_id: int) -> Optional[Order]:
        """
        Recalcula o progresso de um pedido.
        
        Args:
            order_id: ID do pedido
            
        Returns:
            Optional[Order]: Pedido atualizado ou None
        """
        return await self.update_progress(order_id)
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas gerais dos pedidos.
        
        Returns:
            Dict[str, Any]: Estatísticas dos pedidos
        """
        # Total de pedidos
        total_orders_query = select(func.count(Order.id))
        total_orders_result = await self.session.execute(total_orders_query)
        total_orders = total_orders_result.scalar() or 0
        
        # Pedidos por status
        pending_query = select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        pending_result = await self.session.execute(pending_query)
        orders_pending = pending_result.scalar() or 0
        
        in_progress_query = select(func.count(Order.id)).where(Order.status == OrderStatus.IN_PROGRESS)
        in_progress_result = await self.session.execute(in_progress_query)
        orders_in_progress = in_progress_result.scalar() or 0
        
        completed_query = select(func.count(Order.id)).where(Order.status == OrderStatus.COMPLETED)
        completed_result = await self.session.execute(completed_query)
        orders_completed = completed_result.scalar() or 0
        
        # Total de itens
        total_items_query = select(func.sum(Order.items_count))
        total_items_result = await self.session.execute(total_items_query)
        total_items = total_items_result.scalar() or 0
        
        # Itens separados
        items_separated_query = (
            select(func.count(OrderItem.id))
            .where(OrderItem.is_separated == True)
        )
        items_separated_result = await self.session.execute(items_separated_query)
        items_separated = items_separated_result.scalar() or 0
        
        # Itens em compras
        items_in_purchase_query = (
            select(func.count(OrderItem.id))
            .where(OrderItem.sent_to_purchase == True)
        )
        items_in_purchase_result = await self.session.execute(items_in_purchase_query)
        items_in_purchase = items_in_purchase_result.scalar() or 0
        
        # Tempo médio de separação (pedidos completados nos últimos 30 dias)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        avg_time_query = (
            select(func.avg(
                func.extract('epoch', Order.completed_at - Order.created_at) / 3600
            ))
            .where(
                and_(
                    Order.status == OrderStatus.COMPLETED,
                    Order.completed_at >= thirty_days_ago,
                    Order.completed_at.is_not(None)
                )
            )
        )
        avg_time_result = await self.session.execute(avg_time_query)
        average_separation_time = avg_time_result.scalar()
        
        return {
            "total_orders": total_orders,
            "orders_pending": orders_pending,
            "orders_in_progress": orders_in_progress,
            "orders_completed": orders_completed,
            "total_items": total_items,
            "items_separated": items_separated,
            "items_in_purchase": items_in_purchase,
            "average_separation_time": average_separation_time
        }
    
    async def count_all(self) -> int:
        """
        Conta o total de pedidos.
        
        Returns:
            int: Total de pedidos
        """
        query = select(func.count(Order.id))
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def count_by_status(self) -> Dict[str, int]:
        """
        Conta pedidos por status.
        
        Returns:
            Dict[str, int]: Contagem por status
        """
        pending_query = select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
        pending_result = await self.session.execute(pending_query)
        
        in_progress_query = select(func.count(Order.id)).where(Order.status == OrderStatus.IN_PROGRESS)
        in_progress_result = await self.session.execute(in_progress_query)
        
        completed_query = select(func.count(Order.id)).where(Order.status == OrderStatus.COMPLETED)
        completed_result = await self.session.execute(completed_query)
        
        return {
            "pending": pending_result.scalar() or 0,
            "in_progress": in_progress_result.scalar() or 0,
            "completed": completed_result.scalar() or 0
        }