from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum



class TipoAulaEnum(str, Enum):
    TEORIA = "TEORIA"
    LABORATORIO = "LABORATORIO"
    SEMINARIO = "SEMINARIO"

class AulaBase(BaseModel):
    codigo: str = Field(..., example="A-101")
    capacidad: int = Field(..., gt=0, example=40)
    tipo: TipoAulaEnum
    ubicacion: str = Field(..., example="Edificio A, Piso 1")
    equipamiento: Optional[str] = Field(None, example="Proyector, Pizarra")

class AulaCreate(AulaBase):
    pass

class AulaUpdate(BaseModel):
    codigo: Optional[str] = None
    capacidad: Optional[int] = Field(None, gt=0)
    tipo: Optional[TipoAulaEnum] = None
    ubicacion: Optional[str] = None
    equipamiento: Optional[str] = None

class AulaResponse(AulaBase):
    id: int
    
    class Config:
        from_attributes = True


class AulaSearch(BaseModel):
    codigo: Optional[str] = Field(None, description="Buscar por código (coincidencia parcial)")
    tipo: Optional[TipoAulaEnum] = Field(None, description="Filtrar por tipo de aula")
    capacidad_min: Optional[int] = Field(None, ge=0, description="Capacidad mínima requerida")
    capacidad_max: Optional[int] = Field(None, ge=0, description="Capacidad máxima permitida")
    ubicacion: Optional[str] = Field(None, description="Filtrar por ubicación (coincidencia parcial)")
    equipamiento: Optional[str] = Field(None, description="Filtrar por equipamiento (coincidencia parcial)")

class AulaStatistics(BaseModel):
    total_aulas: int
    capacidad_promedio: float
    capacidad_minima: int
    capacidad_maxima: int
    distribucion_por_tipo: Dict[TipoAulaEnum, int]