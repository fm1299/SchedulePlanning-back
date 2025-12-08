from sqlalchemy.orm import Session
from models.tipo_aula import TipoAula
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate
from repositories.base import CRUDBase

class CRUDTipoAula(CRUDBase[TipoAula, TipoAulaCreate, TipoAulaUpdate]):
    def get_by_nombre(self, db: Session, nombre: str):
        return db.query(self.model).filter(self.model.nombre == nombre).first()

tipo_aula_repository = CRUDTipoAula(TipoAula)