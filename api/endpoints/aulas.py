# from fastapi import APIRouter, Depends, status, Query, Path
# from sqlalchemy.orm import Session
# from typing import List, Optional

from core.database import get_db
from services.aula_service import AulaService
from schemas.aula import (
    AulaCreate, 
    AulaUpdate, 
    AulaResponse, 
    AulaSearch,
    AulaStatistics
)

# router = APIRouter()


def get_aula_service(db: Session = Depends(get_db)) -> AulaService:
    return AulaService(db)


@router.get("/", response_model=List[AulaResponse])
def get_aulas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: AulaService = Depends(get_aula_service)
):
    return service.get_all_aulas(skip, limit)


@router.get("/{aula_id}", response_model=AulaResponse)
def get_aula(
    aula_id: int = Path(..., gt=0),
    service: AulaService = Depends(get_aula_service)
):
    return service.get_aula(aula_id)


@router.post("/", response_model=AulaResponse, status_code=status.HTTP_201_CREATED)
def create_aula(
    aula_in: AulaCreate,
    service: AulaService = Depends(get_aula_service)
):
    return service.create_aula(aula_in)


@router.put("/{aula_id}", response_model=AulaResponse)
def update_aula(
    aula_id: int = Path(..., gt=0),
    aula_in: AulaUpdate = ...,
    service: AulaService = Depends(get_aula_service)
):
    return service.update_aula(aula_id, aula_in)


@router.delete("/{aula_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aula(
    aula_id: int = Path(..., gt=0),
    service: AulaService = Depends(get_aula_service)
):
    service.delete_aula(aula_id)
    return None


@router.post("/search", response_model=List[AulaResponse])
def search_aulas(
    search_params: AulaSearch,
    service: AulaService = Depends(get_aula_service)
):
    return service.search_aulas(search_params)


@router.get("/tipo/{tipo_id}", response_model=List[AulaResponse])
def get_aulas_by_tipo(
    tipo_id: int = Path(..., gt=0),
    service: AulaService = Depends(get_aula_service)
):
    return service.get_aulas_by_tipo(tipo_id)


@router.get("/capacity/available", response_model=List[AulaResponse])
def get_available_for_capacity(
    capacidad: int = Query(..., gt=0),
    tipo_id: Optional[int] = Query(None),
    service: AulaService = Depends(get_aula_service)
):
    return service.get_available_for_capacity(capacidad, tipo_id)


@router.get("/statistics/summary", response_model=AulaStatistics)
def get_statistics(
    service: AulaService = Depends(get_aula_service)
):
    return service.get_statistics()


@router.get("/disponibles", response_model=List[AulaResponse])
def get_aulas_disponibles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: AulaService = Depends(get_aula_service)
):
    return service.get_aulas_disponibles(skip, limit)