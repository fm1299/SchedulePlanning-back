from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import get_db
from services.usuario_service import UsuarioService
from schemas.usuario import UsuarioCreate, UsuarioAdminCreate, UsuarioResponse, Token
from core.auth import get_current_admin_user

router = APIRouter()


def get_usuario_service(db: Session = Depends(get_db)) -> UsuarioService:
    return UsuarioService(db)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UsuarioService = Depends(get_usuario_service),
):
    usuario = service.authenticate_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = service.create_token_for_usuario(usuario)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/admins", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_admin(
    admin_in: UsuarioAdminCreate,
    service: UsuarioService = Depends(get_usuario_service),
):
    # Bootstrap creation: only allow if no administrador exists
    if service.count_admins() > 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrador already exists. Use protected creation.")
    try:
        # create usuario + administrador profile
        usuario = service.create_admin_with_profile(admin_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return usuario


@router.get("/me", response_model=UsuarioResponse)
def read_current_admin(current_admin = Depends(get_current_admin_user)):
    return current_admin
