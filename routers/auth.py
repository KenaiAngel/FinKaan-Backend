"""
routers/auth.py — Endpoints de autenticación.

Cada endpoint delega la lógica de negocio al módulo services/auth_service.py,
conservando aquí solo el manejo HTTP (request/response, códigos de estado).
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..database import get_db
from ..redis_client import blacklist_token
from ..security import get_current_user
from ..services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer()


@router.post("/signup", response_model=schemas.TokenResponse, status_code=201)
def signup(body: schemas.SignUpRequest, db: Session = Depends(get_db)):
    return auth_service.register_user(body, db)


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    return auth_service.authenticate_user(body, db)


@router.post("/logout", response_model=schemas.MessageResponse)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    _: models.User = Depends(get_current_user),
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = payload.get("exp", 0)
        ttl = max(int(exp - datetime.now(timezone.utc).timestamp()), 1)
    except JWTError:
        ttl = 60  # fallback conservador

    blacklist_token(token, ttl)
    return {"message": "Sesión cerrada correctamente."}
