from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.database import Base

class Edificio(Base):
    __tablename__ = "edificio"

    id_edificio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, unique=True, nullable=False)
    ubicacion = Column(String)
    pisos = Column(Integer, default=1)

    # Relación inversa (importante para que 'back_populates' funcione)
    aulas = relationship("Aula", back_populates="edificio")