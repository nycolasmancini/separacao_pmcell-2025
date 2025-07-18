"""Modelo de Item em Compras."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, DateTime, 
    ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class PurchaseItem(Base):
    """
    Modelo de item enviado para compras.
    
    Registra itens que precisam ser comprados, permitindo
    acompanhar o status de compra de cada item.
    """
    __tablename__ = "purchase_items"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key - relação 1:1 com OrderItem
    order_item_id = Column(
        Integer, 
        ForeignKey("order_items.id"), 
        nullable=False, 
        unique=True,
        index=True
    )
    
    # Informações de controle
    requested_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Status da compra
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Observações
    notes = Column(String(500), nullable=True)
    completion_notes = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    order_item = relationship("OrderItem", back_populates="purchase_item")
    requested_by = relationship(
        "User",
        foreign_keys=[requested_by_id],
        backref="purchase_requests"
    )
    completed_by = relationship(
        "User",
        foreign_keys=[completed_by_id],
        backref="purchase_completions"
    )
    
    @property
    def order(self):
        """Acesso rápido ao pedido através do item."""
        return self.order_item.order if self.order_item else None
    
    @property
    def duration_hours(self) -> Optional[float]:
        """
        Calcula quanto tempo o item está/esteve em compras.
        
        Returns:
            float: Horas em compras, ou None se não aplicável
        """
        end_time = self.completed_at if self.completed_at else datetime.utcnow()
        delta = end_time - self.requested_at
        return delta.total_seconds() / 3600.0
    
    def complete(self, user_id: int, notes: Optional[str] = None) -> None:
        """
        Marca o item como comprado.
        
        Args:
            user_id: ID do usuário que completou a compra
            notes: Observações sobre a compra
        """
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.completed_by_id = user_id
        self.completion_notes = notes
    
    def __repr__(self) -> str:
        status = "completed" if self.is_completed else "pending"
        return f"<PurchaseItem {self.order_item_id} Status:{status}>"