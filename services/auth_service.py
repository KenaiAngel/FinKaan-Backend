"""
services/auth_service.py — Lógica de negocio para autenticación.
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..security import hash_password, verify_password, create_access_token


def register_user(body: schemas.SignUpRequest, db: Session) -> schemas.TokenResponse:
    """Crea un usuario nuevo y su progreso inicial. Lanza 409 si el email ya existe."""
    existing = db.query(models.User).filter(
        models.User.email == body.email.lower()
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este correo ya tiene una cuenta.",
        )

    user = models.User(
        name=body.name,
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.flush()  # obtiene user.id sin commit

    db.add(models.UserProgress(user_id=user.id))
    db.commit()
    db.refresh(user)

    return schemas.TokenResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        name=user.name,
        onboarding_done=user.onboarding_done,
    )


def authenticate_user(body: schemas.LoginRequest, db: Session) -> schemas.TokenResponse:
    """Valida credenciales y retorna un token. Lanza 401 si son incorrectas."""
    user = db.query(models.User).filter(
        models.User.email == body.email.lower()
    ).first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    return schemas.TokenResponse(
        access_token=create_access_token(user.id),
        user_id=user.id,
        name=user.name,
        onboarding_done=user.onboarding_done,
    )
