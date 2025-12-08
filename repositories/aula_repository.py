from sqlalchemy.orm import Session, joinedload
from models.aula import Aula
from schemas.aula import AulaCreate, AulaUpdate  # Esta importación está bien
from repositories.base import CRUDBase

class CRUDAula(CRUDBase[Aula, AulaCreate, AulaUpdate]):
    def get_with_details(self, db: Session, id_aula: int):
        return db.query(self.model).options(
            joinedload(self.model.edificio),
            joinedload(self.model.tipo_aula)
        ).filter(self.model.id_aula == id_aula).first()
    
    def get_by_codigo(self, db: Session, codigo: str):
        return db.query(self.model).filter(self.model.codigo == codigo).first()
    
    def get_by_edificio(self, db: Session, id_edificio: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.id_edificio == id_edificio
        ).offset(skip).limit(limit).all()
    
    def get_disponibles(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.estado == 'disponible'
        ).offset(skip).limit(limit).all()
    
    def get_by_tipo(self, db: Session, id_tipo: int, skip: int = 0, limit: int = 100):
        return db.query(self.model).filter(
            self.model.id_tipo == id_tipo
        ).offset(skip).limit(limit).all()

aula_repository = CRUDAula(Aula)