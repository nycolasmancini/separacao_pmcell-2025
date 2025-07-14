"""
Testes para verificar a funcionalidade do botão "Finalizar Pedido".
"""
import pytest
from datetime import datetime
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem


def test_order_completion_button_logic_with_separated_items():
    """Test that order can be completed when all items are separated."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=2,
        items_separated=2,
        items_not_sent=0,
        items_in_purchase=0
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=True,
        sent_to_purchase=False,
        not_sent=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=True,
        sent_to_purchase=False,
        not_sent=False
    )
    
    order.items = [item1, item2]
    
    # Should be 100% complete
    assert order.progress_percentage == 100.0
    assert order.is_complete == True


def test_order_completion_button_logic_with_not_sent_items():
    """Test that order can be completed when all items are not_sent."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=2,
        items_separated=0,
        items_not_sent=2,
        items_in_purchase=0
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=False,
        sent_to_purchase=False,
        not_sent=True
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=False,
        sent_to_purchase=False,
        not_sent=True
    )
    
    order.items = [item1, item2]
    
    # Should be 100% complete
    assert order.progress_percentage == 100.0
    assert order.is_complete == True


def test_order_completion_button_logic_mixed_items():
    """Test that order can be completed with mixed separated and not_sent items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=3,
        items_separated=2,
        items_not_sent=1,
        items_in_purchase=0
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=True,
        sent_to_purchase=False,
        not_sent=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=True,
        sent_to_purchase=False,
        not_sent=False
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=40.0,
        total_price=40.0,
        is_separated=False,
        sent_to_purchase=False,
        not_sent=True
    )
    
    order.items = [item1, item2, item3]
    
    # Should be 100% complete (2 separated + 1 not_sent = 3 total)
    assert order.progress_percentage == 100.0
    assert order.is_complete == True


def test_order_completion_button_logic_with_purchase_items():
    """Test that order cannot be completed when items are only in purchase."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=2,
        items_separated=0,
        items_not_sent=0,
        items_in_purchase=2
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=False,
        sent_to_purchase=True,
        not_sent=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=False,
        sent_to_purchase=True,
        not_sent=False
    )
    
    order.items = [item1, item2]
    
    # Should NOT be complete (purchase items don't count)
    assert order.progress_percentage == 0.0
    assert order.is_complete == False