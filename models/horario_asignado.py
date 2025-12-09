from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base

class HorarioAsignado(Base):
    __tablename__ = "horarioasignado"

    id_horario = Column(Integer, primary_key=True, index=True)
    id_grupo = Column(Integer, nullable=False)
    id_aula = Column(Integer, ForeignKey("aula.id_aula"))
    id_dia = Column(Integer, nullable=False)
    id_bloque = Column(Integer, ForeignKey("bloquehorario.id_bloque"))
    id_docente = Column(Integer, ForeignKey("usuario.id_usuario"))

    tipo_clase = Column(String, nullable=False)
    estado = Column(String, nullable=False)
