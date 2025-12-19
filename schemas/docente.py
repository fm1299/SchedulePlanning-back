from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import time, datetime, date
from enum import Enum

# Enums para validación
class TipoDocenteEnum(str, Enum):
    contratado = "contratado"
    nombrado = "nombrado"
    invitado = "invitado"

class RolUsuarioEnum(str, Enum):
    administrador = "administrador"
    docente = "docente"

# Schemas base
class ModelBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True
    )

# Schemas para TipoDocente
class TipoDocenteBase(ModelBase):
    nombre: TipoDocenteEnum

class TipoDocenteCreate(TipoDocenteBase):
    pass

class TipoDocenteUpdate(TipoDocenteBase):
    pass

class TipoDocente(TipoDocenteBase):
    id_tipo: int
    docentes_count: Optional[int] = 0

# Schemas para Departamento
class DepartamentoBase(ModelBase):
    nombre: str
    codigo: str
    id_facultad: int

class Departamento(DepartamentoBase):
    id_departamento: int
    facultad_nombre: Optional[str] = None

# Schemas para Docente
class DocenteBase(ModelBase):
    nombre: str
    apellidos: str
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    grado_academico: Optional[str] = None
    max_horas_sem: int = 40
    #regimen: Optional[str] = None
    #fecha_inicio: Optional[date] = None


    @field_validator('nombre', 'apellidos')
    @classmethod
    def validate_nombres(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise ValueError('El teléfono debe contener solo números y caracteres válidos')
        return v

    @field_validator('max_horas_sem')
    @classmethod
    def validate_horas(cls, v: int) -> int:
        if v < 0 or v > 60:
            raise ValueError('Las horas semanales deben estar entre 0 y 60')
        return v

class DocenteCreate(DocenteBase):
    #id_departamento: int
    id_tipo: int

class DocenteUpdate(ModelBase):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    especialidad: Optional[str] = None
    grado_academico: Optional[str] = None
    max_horas_sem: Optional[int] = None
    #id_departamento: Optional[int] = None
    id_tipo: Optional[int] = None
    #regimen: Optional[str] = None
    #fecha_inicio: Optional[date] = None


class Docente(DocenteBase):
    id_docente: int
    #id_departamento: int
    id_tipo: int
    #departamento: Optional[Departamento] = None
    tipo_docente: Optional[TipoDocente] = None

# Schemas para Usuario y relaciones
class UsuarioBase(ModelBase):
    username: str
    email: Optional[str] = None
    activo: bool = True
    rol: RolUsuarioEnum = RolUsuarioEnum.docente

class UsuarioDocenteBase(ModelBase):
    usuario: UsuarioBase
    docente: Docente

class DocenteCompleto(Docente):
    tiene_usuario: bool = False
    usuario_info: Optional[UsuarioBase] = None

# Response Schemas
class DocenteResponse(ModelBase):
    id_docente: int
    nombre: str
    apellidos: str
    telefono: Optional[str]
    especialidad: Optional[str]
    grado_academico: Optional[str]
    max_horas_sem: int
    #departamento: Departamento
    tipo_docente: TipoDocente
    tiene_usuario: bool
    usuario_info: Optional[UsuarioBase] = None
    #regimen: Optional[str] = None
    #fecha_inicio: Optional[date] = None
    puntaje: Optional[int] = None   # ← se llenará luego


class TipoDocenteResponse(TipoDocente):
    docentes_count: int

# Pagination
class PaginatedResponse(ModelBase):
    items: List
    total: int
    page: int
    size: int
    pages: int

class DocenteListResponse(ModelBase):
    items: List[DocenteResponse]
    total: int
    page: int
    size: int
    pages: int
    
    
    
    
# Schemas para AsignacionDocente
class AsignacionDocenteBase(ModelBase):
    id_grupo: int
    tipo_asignacion: str
    horas_asignadas: int

class AsignacionDocenteCreate(AsignacionDocenteBase):
    pass

class AsignacionDocenteUpdate(ModelBase):
    id_grupo: Optional[int] = None
    tipo_asignacion: Optional[str] = None
    horas_asignadas: Optional[int] = None

class AsignacionDocente(AsignacionDocenteBase):
    id_asignacion: int
    id_docente: int
    grupo_info: Optional[dict] = None
    docente_info: Optional[dict] = None