from fastapi import HTTPException
from sqlalchemy import select
from models.reserva import Reserva
from models.aula import Aula
from schemas.reserva import ReservaCreate
from schemas.reserva import ReservaUpdate
from repositories.reserva_repository import ReservaRepository
from models.historial import HistorialCambios
import json


class ReservaService:
    def __init__(self, db):
        self.db = db
        self.repo = ReservaRepository(db)

    def crear(self, data: ReservaCreate):
        r = Reserva(**data.dict())

        # 1) Conflicto con otras reservas del aula
        if self.repo.conflicto_reserva(r):
            raise HTTPException(400, "❌ Aula ya reservada en ese horario")

        # 2) Conflicto con horario oficial del aula
        bloque = self.repo.conflicto_horario_oficial(r)
        if bloque:
            raise HTTPException(
                400,
                f"❌ Aula ocupada por clase oficial. "
                f"Bloque {bloque.nombre} ({bloque.hora_inicio}-{bloque.hora_fin})"
            )

        # 3) Conflicto con mantenimiento
        m = self.repo.conflicto_mantenimiento(r)
        if m:
            raise HTTPException(400, f"❌ Aula en mantenimiento: {m.motivo}")

        # 4) Validar estado del aula (debe ser disponible)
        aula = self.db.execute(
            select(Aula).where(Aula.id_aula == r.id_aula)
        ).scalar_one()

        if aula.estado != "disponible":
            raise HTTPException(
                400,
                f"❌ El aula no está disponible (estado: {aula.estado})."
            )

        # 5) Conflicto de reservas del docente
        if self.repo.conflicto_reserva_docente(r):
            raise HTTPException(
                400,
                "❌ El docente ya tiene otra reserva en ese horario"
            )

        # 6) Conflicto con horario oficial del docente
        if self.repo.conflicto_docente_horario_oficial(r):
            raise HTTPException(
                400,
                "❌ El docente dicta clase oficial en ese horario"
            )

        # 7) Validar disponibilidad del docente
        if self.repo.docente_no_disponible(r):
            raise HTTPException(
                400,
                "❌ El docente NO está disponible en ese horario"
            )

        # 8) Crear reserva
        reserva_creada = self.repo.add(r)

        # -----------------------
        # Registrar historial
        # -----------------------
        datos_nuevos = json.dumps({
            "id_reserva": reserva_creada.id_reserva,
            "id_aula": reserva_creada.id_aula,
            "id_docente": reserva_creada.id_docente,
            "fecha": str(reserva_creada.fecha),
            "hora_inicio": str(reserva_creada.hora_inicio),
            "hora_fin": str(reserva_creada.hora_fin),
            "descripcion": reserva_creada.descripcion
        })

        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=reserva_creada.id_reserva,
            accion="INSERT",
            datos_anteriores=None,
            datos_nuevos=datos_nuevos,
            usuario=1  
        )

        self.db.add(historial)
        self.db.commit()

        return reserva_creada
    


    def listar(self):
        return self.repo.get_all()

    def obtener(self, id_reserva: int):
        r = self.repo.get(id_reserva)
        if not r:
            raise HTTPException(404, "Reserva no encontrada")
        return r

    def eliminar(self, id_reserva: int):
        r = self.obtener(id_reserva)

        # Guardar datos ANTES de eliminar
        datos_anteriores = json.dumps({
            "id_reserva": r.id_reserva,
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion
        })

        # Registrar historial
        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=id_reserva,
            accion="DELETE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=None,
            usuario=1  # si aún no tienes autenticación
        )
        self.db.add(historial)

        # Eliminar reserva
        self.repo.delete(r)

        return {"message": "Reserva eliminada"}

    
    def actualizar(self, id_reserva: int, data: ReservaUpdate):
        r = self.repo.get(id_reserva)
        if not r:
            raise HTTPException(404, "Reserva no encontrada")

        # Guardar datos anteriores para historial
        datos_antes = {
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion
        }

        # Aplicar cambios
        for field, value in data.dict(exclude_unset=True).items():
            setattr(r, field, value)

        # VALIDACIONES (ignorando la misma reserva)
        if self.repo.conflicto_reserva_update(r):
            raise HTTPException(400, "❌ Conflicto con otra reserva existente")

        bloque = self.repo.conflicto_horario_oficial(r)
        if bloque:
            raise HTTPException(400, f"❌ Aula ocupada por clase oficial: {bloque.nombre}")

        if self.repo.conflicto_mantenimiento(r):
            raise HTTPException(400, "❌ Aula en mantenimiento en ese horario")

        if self.repo.conflicto_docente_horario_oficial(r):
            raise HTTPException(400, "❌ Docente dicta una clase en ese horario")

        if self.repo.conflicto_reserva_docente_update(r):
            raise HTTPException(400, "❌ Docente tiene otra reserva en ese horario")

        if self.repo.docente_no_disponible(r):
            raise HTTPException(400, "❌ Docente no está disponible en ese horario")

        # Guardar cambios
        self.repo.update(r)

        # Registrar historial
        from repositories.historial_repository import HistorialRepository
        HistorialRepository(self.db).agregar(
            tabla="reservas",
            id_registro=r.id_reserva,
            accion="UPDATE",
            antes=datos_antes,
            despues={
                "id_aula": r.id_aula,
                "id_docente": r.id_docente,
                "fecha": str(r.fecha),
                "hora_inicio": str(r.hora_inicio),
                "hora_fin": str(r.hora_fin),
                "descripcion": r.descripcion
            }
        )

        return r

