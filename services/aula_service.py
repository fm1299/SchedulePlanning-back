from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException

from models.aula import Aula
from models.tipo_aula import TipoAula
from schemas.aula import (
    AulaCreate, AulaUpdate, AulaSearch, AulaStatistics,
    AulaFrontend, AulaResponse
)

class AulaService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_aulas(self, skip: int = 0, limit: int = 100) -> List[Aula]:

        return (
        self.db.query(Aula)
        .join(TipoAula)
        .options(joinedload(Aula.tipo_aula))
        .offset(skip)
        .limit(limit)
        .all()
        )
    
    def get_aula(self, aula_id: int) -> Aula:

        aula = self.db.query(Aula)\
            .join(TipoAula)\
            .filter(Aula.id_aula == aula_id)\
            .first()
        if not aula:
            raise HTTPException(status_code=404, detail="Aula no encontrada")
        return aula
    
    def get_aula_by_codigo(self, codigo: str) -> Aula:

        return self.db.query(Aula).filter(Aula.codigo == codigo).first()
    
    def create_aula(self, aula_in: AulaCreate) -> Aula:

        existing = self.get_aula_by_codigo(aula_in.codigo)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Ya existe un aula con el código {aula_in.codigo}"
            )
        

        tipo = self.db.query(TipoAula).filter(TipoAula.id_tipo == aula_in.id_tipo).first()
        if not tipo:
            raise HTTPException(status_code=400, detail="Tipo de aula no encontrado")
        

        aula = Aula(
            codigo=aula_in.codigo,
            nombre=aula_in.nombre,
            id_tipo=aula_in.id_tipo,
            capacidad=aula_in.capacidad,
            ubicacion=aula_in.ubicacion,
            descripcion=aula_in.descripcion,
            equipamiento=aula_in.equipamiento,
            estado=aula_in.estado
        )
        
        self.db.add(aula)
        self.db.commit()
        self.db.refresh(aula)
        return aula
    
    def update_aula(self, aula_id: int, aula_in: AulaUpdate) -> Aula:

        aula = self.get_aula(aula_id)
        

        if aula_in.codigo and aula_in.codigo != aula.codigo:
            existing = self.get_aula_by_codigo(aula_in.codigo)
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Ya existe un aula con el código {aula_in.codigo}"
                )
        

        if aula_in.id_tipo:
            tipo = self.db.query(TipoAula).filter(TipoAula.id_tipo == aula_in.id_tipo).first()
            if not tipo:
                raise HTTPException(status_code=400, detail="Tipo de aula no encontrado")
        

        update_data = aula_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(aula, field, value)
        
        self.db.commit()
        self.db.refresh(aula)
        return aula
    
    def delete_aula(self, aula_id: int) -> None:
        """Eliminar un aula"""
        aula = self.get_aula(aula_id)
        self.db.delete(aula)
        self.db.commit()
    
    def search_aulas(self, search_params: AulaSearch) -> List[Aula]:
        """Buscar aulas según criterios"""
        query = self.db.query(Aula).join(TipoAula)
        
        if search_params.codigo:
            query = query.filter(Aula.codigo.ilike(f"%{search_params.codigo}%"))
        
        if search_params.nombre:
            query = query.filter(Aula.nombre.ilike(f"%{search_params.nombre}%"))
        
        if search_params.id_tipo:
            query = query.filter(Aula.id_tipo == search_params.id_tipo)
        
        if search_params.capacidad_min:
            query = query.filter(Aula.capacidad >= search_params.capacidad_min)
        
        if search_params.capacidad_max:
            query = query.filter(Aula.capacidad <= search_params.capacidad_max)
        
        if search_params.estado:
            query = query.filter(Aula.estado == search_params.estado)
        
        return query.order_by(Aula.codigo).all()
    
    def get_aulas_by_tipo(self, tipo_id: int) -> List[Aula]:
        """Obtener aulas por tipo"""
        return self.db.query(Aula)\
            .filter(Aula.id_tipo == tipo_id)\
            .order_by(Aula.codigo).all()
    
    def get_aulas_disponibles(self, skip: int = 0, limit: int = 100) -> List[Aula]:
        """Obtener aulas disponibles"""
        return self.db.query(Aula)\
            .filter(Aula.estado == 'disponible')\
            .offset(skip).limit(limit).all()
    
    def update_aula_status(self, aula_id: int, status: str) -> Aula:
        """Actualizar estado de un aula"""
        allowed_status = ['disponible', 'ocupada', 'mantenimiento']
        if status not in allowed_status:
            raise HTTPException(
                status_code=400, 
                detail=f"Estado debe ser uno de: {allowed_status}"
            )
        
        aula = self.get_aula(aula_id)
        aula.estado = status
        self.db.commit()
        self.db.refresh(aula)
        return aula
    
    def get_statistics(self) -> AulaStatistics:
        """Obtener estadísticas de aulas"""
        total = self.db.query(func.count(Aula.id_aula)).scalar()
        
        capacidad_stats = self.db.query(
            func.avg(Aula.capacidad).label('promedio'),
            func.min(Aula.capacidad).label('minima'),
            func.max(Aula.capacidad).label('maxima')
        ).first()
        
        estados = self.db.query(
            Aula.estado,
            func.count(Aula.id_aula).label('cantidad')
        ).group_by(Aula.estado).all()
        
        estados_dict = {estado: cantidad for estado, cantidad in estados}
        
        distribucion = self.db.query(
            TipoAula.nombre,
            func.count(Aula.id_aula).label('cantidad')
        ).join(Aula, Aula.id_tipo == TipoAula.id_tipo)\
         .group_by(TipoAula.nombre).all()
        
        return AulaStatistics(
            total_aulas=total,
            capacidad_promedio=float(capacidad_stats.promedio or 0),
            capacidad_minima=capacidad_stats.minima or 0,
            capacidad_maxima=capacidad_stats.maxima or 0,
            aulas_disponibles=estados_dict.get('disponible', 0),
            aulas_ocupadas=estados_dict.get('ocupada', 0),
            aulas_mantenimiento=estados_dict.get('mantenimiento', 0),
            distribucion_por_tipo=[
                {"tipo": nombre, "cantidad": cantidad}
                for nombre, cantidad in distribucion
            ]
        )
    
    def convertir_a_frontend(self, aula: Aula) -> AulaFrontend:

        estado_map = {
            'disponible': 'available',
            'ocupada': 'occupied',
            'mantenimiento': 'maintenance'
        }
        
        return AulaFrontend(
            id=str(aula.id_aula),
            numero=aula.codigo,
            nombre=aula.nombre,
            tipo=aula.tipo_aula.nombre if aula.tipo_aula else "Aula",
            capacidad=aula.capacidad,
            descripcion=aula.descripcion,
            ubicacion=aula.ubicacion,
            status=estado_map.get(aula.estado, 'available')
        )