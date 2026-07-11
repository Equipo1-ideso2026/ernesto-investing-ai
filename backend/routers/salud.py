"""
Endpoint de salud: verifica que el servidor y la conexion a MongoDB
esten activos. Es el primer endpoint que se prueba tras desplegar.
"""
from fastapi import APIRouter

from backend.database import get_db

router = APIRouter(prefix="/api", tags=["salud"])


@router.get("/salud")
def verificar_salud():
    """Comprueba conexion a MongoDB y devuelve un conteo rapido por coleccion."""
    try:
        db = get_db()
        return {
            "estado": "activo",
            "mongodb": "conectado",
            "colecciones": {
                "usuarios": db.usuarios.count_documents({}),
                "precios_ohlcv": db.precios_ohlcv.count_documents({}),
                "predicciones": db.predicciones.count_documents({}),
                "metricas_modelos": db.metricas_modelos.count_documents({}),
                "sentimiento_noticias": db.sentimiento_noticias.count_documents({}),
            },
        }
    except Exception as error:
        return {"estado": "error", "mongodb": "desconectado", "detalle": str(error)}
