#!/usr/bin/env python3
"""Initialize database tables"""
import asyncio
import sys
sys.path.append('/Users/nycolasmancini/Desktop/pmcell-separacao/backend')

# Import all models to ensure they're registered with Base
from app.models import User, Order, OrderItem, OrderAccess, PurchaseItem
from app.core.database import init_db

async def main():
    print("Initializing database tables...")
    print("Models imported:", User, Order, OrderItem, OrderAccess, PurchaseItem)
    await init_db()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(main())