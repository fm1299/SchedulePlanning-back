from fastapi import APIRouter
from api.endpoints import (
    aulas,tipos_aula,auth
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

# api_router.include_router(
#     aulas.router
# )

api_router.include_router(auth.router,
    prefix="/auth",
    tags=["Autenticación"])
api_router.include_router(aulas.router)
api_router.include_router(tipos_aula.router)

# api_router.include_router(
#     aulas.router
# )

api_router.include_router(auth.router,
    prefix="/auth",
    tags=["Autenticación"])
api_router.include_router(aulas.router)
api_router.include_router(tipos_aula.router)

=======
# ❌ Desactivar módulo Aulas
>>>>>>> origin/Yanira
# api_router.include_router(
#     aulas.router,
#     prefix="/aulas",
#     tags=["Aulas"]
# )

# ✔ Activar SOLO tu módulo Bloques



api_router.include_router(reservas.router)


