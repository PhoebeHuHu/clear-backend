"""EDI API routes."""

from fastapi import APIRouter

from app.api.v1.edi.edi_decode_controller import router as decode_router
from app.api.v1.edi.edi_generate_controller import router as generate_router

# Create a router for all EDI operations
router = APIRouter(prefix="/edi")

# Include the generate and decode routers
router.include_router(generate_router)
router.include_router(decode_router)
