from typing import List, Optional
from sqlalchemy.orm import Session

from repositories.aula_repository import AulaRepository
from schemas.aula import AulaCreate, AulaUpdate, AulaResponse, AulaSearch
from models.aula import TipoAula
from core.exceptions import (
    AulaNotFoundException,
    AulaCodigoExistsException,
    ValidationException
)


class AulaService:
    """
    Service layer for Aula (Classroom) business logic.
    Handles validation, orchestration, and business rules.
    """
    
    def __init__(self, db: Session):
        self.repository = AulaRepository(db)
        self.db = db
    
    def get_aula(self, aula_id: int) -> AulaResponse:
        """
        Get a single classroom by ID.
        
        Args:
            aula_id: The classroom ID
            
        Returns:
            AulaResponse with classroom data
            
        Raises:
            AulaNotFoundException: If classroom doesn't exist
        """
        aula = self.repository.get(aula_id)
        if not aula:
            raise AulaNotFoundException(aula_id)
        return AulaResponse.model_validate(aula)
    
    def get_all_aulas(self, skip: int = 0, limit: int = 100) -> List[AulaResponse]:
        """
        Get all classrooms with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of AulaResponse objects
        """
        aulas = self.repository.get_all(skip, limit)
        return [AulaResponse.model_validate(aula) for aula in aulas]
    
    def create_aula(self, aula_in: AulaCreate) -> AulaResponse:
        """
        Create a new classroom with business validation.
        
        Args:
            aula_in: Classroom creation data
            
        Returns:
            AulaResponse with created classroom data
            
        Raises:
            AulaCodigoExistsException: If classroom code already exists
            ValidationException: If data validation fails
        """
        # Business Rule 1: Validate classroom code uniqueness
        existing = self.repository.get_by_codigo(aula_in.codigo)
        if existing:
            raise AulaCodigoExistsException(aula_in.codigo)
        
        # Business Rule 2: Validate capacity is positive
        if aula_in.capacidad <= 0:
            raise ValidationException("La capacidad debe ser mayor a 0")
        
        # Business Rule 3: Validate capacity is reasonable (not too large)
        if aula_in.capacidad > 500:
            raise ValidationException("La capacidad máxima permitida es 500 estudiantes")
        
        # Business Rule 4: Validate classroom code format (optional)
        if not self._validate_codigo_format(aula_in.codigo):
            raise ValidationException(
                "El código del aula debe seguir el formato: [LETRA]-[NUMERO] (ej: A-101)"
            )
        
        # Create the classroom
        aula = self.repository.create(aula_in.model_dump())
        return AulaResponse.model_validate(aula)
    
    def update_aula(self, aula_id: int, aula_in: AulaUpdate) -> AulaResponse:
        """
        Update an existing classroom with business validation.
        
        Args:
            aula_id: The classroom ID to update
            aula_in: Updated classroom data
            
        Returns:
            AulaResponse with updated classroom data
            
        Raises:
            AulaNotFoundException: If classroom doesn't exist
            AulaCodigoExistsException: If new code conflicts with existing
            ValidationException: If data validation fails
        """
        # Check if classroom exists
        existing_aula = self.repository.get(aula_id)
        if not existing_aula:
            raise AulaNotFoundException(aula_id)
        
        # Business Rule: If codigo is being updated, check uniqueness
        if aula_in.codigo and aula_in.codigo != existing_aula.codigo:
            existing_by_codigo = self.repository.get_by_codigo(aula_in.codigo)
            if existing_by_codigo:
                raise AulaCodigoExistsException(aula_in.codigo)
        
        # Business Rule: Validate capacity if being updated
        if aula_in.capacidad is not None:
            if aula_in.capacidad <= 0:
                raise ValidationException("La capacidad debe ser mayor a 0")
            if aula_in.capacidad > 500:
                raise ValidationException("La capacidad máxima permitida es 500 estudiantes")
        
        # Update only provided fields
        aula = self.repository.update(aula_id, aula_in.model_dump(exclude_unset=True))
        return AulaResponse.model_validate(aula)
    
    def delete_aula(self, aula_id: int) -> bool:
        """
        Delete a classroom with business validation.
        
        Args:
            aula_id: The classroom ID to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            AulaNotFoundException: If classroom doesn't exist
            ValidationException: If classroom has active assignments
        """
        # Check if classroom exists
        aula = self.repository.get(aula_id)
        if not aula:
            raise AulaNotFoundException(aula_id)
        
        # Business Rule: Check if classroom has active assignments
        # TODO: Implement check for active assignments when AsignacionRepository is ready
        # if self._has_active_assignments(aula_id):
        #     raise ValidationException(
        #         "No se puede eliminar el aula porque tiene asignaciones activas"
        #     )
        
        return self.repository.delete(aula_id)
    
    def search_aulas(self, search_params: AulaSearch) -> List[AulaResponse]:
        """
        Search classrooms with multiple filters.
        
        Args:
            search_params: Search filters
            
        Returns:
            List of AulaResponse objects matching the filters
        """
        aulas = self.repository.search(
            codigo=search_params.codigo,
            tipo=search_params.tipo,
            capacidad_min=search_params.capacidad_min,
            capacidad_max=search_params.capacidad_max,
            ubicacion=search_params.ubicacion,
            equipamiento=search_params.equipamiento
        )
        return [AulaResponse.model_validate(aula) for aula in aulas]
    
    def get_aulas_by_tipo(self, tipo: TipoAula) -> List[AulaResponse]:
        """
        Get all classrooms of a specific type.
        
        Args:
            tipo: Type of classroom
            
        Returns:
            List of AulaResponse objects
        """
        aulas = self.repository.get_by_tipo(tipo)
        return [AulaResponse.model_validate(aula) for aula in aulas]
    
    def get_available_for_capacity(
        self, 
        capacidad_requerida: int, 
        tipo: Optional[TipoAula] = None
    ) -> List[AulaResponse]:
        """
        Get classrooms that can accommodate the required capacity.
        Business logic for finding suitable classrooms.
        
        Args:
            capacidad_requerida: Number of students
            tipo: Optional classroom type filter
            
        Returns:
            List of suitable AulaResponse objects, ordered by capacity
        """
        # Business Rule: Add 10% buffer to required capacity for comfort
        capacidad_con_buffer = int(capacidad_requerida * 1.1)
        
        aulas = self.repository.get_available_for_capacity(capacidad_con_buffer, tipo)
        return [AulaResponse.model_validate(aula) for aula in aulas]
    
    def get_statistics(self) -> dict:
        """
        Get classroom statistics and analytics.
        
        Returns:
            Dictionary with statistics
        """
        return self.repository.get_statistics()
    
    def _validate_codigo_format(self, codigo: str) -> bool:
        """
        Private method to validate classroom code format.
        
        Args:
            codigo: Classroom code to validate
            
        Returns:
            True if valid format, False otherwise
        """
        import re
        # Format: [LETTER]-[NUMBER] (e.g., A-101, B-205)
        pattern = r'^[A-Z]-\d{1,3}$'
        return bool(re.match(pattern, codigo.upper()))
