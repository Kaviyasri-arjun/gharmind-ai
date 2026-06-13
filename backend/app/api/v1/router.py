"""
GHARMIND AI — V1 API Router
Aggregates all v1 endpoint routers into a single prefix.
"""
from fastapi import APIRouter

from app.api.v1.chat import router as chat_router
from app.api.v1.households import router as households_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.routines import router as routines_router
from app.api.v1.simulator import router as simulator_router
from app.api.v1.twin import router as twin_router

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(households_router)
v1_router.include_router(twin_router)
v1_router.include_router(predictions_router)
v1_router.include_router(routines_router)
v1_router.include_router(simulator_router)
v1_router.include_router(chat_router)
