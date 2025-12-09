from sqlalchemy.orm import Session
from sqlalchemy import insert
from models.historial_cambios import HistorialCambios
import json

class HistorialRepository:
    def __init__(self, db: Session):
        self.db = db

    def agregar(self, tabla: str, id_registro: int, accion: str, antes: dict, despues: dict, usuario=None):
        entry = HistorialCambios(
            tabla_afectada=tabla,
            id_registro=id_registro,
            accion=accion,
            datos_anteriores=json.dumps(antes) if antes else None,
            datos_nuevos=json.dumps(despues) if despues else None,
            usuario=usuario
        )
        self.db.add(entry)
        self.db.commit()
