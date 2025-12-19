from fastapi import APIRouter
from api.endpoints import (
    auth,
    tipos_aula,
    reservas,
    docentes,
    ranking_docentes,
    tipos_docente,
    asignaciones,
    # cursos,
    # horarios,
    # asignaciones,
    # restricciones,
    # conflictos,
    # auth,
    # optimization
)

# Main API router for version 1
api_router = APIRouter()

# Include all endpoint routers with their respective prefixes and tags

api_router.include_router(auth.router,
    prefix="/auth",
    tags=["Autenticación"])

# raking docentes
api_router.include_router(
    ranking_docentes.router,
    prefix="/docentes",
    tags=["Ranking Docentes"],
)

# Docentes
api_router.include_router(
    docentes.router,
    prefix="/docentes",
    tags=["Docentes"],
)


#Tipos Docentes
api_router.include_router(
    tipos_docente.router, 
    prefix="/tipos-docente", 
    tags=["Tipos de Docente"]
)

# Asignaciones
api_router.include_router(asignaciones.router,
    prefix="/asignaciones", 
    tags=["Asignaciones"]
)

# api_router.include_router(
#     auth.router,
#     prefix="/auth",
#     tags=["Autenticación"]
# )

api_router.include_router(tipos_aula.router)



api_router.include_router(reservas.router)


# api_router.include_router(
#     conflictos.router,
#     prefix="/conflictos",
#     tags=["Conflictos"]
# )

# api_router.include_router(
#     optimization.router,
#     prefix="/optimization",
#     tags=["Optimización"]
# )



