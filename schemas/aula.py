from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List, Dict, Any

# Elimina esta línea si existe:
# from repositories.aula_repository import aula_repository

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
    
    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            allowed = ['disponible', 'mantenimiento', 'inhabilitada']
            if v not in allowed:
                raise ValueError(f'Estado debe ser uno de: {allowed}')
        return v

class AulaInDB(AulaBase):
    id_aula: int
    
    # Información relacionada
    edificio_nombre: Optional[str] = None
    tipo_aula_nombre: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class AulaResponse(AulaInDB):
    pass

class AulaSearch(BaseModel):
    codigo: Optional[str] = None
    id_tipo: Optional[int] = None
    id_edificio: Optional[int] = None
    capacidad_min: Optional[int] = None
    capacidad_max: Optional[int] = None
    piso: Optional[int] = None
    estado: Optional[str] = None

class AulaStatistics(BaseModel):
    total_aulas: int
    capacidad_promedio: float
    capacidad_minima: int
    capacidad_maxima: int
    aulas_disponibles: int
    aulas_mantenimiento: int
    aulas_inhabilitadas: int
    distribucion_por_tipo: List[Dict[str, Any]]