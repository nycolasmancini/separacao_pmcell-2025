"""Modelo de usuário do sistema."""
from datetime import datetime
from enum import Enum
from typing import List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship, validates

from app.core.database import Base
from app.core.security import get_password_hash

if TYPE_CHECKING:
    from app.models.order import Order
    from app.models.order_access import OrderAccess


class UserRole(str, Enum):
    """Roles disponíveis para usuários."""
    SEPARATOR = "separator"
    SELLER = "seller"
    BUYER = "buyer"
    ADMIN = "admin"


class User(Base):
    """Modelo de usuário."""
    
    __tablename__ = "users"
    
    # Colunas
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    pin_hash = Column(String(255), nullable=False)
    pin_unique = Column(String(4), nullable=False, unique=True, index=True)  # PIN para unicidade
    role = Column(SQLEnum(UserRole), nullable=False)
    photo_url = Column(String(500), nullable=True)  # URL para foto do usuário
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)  # Último login do usuário
    
    def __init__(self, pin=None, **kwargs):
        """Inicializa o usuário validando campos obrigatórios."""
        # Validar nome antes de criar o objeto
        if 'name' not in kwargs or not kwargs['name']:
            raise ValueError("Nome é obrigatório")
        
        # Validar e hash do PIN se fornecido
        if pin is not None:
            self._validate_pin(pin)
            kwargs['pin_hash'] = get_password_hash(pin)
            kwargs['pin_unique'] = pin  # Para garantir unicidade
        
        super().__init__(**kwargs)
    
    # Relacionamentos 
    order_accesses = relationship("OrderAccess", back_populates="user", lazy="select")
    items_separated = relationship("OrderItem", foreign_keys="OrderItem.separated_by_id", back_populates="separator", lazy="select")
    items_sent_to_purchase = relationship("OrderItem", foreign_keys="OrderItem.sent_to_purchase_by_id", back_populates="purchase_requester", lazy="select")
    
    def _validate_pin(self, pin: str):
        """Valida o PIN do usuário."""
        if not pin:
            raise ValueError("PIN é obrigatório")
        
        if not isinstance(pin, str):
            raise ValueError("PIN deve ser uma string")
        
        if len(pin) != 4:
            raise ValueError("PIN deve ter exatamente 4 dígitos")
        
        if not pin.isdigit():
            raise ValueError("PIN deve conter apenas números")
    
    @property
    def pin(self):
        """Property para compatibilidade com testes (retorna None pois PIN é hasheado)."""
        return None  # PIN não deve ser exposto após hash
    
    def verify_pin(self, pin: str) -> bool:
        """Verifica se o PIN está correto."""
        from app.core.security import verify_password
        return verify_password(pin, self.pin_hash)
    
    @validates('pin_hash')
    def validate_pin_hash(self, key, pin_hash):
        """Valida o hash do PIN."""
        if not pin_hash:
            raise ValueError("Hash do PIN é obrigatório")
        
        return pin_hash
    
    @validates('name')
    def validate_name(self, key, name):
        """Valida o nome do usuário."""
        if not name or not name.strip():
            raise ValueError("Nome é obrigatório")
        
        return name.strip()
    
    def __str__(self):
        """Representação string do usuário."""
        return f"User(name='{self.name}', role={self.role.value})"
    
    def __repr__(self):
        """Representação para debug."""
        return f"<User(id={self.id}, name='{self.name}', role={self.role.value})>"