"""
Endpoints de autenticacion: registro, login, perfil y watchlist.
Todos los endpoints protegidos usan el esquema Bearer (JWT en el header
Authorization) validado por la dependencia obtener_usuario_actual, que
se reutiliza tambien desde otros routers del sistema.
"""
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from backend.database import get_db
from backend.auth.security import (
    hash_password,
    verificar_password,
    generar_token,
    decodificar_token,
)
from backend.auth.models import (
    RegistroRequest,
    LoginRequest,
    LoginResponse,
    UsuarioResponse,
    ActualizarPerfilRequest,
    WatchlistRequest,
)

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])
bearer_scheme = HTTPBearer()


def _usuario_a_response(doc: dict) -> UsuarioResponse:
    """Convierte un documento de Mongo en el esquema publico de usuario."""
    return UsuarioResponse(
        id=str(doc["_id"]),
        nombre_completo=doc["nombre_completo"],
        email=doc["email"],
        username=doc["username"],
        avatar_url=doc.get("avatar_url", "/assets/img/avatar-default.png"),
        watchlist=doc.get("watchlist", []),
    )


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dependencia reutilizable en toda la API: valida el JWT del header
    Authorization y devuelve el documento del usuario desde MongoDB.
    Cualquier router protegido (watchlist, historial, etc.) la importa.
    """
    token = credenciales.credentials
    try:
        payload = decodificar_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido o expirado"
        )

    db = get_db()
    usuario = db.usuarios.find_one({"_id": ObjectId(payload["sub"])})
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    return usuario


@router.post("/registro", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def registrar(datos: RegistroRequest):
    """Crea una cuenta nueva y devuelve un token de sesion inmediato."""
    db = get_db()

    if db.usuarios.find_one({"$or": [{"email": datos.email}, {"username": datos.username}]}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email o el nombre de usuario ya esta registrado",
        )

    documento = {
        "nombre_completo": datos.nombre_completo,
        "email": datos.email,
        "username": datos.username,
        "password_hash": hash_password(datos.password),
        "avatar_url": "/assets/img/avatar-default.png",
        "watchlist": [],
        "fecha_registro": datetime.now(timezone.utc),
        "ultimo_login": datetime.now(timezone.utc),
    }
    resultado = db.usuarios.insert_one(documento)
    documento["_id"] = resultado.inserted_id

    token = generar_token(str(documento["_id"]), documento["username"])
    return LoginResponse(token=token, usuario=_usuario_a_response(documento))


@router.post("/login", response_model=LoginResponse)
def iniciar_sesion(datos: LoginRequest):
    """Valida credenciales y devuelve un token JWT nuevo."""
    db = get_db()
    usuario = db.usuarios.find_one({"username": datos.username})

    if usuario is None or not verificar_password(datos.password, usuario["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
        )

    db.usuarios.update_one(
        {"_id": usuario["_id"]}, {"$set": {"ultimo_login": datetime.now(timezone.utc)}}
    )

    token = generar_token(str(usuario["_id"]), usuario["username"])
    return LoginResponse(token=token, usuario=_usuario_a_response(usuario))


@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual)):
    """Devuelve los datos del usuario autenticado (usado para validar sesion activa)."""
    return _usuario_a_response(usuario)


@router.put("/perfil", response_model=UsuarioResponse)
def actualizar_perfil(
    datos: ActualizarPerfilRequest, usuario: dict = Depends(obtener_usuario_actual)
):
    """Actualiza nombre y/o avatar del usuario autenticado."""
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if cambios:
        db = get_db()
        db.usuarios.update_one({"_id": usuario["_id"]}, {"$set": cambios})
        usuario.update(cambios)
    return _usuario_a_response(usuario)


@router.put("/watchlist", response_model=UsuarioResponse)
def modificar_watchlist(
    datos: WatchlistRequest, usuario: dict = Depends(obtener_usuario_actual)
):
    """Agrega o quita un ticker de la watchlist del usuario autenticado."""
    db = get_db()
    operacion = "$addToSet" if datos.accion == "agregar" else "$pull"
    db.usuarios.update_one({"_id": usuario["_id"]}, {operacion: {"watchlist": datos.ticker}})

    usuario_actualizado = db.usuarios.find_one({"_id": usuario["_id"]})
    return _usuario_a_response(usuario_actualizado)
