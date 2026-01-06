from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship  # <--- Faltaba importar esto
from core.database import Base

class HorarioAsignado(Base):
    __tablename__ = "horarioasignado"

    id_horario = Column(Integer, primary_key=True, index=True)
    
    # Columnas con Foreign Keys (Asegúrate que apunten a tabla.id)
    id_grupo = Column(Integer, ForeignKey("grupo.id_grupo"), nullable=False)
    id_aula = Column(Integer, ForeignKey("aula.id_aula"), nullable=False)
    id_dia = Column(Integer, ForeignKey("dias.id_dia"), nullable=False)
    id_bloque = Column(Integer, ForeignKey("bloquehorario.id_bloque"), nullable=False)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"), nullable=False)
    
    tipo_clase = Column(String, nullable=False)
    estado = Column(String, nullable=False)

    # --- RELACIONES (Esto es lo que te faltaba) ---
    
    # Esta es la que causaba el error. 
    # En Aula pusiste back_populates="aula", así que aquí debe llamarse "aula"
    aula = relationship("Aula", back_populates="horarios")

    # Sería buena idea agregar las otras también para completar el sistema:
    #docente = relationship("Docente")
    #bloque = relationship("BloqueHorario")
    dia = relationship("Dias")
    # grupo = relationship("Grupo")