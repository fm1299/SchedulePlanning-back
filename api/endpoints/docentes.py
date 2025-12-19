# api/endpoints/docentes.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from services.docente_service import DocenteService
from schemas.docente import (
    DocenteCreate,
    DocenteUpdate,
    DocenteResponse,
    DocenteListResponse,
    UsuarioBase,
    #Departamento,
    TipoDocente,
)

from repositories.docente_repository import DocenteRepository

router = APIRouter()


def get_docente_service(db: Session = Depends(get_db)) -> DocenteService:
    # aquí inyectas el repositorio cuando lo definas
    #docente_repo = DocenteRepository(db)
    return DocenteService(db)


@router.get(
    "/",
    response_model=DocenteListResponse,
    summary="Listar docentes",
    description="Obtiene una lista paginada de todos los docentes con información completa",
)
def listar_docentes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros a retornar"),
    #departamento_id: Optional[int] = Query(None, description="Filtrar por departamento"),
    tipo_docente_id: Optional[int] = Query(None, description="Filtrar por tipo de docente"),
    service: DocenteService = Depends(get_docente_service),
):
    try:
        docentes, total = service.listar_docentes(
            skip=skip,
            limit=limit,
            #departamento_id=departamento_id,
            tipo_docente_id=tipo_docente_id,
        )

        items: list[DocenteResponse] = []
        for docente in docentes:
            usuario_info = None
            if getattr(docente, "usuario_docente", None) and docente.usuario_docente.usuario:
                usuario_info = UsuarioBase(
                    username=docente.usuario_docente.usuario.username,
                    email=docente.usuario_docente.usuario.email,
                    activo=docente.usuario_docente.usuario.activo,
                    rol=docente.usuario_docente.usuario.rol,
                )

            items.append(
                DocenteResponse(
                    id_docente=docente.id_docente,
                    nombre=docente.nombre,
                    apellidos=docente.apellidos,
                    telefono=docente.telefono,
                    especialidad=docente.especialidad,
                    grado_academico=docente.grado_academico,
                    max_horas_sem=docente.max_horas_sem,
                    #departamento=Departamento(
                    #    id_departamento=docente.departamento.id_departamento,
                    #    nombre=docente.departamento.nombre,
                    #    codigo=docente.departamento.codigo,
                    #    id_facultad=docente.departamento.id_facultad,
                    #),
                    tipo_docente=TipoDocente(
                        id_tipo=docente.tipo_docente.id_tipo,
                        nombre=docente.tipo_docente.nombre,
                    ),
                    tiene_usuario=service.docente_tiene_usuario(docente.id_docente),
                    usuario_info=usuario_info,
                    #regimen=docente.regimen or "parcial",
                    #fecha_inicio=docente.fecha_inicio,
                    puntaje=None,
                )
            )

        pages = (total + limit - 1) // limit if limit > 0 else 0
        current_page = (skip // limit) + 1 if limit > 0 else 1

        return DocenteListResponse(
            items=items,
            total=total,
            page=current_page,
            size=limit,
            pages=pages,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener docentes: {str(e)}",
        )


@router.get(
    "/{docente_id}",
    response_model=DocenteResponse,
    summary="Obtener docente por ID",
    description="Obtiene la información completa de un docente específico",
)
def obtener_docente(
    docente_id: int,
    service: DocenteService = Depends(get_docente_service),
):
    docente = service.get_docente(docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con ID {docente_id} no encontrado",
        )

    usuario_info = None
    if getattr(docente, "usuario_docente", None) and docente.usuario_docente.usuario:
        usuario_info = UsuarioBase(
            username=docente.usuario_docente.usuario.username,
            email=docente.usuario_docente.usuario.email,
            activo=docente.usuario_docente.usuario.activo,
            rol=docente.usuario_docente.usuario.rol,
        )

    return DocenteResponse(
        id_docente=docente.id_docente,
        nombre=docente.nombre,
        apellidos=docente.apellidos,
        telefono=docente.telefono,
        especialidad=docente.especialidad,
        grado_academico=docente.grado_academico,
        max_horas_sem=docente.max_horas_sem,
        #departamento=Departamento(
        #    id_departamento=docente.departamento.id_departamento,
        #    nombre=docente.departamento.nombre,
        #    codigo=docente.departamento.codigo,
        #    id_facultad=docente.departamento.id_facultad,
        #),
        tipo_docente=TipoDocente(
            id_tipo=docente.tipo_docente.id_tipo,
            nombre=docente.tipo_docente.nombre,
        ),
        tiene_usuario=service.docente_tiene_usuario(docente.id_docente),
        usuario_info=usuario_info,
        #regimen=docente.regimen or "parcial",
        #fecha_inicio=docente.fecha_inicio,
        puntaje=None,
    )


@router.post(
    "/",
    response_model=DocenteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo docente",
    description="Crea un nuevo docente con la información proporcionada",
)
def crear_docente(
    docente_in: DocenteCreate,
    service: DocenteService = Depends(get_docente_service),
):
    try:
        docente_completo = service.crear_docente(docente_in)

        usuario_info = None
        if getattr(docente_completo, "usuario_docente", None) and docente_completo.usuario_docente.usuario:
            usuario_info = UsuarioBase(
                username=docente_completo.usuario_docente.usuario.username,
                email=docente_completo.usuario_docente.usuario.email,
                activo=docente_completo.usuario_docente.usuario.activo,
                rol=docente_completo.usuario_docente.usuario.rol,
            )

        return DocenteResponse(
            id_docente=docente_completo.id_docente,
            nombre=docente_completo.nombre,
            apellidos=docente_completo.apellidos,
            telefono=docente_completo.telefono,
            especialidad=docente_completo.especialidad,
            grado_academico=docente_completo.grado_academico,
            max_horas_sem=docente_completo.max_horas_sem,
            #departamento=Departamento(
            #    id_departamento=docente_completo.departamento.id_departamento,
            #    nombre=docente_completo.departamento.nombre,
            #    codigo=docente_completo.departamento.codigo,
            #    id_facultad=docente_completo.departamento.id_facultad,
            #),
            tipo_docente=TipoDocente(
                id_tipo=docente_completo.tipo_docente.id_tipo,
                nombre=docente_completo.tipo_docente.nombre,
            ),
            tiene_usuario=False,
            #regimen=docente_completo.regimen or "parcial",
            #fecha_inicio=docente_completo.fecha_inicio,
            puntaje=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear docente: {str(e)}",
        )


@router.put(
    "/{docente_id}",
    response_model=DocenteResponse,
    summary="Actualizar docente",
    description="Actualiza la información de un docente existente",
)
def actualizar_docente(
    docente_id: int,
    docente_in: DocenteUpdate,
    service: DocenteService = Depends(get_docente_service),
):
    try:
        service.actualizar_docente(docente_id, docente_in)
        return obtener_docente(docente_id, service)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar docente: {str(e)}",
        )


@router.delete(
    "/{docente_id}",
    summary="Eliminar docente",
    description="Elimina un docente del sistema",
)
def eliminar_docente(
    docente_id: int,
    service: DocenteService = Depends(get_docente_service),
):
    try:
        service.eliminar_docente(docente_id)
        return {
            "message": "Docente eliminado correctamente",
            "docente_id": docente_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar docente: {str(e)}",
        )


@router.get(
    "/{docente_id}/usuario",
    summary="Verificar usuario del docente",
    description="Verifica si un docente tiene un usuario asociado en el sistema",
)
def verificar_usuario_docente(
    docente_id: int,
    service: DocenteService = Depends(get_docente_service),
):
    docente = service.get_docente(docente_id)
    if not docente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Docente con ID {docente_id} no encontrado",
        )

    tiene_usuario = service.docente_tiene_usuario(docente_id)

    return {
        "docente_id": docente_id,
        "nombre_completo": f"{docente.nombre} {docente.apellidos}",
        "tiene_usuario": tiene_usuario,
    }
