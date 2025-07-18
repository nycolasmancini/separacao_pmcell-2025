"""Configuração do banco de dados."""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.core.config import settings


# Base para os modelos
Base = declarative_base()

# Engine e session_maker são criados como lazy properties
_engine = None
_async_session_maker = None


def get_engine():
    """Obtém ou cria o engine assíncrono."""
    global _engine
    if _engine is None:
        # Converte DATABASE_URL para asyncpg se necessário
        database_url = settings.DATABASE_URL
        print(f"Original DATABASE_URL: {database_url}")
        
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            print(f"Converted to asyncpg: {database_url}")
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            print(f"Converted postgres to asyncpg: {database_url}")
            
        _engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
        )
    return _engine


def get_session_maker():
    """Obtém ou cria o session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    return _async_session_maker


# Aliases para compatibilidade
@property
def engine():
    return get_engine()


@property  
def async_session_maker():
    return get_session_maker()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obter sessão do banco.
    
    Yields:
        AsyncSession: Sessão assíncrona do SQLAlchemy.
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas.
    
    Usado principalmente para desenvolvimento e testes.
    Em produção, usar Alembic para migrations.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Alias para compatibilidade
get_db = get_async_session