from sqlalchemy.orm import Session, joinedload
from models.aula import Aula
from schemas.aula import AulaCreate, AulaUpdate
from repositories.base import BaseRepository

class CRUDAula(BaseRepository[Aula]):
    def get_with_details(self, id_aula: int):
        return self.db.query(self.model).options(
            joinedload(self.model.edificio),
            joinedload(self.model.tipo_aula)
        ).filter(self.model.id_aula == id_aula).first()
    
    def get_by_codigo(self, codigo: str):
        return self.db.query(self.model).filter(self.model.codigo == codigo).first()
    
    def get_by_edificio(self, id_edificio: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).filter(
            self.model.id_edificio == id_edificio
        ).offset(skip).limit(limit).all()
    
    def get_disponibles(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).filter(
            self.model.estado == 'disponible'
        ).offset(skip).limit(limit).all()
    
    def get_by_tipo(self, id_tipo: int, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).filter(
            self.model.id_tipo == id_tipo
        ).offset(skip).limit(limit).all()

# Repository class (not instance) - will be instantiated by service with db session
aula_repository = CRUDAula