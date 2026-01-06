from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from core.database import Base

class Reserva(Base):
    __tablename__ = "reservas"

    id_reserva = Column(Integer, primary_key=True, index=True)
    id_aula = Column(Integer, ForeignKey("aula.id_aula"), nullable=False)
    id_docente = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)

    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    descripcion = Column(Text)
    estado = Column(String, default="pendiente")

    # --- AGREGAR ESTO ---
    # Esto permite navegar desde la Reserva hacia el Aula y el Docente
    aula = relationship("Aula", back_populates="reservas")
    #usuario = relationship("Usuario") # Opcional: back_populates si agregas 'reservas' en Usuario