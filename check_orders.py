#!/usr/bin/env python3
"""Check existing orders in the database"""
import asyncio
import sys
sys.path.append('/Users/nycolasmancini/Desktop/pmcell-separacao/backend')

from sqlalchemy import select
from app.core.database import get_async_session
from app.models.order import Order

async def check_orders():
    async for session in get_async_session():
        try:
            # Check all orders
            query = select(Order).order_by(Order.created_at.desc())
            result = await session.execute(query)
            orders = result.scalars().all()
            
            print(f"Total orders in database: {len(orders)}")
            print("-" * 60)
            
            for order in orders:
                print(f"Order #{order.order_number}")
                print(f"  ID: {order.id}")
                print(f"  Client: {order.client_name}")
                print(f"  Seller: {order.seller_name}")
                print(f"  Status: {order.status}")
                print(f"  Items: {order.items_count}")
                print(f"  Progress: {order.progress_percentage}%")
                print(f"  Created: {order.created_at}")
                print()
            
            # Check specifically for order 27830
            order_27830 = await session.execute(
                select(Order).where(Order.order_number == "27830")
            )
            existing = order_27830.scalar_one_or_none()
            
            if existing:
                print("⚠️  ORDER 27830 ALREADY EXISTS IN DATABASE!")
                print(f"   Created at: {existing.created_at}")
                print(f"   ID: {existing.id}")
            else:
                print("✅ Order 27830 does not exist in database")
                
        finally:
            await session.close()

if __name__ == "__main__":
    asyncio.run(check_orders())