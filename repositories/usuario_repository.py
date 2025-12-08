from typing import Optional
from sqlalchemy.orm import Session

from models.usuario import Usuario
from repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, db: Session):
        super().__init__(Usuario, db)

    def get_by_username(self, username: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def get_by_email(self, email: str) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.email == email).first()

    def count_admins(self) -> int:
        return self.db.query(Usuario).filter(Usuario.rol == 'administrador').count()
