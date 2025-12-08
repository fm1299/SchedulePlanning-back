from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db


"""
Use Argon2 for password hashing to avoid bcrypt's 72-byte input truncation
and to provide a stronger, modern KDF. This requires `argon2-cffi`.
so arbitrary-length passwords are safe and won't be silently truncated.

If you prefer raw bcrypt, you must manually truncate passwords to 72 bytes
before hashing: `pw = pw.encode()[:72].decode(errors='ignore')`.
"""
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise credentials_exception


def get_current_admin_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    from repositories.usuario_repository import UsuarioRepository

    payload = decode_token(token)
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    repo = UsuarioRepository(db)
    usuario = repo.get_by_username(username)
    if not usuario or not getattr(usuario, "activo", True):
        raise credentials_exception
    # role must be 'administrador'
    if getattr(usuario, "rol", "docente") != 'administrador':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return usuario
