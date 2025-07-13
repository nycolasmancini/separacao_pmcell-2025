#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simples para popular o banco de dados com dados de teste.
"""
import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.core.security import get_password_hash
from datetime import datetime, timedelta


async def create_test_data():
    """Cria dados de teste."""
    
    async for session in get_async_session():
        try:
            # Criar usuarios
            users_data = [
                {"name": "Administrador", "pin": "1234", "role": UserRole.ADMIN},
                {"name": "Vendedor Teste", "pin": "5678", "role": UserRole.SELLER},
                {"name": "Separador Teste", "pin": "9012", "role": UserRole.SEPARATOR},
                {"name": "Comprador Teste", "pin": "3456", "role": UserRole.BUYER},
                {"name": "Super Admin", "pin": "0000", "role": UserRole.ADMIN},
            ]
            
            for user_data in users_data:
                user = User(
                    name=user_data["name"],
                    pin=user_data["pin"],
                    role=user_data["role"]
                )
                session.add(user)
            
            await session.commit()
            print(f"✓ Criados {len(users_data)} usuarios")
            
            # Criar pedidos de teste
            orders_data = [
                {
                    "order_number": "12345",
                    "client_name": "EMPRESA TESTE LTDA",
                    "seller_name": "João Silva",
                    "total_value": 1250.00,
                    "items_count": 8,
                    "status": OrderStatus.PENDING
                },
                {
                    "order_number": "12346",
                    "client_name": "COMÉRCIO ABC S.A.",
                    "seller_name": "Maria Santos",
                    "total_value": 2350.75,
                    "items_count": 12,
                    "status": OrderStatus.PENDING
                },
                {
                    "order_number": "12347",
                    "client_name": "DISTRIBUIDORA XYZ LTDA",
                    "seller_name": "Pedro Costa",
                    "total_value": 980.50,
                    "items_count": 6,
                    "status": OrderStatus.PENDING
                }
            ]
            
            created_orders = []
            for order_data in orders_data:
                order = Order(
                    order_number=order_data["order_number"],
                    client_name=order_data["client_name"],
                    seller_name=order_data["seller_name"],
                    order_date=datetime.now(),
                    total_value=order_data["total_value"],
                    items_count=order_data["items_count"],
                    status=order_data["status"]
                )
                session.add(order)
                created_orders.append(order)
                
            await session.flush()  # Para ter os IDs
            
            # Criar itens para cada pedido
            all_items_data = [
                # Itens para pedido 1 (EMPRESA TESTE LTDA)
                [
                    {"product_code": "001", "product_reference": "REF-001", "product_name": "PRODUTO TESTE 1", "quantity": 5, "unit_price": 100.00, "total_price": 500.00},
                    {"product_code": "002", "product_reference": "REF-002", "product_name": "PRODUTO TESTE 2", "quantity": 3, "unit_price": 250.00, "total_price": 750.00}
                ],
                # Itens para pedido 2 (COMÉRCIO ABC S.A.)
                [
                    {"product_code": "003", "product_reference": "REF-003", "product_name": "PRODUTO ABC 1", "quantity": 10, "unit_price": 85.50, "total_price": 855.00},
                    {"product_code": "004", "product_reference": "REF-004", "product_name": "PRODUTO ABC 2", "quantity": 8, "unit_price": 125.75, "total_price": 1006.00},
                    {"product_code": "005", "product_reference": "REF-005", "product_name": "PRODUTO ABC 3", "quantity": 2, "unit_price": 244.88, "total_price": 489.75}
                ],
                # Itens para pedido 3 (DISTRIBUIDORA XYZ LTDA)
                [
                    {"product_code": "006", "product_reference": "REF-006", "product_name": "PRODUTO XYZ 1", "quantity": 4, "unit_price": 150.25, "total_price": 601.00},
                    {"product_code": "007", "product_reference": "REF-007", "product_name": "PRODUTO XYZ 2", "quantity": 6, "unit_price": 63.25, "total_price": 379.50}
                ]
            ]
            
            total_items_created = 0
            for i, order in enumerate(created_orders):
                items_data = all_items_data[i]
                for item_data in items_data:
                    item = OrderItem(
                        order_id=order.id,
                        product_code=item_data["product_code"],
                        product_reference=item_data["product_reference"],
                        product_name=item_data["product_name"],
                        quantity=item_data["quantity"],
                        unit_price=item_data["unit_price"],
                        total_price=item_data["total_price"]
                    )
                    session.add(item)
                    total_items_created += 1
            
            await session.commit()
            print(f"✓ Criados {len(created_orders)} pedidos com {total_items_created} itens")
            
            print("\n🔑 PINs de acesso:")
            print("1234 - Administrador")
            print("5678 - Vendedor Teste")
            print("9012 - Separador Teste")
            print("3456 - Comprador Teste")
            print("0000 - Super Admin")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
        break


if __name__ == "__main__":
    asyncio.run(create_test_data())