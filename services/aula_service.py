from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from typing import List, Optional
from fastapi import HTTPException
from models.aula import Aula
from models.tipo_aula import TipoAula
from schemas.aula import (
    AulaCreate, AulaUpdate, AulaSearch, AulaStatistics
)

class AulaService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_aulas(self, skip: int = 0, limit: int = 100) -> List[Aula]:
        return self.db.query(Aula).offset(skip).limit(limit).all()
    
    def get_aula(self, aula_id: int) -> Aula:
        aula = self.db.query(Aula).filter(Aula.id_aula == aula_id).first()
        if not aula:
            raise HTTPException(status_code=404, detail="Aula no encontrada")
        return aula
    
    def create_aula(self, aula_in: AulaCreate) -> Aula:
        existing = self.db.query(Aula).filter(Aula.codigo == aula_in.codigo).first()
        if existing:
            raise HTTPException(status_code=400, detail="El código del aula ya existe")
        
        tipo = self.db.query(TipoAula).filter(TipoAula.id_tipo == aula_in.id_tipo).first()
        if not tipo:
            raise HTTPException(status_code=400, detail="Tipo de aula no encontrado")
        
        aula = Aula(**aula_in.dict())
        self.db.add(aula)
        self.db.commit()
        self.db.refresh(aula)
        return aula
    
    def update_aula(self, aula_id: int, aula_in: AulaUpdate) -> Aula:
        aula = self.get_aula(aula_id)
        
        if aula_in.codigo and aula_in.codigo != aula.codigo:
            existing = self.db.query(Aula).filter(
                Aula.codigo == aula_in.codigo,
                Aula.id_aula != aula_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="El código del aula ya existe")
        
        update_data = aula_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(aula, field, value)
        
        self.db.commit()
        self.db.refresh(aula)
        return aula
    
    def delete_aula(self, aula_id: int) -> None:
        aula = self.get_aula(aula_id)
        
        if aula.mantenimientos:
            raise HTTPException(
                status_code=400, 
                detail="No se puede eliminar el aula porque tiene mantenimientos asociados"
            )
        
        self.db.delete(aula)
        self.db.commit()
    
    def search_aulas(self, search_params: AulaSearch) -> List[Aula]:
        query = self.db.query(Aula)
        
        if search_params.codigo:
            query = query.filter(Aula.codigo.ilike(f"%{search_params.codigo}%"))
        
        if search_params.id_tipo:
            query = query.filter(Aula.id_tipo == search_params.id_tipo)
        
        if search_params.id_edificio:
            query = query.filter(Aula.id_edificio == search_params.id_edificio)
        
        if search_params.capacidad_min:
            query = query.filter(Aula.capacidad >= search_params.capacidad_min)
        
        if search_params.capacidad_max:
            query = query.filter(Aula.capacidad <= search_params.capacidad_max)
        
        if search_params.piso is not None:
            query = query.filter(Aula.piso == search_params.piso)
        
        if search_params.estado:
            query = query.filter(Aula.estado == search_params.estado)
        
        return query.all()
    
    def get_aulas_by_tipo(self, tipo_id: int) -> List[Aula]:
        tipo = self.db.query(TipoAula).filter(TipoAula.id_tipo == tipo_id).first()
        if not tipo:
            raise HTTPException(status_code=404, detail="Tipo de aula no encontrado")
        
        return self.db.query(Aula).filter(Aula.id_tipo == tipo_id).all()
    
    def get_available_for_capacity(self, capacidad: int, tipo_id: Optional[int] = None) -> List[Aula]:
        query = self.db.query(Aula).filter(
            Aula.capacidad >= capacidad,
            Aula.estado == 'disponible'
        )
        
        if tipo_id:
            query = query.filter(Aula.id_tipo == tipo_id)
        
        return query.order_by(Aula.capacidad).all()
    
    def get_aulas_disponibles(self, skip: int = 0, limit: int = 100) -> List[Aula]:
        return self.db.query(Aula).filter(
            Aula.estado == 'disponible'
        ).offset(skip).limit(limit).all()
    
    def get_statistics(self) -> AulaStatistics:
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
            aulas_mantenimiento=estados_dict.get('mantenimiento', 0),
            aulas_inhabilitadas=estados_dict.get('inhabilitada', 0),
            distribucion_por_tipo=[
                {"tipo": nombre, "cantidad": cantidad}
                for nombre, cantidad in distribucion
            ]
        )