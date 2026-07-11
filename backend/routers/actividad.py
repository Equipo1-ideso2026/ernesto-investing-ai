"""
Endpoint de actividad reciente: feed de las ultimas senales generadas
por cualquier modelo/ticker, usado en el widget del Dashboard. Lee
directamente de `predicciones` ordenado por fecha_generacion.
"""
from fastapi import APIRouter, Query

from backend.database import get_db

router = APIRouter(prefix="/api", tags=["actividad"])


@router.get("/actividad-reciente")
def obtener_actividad_reciente(limite: int = Query(20, ge=1, le=100)):
    """Ultimas `limite` predicciones generadas, de cualquier ticker o modelo."""
    db = get_db()
    cursor = db.predicciones.find({}, {"_id": 0}).sort("fecha_generacion", -1).limit(limite)
    return {"actividad": list(cursor)}
