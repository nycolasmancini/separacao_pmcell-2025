"""Configurações globais para os testes."""
import os
import pytest
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Configurar ambiente de teste
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "False"

from app.core.database import Base, get_async_session
from app.core.config import settings

# Import dos modelos para criação das tabelas
from app.models import User, Order, OrderItem, OrderAccess, PurchaseItem


# Removido fixture event_loop - pytest-asyncio fornece sua própria


@pytest.fixture
async def test_engine():
    """Cria um engine de teste."""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    # Criar as tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """
    Cria uma sessão de banco de dados para testes.
    
    Cada teste tem sua própria sessão isolada.
    """
    from sqlalchemy.orm import sessionmaker
    
    # Criar session maker
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Criar e retornar sessão
    async with async_session_maker() as session:
        yield session
        await session.rollback()


