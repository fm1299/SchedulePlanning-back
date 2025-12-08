from fastapi import APIRouter

from api.endpoints import (
    # aulas,   # ❌ DESACTIVADO porque no está completo
    reservas,
  # ✔ SOLO ESTE SE ACTIVA
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

# ❌ Desactivar módulo Aulas
# api_router.include_router(
#     aulas.router,
#     prefix="/aulas",
#     tags=["Aulas"]
# )

# ✔ Activar SOLO tu módulo Bloques



api_router.include_router(reservas.router)


