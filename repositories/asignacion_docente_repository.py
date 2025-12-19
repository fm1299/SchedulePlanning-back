# repositories/asignacion_docente_repository.py
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.docente import AsignacionDocente, Docente, Grupo
from schemas.docente import AsignacionDocenteCreate, AsignacionDocenteUpdate
from repositories.historial_repository import HistorialCambiosRepository

class AsignacionDocenteRepository:
    """
    Equivalente a tu antiguo CRUDAsignacionDocente.
    Encapsula validaciones de horas y creación/actualización de asignaciones.
    """

    def __init__(self, db: Session):
        self.db = db
        self.model = AsignacionDocente
        self.hist_repo = HistorialCambiosRepository(db)

    def get(self, asignacion_id: int) -> Optional[AsignacionDocente]:
        return (
            self.db.query(self.model)
            .filter(self.model.id_asignacion == asignacion_id)
            .first()
        )

    # --- validaciones auxiliares ---

    def _get_horas_asignadas_semestre(
        self,
        docente_id: int,
        semestre_id: int,
    ) -> int:
        total_horas = (
            self.db.query(func.sum(AsignacionDocente.horas_asignadas))
            .join(Grupo, AsignacionDocente.id_grupo == Grupo.id_grupo)
            .filter(
                AsignacionDocente.id_docente == docente_id,
                Grupo.id_semestre == semestre_id,
            )
            .scalar()
        )
        return total_horas or 0

    # --- create/update con validación de horas ---

    def create_with_validacion(
        self,
        obj_in: Dict[str, Any],
        docente_id: int,
        semestre_id: int,
    ) -> AsignacionDocente:
        docente = (
            self.db.query(Docente)
            .filter(Docente.id_docente == docente_id)
            .first()
        )
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente no encontrado",
            )

        horas_actuales = self._get_horas_asignadas_semestre(
            docente_id,
            semestre_id,
        )
        horas_nuevas = obj_in.get("horas_asignadas", 0)
        total_horas = horas_actuales + horas_nuevas

        if total_horas > docente.max_horas_sem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El docente excede su límite de horas. "
                    f"Horas actuales: {horas_actuales}, "
                    f"Horas nuevas: {horas_nuevas}, "
                    f"Límite: {docente.max_horas_sem}"
                ),
            )

        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.flush()  # obtener id_asignacion

        data_nuevos = obj_in.model_dump()
        if data_nuevos.get("fecha_inicio"):
            data_nuevos["fecha_inicio"] = data_nuevos["fecha_inicio"].isoformat()

        
        self.hist_repo.registrar_cambio(
            tabla_afectada="docente",
            id_registro=db_obj.id_docente,
            accion="INSERT",
            datos_anteriores=None,
            datos_nuevos=data_nuevos,
            usuario=None,
        )

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj


    def update_with_validacion(
        self,
        asignacion_id: int,
        obj_in: Dict[str, Any],
        docente_id: int,
        semestre_id: int,
    ) -> AsignacionDocente:
        asignacion = self.get(asignacion_id)
        if not asignacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asignación no encontrada",
            )

        docente = (
            self.db.query(Docente)
            .filter(Docente.id_docente == docente_id)
            .first()
        )
        if not docente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente no encontrado",
            )

        # datos anteriores
        datos_anteriores = {
            "id_asignacion": asignacion.id_asignacion,
            "id_grupo": asignacion.id_grupo,
            "id_docente": asignacion.id_docente,
            "tipo_asignacion": asignacion.tipo_asignacion,
            "horas_asignadas": asignacion.horas_asignadas,
        }

        horas_actuales_total = self._get_horas_asignadas_semestre(
            docente_id,
            semestre_id,
        )
        horas_actuales_sin_esta = horas_actuales_total - asignacion.horas_asignadas
        horas_nuevas = obj_in.get("horas_asignadas", asignacion.horas_asignadas)
        total_horas = horas_actuales_sin_esta + horas_nuevas

        if total_horas > docente.max_horas_sem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "El docente excede su límite de horas. "
                    f"Horas actuales (sin esta): {horas_actuales_sin_esta}, "
                    f"Horas nuevas: {horas_nuevas}, "
                    f"Límite: {docente.max_horas_sem}"
                ),
            )

        for field, value in obj_in.items():
            setattr(asignacion, field, value)

        self.db.add(asignacion)
        self.db.flush()

        datos_nuevos = {
            "id_asignacion": asignacion.id_asignacion,
            "id_grupo": asignacion.id_grupo,
            "id_docente": asignacion.id_docente,
            "tipo_asignacion": asignacion.tipo_asignacion,
            "horas_asignadas": asignacion.horas_asignadas,
        }

        self.hist_repo.registrar_cambio(
            tabla_afectada="asignaciondocente",
            id_registro=asignacion.id_asignacion,
            accion="UPDATE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            usuario=None,
        )

        self.db.commit()
        self.db.refresh(asignacion)
        return asignacion

