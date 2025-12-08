from pydantic import BaseModel, ConfigDict
from typing import Optional

class TipoAulaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class TipoAulaCreate(TipoAulaBase):
    pass

class TipoAulaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class TipoAulaInDB(TipoAulaBase):
    id_tipo: int
    
    model_config = ConfigDict(from_attributes=True)

class TipoAula(TipoAulaInDB):
    pass