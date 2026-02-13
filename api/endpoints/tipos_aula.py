from fastapi import APIRouter, Depends, status, Query, Path, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from services.tipo_aula_service import TipoAulaService
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate, TipoAula
from services.aula_service import AulaService
from schemas.aula import (
    AulaCreate, AulaUpdate, AulaResponse, AulaSearch,
    AulaStatistics, AulaFrontend
)

router = APIRouter(prefix="/aulas", tags=["Aulas"])

def get_aula_service(db: Session = Depends(get_db)) -> AulaService:
    return AulaService(db)


@router.get("/", response_model=List[AulaResponse])
def get_aulas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: AulaService = Depends(get_aula_service)
):
    """Obtener todas las aulas (formato original)"""
    return service.get_all_aulas(skip, limit)


@router.get("/{aula_id}", response_model=AulaResponse)
def get_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    service: AulaService = Depends(get_aula_service)
):
    """Obtener un aula por ID (formato original)"""
    return service.get_aula(aula_id)


@router.post("/", response_model=AulaResponse, status_code=status.HTTP_201_CREATED)
def create_aula(
    aula_in: AulaCreate,
    service: AulaService = Depends(get_aula_service)
):
    """Crear una nueva aula (formato original)"""
    return service.create_aula(aula_in)


@router.put("/{aula_id}", response_model=AulaResponse)
def update_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    aula_in: AulaUpdate = ...,
    service: AulaService = Depends(get_aula_service)
):
    """Actualizar un aula (formato original)"""
    return service.update_aula(aula_id, aula_in)


@router.delete("/{aula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aula(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    service: AulaService = Depends(get_aula_service)
):
    """Eliminar un aula"""
    service.delete_aula(aula_id)
    return None


@router.get("/frontend/all", response_model=List[AulaFrontend])
def get_aulas_frontend(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: AulaService = Depends(get_aula_service)
):
    """Obtener todas las aulas en formato para frontend"""
    aulas = service.get_all_aulas(skip, limit)
    return [service.convertir_a_frontend(aula) for aula in aulas]


@router.post("/frontend/create", response_model=AulaFrontend, status_code=status.HTTP_201_CREATED)
def create_aula_frontend(
    aula_data: dict, 
    service: AulaService = Depends(get_aula_service)
):
    """Crear una nueva aula desde frontend"""
    tipo_nombre = aula_data.get('tipo', 'Aula')
    tipo_aula = service.db.query(TipoAula).filter(
        TipoAula.nombre == tipo_nombre
    ).first()
    
    if not tipo_aula:
        raise HTTPException(status_code=400, detail=f"Tipo '{tipo_nombre}' no encontrado")
    
    estado_map_frontend_backend = {
        'available': 'disponible',
        'occupied': 'ocupada',
        'maintenance': 'mantenimiento'
    }
    
    aula_create = AulaCreate(
        codigo=aula_data.get('numero', ''),
        nombre=aula_data.get('nombre', ''),
        id_tipo=tipo_aula.id_tipo,
        capacidad=aula_data.get('capacidad', 30),
        ubicacion=aula_data.get('ubicacion'),
        descripcion=aula_data.get('descripcion'),
        equipamiento=aula_data.get('equipamiento'),
        estado=estado_map_frontend_backend.get(
            aula_data.get('status', 'available'),
            'disponible'
        )
    )
    
    aula = service.create_aula(aula_create)
    return service.convertir_a_frontend(aula)


@router.patch("/frontend/{aula_id}/status", response_model=AulaFrontend)
def update_aula_status_frontend(
    aula_id: int = Path(..., gt=0, description="ID del aula"),
    status: str = Query(..., description="Nuevo estado para frontend: available, occupied, maintenance"),
    service: AulaService = Depends(get_aula_service)
):
    """Actualizar estado de un aula desde frontend"""
    estado_map = {
        'available': 'disponible',
        'occupied': 'ocupada',
        'maintenance': 'mantenimiento'
    }
    
    if status not in estado_map:
        raise HTTPException(
            status_code=400, 
            detail="Estado debe ser: available, occupied, o maintenance"
        )
    
    aula = service.update_aula_status(aula_id, estado_map[status])
    return service.convertir_a_frontend(aula)


@router.post("/search", response_model=List[AulaResponse])
def search_aulas(
    search_params: AulaSearch,
    service: AulaService = Depends(get_aula_service)
):
    """Buscar aulas por criterios"""
    return service.search_aulas(search_params)


@router.get("/tipo/{tipo_id}", response_model=List[AulaResponse])
def get_aulas_by_tipo(
    tipo_id: int = Path(..., gt=0, description="ID del tipo de aula"),
    service: AulaService = Depends(get_aula_service)
):
    """Obtener aulas por tipo"""
    return service.get_aulas_by_tipo(tipo_id)


@router.get("/statistics/summary", response_model=AulaStatistics)
def get_statistics(
    service: AulaService = Depends(get_aula_service)
):
    """Obtener estadísticas de aulas"""
    return service.get_statistics()


@router.get("/disponibles", response_model=List[AulaResponse])
def get_aulas_disponibles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: AulaService = Depends(get_aula_service)
):
    """Obtener aulas disponibles"""
    return service.get_aulas_disponibles(skip, limit)