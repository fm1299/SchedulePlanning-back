from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from core.database import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    activo = Column(Boolean, default=True)
    rol = Column(String(50), nullable=False, default="docente")
    fecha_creacion = Column(TIMESTAMP, server_default=func.current_timestamp())
    password_updated_at = Column(TIMESTAMP, nullable=True)
    last_login = Column(TIMESTAMP, nullable=True)
    failed_attempts = Column(Integer, default=0)
