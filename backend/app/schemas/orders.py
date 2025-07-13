"""
Schemas Pydantic para operações de pedidos e separação.
"""
from datetime import datetime
from typing import List, Optional, Literal, Any, Dict
from pydantic import BaseModel, Field


class OrderItemUpdate(BaseModel):
    """Schema para atualização de item do pedido."""
    item_id: int = Field(..., description="ID do item")
    separated: Optional[bool] = Field(None, description="Marcar como separado")
    sent_to_purchase: Optional[bool] = Field(None, description="Marcar como enviado para compras")
    not_sent: Optional[bool] = Field(None, description="Marcar como não enviado")
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_id": 1,
                "separated": True,
                "sent_to_purchase": False,
                "not_sent": False
            }
        }


class OrderItemsBatchUpdate(BaseModel):
    """Schema para atualização em lote de itens."""
    updates: List[OrderItemUpdate] = Field(..., min_items=1, description="Lista de atualizações")
    
    class Config:
        json_schema_extra = {
            "example": {
                "updates": [
                    {"item_id": 1, "separated": True},
                    {"item_id": 2, "sent_to_purchase": True}
                ]
            }
        }


class OrderItemResponse(BaseModel):
    """Schema para resposta de item do pedido."""
    id: int = Field(..., description="ID do item")
    product_code: str = Field(..., description="Código do produto")
    product_reference: str = Field(..., description="Referência do produto")
    product_name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., description="Quantidade")
    unit_price: float = Field(..., description="Preço unitário")
    total_price: float = Field(..., description="Preço total")
    separated: bool = Field(..., description="Item separado")
    sent_to_purchase: bool = Field(..., description="Enviado para compras")
    not_sent: bool = Field(default=False, description="Item não enviado")
    separated_at: Optional[datetime] = Field(None, description="Data de separação")
    
    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
    """Schema para resposta detalhada de pedido com itens."""
    id: int = Field(..., description="ID do pedido")
    order_number: str = Field(..., description="Número do orçamento")
    client_name: str = Field(..., description="Nome do cliente")
    seller_name: str = Field(..., description="Nome do vendedor")
    total_value: float = Field(..., description="Valor total")
    items_count: int = Field(..., description="Quantidade total de itens")
    progress_percentage: float = Field(..., description="Porcentagem de progresso")
    status: str = Field(..., description="Status do pedido")
    logistics_type: Optional[str] = Field(None, description="Tipo de logística")
    package_type: Optional[str] = Field(None, description="Tipo de embalagem")
    observations: Optional[str] = Field(None, description="Observações")
    created_at: datetime = Field(..., description="Data de criação")
    items: List[OrderItemResponse] = Field(..., description="Lista de itens")
    
    class Config:
        from_attributes = True


class OrderStats(BaseModel):
    """Schema para estatísticas do dashboard."""
    total_orders: int = Field(..., description="Total de pedidos")
    orders_in_progress: int = Field(..., description="Pedidos em andamento")
    orders_completed: int = Field(..., description="Pedidos concluídos")
    orders_pending: int = Field(..., description="Pedidos pendentes")
    total_items: int = Field(..., description="Total de itens")
    items_separated: int = Field(..., description="Itens separados")
    items_in_purchase: int = Field(..., description="Itens em compras")
    average_separation_time: Optional[float] = Field(None, description="Tempo médio de separação em horas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_orders": 15,
                "orders_in_progress": 5,
                "orders_completed": 8,
                "orders_pending": 2,
                "total_items": 150,
                "items_separated": 120,
                "items_in_purchase": 10,
                "average_separation_time": 2.5
            }
        }


class UserPresence(BaseModel):
    """Schema para presença de usuário em pedido."""
    user_id: int = Field(..., description="ID do usuário")
    user_name: str = Field(..., description="Nome do usuário")
    access_time: datetime = Field(..., description="Horário de acesso")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "user_name": "João Separador",
                "access_time": "2024-07-12T10:30:00"
            }
        }


class OrderWithPresence(BaseModel):
    """Schema para pedido com indicadores de presença."""
    id: int = Field(..., description="ID do pedido")
    order_number: str = Field(..., description="Número do orçamento")
    client_name: str = Field(..., description="Nome do cliente")
    seller_name: str = Field(..., description="Nome do vendedor")
    total_value: float = Field(..., description="Valor total")
    items_count: int = Field(..., description="Quantidade total de itens")
    progress_percentage: float = Field(..., description="Porcentagem de progresso")
    status: str = Field(..., description="Status do pedido")
    created_at: datetime = Field(..., description="Data de criação")
    active_users: List[UserPresence] = Field(default=[], description="Usuários ativos no pedido")
    
    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema para mensagens WebSocket."""
    type: Literal[
        "order_updated", 
        "item_separated", 
        "item_sent_to_purchase",
        "item_not_sent",
        "user_joined",
        "user_left",
        "order_completed",
        "new_order"
    ] = Field(..., description="Tipo da mensagem")
    data: Dict[str, Any] = Field(..., description="Dados da mensagem")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da mensagem")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "type": "item_separated",
                    "data": {
                        "order_id": 1,
                        "item_id": 5,
                        "progress_percentage": 75.0
                    },
                    "timestamp": "2024-07-12T10:30:00"
                },
                {
                    "type": "user_joined",
                    "data": {
                        "order_id": 1,
                        "user_id": 2,
                        "user_name": "João Separador"
                    },
                    "timestamp": "2024-07-12T10:30:00"
                }
            ]
        }


class PurchaseItemResponse(BaseModel):
    """Schema para resposta de item em compras."""
    id: int = Field(..., description="ID do item")
    order_id: int = Field(..., description="ID do pedido")
    order_number: str = Field(..., description="Número do pedido")
    client_name: str = Field(..., description="Nome do cliente")
    product_code: str = Field(..., description="Código do produto")
    product_name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., description="Quantidade")
    requested_at: datetime = Field(..., description="Data de solicitação")
    completed_at: Optional[datetime] = Field(None, description="Data de conclusão")
    
    class Config:
        from_attributes = True


class SeparatorPerformance(BaseModel):
    """Schema para performance de separador."""
    user_id: int = Field(..., description="ID do usuário")
    user_name: str = Field(..., description="Nome do usuário")
    orders_completed: int = Field(..., description="Pedidos completados")
    items_separated: int = Field(..., description="Itens separados")
    average_time_per_order: Optional[float] = Field(None, description="Tempo médio por pedido em horas")
    efficiency_score: float = Field(..., description="Score de eficiência (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 2,
                "user_name": "João Separador",
                "orders_completed": 25,
                "items_separated": 340,
                "average_time_per_order": 1.8,
                "efficiency_score": 87.5
            }
        }