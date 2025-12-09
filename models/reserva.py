from sqlalchemy import Column, Integer, Date, Time, Text, ForeignKey
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
