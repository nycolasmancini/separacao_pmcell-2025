"""
Script para popular o banco de dados com dados de teste.
"""
import asyncio
import argparse
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.core.security import get_password_hash


async def create_users(session: AsyncSession):
    """Cria usuarios de teste."""
    users_data = [
        {"name": "Administrador", "pin": "1234", "role": "admin"},
        {"name": "Vendedor Teste", "pin": "5678", "role": "vendedor"},
        {"name": "Separador Teste", "pin": "9012", "role": "separador"},
        {"name": "Comprador Teste", "pin": "3456", "role": "comprador"},
        {"name": "Super Admin", "pin": "0000", "role": "admin"},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            name=user_data["name"],
            pin=user_data["pin"],  # O modelo j� faz o hash
            role=user_data["role"]
        )
        session.add(user)
        users.append(user)
    
    await session.commit()
    print(f" Criados {len(users)} usu�rios de teste")
    return users


async def create_sample_orders(session: AsyncSession):
    """Cria pedidos de exemplo."""
    orders_data = [
        {
            "order_number": "12345",
            "client_name": "EMPRESA TESTE LTDA",
            "seller_name": "Jo�o Silva",
            "total_value": 1250.00,
            "status": OrderStatus.PENDING,
            "items": [
                {
                    "product_code": "001",
                    "product_reference": "REF-001", 
                    "product_name": "PRODUTO TESTE 1",
                    "quantity": 5,
                    "unit_price": 100.00,
                    "total_price": 500.00
                },
                {
                    "product_code": "002",
                    "product_reference": "REF-002",
                    "product_name": "PRODUTO TESTE 2", 
                    "quantity": 3,
                    "unit_price": 250.00,
                    "total_price": 750.00
                }
            ]
        },
        {
            "order_number": "12346",
            "client_name": "CLIENTE EXEMPLO SA",
            "seller_name": "Maria Santos",
            "total_value": 890.50,
            "status": OrderStatus.IN_PROGRESS,
            "items": [
                {
                    "product_code": "003",
                    "product_reference": "REF-003",
                    "product_name": "PRODUTO EXEMPLO A",
                    "quantity": 2,
                    "unit_price": 200.00,
                    "total_price": 400.00
                },
                {
                    "product_code": "004", 
                    "product_reference": "REF-004",
                    "product_name": "PRODUTO EXEMPLO B",
                    "quantity": 1,
                    "unit_price": 490.50,
                    "total_price": 490.50
                }
            ]
        },
        {
            "order_number": "12347",
            "client_name": "DEMO CORP",
            "seller_name": "Carlos Lima",
            "total_value": 2100.00,
            "status": OrderStatus.COMPLETED,
            "items": [
                {
                    "product_code": "005",
                    "product_reference": "REF-005",
                    "product_name": "PRODUTO DEMO X",
                    "quantity": 10,
                    "unit_price": 150.00,
                    "total_price": 1500.00
                },
                {
                    "product_code": "006",
                    "product_reference": "REF-006", 
                    "product_name": "PRODUTO DEMO Y",
                    "quantity": 4,
                    "unit_price": 150.00,
                    "total_price": 600.00
                }
            ]
        }
    ]
    
    orders = []
    for order_data in orders_data:
        # Criar o pedido
        order = Order(
            order_number=order_data["order_number"],
            client_name=order_data["client_name"],
            seller_name=order_data["seller_name"],
            order_date=datetime.now() - timedelta(days=len(orders)),
            total_value=order_data["total_value"],
            items_count=sum(item["quantity"] for item in order_data["items"]),
            status=order_data["status"]
        )
        session.add(order)
        await session.flush()  # Para ter o ID
        
        # Criar os itens
        for item_data in order_data["items"]:
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
        
        orders.append(order)
    
    await session.commit()
    print(f" Criados {len(orders)} pedidos de exemplo")
    return orders


async def clean_database(session: AsyncSession):
    """Limpa todos os dados do banco."""
    from app.models import User, Order, OrderItem, OrderAccess, PurchaseItem
    
    # Deletar em ordem (relacionamentos)
    await session.execute("DELETE FROM purchase_item")
    await session.execute("DELETE FROM order_access")
    await session.execute("DELETE FROM order_item")
    await session.execute("DELETE FROM order_table")  # Note: table name
    await session.execute("DELETE FROM user_table")   # Note: table name
    
    await session.commit()
    print(">� Banco de dados limpo")


async def main():
    """Fun��o principal do seed."""
    parser = argparse.ArgumentParser(description="Populate database with test data")
    parser.add_argument("--clean", action="store_true", help="Clean database before seeding")
    args = parser.parse_args()
    
    print("<1 Iniciando seed do banco de dados...")
    
    async for session in get_async_session():
        try:
            if args.clean:
                await clean_database(session)
            
            # Criar dados
            users = await create_users(session)
            orders = await create_sample_orders(session)
            
            print("( Seed completo!")
            print(f"=e Usu�rios: {len(users)}")
            print(f"=� Pedidos: {len(orders)}")
            print("\n= PINs de acesso:")
            print("1234 - Administrador")
            print("5678 - Vendedor Teste")
            print("9012 - Separador Teste")
            print("3456 - Comprador Teste")
            print("0000 - Super Admin")
            
        except Exception as e:
            print(f"L Erro no seed: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()
        break


if __name__ == "__main__":
    asyncio.run(main())