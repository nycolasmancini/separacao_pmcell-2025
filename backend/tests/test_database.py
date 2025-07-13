"""Testes para configuração do banco de dados."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.database import (
    get_async_session,
    init_db,
    Base,
    get_session_maker,
    get_engine
)


class TestDatabase:
    """Testes para configuração do banco de dados."""
    
    def test_base_is_declarative_base(self):
        """Testa se Base é uma instância válida de declarative_base."""
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')
        assert Base.metadata is not None
    
    def test_engine_exists(self):
        """Testa se engine foi criado."""
        engine = get_engine()
        assert engine is not None
        assert hasattr(engine, 'url')
    
    def test_session_maker_exists(self):
        """Testa se session maker foi criado."""
        session_maker = get_session_maker()
        assert session_maker is not None
        assert hasattr(session_maker, 'kw')
        assert session_maker.kw.get('expire_on_commit') is False
    
    @pytest.mark.asyncio
    async def test_get_async_session(self):
        """Testa se get_async_session retorna uma sessão válida."""
        async for session in get_async_session():
            assert isinstance(session, AsyncSession)
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
            break
    
    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """Testa se init_db cria as tabelas."""
        # Este teste será expandido quando criarmos os modelos
        await init_db()
        # Por enquanto apenas verifica se não lança exceção
        assert True
    
    def test_database_url_configuration(self):
        """Testa se a URL do banco está configurada corretamente."""
        from app.core.config import settings
        
        engine = get_engine()
        
        # Para desenvolvimento, deve usar SQLite
        if settings.ENVIRONMENT == "development":
            assert "sqlite" in str(engine.url)
        # Para produção, deve usar PostgreSQL
        elif settings.ENVIRONMENT == "production":
            assert "postgresql" in str(engine.url)