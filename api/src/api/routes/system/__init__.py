from fastapi import APIRouter
from .system import router as system_routes

router = APIRouter()
router.include_router(system_routes, tags=["system"])