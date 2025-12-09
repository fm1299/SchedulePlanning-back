from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories.tipo_aula_repository import tipo_aula_repository
from schemas.tipo_aula import TipoAulaCreate, TipoAulaUpdate
from models.tipo_aula import TipoAula

class TipoAulaService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = tipo_aula_repository(TipoAula, db)
    
    def get_all_tipos_aula(self, skip: int = 0, limit: int = 100):
        return self.repository.get_all(skip=skip, limit=limit)
    
    def get_tipo_aula(self, tipo_id: int):
        tipo = self.repository.get(id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        return tipo
    
    def create_tipo_aula(self, tipo_in: TipoAulaCreate):
        existing = self.repository.get_by_nombre(nombre=tipo_in.nombre)
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un tipo de aula con ese nombre")
        
        # Convert Pydantic model to dict for BaseRepository.create()
        tipo_data = tipo_in.model_dump() if hasattr(tipo_in, 'model_dump') else tipo_in.dict()
        return self.repository.create(obj_in=tipo_data)
    
    def update_tipo_aula(self, tipo_id: int, tipo_in: TipoAulaUpdate):
        tipo = self.repository.get(id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        
        if tipo_in.nombre and tipo_in.nombre != tipo.nombre:
            existente = self.repository.get_by_nombre(nombre=tipo_in.nombre)
            if existente:
                raise HTTPException(status_code=400, detail="Nombre de tipo de aula ya existe")
        
        # Convert Pydantic model to dict for BaseRepository.update()
        tipo_data = tipo_in.model_dump(exclude_unset=True) if hasattr(tipo_in, 'model_dump') else tipo_in.dict(exclude_unset=True)
        return self.repository.update(id=tipo_id, obj_in=tipo_data)
    
    def delete_tipo_aula(self, tipo_id: int):
        tipo = self.repository.get(id=tipo_id)
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        
        # Check if tipo has associated aulas (assuming relationship exists)
        if hasattr(tipo, 'aulas') and tipo.aulas:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar el tipo de aula porque tiene aulas asociadas"
            )
        
        return self.repository.delete(id=tipo_id)