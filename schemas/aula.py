from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class AulaBase(BaseModel):
    codigo: str = Field(..., description="Código único del aula (ej: 101, A-201)")
    nombre: str = Field(..., description="Nombre descriptivo del aula")
    id_tipo: int = Field(..., description="ID del tipo de aula (referencia a TipoAula)")
    capacidad: int = Field(..., ge=1, description="Capacidad en personas")
    ubicacion: Optional[str] = Field(None, description="Ubicación física")
    descripcion: Optional[str] = Field(None, description="Descripción detallada")
    equipamiento: Optional[str] = Field(None, description="Equipamiento disponible")
    estado: str = Field(default='disponible', description="Estado: disponible, ocupada, mantenimiento")
    
    @validator('estado')
    def validate_estado(cls, v):
        allowed = ['disponible', 'ocupada', 'mantenimiento']
        if v not in allowed:
            raise ValueError(f'Estado debe ser uno de: {allowed}')
        return v

class AulaCreate(AulaBase):
    pass

class AulaUpdate(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    id_tipo: Optional[int] = None
    capacidad: Optional[int] = None
    ubicacion: Optional[str] = None
    descripcion: Optional[str] = None
    equipamiento: Optional[str] = None
    estado: Optional[str] = None
    
    @validator('estado')
    def validate_estado(cls, v):
        if v is not None:
            allowed = ['disponible', 'ocupada', 'mantenimiento']
            if v not in allowed:
                raise ValueError(f'Estado debe ser uno de: {allowed}')
        return v

class AulaInDB(AulaBase):
    id_aula: int
    tipo_nombre: Optional[str] = Field(None, description="Nombre del tipo de aula")
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class AulaResponse(AulaInDB):
    pass

class AulaFrontend(BaseModel):
    id: str = Field(..., description="ID único del aula")
    numero: str = Field(..., description="Número/código del aula")
    nombre: str = Field(..., description="Nombre del aula")
    tipo: str = Field(..., description="Tipo: Aula, Laboratorio, Oficina")
    capacidad: int = Field(..., description="Capacidad en personas")
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    status: str = Field(default='available', description="Estado para frontend")
    
    @validator('status')
    def validate_status(cls, v):
        allowed = ['available', 'occupied', 'maintenance']
        if v not in allowed:
            raise ValueError(f'Status debe ser uno de: {allowed}')
        return v

class AulaSearch(BaseModel):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    id_tipo: Optional[int] = None
    capacidad_min: Optional[int] = None
    capacidad_max: Optional[int] = None
    estado: Optional[str] = None

class AulaStatistics(BaseModel):
    total_aulas: int
    capacidad_promedio: float
    capacidad_minima: int
    capacidad_maxima: int
    aulas_disponibles: int
    aulas_ocupadas: int
    aulas_mantenimiento: int
    distribucion_por_tipo: List[Dict[str, Any]]