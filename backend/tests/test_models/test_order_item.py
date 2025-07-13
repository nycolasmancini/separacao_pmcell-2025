"""Testes para o modelo OrderItem."""
import pytest
from datetime import datetime

from app.models import Order, OrderItem, User, UserRole


@pytest.mark.asyncio
async def test_create_order_item(db):
    """Testa criação de item do pedido."""
    # Criar pedido primeiro
    order = Order(
        order_number="2025010",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=500.00
    )
    db.add(order)
    await db.commit()
    
    # Criar item
    item = OrderItem(
        order_id=order.id,
        product_code="101",
        product_reference="REF101",
        product_name="Produto Teste",
        quantity=2,
        unit_price=100.00,
        total_price=200.00
    )
    
    db.add(item)
    await db.commit()
    
    assert item.id is not None
    assert item.order_id == order.id
    assert item.product_name == "Produto Teste"
    assert item.is_separated is False
    assert item.sent_to_purchase is False
    assert item.not_sent is False


@pytest.mark.asyncio
async def test_mark_item_as_separated(db):
    """Testa marcar item como separado."""
    # Criar usuário separador
    user = User(
        name="Separador Teste",
        pin="9999",
        role=UserRole.SEPARATOR
    )
    db.add(user)
    
    # Criar pedido e item
    order = Order(
        order_number="2025011",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=300.00
    )
    db.add(order)
    await db.commit()
    
    item = OrderItem(
        order_id=order.id,
        product_code="102",
        product_name="Produto 2",
        quantity=1,
        unit_price=300.00,
        total_price=300.00
    )
    db.add(item)
    await db.commit()
    
    # Marcar como separado
    item.mark_as_separated(user.id)
    await db.commit()
    
    assert item.is_separated is True
    assert item.separated_at is not None
    assert item.separated_by_id == user.id


@pytest.mark.asyncio
async def test_send_item_to_purchase(db):
    """Testa enviar item para compras."""
    # Criar usuário
    user = User(
        name="Comprador Teste",
        pin="8888",
        role=UserRole.BUYER
    )
    db.add(user)
    
    # Criar pedido e item
    order = Order(
        order_number="2025012",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=400.00
    )
    db.add(order)
    await db.commit()
    
    item = OrderItem(
        order_id=order.id,
        product_code="103",
        product_name="Produto 3",
        quantity=2,
        unit_price=200.00,
        total_price=400.00
    )
    db.add(item)
    await db.commit()
    
    # Enviar para compras
    item.send_to_purchase(user.id)
    await db.commit()
    
    assert item.sent_to_purchase is True
    assert item.sent_to_purchase_at is not None
    assert item.sent_to_purchase_by_id == user.id


@pytest.mark.asyncio
async def test_mark_item_as_not_sent(db):
    """Testa marcar item como não enviado."""
    # Criar usuário
    user = User(
        name="Separador 2",
        pin="7777",
        role=UserRole.SEPARATOR
    )
    db.add(user)
    
    # Criar pedido e item
    order = Order(
        order_number="2025013",
        client_name="Cliente Teste",
        seller_name="Vendedor Teste",
        order_date=datetime.utcnow(),
        total_value=150.00
    )
    db.add(order)
    await db.commit()
    
    item = OrderItem(
        order_id=order.id,
        product_code="104",
        product_name="Produto 4",
        quantity=3,
        unit_price=50.00,
        total_price=150.00
    )
    db.add(item)
    await db.commit()
    
    # Marcar como não enviado
    reason = "Produto em falta no estoque"
    item.mark_as_not_sent(user.id, reason)
    await db.commit()
    
    assert item.not_sent is True
    assert item.not_sent_at is not None
    assert item.not_sent_by_id == user.id
    assert item.not_sent_reason == reason