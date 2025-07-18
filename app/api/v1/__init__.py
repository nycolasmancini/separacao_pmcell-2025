from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .orders import router as orders_router
from .users import router as users_router
from .websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(orders_router, prefix="/orders", tags=["orders"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(websocket_router, prefix="/ws", tags=["websocket"])