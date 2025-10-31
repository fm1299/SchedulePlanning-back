from sqlalchemy import Column, Integer, String, Enum
from core.database import Base
import enum

class TipoAula(str, enum.Enum):
    TEORIA = "TEORIA"
    LABORATORIO = "LABORATORIO"
    SEMINARIO = "SEMINARIO"

class Aula(Base):
    __tablename__ = "aulas"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, index=True, nullable=False)
    capacidad = Column(Integer, nullable=False)
    tipo = Column(Enum(TipoAula), nullable=False)
    ubicacion = Column(String, nullable=False)
    equipamiento = Column(String, nullable=True)
