"""
Endpoints para gerenciamento de pedidos.
"""
from pathlib import Path
from typing import List, Optional
import tempfile
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_session, get_current_user
from app.models.user import User
from app.models.order import Order
from app.repositories.order import OrderRepository
from app.repositories.order_item import OrderItemRepository
from app.repositories.order_access import OrderAccessRepository
from app.services.pdf_parser import PDFParser, PDFParseError
from app.schemas.pdf import (
    PDFPreviewResponse,
    PDFExtractedData, 
    OrderCreateFromPDF,
    OrderResponse
)
from app.schemas.orders import (
    OrderItemUpdate,
    OrderItemsBatchUpdate,
    OrderDetailResponse,
    OrderItemResponse,
    OrderStats,
    PurchaseItemResponse
)
from app.api.v1.websocket import (
    notify_item_separated,
    notify_item_sent_to_purchase,
    notify_order_completed,
    notify_new_order,
    notify_order_updated
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=PDFPreviewResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    logistics_type: Optional[str] = Form(None),
    package_type: Optional[str] = Form(None), 
    observations: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Upload de PDF e extração de dados para preview.
    
    Args:
        file: Arquivo PDF do pedido
        logistics_type: Tipo de logística (opcional)
        package_type: Tipo de embalagem (opcional)
        observations: Observações (opcional)
        current_user: Usuário autenticado
        
    Returns:
        PDFPreviewResponse: Dados extraídos para preview
    """
    # Validações do arquivo
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.size and file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        # Salva arquivo temporário
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)
        
        # Extrai dados do PDF
        parser = PDFParser()
        extracted_data = parser.extract(temp_path)
        
        # Remove arquivo temporário
        temp_path.unlink()
        
        # Converte para schema Pydantic para validação
        pdf_data = PDFExtractedData(**extracted_data)
        
        logger.info(
            f"PDF uploaded successfully by user {current_user.id}: "
            f"order {pdf_data.order_number}, {len(pdf_data.items)} items"
        )
        
        return PDFPreviewResponse(
            success=True,
            message="PDF processado com sucesso",
            data=pdf_data,
            errors=None
        )
        
    except PDFParseError as e:
        logger.warning(f"PDF parse error for user {current_user.id}: {str(e)}")
        return PDFPreviewResponse(
            success=False,
            message="Erro ao processar PDF",
            data=None,
            errors=[str(e)]
        )
    except Exception as e:
        logger.error(f"Unexpected error uploading PDF for user {current_user.id}: {str(e)}")
        # Remove arquivo temporário em caso de erro
        if 'temp_path' in locals() and temp_path.exists():
            temp_path.unlink()
        
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao processar PDF"
        )


@router.post("/confirm", response_model=OrderResponse)
async def confirm_order(
    order_data: OrderCreateFromPDF,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Confirma criação do pedido a partir dos dados extraídos do PDF.
    
    Args:
        order_data: Dados do pedido para criação
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        OrderResponse: Dados do pedido criado
    """
    try:
        repository = OrderRepository(session)
        
        # Verifica se o pedido já existe
        existing_order = await repository.get_by_order_number(
            order_data.pdf_data.order_number
        )
        if existing_order:
            raise HTTPException(
                status_code=400,
                detail=f"Pedido {order_data.pdf_data.order_number} já existe"
            )
        
        # Cria o pedido
        order = await repository.create_from_pdf_data(
            pdf_data=order_data.pdf_data,
            logistics_type=order_data.logistics_type,
            package_type=order_data.package_type,
            observations=order_data.observations
        )
        
        logger.info(
            f"Order created successfully by user {current_user.id}: "
            f"order {order.order_number}, ID {order.id}"
        )
        
        # Notificar via WebSocket sobre novo pedido
        await notify_new_order(order.id, order.order_number, order.client_name)
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            client_name=order.client_name,
            seller_name=order.seller_name,
            total_value=order.total_value,
            items_count=order.items_count,
            progress_percentage=order.progress_percentage,
            created_at=order.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar pedido"
        )


@router.get("", response_model=List[OrderResponse])
async def list_orders(
    page: int = 1,
    per_page: int = 20,
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Lista pedidos com paginação e filtros.
    
    Args:
        page: Número da página (1-based)
        per_page: Itens por página (max 100)
        status: Filtro por status (opcional)
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        List[OrderResponse]: Lista de pedidos
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be >= 1")
    
    if per_page < 1 or per_page > 100:
        raise HTTPException(status_code=400, detail="Per page must be between 1 and 100")
    
    try:
        logger.info(f"Orders requested by user {current_user.id}")
        
        repository = OrderRepository(session)
        offset = (page - 1) * per_page
        orders = await repository.list_paginated(offset=offset, limit=per_page, status_filter=status)
        
        return [
            OrderResponse(
                id=order.id,
                order_number=order.order_number,
                client_name=order.client_name,
                seller_name=order.seller_name,
                total_value=order.total_value,
                items_count=order.items_count,
                progress_percentage=order.progress_percentage,
                created_at=order.created_at
            ) for order in orders
        ]
        
    except Exception as e:
        logger.error(f"Error listing orders for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao listar pedidos"
        )


@router.get("/purchase-items", response_model=List[PurchaseItemResponse])
async def get_purchase_items(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os itens enviados para compras.
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        List[PurchaseItemResponse]: Lista de itens em compras
    """
    try:
        from app.repositories.purchase_item import PurchaseItemRepository
        
        logger.info(f"Purchase items requested by user {current_user.id} ({current_user.name})")
        
        purchase_repo = PurchaseItemRepository(session)
        purchase_items = await purchase_repo.get_pending_items()
        
        logger.info(f"Found {len(purchase_items)} purchase items")
        
        result = []
        for item in purchase_items:
            try:
                # Verificar se as relações existem
                if not item.order_item:
                    logger.warning(f"Purchase item {item.id} has no order_item")
                    continue
                    
                if not item.order_item.order:
                    logger.warning(f"Purchase item {item.id} order_item has no order")
                    continue
                    
                result.append(PurchaseItemResponse(
                    id=item.order_item.id,
                    order_id=item.order_item.order_id,
                    order_number=item.order_item.order.order_number,
                    client_name=item.order_item.order.client_name,
                    product_code=item.order_item.product_code,
                    product_name=item.order_item.product_name,
                    quantity=item.order_item.quantity,
                    requested_at=item.requested_at,
                    completed_at=item.completed_at
                ))
            except Exception as item_error:
                logger.error(f"Error processing purchase item {item.id}: {str(item_error)}")
                continue
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting purchase items for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar itens em compras"
        )


@router.get("/stats", response_model=OrderStats)
async def get_orders_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas dos pedidos para o dashboard.
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        OrderStats: Estatísticas dos pedidos
    """
    try:
        logger.info(f"Stats requested by user {current_user.id}")
        
        order_repo = OrderRepository(session)
        
        # Get basic order stats
        total_orders = await order_repo.count_all()
        orders_by_status = await order_repo.count_by_status()
        
        # Calculate stats
        orders_pending = orders_by_status.get('pending', 0)
        orders_in_progress = orders_by_status.get('in_progress', 0)
        orders_completed = orders_by_status.get('completed', 0)
        
        # Get item stats
        from app.repositories.order_item import OrderItemRepository
        item_repo = OrderItemRepository(session)
        total_items = await item_repo.count_all()
        items_separated = await item_repo.count_separated()
        items_in_purchase = await item_repo.count_in_purchase()
        
        return OrderStats(
            total_orders=total_orders,
            orders_in_progress=orders_in_progress,
            orders_completed=orders_completed,
            orders_pending=orders_pending,
            total_items=total_items,
            items_separated=items_separated,
            items_in_purchase=items_in_purchase,
            average_separation_time=None  # TODO: Implement if needed
        )
        
    except Exception as e:
        logger.error(f"Error getting orders stats for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar estatísticas"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Busca pedido por ID.
    
    Args:
        order_id: ID do pedido
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        OrderResponse: Dados do pedido
    """
    try:
        repository = OrderRepository(session)
        order = await repository.get(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            client_name=order.client_name,
            seller_name=order.seller_name,
            total_value=order.total_value,
            items_count=order.items_count,
            progress_percentage=order.progress_percentage,
            created_at=order.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar pedido"
        )


@router.get("/{order_id}/detail", response_model=OrderDetailResponse)
async def get_order_detail(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Busca detalhes completos do pedido incluindo itens.
    
    Args:
        order_id: ID do pedido
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        OrderDetailResponse: Dados completos do pedido
    """
    try:
        # Registrar acesso ao pedido
        access_repo = OrderAccessRepository(session)
        await access_repo.create_access(order_id, current_user.id)
        
        # Buscar pedido
        order_repo = OrderRepository(session)
        order = await order_repo.get(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        # Buscar itens
        item_repo = OrderItemRepository(session)
        items = await item_repo.get_by_order(order_id)
        
        return OrderDetailResponse(
            id=order.id,
            order_number=order.order_number,
            client_name=order.client_name,
            seller_name=order.seller_name,
            total_value=order.total_value,
            items_count=order.items_count,
            progress_percentage=order.progress_percentage,
            status=order.status,
            logistics_type=order.logistics_type,
            package_type=order.package_type,
            observations=order.observations,
            created_at=order.created_at,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_code=item.product_code,
                    product_reference=item.product_reference,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    separated=item.is_separated,
                    sent_to_purchase=item.sent_to_purchase,
                    separated_at=item.separated_at
                )
                for item in items
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order detail {order_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar detalhes do pedido"
        )


@router.patch("/{order_id}/items", response_model=OrderDetailResponse)
async def update_order_items(
    order_id: int,
    updates: OrderItemsBatchUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza múltiplos itens do pedido em lote.
    
    Args:
        order_id: ID do pedido
        updates: Lista de atualizações para os itens
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        OrderDetailResponse: Dados atualizados do pedido
    """
    try:
        # Verificar se o pedido existe
        order_repo = OrderRepository(session)
        order = await order_repo.get(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        item_repo = OrderItemRepository(session)
        
        # Processar cada atualização
        for update in updates.updates:
            item = await item_repo.get(update.item_id)
            if not item or item.order_id != order_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {update.item_id} não encontrado no pedido {order_id}"
                )
            
            # Aplicar atualizações
            if update.separated is not None:
                if update.separated:
                    await item_repo.mark_separated(update.item_id, current_user.id)
                    logger.info(f"Item {update.item_id} marked as separated by user {current_user.id}")
                    
                    # Notificar separação via WebSocket
                    # Vamos calcular progresso temporário para a notificação
                    temp_order = await order_repo.get(order_id)
                    if temp_order:
                        await notify_item_separated(order_id, update.item_id, temp_order.progress_percentage)
                else:
                    # Reverter separação se necessário
                    item.is_separated = False
                    item.separated_at = None
                    item.separated_by_id = None
            
            if update.sent_to_purchase is not None:
                if update.sent_to_purchase:
                    purchase_item = await item_repo.send_to_purchase(update.item_id, current_user.id)
                    if purchase_item:
                        logger.info(f"Item {update.item_id} sent to purchase by user {current_user.id}")
                        
                        # Notificar envio para compras via WebSocket
                        await notify_item_sent_to_purchase(order_id, update.item_id)
                else:
                    await item_repo.mark_not_sent(update.item_id, current_user.id)
                    logger.info(f"Item {update.item_id} marked as not sent by user {current_user.id}")
        
        # Commit todas as mudanças
        await session.commit()
        
        # Recalcular progresso do pedido
        updated_order = await order_repo.recalculate_progress(order_id)
        await session.commit()
        
        # Notificar atualização do pedido e verificar se foi completado
        if updated_order:
            await notify_order_updated(order_id, updated_order.progress_percentage)
            
            # Se pedido foi completado, notificar
            if updated_order.progress_percentage >= 100.0:
                await notify_order_completed(order_id)
        
        # Retornar dados atualizados
        return await get_order_detail(order_id, session, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order items {order_id} for user {current_user.id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar itens do pedido"
        )


@router.patch("/{order_id}/items/{item_id}/purchase")
async def send_item_to_purchase(
    order_id: int,
    item_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """
    Envia item específico para compras.
    
    Args:
        order_id: ID do pedido
        item_id: ID do item
        session: Sessão do banco de dados
        current_user: Usuário autenticado
        
    Returns:
        JSON response com status
    """
    try:
        # Verificar se o pedido existe
        order_repo = OrderRepository(session)
        order = await order_repo.get(order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        
        item_repo = OrderItemRepository(session)
        item = await item_repo.get(item_id)
        
        if not item or item.order_id != order_id:
            raise HTTPException(
                status_code=404,
                detail="Item não encontrado no pedido"
            )
        
        if item.sent_to_purchase:
            raise HTTPException(
                status_code=400,
                detail="Item já foi enviado para compras"
            )
        
        # Enviar para compras
        purchase_item = await item_repo.send_to_purchase(item_id, current_user.id)
        await session.commit()
        
        # Recalcular progresso do pedido
        updated_order = await order_repo.recalculate_progress(order_id)
        await session.commit()
        
        if purchase_item:
            logger.info(f"Item {item_id} sent to purchase by user {current_user.id}")
            
            # Notificar via WebSocket
            await notify_item_sent_to_purchase(order_id, item_id)
            
            # Notificar atualização do progresso
            if updated_order:
                await notify_order_updated(order_id, updated_order.progress_percentage)
                
                # Se pedido foi completado, notificar
                if updated_order.progress_percentage >= 100.0:
                    await notify_order_completed(order_id)
            
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "Item enviado para compras com sucesso",
                    "item_id": item_id,
                    "purchase_item_id": purchase_item.id
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Erro ao enviar item para compras"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending item {item_id} to purchase for user {current_user.id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao enviar item para compras"
        )




