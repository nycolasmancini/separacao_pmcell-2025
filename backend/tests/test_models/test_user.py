"""Testes para o modelo User."""
import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models.user import User, UserRole
from app.core.database import Base


class TestUserModel:
    """Testes para o modelo User."""
    
    def test_user_creation(self):
        """Testa criação básica de um usuário."""
        user = User(
            name="João Silva",
            pin="1234",
            role=UserRole.SEPARATOR
        )
        
        assert user.name == "João Silva"
        assert user.pin_hash is not None  # PIN deve ser hasheado
        assert user.verify_pin("1234")  # Verifica se PIN está correto
        assert user.role == UserRole.SEPARATOR
        assert user.id is None  # Ainda não foi salvo no banco
    
    def test_user_roles(self):
        """Testa os diferentes tipos de roles."""
        assert UserRole.SEPARATOR.value == "separator"
        assert UserRole.SELLER.value == "seller"
        assert UserRole.BUYER.value == "buyer"
        assert UserRole.ADMIN.value == "admin"
    
    def test_user_str_representation(self):
        """Testa representação string do usuário."""
        user = User(name="Maria", pin="5678", role=UserRole.SELLER)
        assert str(user) == "User(name='Maria', role=seller)"
    
    def test_user_repr(self):
        """Testa representação repr do usuário."""
        user = User(name="Pedro", pin="9999", role=UserRole.ADMIN)
        repr_str = repr(user)
        assert "User" in repr_str
        assert "Pedro" in repr_str
        assert "admin" in repr_str
    
    @pytest.mark.asyncio
    async def test_user_save_to_db(self, db):
        """Testa salvar usuário no banco de dados."""
        
        user = User(
            name="Ana Costa",
            pin="4321",
            role=UserRole.BUYER
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        assert user.id is not None
        assert isinstance(user.created_at, datetime)
        assert user.created_at.tzinfo is None  # Deve ser UTC naive
    
    @pytest.mark.asyncio
    async def test_user_unique_pin(self, db):
        """Testa que PIN deve ser único (constraint violation no pin_unique)."""
        
        user1 = User(name="User 1", pin="1111", role=UserRole.SEPARATOR)
        user2 = User(name="User 2", pin="1111", role=UserRole.SELLER)
        
        # Verificar que mesmo PIN é armazenado em pin_unique
        assert user1.pin_unique == "1111"
        assert user2.pin_unique == "1111"
        
        db.add(user1)
        await db.commit()
        
        db.add(user2)
        with pytest.raises(IntegrityError):
            await db.commit()
    
    @pytest.mark.asyncio
    async def test_user_required_fields(self, db):
        """Testa que campos obrigatórios devem ser preenchidos."""
        
        # Teste sem nome - deve falhar na validação
        with pytest.raises(ValueError, match="Nome é obrigatório"):
            user = User(pin="1234", role=UserRole.SEPARATOR)
    
    def test_user_pin_validation(self):
        """Testa validação do PIN."""
        # PIN deve ter exatamente 4 dígitos
        with pytest.raises(ValueError, match="PIN deve ter exatamente 4 dígitos"):
            User(name="Test", pin="123", role=UserRole.SEPARATOR)
        
        with pytest.raises(ValueError, match="PIN deve ter exatamente 4 dígitos"):
            User(name="Test", pin="12345", role=UserRole.SEPARATOR)
        
        with pytest.raises(ValueError, match="PIN deve conter apenas números"):
            User(name="Test", pin="12a4", role=UserRole.SEPARATOR)
    
    def test_user_relationships(self):
        """Testa relacionamentos do modelo User."""
        user = User(name="Test", pin="1234", role=UserRole.SEPARATOR)
        
        # Por enquanto os relacionamentos estão comentados
        # Serão testados quando os modelos Order e OrderAccess forem criados
        # assert hasattr(user, 'orders')
        # assert hasattr(user, 'order_accesses')
        
        # Teste temporário - apenas verifica que o modelo pode ser criado
        assert user is not None
    
    @pytest.mark.asyncio
    async def test_user_cascade_delete(self, db):
        """Testa que deletar usuário não deleta pedidos (SET NULL)."""
        
        user = User(name="To Delete", pin="9999", role=UserRole.SELLER)
        db.add(user)
        await db.commit()
        
        user_id = user.id
        
        # Este teste será expandido quando criarmos o modelo Order
        # Por ora, apenas verifica que o usuário pode ser deletado
        await db.delete(user)
        await db.commit()
        
        # Verifica que foi deletado
        result = await db.get(User, user_id)
        assert result is None