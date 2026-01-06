from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base

class TipoAula(Base):
    __tablename__ = "tipoaula"
    
    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    
    aulas = relationship("Aula", back_populates="tipo_aula")