# models/historial.py
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from core.database import Base


class HistorialCambios(Base):
    __tablename__ = "historialcambios"

    id_historial = Column(Integer, primary_key=True, index=True)
    tabla_afectada = Column(String(100), nullable=False)
    id_registro = Column(Integer, nullable=False)
    accion = Column(String(50), nullable=False)  # 'INSERT', 'UPDATE', 'DELETE'
    datos_anteriores = Column(Text, nullable=True)  # JSON como texto
    datos_nuevos = Column(Text, nullable=True)      # JSON como texto
    usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    fecha_cambio = Column(TIMESTAMP, server_default=func.now())

    usuario_rel = relationship("Usuario", backref="historial_cambios")
