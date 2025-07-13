"""Testes para operações CRUD dos repositories."""
import pytest
from datetime import datetime

from app.models import User, UserRole, Order, OrderStatus
from app.repositories import UserRepository, OrderRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db):
    """Testa operações CRUD do UserRepository."""
    repo = UserRepository(db)
    
    # Create
    user = await repo.create(
        name="Test User",
        pin="9876",
        role=UserRole.SEPARATOR
    )
    await db.commit()
    
    assert user.id is not None
    assert user.name == "Test User"
    
    # Read
    found_user = await repo.get(user.id)
    assert found_user == user
    
    # Read by PIN
    found_by_pin = await repo.get_by_pin("9876")
    assert found_by_pin == user
    
    # Update
    updated = await repo.update(user.id, name="Updated User")
    await db.commit()
    assert updated.name == "Updated User"
    
    # List
    users = await repo.get_all()
    assert len(users) >= 1
    
    # Delete
    deleted = await repo.delete(user.id)
    await db.commit()
    assert deleted is True
    
    # Verify deletion
    not_found = await repo.get(user.id)
    assert not_found is None


@pytest.mark.asyncio
async def test_order_repository_crud(db):
    """Testa operações CRUD do OrderRepository."""
    repo = OrderRepository(db)
    
    # Create
    order = await repo.create(
        order_number="2025100",
        client_name="Test Client",
        seller_name="Test Seller",
        order_date=datetime.utcnow(),
        total_value=1500.00,
        status=OrderStatus.PENDING
    )
    await db.commit()
    
    assert order.id is not None
    assert order.order_number == "2025100"
    
    # Read
    found_order = await repo.get(order.id)
    assert found_order == order
    
    # Read by order number
    found_by_number = await repo.get_by_order_number("2025100")
    assert found_by_number == order
    
    # Update
    updated = await repo.update(
        order.id, 
        status=OrderStatus.IN_PROGRESS,
        items_separated=5
    )
    await db.commit()
    assert updated.status == OrderStatus.IN_PROGRESS
    assert updated.items_separated == 5
    
    # Count
    count = await repo.count(status=OrderStatus.IN_PROGRESS)
    assert count >= 1
    
    # Exists
    exists = await repo.exists(order_number="2025100")
    assert exists is True


@pytest.mark.asyncio
async def test_repository_pagination(db):
    """Testa paginação do repository."""
    repo = UserRepository(db)
    
    # Criar múltiplos usuários
    for i in range(10):
        await repo.create(
            name=f"User {i}",
            pin=f"100{i}",
            role=UserRole.SEPARATOR
        )
    await db.commit()
    
    # Testar paginação
    page1 = await repo.get_multi(skip=0, limit=5)
    assert len(page1) == 5
    
    page2 = await repo.get_multi(skip=5, limit=5)
    assert len(page2) == 5
    
    # Verificar que são diferentes
    page1_ids = [u.id for u in page1]
    page2_ids = [u.id for u in page2]
    assert set(page1_ids).isdisjoint(set(page2_ids))


@pytest.mark.asyncio
async def test_repository_filters(db):
    """Testa filtros do repository."""
    user_repo = UserRepository(db)
    
    # Criar usuários com diferentes roles
    await user_repo.create(name="Seller 1", pin="2001", role=UserRole.SELLER)
    await user_repo.create(name="Seller 2", pin="2002", role=UserRole.SELLER)
    await user_repo.create(name="Separator 1", pin="2003", role=UserRole.SEPARATOR)
    await user_repo.create(name="Buyer 1", pin="2004", role=UserRole.BUYER)
    await db.commit()
    
    # Filtrar por role
    sellers = await user_repo.get_by_role(UserRole.SELLER)
    assert len(sellers) >= 2
    assert all(u.role == UserRole.SELLER for u in sellers)
    
    separators = await user_repo.get_by_role(UserRole.SEPARATOR)
    assert len(separators) >= 1
    assert all(u.role == UserRole.SEPARATOR for u in separators)


@pytest.mark.asyncio
async def test_repository_bulk_operations(db):
    """Testa operações em lote do repository."""
    repo = UserRepository(db)
    
    # Bulk create
    users_data = [
        {"name": f"Bulk User {i}", "pin": f"300{i}", "role": UserRole.SEPARATOR}
        for i in range(5)
    ]
    
    created_users = await repo.bulk_create(users_data)
    await db.commit()
    
    assert len(created_users) == 5
    assert all(u.id is not None for u in created_users)