from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.reserva import Reserva
from models.horario_asignado import HorarioAsignado
from models.bloque_model import BloqueHorario
from models.mantenimiento_aula import MantenimientoAula
from models.disponibilidad_docente import DisponibilidadDocente
from models.dias import Dias

dias_map = {
    0: 1,  # Lunes
    1: 2,  # Martes
    2: 3,  # Miércoles
    3: 4,  # Jueves
    4: 5,  # Viernes
    5: 6,  # Sábado
}

class ReservaRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------- CRUD ---------------- #

    def get(self, id_reserva: int):
        return self.db.get(Reserva, id_reserva)

    def get_all(self):
        return self.db.execute(select(Reserva)).scalars().all()

    def add(self, reserva: Reserva):
        self.db.add(reserva)
        self.db.commit()
        self.db.refresh(reserva)
        return reserva

    def delete(self, reserva: Reserva):
        self.db.delete(reserva)
        self.db.commit()

    def update(self, reserva: Reserva):
        self.db.commit()
        self.db.refresh(reserva)
        return reserva


    # ---------------- VALIDACIONES ---------------- #

    # 1) Conflicto con otras reservas (AULA)
    def conflicto_reserva(self, r: Reserva):
        stmt = (
            select(Reserva)
            .where(Reserva.id_aula == r.id_aula)
            .where(Reserva.fecha == r.fecha)
            .where(r.hora_inicio < Reserva.hora_fin)
            .where(r.hora_fin > Reserva.hora_inicio)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # 2) Conflicto con horario oficial del AULA (incluye día)
    def conflicto_horario_oficial(self, r: Reserva):
        dia_semana = dias_map[r.fecha.weekday()]  # convertir fecha → id_dia

        stmt = (
            select(HorarioAsignado, BloqueHorario)
            .join(BloqueHorario, HorarioAsignado.id_bloque == BloqueHorario.id_bloque)
            .where(HorarioAsignado.id_aula == r.id_aula)
            .where(HorarioAsignado.id_dia == dia_semana)
        )

        result = self.db.execute(stmt).all()

        for horario, bloque in result:
            if r.hora_inicio < bloque.hora_fin and r.hora_fin > bloque.hora_inicio:
                return bloque

        return None

    # 3) Conflicto con mantenimiento
    def conflicto_mantenimiento(self, r: Reserva):
        stmt = (
            select(MantenimientoAula)
            .where(MantenimientoAula.id_aula == r.id_aula)
            .where(func.date(MantenimientoAula.fecha_inicio) <= r.fecha)
            .where(func.date(MantenimientoAula.fecha_fin) >= r.fecha)
            .where(MantenimientoAula.estado.in_(["programado", "en_proceso"]))
        )

        mantenimientos = self.db.execute(stmt).scalars().all()

        for m in mantenimientos:
            if r.hora_inicio < m.fecha_fin.time() and r.hora_fin > m.fecha_inicio.time():
                return m

        return None

    # 4) Conflicto con horario oficial del DOCENTE
    def conflicto_docente_horario_oficial(self, r: Reserva):
        dia_semana = dias_map[r.fecha.weekday()]

        stmt = (
            select(HorarioAsignado, BloqueHorario)
            .join(BloqueHorario, HorarioAsignado.id_bloque == BloqueHorario.id_bloque)
            .where(HorarioAsignado.id_docente == r.id_docente)
            .where(HorarioAsignado.id_dia == dia_semana)
        )

        result = self.db.execute(stmt).all()

        for horario, bloque in result:
            if r.hora_inicio < bloque.hora_fin and r.hora_fin > bloque.hora_inicio:
                return bloque

        return None

    # 5) El docente NO está disponible
    def docente_no_disponible(self, r: Reserva):
        dia_semana = dias_map[r.fecha.weekday()]

        stmt = select(DisponibilidadDocente).where(
            DisponibilidadDocente.id_docente == r.id_docente,
            DisponibilidadDocente.id_dia == dia_semana,
            DisponibilidadDocente.hora_inicio <= r.hora_inicio,
            DisponibilidadDocente.hora_fin >= r.hora_fin,
            DisponibilidadDocente.disponible == True
        )

        return self.db.execute(stmt).scalar_one_or_none() is None

    # 6) Conflicto con otras reservas del DOCENTE
    def conflicto_reserva_docente(self, r: Reserva):
        stmt = (
            select(Reserva)
            .where(Reserva.id_docente == r.id_docente)
            .where(Reserva.fecha == r.fecha)
            .where(r.hora_inicio < Reserva.hora_fin)
            .where(r.hora_fin > Reserva.hora_inicio)
        )
        return self.db.execute(stmt).scalar_one_or_none()
    

    def conflicto_reserva_update(self, r: Reserva):
        stmt = (
            select(Reserva)
            .where(Reserva.id_aula == r.id_aula)
            .where(Reserva.fecha == r.fecha)
            .where(Reserva.id_reserva != r.id_reserva)  # ignorar la misma
            .where(r.hora_inicio < Reserva.hora_fin)
            .where(r.hora_fin > Reserva.hora_inicio)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def conflicto_reserva_docente_update(self, r: Reserva):
        stmt = (
            select(Reserva)
            .where(Reserva.id_docente == r.id_docente)
            .where(Reserva.fecha == r.fecha)
            .where(Reserva.id_reserva != r.id_reserva)
            .where(r.hora_inicio < Reserva.hora_fin)
            .where(r.hora_fin > Reserva.hora_inicio)
        )
        return self.db.execute(stmt).scalar_one_or_none()

