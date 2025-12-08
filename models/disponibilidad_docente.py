from sqlalchemy import Column, Integer, Boolean, ForeignKey, Time
from core.database import Base

class DisponibilidadDocente(Base):
    __tablename__ = "disponibilidaddocente"

    id_disponibilidad = Column(Integer, primary_key=True, index=True)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"), nullable=False)
    id_semestre = Column(Integer, ForeignKey("semestre.id_semestre"), nullable=False)
    id_dia = Column(Integer, ForeignKey("dias.id_dia"), nullable=False)

    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

    disponible = Column(Boolean, default=True)
