from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class TipoAula(Base):
    __tablename__ = "tipoaula"
    
    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(200))
    
    aulas = relationship("Aula", back_populates="tipo_aula")
    
    def __repr__(self):
        return f"<TipoAula(id={self.id_tipo}, nombre={self.nombre})>"