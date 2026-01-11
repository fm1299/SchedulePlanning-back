from sqlalchemy import Column, Integer, String, ForeignKey
from core.database import Base


class Administrador(Base):
    __tablename__ = "administrador"

    id_administrador = Column(Integer, primary_key=True, index=True)
    id_departamento = Column(Integer, nullable=False)
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=True)
    estado = Column(String(50), default="activo")


class UsuarioAdministrador(Base):
    __tablename__ = "usuario_administrador"

    id_usuario = Column(Integer, primary_key=True)
    id_administrador = Column(Integer, nullable=False, unique=True)
    # Note: foreign key constraints are omitted to avoid dependency ordering issues
    # If you have Departamento and Usuario models created before, you can add:
    # id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), primary_key=True)
    # id_administrador = Column(Integer, ForeignKey('administrador.id_administrador'), unique=True)