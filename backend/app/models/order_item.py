"""Modelo de Item do Pedido."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderItem(Base):
    """
    Modelo de item do pedido.
    
    Representa um produto/item dentro de um pedido,
    com controle de separação e envio para compras.
    """
    __tablename__ = "order_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Informações do produto
    product_code = Column(String(50), nullable=False)
    product_reference = Column(String(100), nullable=True)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Controle de separação
    is_separated = Column(Boolean, default=False, nullable=False)
    separated_at = Column(DateTime, nullable=True)
    separated_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Controle de compras
    sent_to_purchase = Column(Boolean, default=False, nullable=False)
    sent_to_purchase_at = Column(DateTime, nullable=True)
    sent_to_purchase_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Controle de não enviado
    not_sent = Column(Boolean, default=False, nullable=False)
    not_sent_reason = Column(String(200), nullable=True)
    not_sent_at = Column(DateTime, nullable=True)
    not_sent_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    order = relationship("Order", back_populates="items")
    separator = relationship(
        "User", 
        foreign_keys=[separated_by_id],
        back_populates="items_separated"
    )
    purchase_requester = relationship(
        "User", 
        foreign_keys=[sent_to_purchase_by_id],
        back_populates="items_sent_to_purchase"
    )
    not_sent_by = relationship(
        "User",
        foreign_keys=[not_sent_by_id]
    )
    purchase_item = relationship(
        "PurchaseItem", 
        back_populates="order_item", 
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def mark_as_separated(self, user_id: int) -> None:
        """
        Marca o item como separado.
        
        Args:
            user_id: ID do usuário que separou o item
        """
        self.is_separated = True
        self.separated_at = datetime.utcnow()
        self.separated_by_id = user_id
        
    def send_to_purchase(self, user_id: int) -> None:
        """
        Envia o item para compras.
        
        Args:
            user_id: ID do usuário que enviou para compras
        """
        self.sent_to_purchase = True
        self.sent_to_purchase_at = datetime.utcnow()
        self.sent_to_purchase_by_id = user_id
        
    def mark_as_not_sent(self, user_id: int, reason: Optional[str] = None) -> None:
        """
        Marca o item como não enviado.
        
        Args:
            user_id: ID do usuário que marcou como não enviado
            reason: Motivo de não envio
        """
        self.not_sent = True
        self.not_sent_at = datetime.utcnow()
        self.not_sent_by_id = user_id
        self.not_sent_reason = reason
    
    def __repr__(self) -> str:
        return f"<OrderItem {self.product_name} - Qty: {self.quantity}>"