from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.aula import Aula, TipoAula
from repositories.base import BaseRepository


class AulaRepository(BaseRepository[Aula]):
    """
    Repository for Aula (Classroom) entity.
    Handles all database operations related to classrooms.
    """
    
    def __init__(self, db: Session):
        super().__init__(Aula, db)
    
    def get_by_codigo(self, codigo: str) -> Optional[Aula]:
        """
        Get a classroom by its unique code.
        
        Args:
            codigo: The classroom code (e.g., "A-101")
            
        Returns:
            Aula object if found, None otherwise
        """
        return self.db.query(Aula).filter(Aula.codigo == codigo).first()
    
    def get_by_tipo(self, tipo: TipoAula, skip: int = 0, limit: int = 100) -> List[Aula]:
        """
        Get classrooms filtered by type.
        
        Args:
            tipo: Type of classroom (TEORIA, LABORATORIO, SEMINARIO)
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of Aula objects matching the type
        """
        return (
            self.db.query(Aula)
            .filter(Aula.tipo == tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_capacidad_minima(self, capacidad_minima: int) -> List[Aula]:
        """
        Get classrooms with minimum capacity.
        
        Args:
            capacidad_minima: Minimum required capacity
            
        Returns:
            List of Aula objects with capacity >= capacidad_minima
        """
        return (
            self.db.query(Aula)
            .filter(Aula.capacidad >= capacidad_minima)
            .order_by(Aula.capacidad.asc())
            .all()
        )
    
    def get_by_ubicacion(self, ubicacion: str) -> List[Aula]:
        """
        Get classrooms by location (partial match).
        
        Args:
            ubicacion: Location/building of the classroom
            
        Returns:
            List of Aula objects in the specified location
        """
        return (
            self.db.query(Aula)
            .filter(Aula.ubicacion.ilike(f"%{ubicacion}%"))
            .all()
        )
    
    def search(
        self, 
        codigo: Optional[str] = None,
        tipo: Optional[TipoAula] = None,
        capacidad_min: Optional[int] = None,
        capacidad_max: Optional[int] = None,
        ubicacion: Optional[str] = None,
        equipamiento: Optional[str] = None
    ) -> List[Aula]:
        """
        Advanced search for classrooms with multiple filters.
        All filters are optional and combined with AND logic.
        
        Args:
            codigo: Filter by classroom code (partial match)
            tipo: Filter by classroom type
            capacidad_min: Minimum capacity
            capacidad_max: Maximum capacity
            ubicacion: Filter by location (partial match)
            equipamiento: Filter by equipment (partial match)
            
        Returns:
            List of Aula objects matching all provided filters
        """
        query = self.db.query(Aula)
        
        if codigo:
            query = query.filter(Aula.codigo.ilike(f"%{codigo}%"))
        
        if tipo:
            query = query.filter(Aula.tipo == tipo)
        
        if capacidad_min is not None:
            query = query.filter(Aula.capacidad >= capacidad_min)
        
        if capacidad_max is not None:
            query = query.filter(Aula.capacidad <= capacidad_max)
        
        if ubicacion:
            query = query.filter(Aula.ubicacion.ilike(f"%{ubicacion}%"))
        
        if equipamiento:
            query = query.filter(Aula.equipamiento.ilike(f"%{equipamiento}%"))
        
        return query.order_by(Aula.codigo).all()
    
    def get_available_for_capacity(self, capacidad_requerida: int, tipo: Optional[TipoAula] = None) -> List[Aula]:
        """
        Get classrooms that can accommodate the required capacity.
        
        Args:
            capacidad_requerida: Number of students that need to fit
            tipo: Optional filter by classroom type
            
        Returns:
            List of suitable Aula objects
        """
        query = self.db.query(Aula).filter(Aula.capacidad >= capacidad_requerida)
        
        if tipo:
            query = query.filter(Aula.tipo == tipo)
        
        return query.order_by(Aula.capacidad.asc()).all()
    
    def count_by_tipo(self, tipo: TipoAula) -> int:
        """
        Count classrooms by type.
        
        Args:
            tipo: Type of classroom
            
        Returns:
            Number of classrooms of the specified type
        """
        return self.db.query(Aula).filter(Aula.tipo == tipo).count()
    
    def get_statistics(self) -> dict:
        """
        Get classroom statistics (total count, average capacity, etc.).
        
        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func
        
        stats = self.db.query(
            func.count(Aula.id).label('total'),
            func.avg(Aula.capacidad).label('capacidad_promedio'),
            func.max(Aula.capacidad).label('capacidad_maxima'),
            func.min(Aula.capacidad).label('capacidad_minima')
        ).first()
        
        return {
            'total_aulas': stats.total or 0,
            'capacidad_promedio': float(stats.capacidad_promedio or 0),
            'capacidad_maxima': stats.capacidad_maxima or 0,
            'capacidad_minima': stats.capacidad_minima or 0,
            'por_tipo': {
                'teoria': self.count_by_tipo(TipoAula.TEORIA),
                'laboratorio': self.count_by_tipo(TipoAula.LABORATORIO),
                'seminario': self.count_by_tipo(TipoAula.SEMINARIO)
            }
        }
