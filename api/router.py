from fastapi import APIRouter
from api.endpoints import (
    aulas, reservas,tipos_aula,auth
)

# Main API router for version 1
api_router = APIRouter()

# Include all endpoint routers with their respective prefixes and tags

api_router.include_router(auth.router,
    prefix="/auth",
    tags=["Autenticación"])

api_router.include_router(aulas.router,
    prefix="/aulas",
    tags=["Aulas"])

api_router.include_router(tipos_aula.router)



api_router.include_router(reservas.router)


