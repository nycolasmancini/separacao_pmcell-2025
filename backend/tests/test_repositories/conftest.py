"""Configurações específicas para testes de repositories."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import User, Order, OrderItem, OrderAccess, PurchaseItem


class TestDatabase:
    """Classe helper para gerenciar o banco de teste."""
    
    def __init__(self):
        self.engine = None
        self.session_maker = None
        
    async def setup(self):
        """Configura o banco de teste."""
        self.engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            echo=False,
        )
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        self.session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
    async def get_session(self):
        """Retorna uma nova sessão."""
        async with self.session_maker() as session:
            return session
            
    async def cleanup(self):
        """Limpa o banco."""
        if self.engine:
            await self.engine.dispose()


@pytest_asyncio.fixture
async def db():
    """
    Cria uma sessão de banco de dados para testes.
    
    Cada teste tem sua própria sessão isolada.
    """
    test_db = TestDatabase()
    await test_db.setup()
    
    session = await test_db.get_session()
    
    yield session
    
    await session.close()
    await test_db.cleanup()