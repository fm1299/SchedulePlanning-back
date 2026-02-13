from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Aula(Base):
    __tablename__ = "aula"
    
    id_aula = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipoaula.id_tipo"), nullable=False)
    capacidad = Column(Integer, nullable=False)
    ubicacion = Column(String(100))
    descripcion = Column(Text)
    equipamiento = Column(Text)
    estado = Column(String(20), default="disponible", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    tipo_aula = relationship("TipoAula", back_populates="aulas")
    
    reservas = relationship("Reserva", back_populates="aula")
    horarios = relationship("HorarioAsignado", back_populates="aula")
    mantenimientos = relationship("MantenimientoAula", back_populates="aula")

    def __repr__(self):
        return f"<Aula(id={self.id_aula}, codigo={self.codigo}, nombre={self.nombre})>"