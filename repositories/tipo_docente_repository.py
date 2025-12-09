# repositories/tipo_docente_repository.py
from typing import List, Optional, Tuple

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.docente import TipoDocente, Docente
from schemas.docente import TipoDocenteCreate, TipoDocenteUpdate
from repositories.historial_repository import HistorialCambiosRepository

class TipoDocenteRepository:
    """
    Equivalente a tu antiguo CRUDTipoDocente, pero adaptado a la nueva arquitectura.
    """

    def __init__(self, db: Session):
        self.db = db
        self.model = TipoDocente
        self.hist_repo = HistorialCambiosRepository(db)

    # --- básicos ---

    def get(self, tipo_id: int) -> Optional[TipoDocente]:
        return (
            self.db.query(self.model)
            .filter(self.model.id_tipo == tipo_id)
            .first()
        )

    def delete(self, tipo_id: int) -> bool:
        obj = self.get(tipo_id)
        if not obj:
            return False

        datos_anteriores = {
            "id_tipo": obj.id_tipo,
            "nombre": obj.nombre,
        }

        self.db.delete(obj)
        self.db.flush()

        self.hist_repo.registrar_cambio(
            tabla_afectada="tipodocente",
            id_registro=tipo_id,
            accion="DELETE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=None,
            usuario=None,
        )

        self.db.commit()
        return True


    # --- específicos ---

    def get_by_nombre(self, nombre: str) -> Optional[TipoDocente]:
        return (
            self.db.query(self.model)
            .filter(self.model.nombre == nombre)
            .first()
        )

    def get_with_docentes_count(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Tuple[TipoDocente, int]]:
        """
        Devuelve lista de (TipoDocente, docentes_count)
        """
        resultados = (
            self.db.query(
                self.model,
                func.count(Docente.id_docente).label("docentes_count"),
            )
            .outerjoin(Docente, self.model.id_tipo == Docente.id_tipo)
            .group_by(self.model.id_tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return resultados

    def create(self, obj_in: TipoDocenteCreate) -> TipoDocente:
        existente = self.get_by_nombre(obj_in.nombre)
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un tipo de docente con el nombre: {obj_in.nombre}",
            )

        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.flush()  # obtener id_tipo

        self.hist_repo.registrar_cambio(
            tabla_afectada="tipodocente",
            id_registro=db_obj.id_tipo,
            accion="INSERT",
            datos_anteriores=None,
            datos_nuevos=obj_in.model_dump(),
            usuario=None,
        )

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        tipo_obj: TipoDocente,
        obj_in: TipoDocenteUpdate,
    ) -> TipoDocente:
        # datos anteriores
        datos_anteriores = {
            "id_tipo": tipo_obj.id_tipo,
            "nombre": tipo_obj.nombre,
        }

        update_data = obj_in.model_dump(exclude_unset=True)

        if "nombre" in update_data:
            existente = self.get_by_nombre(update_data["nombre"])
            if existente and existente.id_tipo != tipo_obj.id_tipo:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un tipo de docente con el nombre: {update_data['nombre']}",
                )

        for field, value in update_data.items():
            setattr(tipo_obj, field, value)

        self.db.add(tipo_obj)
        self.db.flush()

        datos_nuevos = {
            "id_tipo": tipo_obj.id_tipo,
            "nombre": tipo_obj.nombre,
        }

        self.hist_repo.registrar_cambio(
            tabla_afectada="tipodocente",
            id_registro=tipo_obj.id_tipo,
            accion="UPDATE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            usuario=None,
        )

        self.db.commit()
        self.db.refresh(tipo_obj)
        return tipo_obj
