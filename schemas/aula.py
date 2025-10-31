from pydantic import BaseModel, Field
from typing import Optional
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
