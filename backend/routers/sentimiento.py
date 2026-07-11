"""
Endpoint de sentimiento: noticias simuladas analizadas con VADER
para un ticker, mas un resumen agregado (promedio y conteo por
categoria). Lee de la coleccion `sentimiento_noticias`.
"""
from fastapi import APIRouter, HTTPException, status

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/sentimiento", tags=["sentimiento"])


@router.get("/{ticker}")
def obtener_sentimiento(ticker: str):
    """Noticias analizadas + resumen agregado de sentimiento para un ticker."""
    ticker = ticker.upper()
    if ticker not in settings.TICKERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker no reconocido. Tickers validos: {settings.TICKERS}",
        )

    db = get_db()
    noticias = list(
        db.sentimiento_noticias.find({"ticker": ticker}, {"_id": 0, "ticker": 0}).sort("fecha", -1)
    )

    if not noticias:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay noticias analizadas para {ticker}. Ejecuta el Notebook 05.",
        )

    promedio_compound = round(sum(n["compound"] for n in noticias) / len(noticias), 4)
    conteo = {
        "BULLISH": sum(1 for n in noticias if n["clasificacion"] == "BULLISH"),
        "BEARISH": sum(1 for n in noticias if n["clasificacion"] == "BEARISH"),
        "NEUTRAL": sum(1 for n in noticias if n["clasificacion"] == "NEUTRAL"),
    }

    return {
        "ticker": ticker,
        "promedio_compound": promedio_compound,
        "conteo": conteo,
        "noticias": noticias,
    }
