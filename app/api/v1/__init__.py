from fastapi import APIRouter

from app.api.v1.edi import router as edi_router

api_router = APIRouter()

# Import and include your route modules here
# from . import users, items, etc.

api_router.include_router(edi_router)

__all__ = ["api_router"]
