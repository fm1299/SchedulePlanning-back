# api/endpoints/ranking_docentes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from core.database import get_db
from models.docente import Docente 
from services.docente_service import DocenteService

router = APIRouter()

def get_docente_service(db: Session = Depends(get_db)) -> DocenteService:
    return DocenteService(db)

@router.get(
    "/ranking",
    summary="Ranking de docentes",
    response_model=List[Dict[str, Any]]  # idealmente luego un schema Pydantic
)
def ranking_docentes(
    db: Session = Depends(get_db),
    service: DocenteService = Depends(get_docente_service),
):
    docentes = db.query(Docente).all()
    ranking = [service.calcular_puntaje(d) for d in docentes]
    ranking.sort(key=lambda x: x["puntaje"], reverse=True)
    return ranking