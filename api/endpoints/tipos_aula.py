from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from services.tipo_aula_service import TipoAulaService
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate, TipoAula

router = APIRouter(prefix="/tipos-aula", tags=["tipos-aula"])


def get_tipo_aula_service(db: Session = Depends(get_db)) -> TipoAulaService:
    return TipoAulaService(db)


@router.get("/", response_model=List[TipoAula])
def get_tipos_aula(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    service: TipoAulaService = Depends(get_tipo_aula_service)
):
    return service.get_all_tipos_aula(skip, limit)


@router.get("/{tipo_id}", response_model=TipoAula)
def get_tipo_aula(
    tipo_id: int = Path(..., gt=0),
    service: TipoAulaService = Depends(get_tipo_aula_service)
):
    return service.get_tipo_aula(tipo_id)


@router.post("/", response_model=TipoAula, status_code=status.HTTP_201_CREATED)
def create_tipo_aula(
    tipo_in: TipoAulaCreate,
    service: TipoAulaService = Depends(get_tipo_aula_service)
):
    return service.create_tipo_aula(tipo_in)


@router.put("/{tipo_id}", response_model=TipoAula)
def update_tipo_aula(
    tipo_id: int = Path(..., gt=0),
    tipo_in: TipoAulaUpdate = ...,
    service: TipoAulaService = Depends(get_tipo_aula_service)
):
    return service.update_tipo_aula(tipo_id, tipo_in)


@router.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tipo_aula(
    tipo_id: int = Path(..., gt=0),
    service: TipoAulaService = Depends(get_tipo_aula_service)
):
    service.delete_tipo_aula(tipo_id)
    return None