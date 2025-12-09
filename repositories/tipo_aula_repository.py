from sqlalchemy.orm import Session
from models.tipo_aula import TipoAula
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate
from repositories.base import BaseRepository

class CRUDTipoAula(BaseRepository[TipoAula]):
    def get_by_nombre(self, nombre: str):
        return self.db.query(self.model).filter(self.model.nombre == nombre).first()

# Note: Repository instance is created without db session
# The db session is now passed in __init__ when service layer creates the repo
tipo_aula_repository = CRUDTipoAula