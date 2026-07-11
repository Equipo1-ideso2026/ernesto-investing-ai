"""
Endpoints de metricas: comparador de los 5 clasificadores (+ regresor)
para un ticker especifico, y analitica global agregada por tipo de
modelo a traves de los 5 tickers. Ambos leen unicamente de la
coleccion metricas_modelos, poblada por los notebooks de entrenamiento.
"""
from fastapi import APIRouter, HTTPException, status

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/metricas", tags=["metricas"])

TODOS_LOS_MODELOS = settings.MODELOS_CLASIFICACION + [settings.MODELO_REGRESION]


@router.get("/comparador/{ticker}")
def comparar_modelos(ticker: str):
    """Metricas de los 5 clasificadores + el regresor para un ticker, en un solo llamado."""
    ticker = ticker.upper()
    if ticker not in settings.TICKERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker no reconocido. Tickers validos: {settings.TICKERS}",
        )

    db = get_db()
    modelos = []
    for modelo in TODOS_LOS_MODELOS:
        doc = db.metricas_modelos.find_one({"ticker": ticker, "modelo": modelo})
        if doc:
            doc.pop("_id", None)
            modelos.append(doc)

    if not modelos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay metricas entrenadas para {ticker}. Ejecuta los notebooks de modelos.",
        )

    return {"ticker": ticker, "modelos": modelos}


@router.get("/global")
def analitica_global():
    """
    Promedios de accuracy/F1 (clasificadores) o RMSE (regresor) de cada
    tipo de modelo, agregando los 5 tickers. Util para el modulo de
    Analitica Global del frontend.
    """
    db = get_db()
    resultados = []

    for modelo in TODOS_LOS_MODELOS:
        documentos = list(db.metricas_modelos.find({"modelo": modelo}))
        if not documentos:
            continue

        accuracies = [d["metricas"]["accuracy"] for d in documentos if d["metricas"].get("accuracy") is not None]
        f1s = [d["metricas"]["f1"] for d in documentos if d["metricas"].get("f1") is not None]
        rmses = [d["metricas"]["rmse"] for d in documentos if d["metricas"].get("rmse") is not None]

        resultados.append({
            "modelo": modelo,
            "tickers_evaluados": len(documentos),
            "accuracy_promedio": round(sum(accuracies) / len(accuracies), 4) if accuracies else None,
            "f1_promedio": round(sum(f1s) / len(f1s), 4) if f1s else None,
            "rmse_promedio": round(sum(rmses) / len(rmses), 4) if rmses else None,
        })

    return {"resultados": resultados}
