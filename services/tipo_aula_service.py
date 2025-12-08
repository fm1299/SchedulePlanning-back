from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.tipo_aula_repository import tipo_aula_repository
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate

class TipoAulaService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_tipos_aula(self, skip: int = 0, limit: int = 100):
        return tipo_aula_repository.get_multi(self.db, skip=skip, limit=limit)
    
    def get_tipo_aula(self, tipo_id: int):
        tipo = tipo_aula_repository.get(self.db, id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        return tipo
    
    def create_tipo_aula(self, tipo_in: TipoAulaCreate):
        existing = tipo_aula_repository.get_by_nombre(self.db, nombre=tipo_in.nombre)
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de aula con ese nombre")
        
        return tipo_aula_repository.create(self.db, obj_in=tipo_in)
    
    def update_tipo_aula(self, tipo_id: int, tipo_in: TipoAulaUpdate):
        tipo = tipo_aula_repository.get(self.db, id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        
        if tipo_in.nombre and tipo_in.nombre != tipo.nombre:
            existente = tipo_aula_repository.get_by_nombre(self.db, nombre=tipo_in.nombre)
            if existente:
                raise HTTPException(status_code=400, detail="Nombre de tipo de aula ya existe")
        
        return tipo_aula_repository.update(self.db, db_obj=tipo, obj_in=tipo_in)
    
    def delete_tipo_aula(self, tipo_id: int):
        tipo = tipo_aula_repository.get(self.db, id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        
        if tipo.aulas:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar el tipo de aula porque tiene aulas asociadas"
            )
        
        return tipo_aula_repository.remove(self.db, id=tipo_id)