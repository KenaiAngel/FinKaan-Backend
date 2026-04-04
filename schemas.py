"""
schemas.py — Esquemas Pydantic para request/response de FinKaan
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


# ─── Auth ─────────────────────────────────────────────────────────────────────

class SignUpRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    onboarding_done: bool


# ─── Usuario ──────────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    language: int
    onboarding_done: bool
    situation: int | None
    goal: int | None
    finance_level: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateNameRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)

    @field_validator("name")
    @classmethod
    def name_strip(cls, v: str) -> str:
        return v.strip()


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6, max_length=128)


class UpdateLanguageRequest(BaseModel):
    language: int = Field(ge=0, le=9)  # 10 idiomas en AppLanguage


# ─── Onboarding ───────────────────────────────────────────────────────────────

class OnboardingRequest(BaseModel):
    language: int = Field(ge=0, le=9)
    situation: int = Field(ge=0, le=3)
    goal: int = Field(ge=0, le=3)
    finance_level: int = Field(ge=0, le=2)


# ─── Progreso ─────────────────────────────────────────────────────────────────

class ProgressResponse(BaseModel):
    total_xp: int
    level: int
    streak: int
    completed_ids: list[int]
    unlocked_ids: list[int]
    streak_days: list[bool]
    theme_mode: int


class CompleteScenarioRequest(BaseModel):
    scenario_id: int
    xp_earned: int = Field(ge=0)
    # El cliente envía el siguiente id a desbloquear (lo calcula él)
    next_scenario_id: int | None = None


class UpdateThemeRequest(BaseModel):
    theme_mode: int = Field(ge=0, le=2)


# ─── Scenarios ────────────────────────────────────────────────────────────────

class ScenarioOut(BaseModel):
    """
    Respuesta de un escenario desde el servidor.
    `data` contiene el objeto completo del escenario
    (mismo shape que el JSON local en assets/scenarios.json).
    """
    id: int
    order_index: int
    data: dict  # JSON desempaquetado


# ─── Generic ──────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
