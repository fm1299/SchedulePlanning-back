from typing import Any, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """
    Base exception class for all custom API exceptions.
    All custom exceptions should inherit from this class.
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Error interno del servidor"
    error_code: str = "INTERNAL_ERROR"
    
    def __init__(
        self, 
        detail: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[dict[str, Any]] = None
    ):
        self.detail = detail or self.detail
        self.status_code = status_code or self.status_code
        
        # Add custom error code to headers
        if headers is None:
            headers = {}
        headers["X-Error-Code"] = self.error_code
        
        super().__init__(
            status_code=self.status_code,
            detail=self.detail,
            headers=headers
        )


# ========== NOT FOUND EXCEPTIONS ==========

class NotFoundException(BaseAPIException):
    """Exception raised when a resource is not found"""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Recurso no encontrado"
    error_code = "NOT_FOUND"


class AulaNotFoundException(NotFoundException):
    """Exception raised when a classroom is not found"""
    error_code = "AULA_NOT_FOUND"
    
    def __init__(self, aula_id: int):
        super().__init__(detail=f"Aula con ID {aula_id} no encontrada")


class DocenteNotFoundException(NotFoundException):
    """Exception raised when a teacher is not found"""
    error_code = "DOCENTE_NOT_FOUND"
    
    def __init__(self, docente_id: int):
        super().__init__(detail=f"Docente con ID {docente_id} no encontrado")


class CursoNotFoundException(NotFoundException):
    """Exception raised when a course is not found"""
    error_code = "CURSO_NOT_FOUND"
    
    def __init__(self, curso_id: int):
        super().__init__(detail=f"Curso con ID {curso_id} no encontrado")


class HorarioNotFoundException(NotFoundException):
    """Exception raised when a schedule is not found"""
    error_code = "HORARIO_NOT_FOUND"
    
    def __init__(self, horario_id: int):
        super().__init__(detail=f"Horario con ID {horario_id} no encontrado")


class AsignacionNotFoundException(NotFoundException):
    """Exception raised when an assignment is not found"""
    error_code = "ASIGNACION_NOT_FOUND"
    
    def __init__(self, asignacion_id: int):
        super().__init__(detail=f"Asignación con ID {asignacion_id} no encontrada")


# ========== CONFLICT EXCEPTIONS ==========

class ConflictException(BaseAPIException):
    """Exception raised when there's a conflict with existing data"""
    status_code = status.HTTP_409_CONFLICT
    detail = "Conflicto con datos existentes"
    error_code = "CONFLICT"


class AulaCodigoExistsException(ConflictException):
    """Exception raised when a classroom code already exists"""
    error_code = "AULA_CODIGO_EXISTS"
    
    def __init__(self, codigo: str):
        super().__init__(detail=f"Ya existe un aula con el código '{codigo}'")


class HorarioConflictException(ConflictException):
    """Exception raised when there's a schedule conflict"""
    error_code = "HORARIO_CONFLICT"
    
    def __init__(self, detalle: str):
        super().__init__(detail=f"Conflicto de horario: {detalle}")


class AsignacionConflictException(ConflictException):
    """Exception raised when there's an assignment conflict"""
    error_code = "ASIGNACION_CONFLICT"
    
    def __init__(self, detalle: str):
        super().__init__(detail=f"Conflicto en asignación: {detalle}")


# ========== VALIDATION EXCEPTIONS ==========

class ValidationException(BaseAPIException):
    """Exception raised when business validation fails"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Error de validación"
    error_code = "VALIDATION_ERROR"


class CapacidadInsuficienteException(ValidationException):
    """Exception raised when classroom capacity is insufficient"""
    error_code = "CAPACIDAD_INSUFICIENTE"
    
    def __init__(self, capacidad_aula: int, cantidad_estudiantes: int):
        super().__init__(
            detail=f"Capacidad del aula ({capacidad_aula}) insuficiente para {cantidad_estudiantes} estudiantes"
        )


class TipoAulaInvalidoException(ValidationException):
    """Exception raised when classroom type doesn't match course requirements"""
    error_code = "TIPO_AULA_INVALIDO"
    
    def __init__(self, tipo_requerido: str, tipo_aula: str):
        super().__init__(
            detail=f"El curso requiere un aula de tipo '{tipo_requerido}', pero el aula es de tipo '{tipo_aula}'"
        )


class DocenteNoDisponibleException(ValidationException):
    """Exception raised when a teacher is not available"""
    error_code = "DOCENTE_NO_DISPONIBLE"
    
    def __init__(self, docente_nombre: str, horario: str):
        super().__init__(
            detail=f"El docente {docente_nombre} no está disponible en el horario {horario}"
        )


class HorasInsuficientesException(ValidationException):
    """Exception raised when assigned hours don't match course requirements"""
    error_code = "HORAS_INSUFICIENTES"
    
    def __init__(self, horas_requeridas: int, horas_asignadas: int):
        super().__init__(
            detail=f"El curso requiere {horas_requeridas} horas, pero solo se han asignado {horas_asignadas}"
        )


# ========== AUTHENTICATION & AUTHORIZATION EXCEPTIONS ==========

class UnauthorizedException(BaseAPIException):
    """Exception raised for authentication failures"""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "No autorizado"
    error_code = "UNAUTHORIZED"


class InvalidCredentialsException(UnauthorizedException):
    """Exception raised when login credentials are invalid"""
    error_code = "INVALID_CREDENTIALS"
    
    def __init__(self):
        super().__init__(detail="Credenciales inválidas")


class TokenExpiredException(UnauthorizedException):
    """Exception raised when token has expired"""
    error_code = "TOKEN_EXPIRED"
    
    def __init__(self):
        super().__init__(detail="Token expirado")


class ForbiddenException(BaseAPIException):
    """Exception raised when user lacks permission"""
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Acceso prohibido"
    error_code = "FORBIDDEN"
    
    def __init__(self, detalle: Optional[str] = None):
        super().__init__(detail=detalle or self.detail)


# ========== DATABASE EXCEPTIONS ==========

class DatabaseException(BaseAPIException):
    """Exception raised for database-related errors"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Error de base de datos"
    error_code = "DATABASE_ERROR"


class DatabaseConnectionException(DatabaseException):
    """Exception raised when database connection fails"""
    error_code = "DATABASE_CONNECTION_ERROR"
    
    def __init__(self):
        super().__init__(detail="No se pudo conectar a la base de datos")


# ========== OPTIMIZATION EXCEPTIONS ==========

class OptimizationException(BaseAPIException):
    """Exception raised when optimization fails"""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Error en el proceso de optimización"
    error_code = "OPTIMIZATION_ERROR"


class NoSolutionFoundException(OptimizationException):
    """Exception raised when optimization finds no valid solution"""
    error_code = "NO_SOLUTION_FOUND"
    
    def __init__(self, detalle: Optional[str] = None):
        super().__init__(
            detail=detalle or "No se encontró una solución óptima con las restricciones actuales"
        )


class ConstraintViolationException(OptimizationException):
    """Exception raised when constraints cannot be satisfied"""
    error_code = "CONSTRAINT_VIOLATION"
    
    def __init__(self, restriccion: str):
        super().__init__(detail=f"Violación de restricción: {restriccion}")
