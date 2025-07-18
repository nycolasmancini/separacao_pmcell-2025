"""Repository base com operações CRUD genéricas."""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Repository base com operações CRUD genéricas.
    
    Fornece métodos comuns para todos os repositories,
    reduzindo duplicação de código.
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Inicializa o repository.
        
        Args:
            model: Classe do modelo SQLAlchemy
            session: Sessão assíncrona do banco
        """
        self.model = model
        self.session = session
        
    async def create(self, **kwargs) -> ModelType:
        """
        Cria um novo registro.
        
        Args:
            **kwargs: Campos do modelo
            
        Returns:
            ModelType: Instância criada
        """
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.flush()
        return db_obj
    
    async def get(self, id: int) -> Optional[ModelType]:
        """
        Busca um registro por ID.
        
        Args:
            id: ID do registro
            
        Returns:
            Optional[ModelType]: Registro encontrado ou None
        """
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by(self, **kwargs) -> Optional[ModelType]:
        """
        Busca um registro por campos específicos.
        
        Args:
            **kwargs: Campos para filtrar
            
        Returns:
            Optional[ModelType]: Primeiro registro encontrado ou None
        """
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        **kwargs
    ) -> List[ModelType]:
        """
        Busca múltiplos registros com paginação.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            **kwargs: Campos para filtrar
            
        Returns:
            List[ModelType]: Lista de registros
        """
        query = select(self.model)
        
        # Aplicar filtros
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
                
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_all(self, **kwargs) -> List[ModelType]:
        """
        Busca todos os registros.
        
        Args:
            **kwargs: Campos para filtrar
            
        Returns:
            List[ModelType]: Lista de todos os registros
        """
        query = select(self.model)
        
        # Aplicar filtros
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
                
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        id: int, 
        **kwargs
    ) -> Optional[ModelType]:
        """
        Atualiza um registro.
        
        Args:
            id: ID do registro
            **kwargs: Campos para atualizar
            
        Returns:
            Optional[ModelType]: Registro atualizado ou None
        """
        db_obj = await self.get(id)
        if db_obj:
            for key, value in kwargs.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            await self.session.flush()
        return db_obj
    
    async def delete(self, id: int) -> bool:
        """
        Deleta um registro.
        
        Args:
            id: ID do registro
            
        Returns:
            bool: True se deletado, False se não encontrado
        """
        db_obj = await self.get(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.flush()
            return True
        return False
    
    async def count(self, **kwargs) -> int:
        """
        Conta registros.
        
        Args:
            **kwargs: Campos para filtrar
            
        Returns:
            int: Número de registros
        """
        query = select(func.count()).select_from(self.model)
        
        # Aplicar filtros
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
                
        result = await self.session.execute(query)
        return result.scalar() or 0
    
    async def exists(self, **kwargs) -> bool:
        """
        Verifica se existe registro com os campos especificados.
        
        Args:
            **kwargs: Campos para verificar
            
        Returns:
            bool: True se existe
        """
        count = await self.count(**kwargs)
        return count > 0
    
    async def get_with_relations(
        self, 
        id: int, 
        relations: List[str]
    ) -> Optional[ModelType]:
        """
        Busca um registro com relacionamentos carregados.
        
        Args:
            id: ID do registro
            relations: Lista de nomes de relacionamentos
            
        Returns:
            Optional[ModelType]: Registro com relacionamentos ou None
        """
        query = select(self.model).where(self.model.id == id)
        
        # Carregar relacionamentos
        for relation in relations:
            if hasattr(self.model, relation):
                query = query.options(selectinload(getattr(self.model, relation)))
                
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Cria múltiplos registros de uma vez.
        
        Args:
            objects: Lista de dicionários com dados
            
        Returns:
            List[ModelType]: Lista de registros criados
        """
        db_objects = [self.model(**obj) for obj in objects]
        self.session.add_all(db_objects)
        await self.session.flush()
        return db_objects