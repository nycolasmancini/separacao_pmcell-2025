"""Modelo de Pedido."""
from enum import Enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    Enum as SQLAlchemyEnum, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderStatus(str, Enum):
    """Status possíveis de um pedido."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(Base):
    """
    Modelo de pedido.
    
    Representa um pedido importado de um PDF com suas informações
    principais e relacionamentos com itens e acessos.
    """
    __tablename__ = "orders"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Informações do pedido
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    client_name = Column(String(200), nullable=False)
    seller_name = Column(String(100), nullable=False)
    order_date = Column(DateTime, nullable=False)
    total_value = Column(Float, nullable=False)
    
    # Controle de status
    status = Column(
        SQLAlchemyEnum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )
    
    # Logística
    logistics_type = Column(String(50), nullable=True)
    package_type = Column(String(50), nullable=True)
    observations = Column(String(500), nullable=True)
    
    # Contadores
    items_count = Column(Integer, default=0, nullable=False)
    items_separated = Column(Integer, default=0, nullable=False)
    items_in_purchase = Column(Integer, default=0, nullable=False)
    items_not_sent = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    accesses = relationship("OrderAccess", back_populates="order", cascade="all, delete-orphan")
    
    @property
    def progress_percentage(self) -> float:
        """
        Calcula a porcentagem de progresso do pedido.
        Itens separados E não enviados contam como processados (compras não contam).
        
        Returns:
            float: Porcentagem de 0 a 100
        """
        if self.items_count == 0:
            return 0.0
        
        # Usar contadores para evitar lazy loading quando disponíveis
        # Itens separados E não enviados contam como processados
        if self.items_separated is not None and self.items_not_sent is not None:
            processed_items = self.items_separated + self.items_not_sent
        else:
            # Fallback para contar diretamente os itens (usado em testes)
            processed_items = sum(1 for item in self.items if item.is_separated or item.not_sent)
            
        return (processed_items / self.items_count) * 100
    
    @property
    def is_complete(self) -> bool:
        """
        Verifica se o pedido está completo.
        Itens separados E não enviados contam como processados (compras não contam).
        """
        if self.items_count == 0:
            return False
        
        # Usar contadores para evitar lazy loading quando disponíveis
        # Itens separados E não enviados contam para completar pedido
        if self.items_separated is not None and self.items_not_sent is not None:
            processed_count = self.items_separated + self.items_not_sent
            return processed_count == self.items_count
        else:
            # Fallback para contar diretamente os itens (usado em testes)
            processed_count = sum(1 for item in self.items if item.is_separated or item.not_sent)
            return processed_count == self.items_count
    
    def __repr__(self) -> str:
        return f"<Order {self.order_number} - {self.client_name}>"