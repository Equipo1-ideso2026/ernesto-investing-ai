"""
Utilidades de seguridad: hash de contrasenas con bcrypt y
generacion/verificacion de tokens JWT para la sesion de usuario.
"""
from datetime import datetime, timezone

import bcrypt
import jwt

from backend.config import settings


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contrasena en texto plano."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verificar_password(password: str, password_hash: str) -> bool:
    """Compara una contrasena en texto plano contra su hash almacenado."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def generar_token(usuario_id: str, username: str) -> str:
    """Genera un JWT firmado, valido por el tiempo definido en settings."""
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": usuario_id,
        "username": username,
        "iat": ahora,
        "exp": ahora + settings.JWT_EXPIRATION,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """
    Decodifica y valida un JWT. Lanza jwt.PyJWTError si el token
    es invalido, esta mal formado o ha expirado.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
