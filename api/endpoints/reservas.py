from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from services.reserva_service import ReservaService
from schemas.reserva import ReservaCreate, ReservaResponse, ReservaUpdate, ReservaEstadoUpdate
from typing import List

router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)

# Inyección de dependencia
def get_service(db: Session = Depends(get_db)):
    return ReservaService(db)


# ------------------- ENDPOINTS ------------------- #

@router.post("/", response_model=ReservaResponse, status_code=201)
def crear_reserva(
    data: ReservaCreate,
    service: ReservaService = Depends(get_service)
):
    """
    Crea una reserva realizando TODAS las validaciones:
    - solapamiento con otras reservas
    - conflicto con horario oficial
    - conflicto con mantenimiento
    """
    return service.crear(data)



@router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    service: ReservaService = Depends(get_service)
):
    """
    Lista todas las reservas del sistema.
    """
    return service.listar()


@router.get("/docente/{id_docente}", response_model=List[ReservaResponse])
def listar_reservas_propias(
    id_docente: int,
    service: ReservaService = Depends(get_service)
):
    """
    Lista las reservas que pertenecen a un docente específico.
    (Simulación de 'Mis Reservas')
    """
    return service.listar_propias(id_docente)


@router.get("/{id_reserva}", response_model=ReservaResponse)
def obtener_reserva(
    id_reserva: int,
    service: ReservaService = Depends(get_service)
):
    """
    Obtiene una reserva por ID.
    """
    return service.obtener(id_reserva)


@router.delete("/{id_reserva}", status_code=200)
def eliminar_reserva(
    id_reserva: int,
    id_usuario: int,
    service: ReservaService = Depends(get_service)
):
    """
    Elimina una reserva específica.
    """
    return service.eliminar(id_reserva, id_solicitante=id_usuario)


@router.put("/{id_reserva}", response_model=ReservaResponse)
def actualizar_reserva(
    id_reserva: int, 
    data: ReservaUpdate, 
    id_usuario: int,  
    db: Session = Depends(get_db)
):
    #SE LO PASAS AL SERVICIO
    return ReservaService(db).actualizar(id_reserva, data, id_solicitante=id_usuario)


@router.patch("/{id_reserva}/estado", response_model=ReservaResponse)
def cambiar_estado_reserva(
    id_reserva: int, 
    data: ReservaEstadoUpdate, 
    service: ReservaService = Depends(get_service)
):
    """
    ADMINISTRADOR: Aceptar ('confirmada') o Rechazar ('rechazada') una reserva.
    """
    return service.gestionar_estado(id_reserva, data)