from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship  # <--- IMPORTANTE: Faltaba importar esto
from core.database import Base

class MantenimientoAula(Base):
    __tablename__ = "mantenimientoaula"

    id_mantenimiento = Column(Integer, primary_key=True, index=True)
    
    # Asegúrate que tenga el ForeignKey
    id_aula = Column(Integer, ForeignKey("aula.id_aula"), nullable=False)

    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)

    motivo = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    # --- AGREGAR ESTA LÍNEA ---
    # Esto conecta de vuelta con la clase Aula
    aula = relationship("Aula", back_populates="mantenimientos")