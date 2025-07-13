"""
Testes para cálculo de progresso dos pedidos.
"""
import pytest
from datetime import datetime
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem


def test_order_progress_percentage_empty():
    """Test progress percentage with no items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=0
    )
    
    assert order.progress_percentage == 0.0


def test_order_progress_percentage_with_separated_items():
    """Test progress percentage with only separated items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=3
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=10.0,
        total_price=10.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=20.0,
        total_price=20.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=False,
        sent_to_purchase=False
    )
    
    order.items = [item1, item2, item3]
    
    # 2 of 3 items separated = 66.67%
    expected = (2 / 3) * 100
    assert abs(order.progress_percentage - expected) < 0.01


def test_order_progress_percentage_with_purchase_items():
    """Test progress percentage with items sent to purchase."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=3
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=10.0,
        total_price=10.0,
        is_separated=False,
        sent_to_purchase=True  # Sent to purchase should NOT count as progress
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=20.0,
        total_price=20.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=False,
        sent_to_purchase=False
    )
    
    order.items = [item1, item2, item3]
    
    # Only 1 of 3 items separated (purchase items don't count) = 33.33%
    expected = (1 / 3) * 100
    assert abs(order.progress_percentage - expected) < 0.01


def test_order_progress_percentage_mixed_items():
    """Test progress percentage with both separated and purchase items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=4
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=10.0,
        total_price=10.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=20.0,
        total_price=20.0,
        is_separated=False,
        sent_to_purchase=True
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=True,
        sent_to_purchase=True  # Both separated AND in purchase (only separated counts)
    )
    item4 = OrderItem(
        product_code="004",
        product_name="Item 4",
        quantity=1,
        unit_price=40.0,
        total_price=40.0,
        is_separated=False,
        sent_to_purchase=False  # Not processed
    )
    
    order.items = [item1, item2, item3, item4]
    
    # Only 2 of 4 items separated (purchase items don't count) = 50%
    expected = (2 / 4) * 100
    assert order.progress_percentage == expected


def test_order_progress_percentage_100_percent():
    """Test progress percentage when all items are separated."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=2
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=True,
        sent_to_purchase=False
    )
    
    order.items = [item1, item2]
    
    # All items separated = 100%
    assert order.progress_percentage == 100.0


def test_order_is_complete_empty():
    """Test is_complete with no items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=0
    )
    
    assert not order.is_complete


def test_order_is_complete_partial():
    """Test is_complete with partially processed items."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=2
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=50.0,
        total_price=50.0,
        is_separated=False,
        sent_to_purchase=False  # Not processed
    )
    
    order.items = [item1, item2]
    
    assert not order.is_complete


def test_order_is_complete_all_separated():
    """Test is_complete when all items are separated."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=3
    )
    
    # Add items
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=35.0,
        total_price=35.0,
        is_separated=True,
        sent_to_purchase=True
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=35.0,
        total_price=35.0,
        is_separated=True,
        sent_to_purchase=False
    )
    
    order.items = [item1, item2, item3]
    
    assert order.is_complete


def test_percentage_decimal_formatting():
    """Test that percentage formatting works correctly for edge cases."""
    order = Order(
        order_number="12345",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=100.0,
        items_count=3
    )
    
    # Add items where only 1 of 3 is processed = 33.3333...%
    item1 = OrderItem(
        product_code="001",
        product_name="Item 1",
        quantity=1,
        unit_price=30.0,
        total_price=30.0,
        is_separated=True,
        sent_to_purchase=False
    )
    item2 = OrderItem(
        product_code="002",
        product_name="Item 2",
        quantity=1,
        unit_price=35.0,
        total_price=35.0,
        is_separated=False,
        sent_to_purchase=False
    )
    item3 = OrderItem(
        product_code="003",
        product_name="Item 3",
        quantity=1,
        unit_price=35.0,
        total_price=35.0,
        is_separated=False,
        sent_to_purchase=False
    )
    
    order.items = [item1, item2, item3]
    
    percentage = order.progress_percentage
    
    # Should be exactly 33.333...
    expected = (1 / 3) * 100
    assert abs(percentage - expected) < 0.001
    
    # When formatted to 2 decimal places, should be 33.33
    formatted = round(percentage, 2)
    assert formatted == 33.33