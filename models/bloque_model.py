from sqlalchemy import Column, Integer, String, Time
from core.database import Base

class BloqueHorario(Base):
    __tablename__ = "bloquehorario"   # confirmar si tu tabla usa este nombre

    id_bloque = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    duracion = Column(Integer, nullable=False)