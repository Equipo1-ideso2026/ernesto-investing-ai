"""
Endpoint de ranking: ordena los 5 tickers del proyecto por la fuerza
de su senal consolidada, combinando los 5 modelos de clasificacion.
Lee unicamente de la coleccion `predicciones` (la ultima entrada de
cada modelo por ticker); no recalcula nada.
"""
from fastapi import APIRouter

from backend.config import settings
from backend.database import get_db

router = APIRouter(prefix="/api/ranking", tags=["ranking"])

MODELOS_CLASIFICACION = settings.MODELOS_CLASIFICACION  # ["svc", "lstm", "bilstm", "gru", "simplernn"]


@router.get("")
def obtener_ranking():
    """
    Para cada ticker, promedia la probabilidad firmada (+prob si BUY,
    -prob si SELL) de los 5 clasificadores. El resultado es la
    "fuerza de senal": valores cercanos a +1 indican consenso fuerte
    de compra, cercanos a -1 consenso fuerte de venta.
    """
    db = get_db()
    ranking = []

    for ticker in settings.TICKERS:
        senales_por_modelo = {}
        valores_firmados = []

        for modelo in MODELOS_CLASIFICACION:
            doc = db.predicciones.find_one(
                {"ticker": ticker, "modelo": modelo}, sort=[("fecha_generacion", -1)]
            )
            if doc:
                senales_por_modelo[modelo] = doc["senal"]
                signo = 1 if doc["senal"] == "BUY" else -1
                valores_firmados.append(signo * doc["probabilidad"])

        if not valores_firmados:
            continue

        fuerza_senal = round(sum(valores_firmados) / len(valores_firmados), 4)
        votos_buy = sum(1 for s in senales_por_modelo.values() if s == "BUY")
        votos_sell = len(senales_por_modelo) - votos_buy
        senal_consenso = "BUY" if votos_buy >= votos_sell else "SELL"

        ranking.append({
            "ticker": ticker,
            "senal_consenso": senal_consenso,
            "fuerza_senal": fuerza_senal,
            "modelos": senales_por_modelo,
        })

    ranking.sort(key=lambda item: item["fuerza_senal"], reverse=True)
    return {"ranking": ranking}
