from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, TIMESTAMP, Time, Date, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class TipoDocente(Base):
    __tablename__ = "tipodocente"
    
    id_tipo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    
    # Relaciones
    docentes = relationship("Docente", back_populates="tipo_docente")

class Facultad(Base):
    __tablename__ = "facultad"
    
    id_facultad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    codigo = Column(String(50), unique=True, nullable=False)
    createdat = Column(TIMESTAMP, server_default=func.now())


class Docente(Base):
    __tablename__ = "docente"
    
    id_docente = Column(Integer, primary_key=True, index=True)
    #id_departamento = Column(Integer, ForeignKey("departamento.id_departamento"), nullable=False)
    id_tipo = Column(Integer, ForeignKey("tipodocente.id_tipo"), nullable=False)
    nombre = Column(String(255), nullable=False)
    apellidos = Column(String(255), nullable=False)
    telefono = Column(String(50), nullable=True)
    especialidad = Column(String(255), nullable=True)
    grado_academico = Column(String(100), nullable=True)
    max_horas_sem = Column(Integer, default=40)
    #regimen = Column(String(50), default="parcial")
    #fecha_inicio = Column(Date, nullable=True)

    
    # Relaciones
    tipo_docente = relationship("TipoDocente", back_populates="docentes")
    #departamento = relationship("Departamento", back_populates="docentes")
    usuario_docente = relationship("UsuarioDocente", back_populates="docente", uselist=False)

class UsuarioDocente(Base):
    __tablename__ = "usuariodocente"
    
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), primary_key=True)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"), unique=True, nullable=False)
    
    # Relaciones
    usuario = relationship("Usuario")
    docente = relationship("Docente", back_populates="usuario_docente")

class Semestre(Base):
    __tablename__ = "semestre"
    
    id_semestre = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, nullable=False)
    año = Column(Integer, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    activo = Column(Boolean, default=False)

class AsignacionDocente(Base):
    __tablename__ = "asignaciondocente"
    
    id_asignacion = Column(Integer, primary_key=True, index=True)
    id_grupo = Column(Integer, ForeignKey("grupo.id_grupo"), nullable=False)
    id_docente = Column(Integer, ForeignKey("docente.id_docente"), nullable=False)
    tipo_asignacion = Column(String(50), nullable=False)
    horas_asignadas = Column(Integer, nullable=False)
    
    # Relaciones
    grupo = relationship("Grupo")
    docente = relationship("Docente")

class Grupo(Base):
    __tablename__ = "grupo"
    
    id_grupo = Column(Integer, primary_key=True, index=True)
    id_curso = Column(Integer, ForeignKey("curso.id_curso"), nullable=False)
    id_semestre = Column(Integer, ForeignKey("semestre.id_semestre"), nullable=False)
    letra = Column(String(10), nullable=False)
    capacidad_max = Column(Integer, nullable=False)
    estudiantes_ins = Column(Integer, default=0)
    estado = Column(String(50), default="activo")
    
    # Relaciones
    semestre = relationship("Semestre")