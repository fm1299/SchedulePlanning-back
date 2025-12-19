# api/endpoints/asignaciones.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.asignacion_docente_repository import AsignacionDocenteRepository  # lo crearás
from repositories.docente_repository import DocenteRepository
from schemas.docente import AsignacionDocente, AsignacionDocenteCreate, AsignacionDocenteUpdate

router = APIRouter()


def get_asignacion_repo(db: Session = Depends(get_db)) -> AsignacionDocenteRepository:
    return AsignacionDocenteRepository(db)


def get_docente_repo(db: Session = Depends(get_db)) -> DocenteRepository:
    return DocenteRepository(db)


@router.post(
    "/docentes/{docente_id}/asignaciones",
    response_model=AsignacionDocente,
    status_code=status.HTTP_201_CREATED,
    summary="Crear asignación de docente",
    description="Asigna un docente a un grupo validando que no exceda sus horas máximas",
)
def crear_asignacion(
    docente_id: int,
    asignacion_in: AsignacionDocenteCreate,
    semestre_id: int = Query(..., description="ID del semestre para validación de horas"),
    repo: AsignacionDocenteRepository = Depends(get_asignacion_repo),
):
    try:
        asignacion_data = asignacion_in.model_dump()
        asignacion_data["id_docente"] = docente_id

        nueva_asignacion = repo.create_with_validacion(
            asignacion_data,
            docente_id=docente_id,
            semestre_id=semestre_id,
        )
        return nueva_asignacion
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear asignación: {str(e)}",
        )


@router.put(
    "/asignaciones/{asignacion_id}",
    response_model=AsignacionDocente,
    summary="Actualizar asignación",
    description="Actualiza una asignación validando que no exceda las horas máximas del docente",
)
def actualizar_asignacion(
    asignacion_id: int,
    asignacion_in: AsignacionDocenteUpdate,
    docente_id: int = Query(..., description="ID del docente"),
    semestre_id: int = Query(..., description="ID del semestre para validación"),
    repo: AsignacionDocenteRepository = Depends(get_asignacion_repo),
):
    try:
        asignacion_actualizada = repo.update_with_validacion(
            asignacion_id,
            asignacion_in.model_dump(exclude_unset=True),
            docente_id=docente_id,
            semestre_id=semestre_id,
        )
        return asignacion_actualizada
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar asignación: {str(e)}",
        )


@router.get(
    "/docentes/{docente_id}/horas-asignadas",
    summary="Obtener horas asignadas del docente",
    description="Obtiene el total de horas asignadas a un docente en un semestre",
)
def obtener_horas_asignadas(
    docente_id: int,
    semestre_id: int = Query(..., description="ID del semestre"),
    docente_repo: DocenteRepository = Depends(get_docente_repo),
):
    try:
        horas_asignadas = docente_repo.get_horas_asignadas_semestre(docente_id, semestre_id)
        docente = docente_repo.get(docente_id)

        return {
            "docente_id": docente_id,
            "semestre_id": semestre_id,
            "horas_asignadas": horas_asignadas,
            "max_horas_sem": docente.max_horas_sem if docente else 0,
            "horas_disponibles": (docente.max_horas_sem - horas_asignadas) if docente else 0,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horas asignadas: {str(e)}",
        )
