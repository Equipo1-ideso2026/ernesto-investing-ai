"""
Esquemas Pydantic para el modulo de autenticacion: validan las
peticiones entrantes y dan forma a las respuestas de la API.
"""
from pydantic import BaseModel, EmailStr, Field


class RegistroRequest(BaseModel):
    nombre_completo: str = Field(min_length=2, max_length=100)
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    username: str
    password: str


class UsuarioResponse(BaseModel):
    id: str
    nombre_completo: str
    email: str
    username: str
    avatar_url: str
    watchlist: list[str]


class LoginResponse(BaseModel):
    token: str
    usuario: UsuarioResponse


class ActualizarPerfilRequest(BaseModel):
    nombre_completo: str | None = None
    avatar_url: str | None = None


class WatchlistRequest(BaseModel):
    ticker: str
    accion: str  # "agregar" o "quitar"
