from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Aula(Base):
    __tablename__ = "aula"

    id_aula = Column(Integer, primary_key=True, index=True)
    id_edificio = Column(Integer, nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipoaula.id_tipo"), nullable=False)

    codigo = Column(String, nullable=False, unique=True)
    capacidad = Column(Integer, nullable=False)
    piso = Column(Integer, nullable=False)

    equipamiento = Column(String)
    estado = Column(String)
    
    # Relationship to TipoAula
    tipo_aula = relationship("TipoAula", back_populates="aulas")

