from fastapi import HTTPException
from sqlalchemy import select
from models.reserva import Reserva
from models.aula import Aula
from schemas.reserva import ReservaCreate, ReservaUpdate, ReservaEstadoUpdate
from repositories.reserva_repository import ReservaRepository
from models.historial_cambios import HistorialCambios
from models.usuario import Usuario
import json

class ReservaService:
    def __init__(self, db):
        self.db = db
        self.repo = ReservaRepository(db)

    def crear(self, data: ReservaCreate):
        # 1. Creamos el objeto y forzamos estado PENDIENTE
        nueva_reserva = Reserva(**data.model_dump())
        nueva_reserva.estado = "pendiente"

        # ---------------- VALIDACIONES (El Filtro Automático) ---------------- #
        
        # NOTA: Usamos 'nueva_reserva' en lugar de 'r'

        # 1) Conflicto con reservas YA CONFIRMADAS (Permite solaparse con otras pendientes)
        # Asegúrate de haber agregado este método al repositorio como hablamos antes
        if self.repo.conflicto_reserva_confirmada(nueva_reserva):
            raise HTTPException(400, "❌ El aula ya está ocupada por una reserva confirmada.")

        # 2) Conflicto con horario oficial del aula
        bloque = self.repo.conflicto_horario_oficial(nueva_reserva)
        if bloque:
            raise HTTPException(
                400,
                f"❌ Aula ocupada por clase oficial. Bloque {bloque.nombre} ({bloque.hora_inicio}-{bloque.hora_fin})"
            )

        # 3) Conflicto con mantenimiento
        m = self.repo.conflicto_mantenimiento(nueva_reserva)
        if m:
            raise HTTPException(400, f"❌ Aula en mantenimiento: {m.motivo}")

        # 4) Validar estado del aula (debe ser disponible)
        aula = self.db.execute(
            select(Aula).where(Aula.id_aula == nueva_reserva.id_aula)
        ).scalar_one_or_none()

        if not aula:
             raise HTTPException(404, "❌ El aula especificada no existe.")

        if aula.estado != "disponible":
            raise HTTPException(
                400,
                f"❌ El aula no está disponible (estado: {aula.estado})."
            )

        # 5) Conflicto con horario oficial del docente
        if self.repo.conflicto_docente_horario_oficial(nueva_reserva):
            raise HTTPException(400, "❌ El docente dicta clase oficial en ese horario")

        # 6) Validar disponibilidad del docente
        if self.repo.docente_no_disponible(nueva_reserva):
            raise HTTPException(400, "❌ El docente NO está disponible en ese horario")

        # ---------------- GUARDAR ---------------- #
        reserva_creada = self.repo.add(nueva_reserva)

        # Registrar historial
        datos_nuevos = json.dumps({
            "id_reserva": reserva_creada.id_reserva,
            "id_aula": reserva_creada.id_aula,
            "id_docente": reserva_creada.id_docente,
            "fecha": str(reserva_creada.fecha),
            "hora_inicio": str(reserva_creada.hora_inicio),
            "hora_fin": str(reserva_creada.hora_fin),
            "descripcion": reserva_creada.descripcion,
            "estado": reserva_creada.estado
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

    # ---------------- NUEVO MÉTODO PARA EL ADMINISTRADOR ---------------- #
    def gestionar_estado(self, id_reserva: int, data: ReservaEstadoUpdate):
        reserva = self.repo.get(id_reserva)
        if not reserva:
            raise HTTPException(404, "Reserva no encontrada")

        nuevo_estado = data.estado.lower()
        if nuevo_estado not in ["confirmada", "rechazada", "pendiente"]:
             raise HTTPException(400, "Estado no válido")

        # Datos anteriores para el historial
        datos_antes = json.dumps({"estado": reserva.estado})

        # Si el admin quiere CONFIRMAR, verificamos doble choque por seguridad
        if nuevo_estado == "confirmada":
            if self.repo.conflicto_reserva_confirmada(reserva):
                raise HTTPException(409, "❌ No se puede confirmar: El horario ya fue ocupado por otra reserva.")

        # Aplicar cambio
        reserva.estado = nuevo_estado
        self.repo.update(reserva)

        # Historial del cambio de estado
        datos_despues = json.dumps({"estado": reserva.estado})
        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=reserva.id_reserva,
            accion="UPDATE",
            datos_anteriores=datos_antes,
            datos_nuevos=datos_despues,
            usuario=1 
        )
        self.db.add(historial)
        self.db.commit()

        return reserva 


    def listar(self):
        return self.repo.get_all()

    def obtener(self, id_reserva: int):
        r = self.repo.get(id_reserva)
        if not r:
            raise HTTPException(404, "Reserva no encontrada")
        return r
    

    def eliminar(self, id_reserva: int, id_solicitante: int):
        r = self.obtener(id_reserva)

        # 1. Verificar Rol
        usuario = self.db.query(Usuario).filter(Usuario.id_usuario == id_solicitante).first()
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")
            
        es_admin = (usuario.rol == 'administrador')
        es_dueno = (r.id_docente == id_solicitante)

        if not es_admin and not es_dueno:
            raise HTTPException(403, "⛔ No tienes permiso para eliminar esta reserva.")

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

        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=id_reserva,
            accion="DELETE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=None,
            usuario=id_solicitante
        )
        self.db.add(historial)

        # Eliminar
        self.repo.delete(r)
        return {"message": "Reserva cancelada/eliminada correctamente"}

    '''
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
            usuario=1 
        )
        self.db.add(historial)

        # Eliminar reserva
        self.repo.delete(r)

        return {"message": "Reserva eliminada"}
    '''
    '''
    def actualizar(self, id_reserva: int, data: ReservaUpdate):
        r = self.repo.get(id_reserva)
        if not r:
            raise HTTPException(404, "Reserva no encontrada")

        # Guardar datos anteriores para historial
        datos_antes = json.dumps({
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion
        })

        # Aplicar cambios en memoria (sin guardar aún)
        # model_dump(exclude_unset=True) ignora los campos que no enviaste
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(r, field, value)

        # --- RE-VALIDACIONES ---
        # Es vital validar de nuevo porque al cambiar la hora podría haber nuevos choques
        
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

        # Registrar historial (Manual para no depender de HistorialRepository aun)
        datos_despues = json.dumps({
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion
        })

        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=r.id_reserva,
            accion="UPDATE",
            datos_anteriores=datos_antes,
            datos_nuevos=datos_despues,
            usuario=1
        )
        self.db.add(historial)
        self.db.commit()

        return r
    '''

    def actualizar(self, id_reserva: int, data: ReservaUpdate, id_solicitante: int):
        # 1. Obtener la reserva
        r = self.repo.get(id_reserva)
        if not r:
            raise HTTPException(404, "Reserva no encontrada")

        # 2. Verificar Permisos (Admin o Dueño)
        usuario = self.db.query(Usuario).filter(Usuario.id_usuario == id_solicitante).first()
        if not usuario:
            raise HTTPException(404, "Usuario no encontrado")

        es_admin = (usuario.rol == 'administrador')
        es_dueno = (r.id_docente == id_solicitante)

        if not es_admin and not es_dueno:
            raise HTTPException(403, "⛔ No tienes permiso para editar esta reserva.")

        # ---------------------------------------------------------
        # PASO A: Capturar DATOS ANTES
        # ---------------------------------------------------------
        datos_antes = json.dumps({
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion,
            "estado": r.estado 
        })

        # ---------------------------------------------------------
        # PASO B: Detección de Cambios Sensibles + SEGURIDAD + Aplicar
        # ---------------------------------------------------------
        campos_criticos = ["fecha", "hora_inicio", "hora_fin", "id_aula"]
        cambio_sensible = False
        
        datos_nuevos_dict = data.model_dump(exclude_unset=True)

        for field, nuevo_valor in datos_nuevos_dict.items():
            valor_actual = getattr(r, field)
            
            # --- 🛡️ AQUÍ ESTÁ EL CAMBIO QUE FALTABA 🛡️ ---
            # Si intentan cambiar el dueño (id_docente) y NO son admin -> ERROR
            if field == 'id_docente' and not es_admin:
                if valor_actual != nuevo_valor:
                    raise HTTPException(403, "⛔ No puedes transferir tu reserva a otro docente.")
            # -----------------------------------------------

            # Si el valor es diferente al que ya tenía
            if valor_actual != nuevo_valor:
                # Checamos si es un campo crítico
                if field in campos_criticos:
                    cambio_sensible = True
                
                # Aplicamos el cambio
                setattr(r, field, nuevo_valor)

        # ---------------------------------------------------------
        # PASO C: Lógica de Estado (Si cambió algo crítico -> Pendiente)
        # ---------------------------------------------------------
        if not es_admin:
            # Si el usuario es Docente y tocó fecha/hora/aula de una confirmada...
            if cambio_sensible and r.estado == 'confirmada':
                r.estado = 'pendiente' # ¡Pierde la confirmación!

        # ---------------------------------------------------------
        # PASO D: Re-Validaciones
        # ---------------------------------------------------------
        if self.repo.conflicto_reserva_confirmada(r):
            raise HTTPException(409, "❌ El cambio genera conflicto con otra reserva ya confirmada.")

        bloque = self.repo.conflicto_horario_oficial(r)
        if bloque:
            raise HTTPException(400, f"❌ Aula ocupada por clase oficial: {bloque.nombre}")

        if self.repo.conflicto_mantenimiento(r):
            raise HTTPException(400, "❌ Aula en mantenimiento en ese horario")

        if self.repo.conflicto_docente_horario_oficial(r):
            raise HTTPException(400, "❌ Docente dicta una clase en ese horario")
            
        if self.repo.conflicto_reserva_docente_update(r):
             raise HTTPException(400, "❌ Docente tiene otra reserva en ese horario")

        # ---------------------------------------------------------
        # PASO E: Guardar
        # ---------------------------------------------------------
        self.repo.update(r)

        # ---------------------------------------------------------
        # PASO F: Historial Final
        # ---------------------------------------------------------
        datos_despues = json.dumps({
            "id_aula": r.id_aula,
            "id_docente": r.id_docente,
            "fecha": str(r.fecha),
            "hora_inicio": str(r.hora_inicio),
            "hora_fin": str(r.hora_fin),
            "descripcion": r.descripcion,
            "estado": r.estado
        })

        historial = HistorialCambios(
            tabla_afectada="reservas",
            id_registro=r.id_reserva,
            accion="UPDATE",
            datos_anteriores=datos_antes,
            datos_nuevos=datos_despues,
            usuario=id_solicitante
        )
        self.db.add(historial)
        self.db.commit()

        return r
    
    def listar_propias(self, id_docente: int):
        # Aquí podrías agregar lógica extra (ej. ordenar por fecha más reciente)
        return self.repo.get_by_docente(id_docente)