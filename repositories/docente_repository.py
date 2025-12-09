# repositories/docente_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from models.docente import Docente, TipoDocente, UsuarioDocente, AsignacionDocente, Grupo
from schemas.docente import DocenteCreate, DocenteUpdate
from repositories.historial_repository import HistorialCambiosRepository

class DocenteRepository:
    def __init__(self, db: Session):
        self.db = db
        self.hist_repo = HistorialCambiosRepository(db)
        
        
    def get(self, docente_id: int) -> Optional[Docente]:
        return (
            self.db.query(Docente)
            .options(
                joinedload(Docente.tipo_docente),
                #joinedload(Docente.departamento),
                joinedload(Docente.usuario_docente).joinedload(UsuarioDocente.usuario),
            )
            .filter(Docente.id_docente == docente_id)
            .first()
        )

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        #departamento_id: Optional[int] = None,
        tipo_docente_id: Optional[int] = None,
    ) -> List[Docente]:
        query = (
            self.db.query(Docente)
            .options(
                joinedload(Docente.tipo_docente),
                #joinedload(Docente.departamento),
                joinedload(Docente.usuario_docente).joinedload(UsuarioDocente.usuario),
            )
        )

        #if departamento_id:
        #    query = query.filter(Docente.id_departamento == departamento_id)
        if tipo_docente_id:
            query = query.filter(Docente.id_tipo == tipo_docente_id)

        return query.offset(skip).limit(limit).all()

    def get_count(self) -> int:
        return self.db.query(func.count(Docente.id_docente)).scalar() or 0

    def create(self, obj_in: DocenteCreate) -> Docente:
        #departamento = (
        #    self.db.query(Departamento)
        #    .filter(Departamento.id_departamento == obj_in.id_departamento)
        #    .first()
        #)
        #if not departamento:
        #    raise HTTPException(
        #        status_code=status.HTTP_400_BAD_REQUEST,
        #        detail="El departamento especificado no existe",
        #    )

        tipo_docente = (
            self.db.query(TipoDocente)
            .filter(TipoDocente.id_tipo == obj_in.id_tipo)
            .first()
        )
        if not tipo_docente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El tipo de docente especificado no existe",
            )

        # Crear docente
        db_obj = Docente(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.flush() # Para obtejer id_docente sin cerrar transacción
        
        
        # Registrar historial (Insert)
        self.hist_repo.registrar_cambio (
            tabla_afectada = "docente",
            id_registro = db_obj.id_docente,
            accion = "INSERT",
            datos_anteriores = None,
            datos_nuevos = obj_in.model_dump(),
            usuario = None, # Aquí se podría pasar id_usuario si se tiene en el contexto
        )
        
        
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, docente_id: int, obj_in: DocenteUpdate) -> Docente:
        db_obj = self.get(docente_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Docente no encontrado",
            )

        # 1) Capturar datos ANTERIORES (como dict)
        datos_anteriores = {
            "id_docente": db_obj.id_docente,
            #"id_departamento": db_obj.id_departamento,
            "id_tipo": db_obj.id_tipo,
            "nombre": db_obj.nombre,
            "apellidos": db_obj.apellidos,
            "telefono": db_obj.telefono,
            "especialidad": db_obj.especialidad,
            "grado_academico": db_obj.grado_academico,
            "max_horas_sem": db_obj.max_horas_sem,
           # "regimen": getattr(db_obj, "regimen", None),
           # "fecha_inicio": getattr(db_obj, "fecha_inicio", None).isoformat()
           # if getattr(db_obj, "fecha_inicio", None)
            #else None,
        }


        update_data = obj_in.model_dump(exclude_unset=True)

        ## 2) Validaciones de FKs 
        #if "id_departamento" in update_data:
        #    departamento = (
        #        self.db.query(Departamento)
        #        .filter(Departamento.id_departamento == update_data["id_departamento"])
        #        .first()
        #    )
        #    if not departamento:
        #        raise HTTPException(
        #            status_code=status.HTTP_400_BAD_REQUEST,
        #            detail="El departamento especificado no existe",
        #        )

        if "id_tipo" in update_data:
            tipo_docente = (
                self.db.query(TipoDocente)
                .filter(TipoDocente.id_tipo == update_data["id_tipo"])
                .first()
            )
            if not tipo_docente:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El tipo de docente especificado no existe",
                )

        # 3) Aplicar cambios al objeto 
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.flush()  # aplicar UPDATE en BD pero sin commit

        # 4) Capturar datos NUEVOS
        datos_nuevos = {
            "id_docente": db_obj.id_docente,
            #"id_departamento": db_obj.id_departamento,
            "id_tipo": db_obj.id_tipo,
            "nombre": db_obj.nombre,
            "apellidos": db_obj.apellidos,
            "telefono": db_obj.telefono,
            "especialidad": db_obj.especialidad,
            "grado_academico": db_obj.grado_academico,
            "max_horas_sem": db_obj.max_horas_sem,
            #"regimen": getattr(db_obj, "regimen", None),
            #"fecha_inicio": getattr(db_obj, "fecha_inicio", None).isoformat()
            #if getattr(db_obj, "fecha_inicio", None)
            #else None,
        }

        # 5) Registrar historial (UPDATE)
        self.hist_repo.registrar_cambio(
            tabla_afectada="docente",
            id_registro=db_obj.id_docente,
            accion="UPDATE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            usuario=None,  # aquí se podría pasar id_usuario si se tiene
        )

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, docente_id: int) -> None:
        db_obj = self.db.query(Docente).filter(Docente.id_docente == docente_id).first()
        if not db_obj:
            return

        # 1) Capturar datos ANTERIORES antes de borrar
        datos_anteriores = {
            "id_docente": db_obj.id_docente,
            #"id_departamento": db_obj.id_departamento,
            "id_tipo": db_obj.id_tipo,
            "nombre": db_obj.nombre,
            "apellidos": db_obj.apellidos,
            "telefono": db_obj.telefono,
            "especialidad": db_obj.especialidad,
            "grado_academico": db_obj.grado_academico,
            "max_horas_sem": db_obj.max_horas_sem,
            #"regimen": getattr(db_obj, "regimen", None),
            #"fecha_inicio": getattr(db_obj, "fecha_inicio", None).isoformat()
            #if getattr(db_obj, "fecha_inicio", None)
            #else None,
        }

        # 2) Borrar el docente
        self.db.delete(db_obj)
        self.db.flush()  # ejecutar DELETE en BD pero sin commit

        # 3) Registrar historial (DELETE)
        self.hist_repo.registrar_cambio(
            tabla_afectada="docente",
            id_registro=docente_id,
            accion="DELETE",
            datos_anteriores=datos_anteriores,
            datos_nuevos=None,
            usuario=None,
        )

        self.db.commit()

    def docente_tiene_usuario(self, docente_id: int) -> bool:
        usuario_docente = (
            self.db.query(UsuarioDocente)
            .filter(UsuarioDocente.id_docente == docente_id)
            .first()
        )
        return usuario_docente is not None

    def get_horas_asignadas_semestre(self, docente_id: int, semestre_id: int) -> int:
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
