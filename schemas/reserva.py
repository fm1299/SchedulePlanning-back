from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class ReservaBase(BaseModel):
    id_aula: int
    id_docente: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    descripcion: Optional[str] = None

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    id_aula: Optional[int] = None
    id_docente: Optional[int] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    descripcion: Optional[str] = None

class ReservaResponse(ReservaBase):
    id_reserva: int

    class Config:
        from_attributes = True
