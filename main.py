from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import Base, engine
#from models import Base
from api.router import api_router

from models.usuario import Usuario
from models.aula import Aula
from models.reserva import Reserva
from models.bloque_model import BloqueHorario
from models.horario_asignado import HorarioAsignado
from models.mantenimiento_aula import MantenimientoAula
from models.historial import HistorialCambios
from models.administrador import Administrador



app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Sistema de Asignación de Aulas - UNSA"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/health")
def health_check():
    return {"status": "healthy"}