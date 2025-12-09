from typing import Optional
from sqlalchemy.orm import Session

from services.usuario_service import UsuarioService
from models.usuario import Usuario
from schemas.admin import AdminCreate


class AdminService:
    """Compatibility adapter that delegates to UsuarioService."""
    def __init__(self, db: Session):
        self.service = UsuarioService(db)

    def create_admin(self, admin_in: AdminCreate) -> Usuario:
        # Convert AdminCreate to UsuarioCreate-like dict
        payload = {
            "username": admin_in.username,
            "password": admin_in.password,
            "email": getattr(admin_in, "email", None),
            "rol": getattr(admin_in, "is_superuser", False) and "administrador" or "docente",
        }
        from schemas.usuario import UsuarioCreate
        usuario_in = UsuarioCreate(**payload)
        return self.service.create_usuario(usuario_in)

    def authenticate_admin(self, username: str, password: str) -> Optional[Usuario]:
        return self.service.authenticate_usuario(username, password)

    def create_token_for_admin(self, admin: Usuario) -> str:
        return self.service.create_token_for_usuario(admin)

    def get_by_username(self, username: str) -> Optional[Usuario]:
        return self.service.get_by_username(username)

    def count_admins(self) -> int:
        return self.service.count_admins()
