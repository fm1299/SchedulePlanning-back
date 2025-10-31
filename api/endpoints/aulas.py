from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from services.aula_service import AulaService
from schemas.aula import (
    AulaCreate, 
    AulaUpdate, 
    AulaResponse, 
    AulaSearch,
    AulaStatistics
)
from models.aula import TipoAula
# from api.deps import get_current_active_user, get_current_admin_user
# from app.models.user import User

router = APIRouter()


def get_aula_service(db: Session = Depends(get_db)) -> AulaService:
    """Dependency injection for AulaService"""
    return AulaService(db)


@router.get(
    "/", 
    response_model=List[AulaResponse],
    summary="Obtener lista de aulas",
    description="Retorna una lista paginada de todas las aulas registradas",
    response_description="Lista de aulas"
)
def get_aulas(
    skip: int = Query(0, ge=0, description="Número de registros a saltar para paginación"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a retornar"),
    service: AulaService = Depends(get_aula_service),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Obtener lista de aulas con paginación.
    
    - **skip**: Número de registros a saltar (para paginación)
    - **limit**: Límite de registros a retornar (máximo 100)
    
    Requiere autenticación.
    """
    return service.get_all_aulas(skip, limit)


@router.get(
    "/{aula_id}", 
    response_model=AulaResponse,
    summary="Obtener aula por ID",
    response_description="Detalles del aula"
)
def get_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    service: AulaService = Depends(get_aula_service),
    # current_user: User = Depends(get_current_active_user)
):
    """
    Obtener un aula específica por su ID.
    
    - **aula_id**: ID único del aula
    
    Requiere autenticación.
    """
    return service.get_aula(aula_id)


@router.post(
    "/", 
    response_model=AulaResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva aula",
    response_description="Aula creada"
)
def create_aula(
    aula_in: AulaCreate,
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_admin_user)  # Only admins
):
    """
    Crear una nueva aula en el sistema.
    
    - **codigo**: Código único del aula (formato: LETRA-NUMERO, ej: A-101)
    - **capacidad**: Capacidad máxima de estudiantes (1-500)
    - **tipo**: Tipo de aula (TEORIA, LABORATORIO, SEMINARIO)
    - **ubicacion**: Ubicación física del aula
    - **equipamiento**: Equipamiento disponible (opcional)
    
    Requiere permisos de administrador.
    """
    return service.create_aula(aula_in)


@router.put(
    "/{aula_id}", 
    response_model=AulaResponse,
    summary="Actualizar aula"
)
def update_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    aula_in: AulaUpdate = ...,
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_admin_user)  # Only admins
):
    """
    Actualizar información de un aula existente.
    
    Todos los campos son opcionales. Solo se actualizarán los campos proporcionados.
    
    Requiere permisos de administrador.
    """
    return service.update_aula(aula_id, aula_in)


@router.delete(
    "/{aula_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar aula"
)
def delete_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_admin_user)  # Only admins
):
    """
    Eliminar un aula del sistema.
    
    No se puede eliminar un aula con asignaciones activas.
    
    Requiere permisos de administrador.
    """
    service.delete_aula(aula_id)
    return None


@router.post(
    "/search",
    response_model=List[AulaResponse],
    summary="Buscar aulas con filtros",
    description="Búsqueda avanzada de aulas con múltiples filtros opcionales"
)
def search_aulas(
    search_params: AulaSearch,
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_active_user)
):
    """
    Búsqueda avanzada de aulas con filtros opcionales.
    
    Todos los filtros son opcionales y se combinan con lógica AND.
    
    - **codigo**: Buscar por código (coincidencia parcial)
    - **tipo**: Filtrar por tipo de aula
    - **capacidad_min**: Capacidad mínima requerida
    - **capacidad_max**: Capacidad máxima permitida
    - **ubicacion**: Filtrar por ubicación (coincidencia parcial)
    - **equipamiento**: Filtrar por equipamiento (coincidencia parcial)
    """
    return service.search_aulas(search_params)


@router.get(
    "/tipo/{tipo}",
    response_model=List[AulaResponse],
    summary="Obtener aulas por tipo",
    description="Retorna todas las aulas de un tipo específico"
)
def get_aulas_by_tipo(
    tipo: TipoAula = Path(..., description="Tipo de aula"),
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_active_user)
):
    """
    Obtener todas las aulas de un tipo específico.
    
    - **tipo**: TEORIA, LABORATORIO, o SEMINARIO
    """
    return service.get_aulas_by_tipo(tipo)


@router.get(
    "/capacity/available",
    response_model=List[AulaResponse],
    summary="Obtener aulas disponibles para capacidad",
    description="Encuentra aulas que pueden acomodar la capacidad requerida"
)
def get_available_for_capacity(
    capacidad: int = Query(..., gt=0, description="Capacidad requerida de estudiantes"),
    tipo: Optional[TipoAula] = Query(None, description="Tipo de aula (opcional)"),
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_active_user)
):
    """
    Obtener aulas que pueden acomodar la capacidad requerida.
    
    El sistema agrega automáticamente un 10% de buffer para mayor comodidad.
    Los resultados se ordenan por capacidad ascendente.
    
    - **capacidad**: Número de estudiantes a acomodar
    - **tipo**: Filtro opcional por tipo de aula
    """
    return service.get_available_for_capacity(capacidad, tipo)


@router.get(
    "/statistics/summary",
    response_model=AulaStatistics,
    summary="Obtener estadísticas de aulas",
    description="Retorna estadísticas generales sobre las aulas"
)
def get_statistics(
    service: AulaService = Depends(get_aula_service),
    #current_user: User = Depends(get_current_active_user)
):
    """
    Obtener estadísticas generales de las aulas.
    
    Incluye:
    - Total de aulas
    - Capacidad promedio, mínima y máxima
    - Distribución por tipo de aula
    """
    return service.get_statistics()
