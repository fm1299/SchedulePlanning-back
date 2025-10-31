from fastapi import APIRouter
from endpoints import (
    aulas,
    # docentes,
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

api_router.include_router(
    aulas.router
)

# api_router.include_router(
#     auth.router,
#     prefix="/auth",
#     tags=["Autenticación"]
# )

# api_router.include_router(
#     docentes.router,
#     prefix="/docentes",
#     tags=["Docentes"]
# )

# api_router.include_router(
#     cursos.router,
#     prefix="/cursos",
#     tags=["Cursos"]
# )

# api_router.include_router(
#     horarios.router,
#     prefix="/horarios",
#     tags=["Horarios"]
# )

# api_router.include_router(
#     asignaciones.router,
#     prefix="/asignaciones",
#     tags=["Asignaciones"]
# )

# api_router.include_router(
#     restricciones.router,
#     prefix="/restricciones",
#     tags=["Restricciones"]
# )

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
