"""
Endpoints de predicciones: senal actual del SVC, senales de las 4
arquitecturas RNN, y pronostico de precios del regresor LSTM.
Todos leen la ultima entrada guardada en la coleccion `predicciones`;
ninguno vuelve a ejecutar ni entrenar un modelo.
"""
from fastapi import APIRouter, HTTPException, Query, status

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/predicciones", tags=["predicciones"])

MODELOS_RNN_VALIDOS = ["lstm", "bilstm", "gru", "simplernn"]


def _validar_ticker(ticker: str) -> str:
    ticker = ticker.upper()
    if ticker not in settings.TICKERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker no reconocido. Tickers validos: {settings.TICKERS}",
        )
    return ticker


def _ultima_prediccion(db, ticker: str, modelo: str) -> dict:
    doc = db.predicciones.find_one(
        {"ticker": ticker, "modelo": modelo},
        sort=[("fecha_generacion", -1)],
    )
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay predicciones de {modelo} para {ticker}. Ejecuta el notebook correspondiente.",
        )
    doc.pop("_id", None)
    return doc


@router.get("/svc/{ticker}")
def obtener_prediccion_svc(ticker: str):
    """Ultima senal BUY/SELL generada por el clasificador SVC."""
    ticker = _validar_ticker(ticker)
    db = get_db()
    return _ultima_prediccion(db, ticker, "svc")


@router.get("/rnn/{ticker}")
def obtener_predicciones_rnn(
    ticker: str,
    modelo: str = Query(
        None, description="lstm | bilstm | gru | simplernn. Si se omite, devuelve las 4."
    ),
):
    """Senal actual de una arquitectura RNN especifica, o de las 4 si no se indica `modelo`."""
    ticker = _validar_ticker(ticker)
    db = get_db()

    if modelo:
        if modelo not in MODELOS_RNN_VALIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Modelo no valido. Opciones: {MODELOS_RNN_VALIDOS}",
            )
        return {"ticker": ticker, "predicciones": [_ultima_prediccion(db, ticker, modelo)]}

    predicciones = []
    for m in MODELOS_RNN_VALIDOS:
        doc = db.predicciones.find_one({"ticker": ticker, "modelo": m}, sort=[("fecha_generacion", -1)])
        if doc:
            doc.pop("_id", None)
            predicciones.append(doc)

    if not predicciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay predicciones RNN para {ticker}. Ejecuta los Notebooks 03/03b.",
        )

    return {"ticker": ticker, "predicciones": predicciones}


@router.get("/lstm-regressor/{ticker}")
def obtener_pronostico_lstm(ticker: str, horizonte: int = Query(30, description="7, 14, 30 o 60 dias")):
    """Pronostico de precio del regresor LSTM para el horizonte solicitado."""
    ticker = _validar_ticker(ticker)
    if horizonte not in (7, 14, 30, 60):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El horizonte debe ser 7, 14, 30 o 60 dias",
        )

    db = get_db()
    doc = db.predicciones.find_one(
        {"ticker": ticker, "modelo": "lstm_regressor", "horizonte_dias": horizonte},
        sort=[("fecha_generacion", -1)],
    )
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay pronostico para {ticker} a {horizonte} dias. Ejecuta el Notebook 04.",
        )
    doc.pop("_id", None)
    return doc
