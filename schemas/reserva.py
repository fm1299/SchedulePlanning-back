from pydantic import BaseModel, model_validator
from datetime import date, time
from typing import Optional

class ReservaBase(BaseModel):
    id_aula: int
    id_docente: int
    fecha: date
    hora_inicio: time
    hora_fin: time
    descripcion: Optional[str] = None

    @model_validator(mode='after')
    def check_times(self):
        if self.hora_inicio >= self.hora_fin:
            raise ValueError('La hora de inicio debe ser menor a la hora de fin')
        return self

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    id_aula: Optional[int] = None
    id_docente: Optional[int] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    descripcion: Optional[str] = None

#Para que el Admin cambie el estado
class ReservaEstadoUpdate(BaseModel):
    estado: str  # "confirmada" o "rechazada"


class ReservaResponse(ReservaBase):
    id_reserva: int
    estado: str 

    class Config:
        from_attributes = True
