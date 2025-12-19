# api/endpoints/tipos_docente.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from repositories.tipo_docente_repository import TipoDocenteRepository
from repositories.asignacion_docente_repository import  AsignacionDocenteRepository
from repositories.docente_repository import DocenteRepository
from schemas.docente import TipoDocenteResponse, TipoDocente, TipoDocenteCreate, TipoDocenteUpdate

router = APIRouter()


def get_tipo_docente_repo(db: Session = Depends(get_db)) -> TipoDocenteRepository:
    return TipoDocenteRepository(db)


@router.get(
    "/",
    response_model=List[TipoDocenteResponse],
    summary="Listar tipos de docente",
    description="Obtiene todos los tipos de docente disponibles en el sistema",
)
def listar_tipos_docente(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
    repo: TipoDocenteRepository = Depends(get_tipo_docente_repo),
):
    try:
        tipos_con_count = repo.get_with_docentes_count(skip=skip, limit=limit)
        response: list[TipoDocenteResponse] = []
        for tipo, docentes_count in tipos_con_count:
            response.append(
                TipoDocenteResponse(
                    id_tipo=tipo.id_tipo,
                    nombre=tipo.nombre,
                    docentes_count=docentes_count,
                )
            )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipos de docente: {str(e)}",
        )


@router.get(
    "/{tipo_id}",
    response_model=TipoDocenteResponse,
    summary="Obtener tipo de docente por ID",
    description="Obtiene un tipo de docente específico por su ID",
)
def obtener_tipo_docente(
    tipo_id: int,
    repo: TipoDocenteRepository = Depends(get_tipo_docente_repo),
):
    tipo = repo.get(tipo_id)
    if not tipo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tipo de docente con ID {tipo_id} no encontrado",
        )

    docentes_count = len(list(tipo.docentes))
    return TipoDocenteResponse(
        id_tipo=tipo.id_tipo,
        nombre=tipo.nombre,
        docentes_count=docentes_count,
    )


@router.post(
    "/",
    response_model=TipoDocente,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo tipo de docente",
    description="Crea un nuevo tipo de docente en el sistema",
)
def crear_tipo_docente(
    tipo_in: TipoDocenteCreate,
    repo: TipoDocenteRepository = Depends(get_tipo_docente_repo),
):
    try:
        return repo.create(tipo_in)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tipo de docente: {str(e)}",
        )


@router.put(
    "/{tipo_id}",
    response_model=TipoDocente,
    summary="Actualizar tipo de docente",
    description="Actualiza la información de un tipo de docente existente",
)
def actualizar_tipo_docente(
    tipo_id: int,
    tipo_in: TipoDocenteUpdate,
    repo: TipoDocenteRepository = Depends(get_tipo_docente_repo),
):
    try:
        tipo_actual = repo.get(tipo_id)
        if not tipo_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de docente con ID {tipo_id} no encontrado",
            )

        return repo.update(tipo_actual, tipo_in)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar tipo de docente: {str(e)}",
        )


@router.delete(
    "/{tipo_id}",
    summary="Eliminar tipo de docente",
    description="Elimina un tipo de docente del sistema",
)
def eliminar_tipo_docente(
    tipo_id: int,
    repo: TipoDocenteRepository = Depends(get_tipo_docente_repo),
):
    try:
        tipo = repo.get(tipo_id)
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tipo de docente con ID {tipo_id} no encontrado",
            )

        if len(list(tipo.docentes)) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un tipo de docente que tiene docentes asociados",
            )

        success = repo.delete(tipo_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el tipo de docente",
            )

        return {
            "message": "Tipo de docente eliminado correctamente",
            "tipo_id": tipo_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo de docente: {str(e)}",
        )
