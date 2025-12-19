from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List, Dict, Any

from enum import Enum



class TipoAulaEnum(str, Enum):
    TEORIA = "TEORIA"
    LABORATORIO = "LABORATORIO"
    SEMINARIO = "SEMINARIO"

class AulaBase(BaseModel):
    id_edificio: int
    id_tipo: int
    codigo: str
    capacidad: int
    piso: int
    equipamiento: Optional[str] = None
    estado: str = Field(default='disponible')
    
    @validator('estado')
    def validate_estado(cls, v):
        allowed = ['disponible', 'mantenimiento', 'inhabilitada']
        if v not in allowed:
            raise ValueError(f'Estado debe ser uno de: {allowed}')
        return v

class AulaCreate(AulaBase):
    pass

class AulaUpdate(BaseModel):
    id_edificio: Optional[int] = None
    id_tipo: Optional[int] = None
    codigo: Optional[str] = None
    capacidad: Optional[int] = None
    piso: Optional[int] = None
    equipamiento: Optional[str] = None
    estado: Optional[str] = None
    
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
