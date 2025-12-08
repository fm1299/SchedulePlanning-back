from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session

from repositories.usuario_repository import UsuarioRepository
from repositories.administrador_repository import AdministradorRepository
from models.usuario import Usuario
from schemas.usuario import UsuarioCreate
from core.auth import get_password_hash, verify_password, create_access_token
from core.config import settings


class UsuarioService:
    def __init__(self, db: Session):
        self.repo = UsuarioRepository(db)

    def create_usuario(self, usuario_in: UsuarioCreate) -> Usuario:
        existing = self.repo.get_by_username(usuario_in.username)
        if existing:
            raise ValueError("Username already exists")
        hashed = get_password_hash(usuario_in.password)
        obj = {
            "username": usuario_in.username,
            "email": usuario_in.email,
            "password_hash": hashed,
            "rol": usuario_in.rol or "docente",
        }
        return self.repo.create(obj)

    def authenticate_usuario(self, username: str, password: str) -> Optional[Usuario]:
        usuario = self.repo.get_by_username(username)
        if not usuario:
            return None
        if not verify_password(password, usuario.password_hash):
            return None
        return usuario

    def create_token_for_usuario(self, usuario: Usuario) -> str:
        data = {"sub": usuario.username}
        expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return create_access_token(data=data, expires_delta=expire)

    def get_by_username(self, username: str) -> Optional[Usuario]:
        return self.repo.get_by_username(username)

    def count_admins(self) -> int:
        return self.repo.count_admins()

    def create_admin_with_profile(self, admin_in) -> Usuario:
        """Create a Usuario with role 'administrador', an Administrador profile, and link them."""
        # create usuario
        usuario_in = admin_in
        usuario_in.rol = 'administrador'
        usuario = self.create_usuario(usuario_in)

        # create administrador record
        admin_repo = AdministradorRepository(self.repo.db)
        admin_obj = {
            "id_departamento": admin_in.id_departamento,
            "nombre": admin_in.nombre,
            "apellidos": admin_in.apellidos,
            "telefono": admin_in.telefono,
            "estado": admin_in.estado or 'activo',
        }
        administrador = admin_repo.create_administrador(admin_obj)

        # link usuario <-> administrador
        admin_repo.link_usuario_administrador(usuario.id_usuario, administrador.id_administrador)

        return usuario
