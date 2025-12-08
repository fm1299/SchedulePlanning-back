from sqlalchemy.orm import Session
from models.administrador import Administrador, UsuarioAdministrador
from repositories.base import BaseRepository


class AdministradorRepository(BaseRepository[Administrador]):
    def __init__(self, db: Session):
        super().__init__(Administrador, db)

    def create_administrador(self, obj_in: dict) -> Administrador:
        return self.create(obj_in)

    def link_usuario_administrador(self, id_usuario: int, id_administrador: int):
        ua = UsuarioAdministrador(id_usuario=id_usuario, id_administrador=id_administrador)
        self.db.add(ua)
        self.db.commit()
        return ua
