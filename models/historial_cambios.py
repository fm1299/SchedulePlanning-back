from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from core.database import Base

class HistorialCambios(Base):
    __tablename__ = "historialcambios"   # 👈 MUY IMPORTANTE: SQLAlchemy lo convierte a minúsculas

    id_historial = Column(Integer, primary_key=True, index=True)
    tabla_afectada = Column(String(100), nullable=False)
    id_registro = Column(Integer, nullable=False)
    accion = Column(String(50), nullable=False)  # INSERT / UPDATE / DELETE
    datos_anteriores = Column(Text)
    datos_nuevos = Column(Text)
    usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="SET NULL"))
    fecha_cambio = Column(TIMESTAMP, server_default=func.now())
