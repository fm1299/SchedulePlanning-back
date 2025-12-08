from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UsuarioCreate(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr] = None
    rol: Optional[str] = "docente"


class UsuarioAdminCreate(UsuarioCreate):
    id_departamento: int
    nombre: str
    apellidos: str
    telefono: Optional[str] = None
    estado: Optional[str] = "activo"


class UsuarioResponse(BaseModel):
    id_usuario: int
    username: str
    email: Optional[EmailStr] = None
    activo: bool
    rol: str
    fecha_creacion: Optional[datetime]

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
