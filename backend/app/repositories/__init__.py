"""
Repositórios para acesso ao banco de dados.

Este módulo implementa o padrão Repository para abstrair
o acesso ao banco de dados e facilitar testes.
"""
from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.order import OrderRepository
from app.repositories.order_item import OrderItemRepository
from app.repositories.order_access import OrderAccessRepository
from app.repositories.purchase_item import PurchaseItemRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "OrderRepository",
    "OrderItemRepository",
    "OrderAccessRepository",
    "PurchaseItemRepository",
]