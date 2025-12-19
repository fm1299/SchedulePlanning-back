import json
from datetime import date, datetime
from typing import Optional, Dict, Any

from sqlalchemy.orm import Session
from models.historial import HistorialCambios


class HistorialCambiosRepository:
    def __init__(self, db: Session):
        self.db = db

    def _normalize(self, data: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if data is None:
            return None
        out: Dict[str, Any] = {}
        for k, v in data.items():
            if isinstance(v, (date, datetime)):
                out[k] = v.isoformat()
            else:
                out[k] = v
        return out

    def registrar_cambio(
        self,
        tabla_afectada: str,
        id_registro: int,
        accion: str,  # 'INSERT', 'UPDATE', 'DELETE'
        datos_anteriores: Optional[Dict[str, Any]] = None,
        datos_nuevos: Optional[Dict[str, Any]] = None,
        usuario: Optional[int] = None,
    ) -> HistorialCambios:
        datos_anteriores = self._normalize(datos_anteriores)
        datos_nuevos = self._normalize(datos_nuevos)

        historial = HistorialCambios(
            tabla_afectada=tabla_afectada,
            id_registro=id_registro,
            accion=accion,
            datos_anteriores=json.dumps(datos_anteriores) if datos_anteriores is not None else None,
            datos_nuevos=json.dumps(datos_nuevos) if datos_nuevos is not None else None,
            usuario=usuario,
        )
        self.db.add(historial)
        return historial
