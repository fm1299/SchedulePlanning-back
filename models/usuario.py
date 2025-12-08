from sqlalchemy import Column, Integer, String, Boolean, DateTime
from core.database import Base

class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    email = Column(String)
    activo = Column(Boolean, default=True)
    rol = Column(String, default="docente")
    fecha_creacion = Column(DateTime)
    password_updated_at = Column(DateTime)
    last_login = Column(DateTime)
    failed_attempts = Column(Integer, default=0)
