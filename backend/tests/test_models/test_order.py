"""Testes para o modelo Order."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.models import Order, OrderStatus, OrderItem


@pytest.mark.asyncio
async def test_create_order(db):
    """Testa criação de pedido."""
    order = Order(
        order_number="2025001",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=1000.00,
        status=OrderStatus.PENDING,
        logistics_type="Correios",
        package_type="Caixa",
        observations="Teste de pedido"
    )
    
    db.add(order)
    await db.commit()
    
    assert order.id is not None
    assert order.order_number == "2025001"
    assert order.client_name == "Cliente Teste"
    assert order.status == OrderStatus.PENDING
    assert order.progress_percentage == 0.0
    assert order.is_complete is False


@pytest.mark.asyncio
async def test_order_unique_number(db):
    """Testa que número do pedido é único."""
    order1 = Order(
        order_number="2025002",
        client_name="Cliente 1",
        seller_name="Vendedor 1",
        order_date=datetime.utcnow(),
        total_value=500.00
    )
    
    order2 = Order(
        order_number="2025002",  # Mesmo número
        client_name="Cliente 2",
        seller_name="Vendedor 2",
        order_date=datetime.utcnow(),
        total_value=600.00
    )
    
    db.add(order1)
    await db.commit()
    
    db.add(order2)
    with pytest.raises(IntegrityError):
        await db.commit()


@pytest.mark.asyncio
async def test_order_progress_calculation(db):
    """Testa cálculo de progresso do pedido."""
    order = Order(
        order_number="2025003",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=1500.00,
        items_count=10,
        items_separated=3
    )
    
    db.add(order)
    await db.commit()
    
    assert order.progress_percentage == 30.0  # 3 de 10 = 30%
    assert order.is_complete is False
    
    # Simular todos separados
    order.items_separated = 10
    assert order.progress_percentage == 100.0
    assert order.is_complete is True


@pytest.mark.asyncio
async def test_order_status_enum(db):
    """Testa enum de status do pedido."""
    order = Order(
        order_number="2025004",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=800.00
    )
    
    # Testar todos os status
    for status in OrderStatus:
        order.status = status
        db.add(order)
        await db.commit()
        assert order.status == status


@pytest.mark.asyncio
async def test_order_timestamps(db):
    """Testa timestamps automáticos."""
    order = Order(
        order_number="2025005",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=2000.00
    )
    
    db.add(order)
    await db.commit()
    
    assert order.created_at is not None
    assert order.updated_at is not None
    assert order.completed_at is None
    
    # Atualizar pedido
    original_updated = order.updated_at
    order.status = OrderStatus.COMPLETED
    order.completed_at = datetime.utcnow()
    await db.commit()
    
    assert order.updated_at > original_updated
    assert order.completed_at is not None