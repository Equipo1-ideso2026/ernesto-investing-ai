"""
Endpoints de datos de mercado: serie OHLCV de un ticker, matriz de
correlacion entre los 5 tickers, y comparacion de varios tickers a la vez.

Nota de diseno: la correlacion y la comparacion se calculan al vuelo
con pandas sobre los precios ya guardados en precios_ohlcv (nunca se
vuelve a descargar de yfinance ni se re-entrena ningun modelo). Es una
agregacion ligera, no un recalculo de IA, por eso sigue respetando el
principio de que la API "solo lee" del backend de datos.
"""
from fastapi import APIRouter, HTTPException, Query, status
import pandas as pd

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/mercado", tags=["mercado"])


def _documento_a_punto(doc: dict) -> dict:
    """Proyecta un documento de precios_ohlcv al formato de respuesta publico."""
    return {
        "fecha": doc["fecha"],
        "open": doc.get("open"),
        "high": doc.get("high"),
        "low": doc.get("low"),
        "close": doc.get("close"),
        "volume": doc.get("volume"),
        "indicadores": doc.get("indicadores", {}),
    }


@router.get("/correlacion")
def obtener_correlacion(periodo: int = Query(180, ge=30, le=730)):
    """
    Matriz de correlacion de los retornos diarios entre los 5 tickers
    del proyecto, calculada sobre los ultimos `periodo` dias disponibles.
    """
    db = get_db()
    series = {}

    for ticker in settings.TICKERS:
        cursor = (
            db.precios_ohlcv.find({"ticker": ticker}, {"fecha": 1, "close": 1})
            .sort("fecha", -1)
            .limit(periodo)
        )
        documentos = list(cursor)[::-1]
        if documentos:
            serie = pd.Series(
                [d["close"] for d in documentos],
                index=[d["fecha"] for d in documentos],
                name=ticker,
            )
            series[ticker] = serie

    if len(series) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay suficientes datos para calcular la correlacion",
        )

    df = pd.DataFrame(series).pct_change().dropna(how="all")
    matriz_correlacion = df.corr().round(4)

    tickers_disponibles = list(matriz_correlacion.columns)
    matriz = [
        [None if pd.isna(v) else float(v) for v in fila]
        for fila in matriz_correlacion.values
    ]

    return {"tickers": tickers_disponibles, "matriz": matriz}


@router.get("/comparar")
def comparar_tickers(
    tickers: str = Query(..., description="Tickers separados por coma, ej: FSM,BVN"),
    periodo: int = Query(90, ge=7, le=730),
):
    """Devuelve la serie OHLCV de varios tickers a la vez, para superponer en un solo grafico."""
    lista_tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    invalidos = [t for t in lista_tickers if t not in settings.TICKERS]
    if invalidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tickers no reconocidos: {invalidos}. Validos: {settings.TICKERS}",
        )

    db = get_db()
    series = []
    for ticker in lista_tickers:
        cursor = db.precios_ohlcv.find({"ticker": ticker}).sort("fecha", -1).limit(periodo)
        documentos = list(cursor)[::-1]
        series.append({"ticker": ticker, "datos": [_documento_a_punto(d) for d in documentos]})

    return {"tickers": lista_tickers, "series": series}


@router.get("/{ticker}")
def obtener_mercado(ticker: str, periodo: int = Query(90, ge=7, le=730)):
    """Serie OHLCV + indicadores tecnicos de un ticker, ultimos `periodo` dias."""
    ticker = ticker.upper()
    if ticker not in settings.TICKERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker no reconocido. Tickers validos: {settings.TICKERS}",
        )

    db = get_db()
    cursor = db.precios_ohlcv.find({"ticker": ticker}).sort("fecha", -1).limit(periodo)
    documentos = list(cursor)[::-1]

    if not documentos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay datos de mercado para {ticker}. Ejecuta el Notebook 01 primero.",
        )

    return {
        "ticker": ticker,
        "total_dias": len(documentos),
        "datos": [_documento_a_punto(d) for d in documentos],
    }
