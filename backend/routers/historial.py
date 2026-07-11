"""
Endpoint de historial: predicciones pasadas de un ticker, filtradas
por rango de fechas. Reutiliza la coleccion `predicciones` (que ya
es un log append-only) en vez de crear una coleccion nueva.
"""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, status

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/historial", tags=["historial"])


@router.get("/{ticker}")
def obtener_historial(
    ticker: str,
    desde: str | None = Query(None, description="Fecha ISO, ej: 2026-06-01"),
    hasta: str | None = Query(None, description="Fecha ISO, ej: 2026-07-01"),
):
    """Predicciones de un ticker entre `desde` y `hasta` (por defecto, ultimos 30 dias)."""
    ticker = ticker.upper()
    if ticker not in settings.TICKERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker no reconocido. Tickers validos: {settings.TICKERS}",
        )

    ahora = datetime.now(timezone.utc)
    fecha_hasta = datetime.fromisoformat(hasta) if hasta else ahora
    fecha_desde = datetime.fromisoformat(desde) if desde else ahora - timedelta(days=30)

    if hasta:
        # Sin esto, "hasta" se interpreta como la medianoche de ese dia
        # (00:00:00), excluyendo por error todo lo ocurrido durante el
        # resto de ese mismo dia. Se extiende al ultimo instante del dia.
        fecha_hasta = fecha_hasta.replace(hour=23, minute=59, second=59, microsecond=999999)

    db = get_db()
    cursor = (
        db.predicciones.find(
            {
                "ticker": ticker,
                "fecha_generacion": {"$gte": fecha_desde, "$lte": fecha_hasta},
            },
            {"_id": 0, "ticker": 0},
        )
        .sort("fecha_generacion", -1)
    )
    resultados = list(cursor)

    return {
        "ticker": ticker,
        "desde": fecha_desde.date().isoformat(),
        "hasta": fecha_hasta.date().isoformat(),
        "total": len(resultados),
        "resultados": resultados,
    }
