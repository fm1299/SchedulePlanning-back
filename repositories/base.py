from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from core.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
