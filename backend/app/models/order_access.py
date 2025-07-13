"""Modelo de Acesso ao Pedido."""
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, DateTime, ForeignKey, 
    UniqueConstraint, Index
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderAccess(Base):
    """
    Modelo de controle de acesso aos pedidos.
    
    Registra quando um usuário acessa um pedido para separação,
    permitindo controlar quem está trabalhando em cada pedido
    e calcular o tempo de separação.
    """
    __tablename__ = "order_accesses"
    
    # Evita que o mesmo usuário tenha múltiplos acessos ativos ao mesmo pedido
    __table_args__ = (
        UniqueConstraint('order_id', 'user_id', 'left_at', name='_order_user_active_uc'),
        Index('idx_order_user_active', 'order_id', 'user_id', 'left_at'),
    )
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps de controle
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    order = relationship("Order", back_populates="accesses")
    user = relationship("User", back_populates="order_accesses")
    
    @property
    def is_active(self) -> bool:
        """Verifica se o acesso está ativo (usuário ainda no pedido)."""
        return self.left_at is None
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """
        Calcula a duração do acesso em segundos.
        
        Returns:
            int: Duração em segundos, ou None se ainda ativo
        """
        if self.left_at is None:
            return None
        return int((self.left_at - self.accessed_at).total_seconds())
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """
        Calcula a duração do acesso em minutos.
        
        Returns:
            float: Duração em minutos, ou None se ainda ativo
        """
        seconds = self.duration_seconds
        if seconds is None:
            return None
        return seconds / 60.0
    
    def leave(self) -> None:
        """Marca o momento que o usuário saiu do pedido."""
        if self.is_active:
            self.left_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        status = "active" if self.is_active else "finished"
        return f"<OrderAccess Order:{self.order_id} User:{self.user_id} Status:{status}>"