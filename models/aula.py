from sqlalchemy import Column, Integer, String, ForeignKey  # <--- ASEGÚRATE DE IMPORTAR ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Aula(Base):
    __tablename__ = "aula"

    id_aula = Column(Integer, primary_key=True, index=True)

    # --- AQUÍ ESTÁ EL ERROR ACTUAL ---
    # Tienes que decir explícitamente a qué tabla y columna apuntan
    id_edificio = Column(Integer, ForeignKey("edificio.id_edificio"), nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipoaula.id_tipo"), nullable=False) 
    # Nota: Asegúrate que "tipoaula" es el nombre exacto de la tabla en models/tipo_aula.py (__tablename__)

    codigo = Column(String, nullable=False, unique=True)
    capacidad = Column(Integer, nullable=False)
    piso = Column(Integer, nullable=False)

    equipamiento = Column(String)
    estado = Column(String, default="disponible")

    # Relaciones (ahora sí funcionarán porque existen las ForeignKey arriba)
    #edificio = relationship("Edificio", back_populates="aulas")
    #tipo = relationship("TipoAula", back_populates="aulas")
    
    # Resto de relaciones...
    reservas = relationship("Reserva", back_populates="aula")
    horarios = relationship("HorarioAsignado", back_populates="aula")
    mantenimientos = relationship("MantenimientoAula", back_populates="aula")