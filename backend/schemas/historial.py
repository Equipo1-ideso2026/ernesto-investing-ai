"""
Esquemas Pydantic para el historial de predicciones filtrado por
fecha, y para el modulo de sentimiento de noticias (NLP/VADER).
"""
from datetime import datetime

from pydantic import BaseModel


class HistorialItem(BaseModel):
    modelo: str
    tipo: str
    fecha_generacion: datetime
    senal: str | None = None
    probabilidad: float | None = None
    precio_predicho: float | None = None
    horizonte_dias: int | None = None


class HistorialResponse(BaseModel):
    ticker: str
    desde: str
    hasta: str
    total: int
    resultados: list[HistorialItem]


class NoticiaSentimiento(BaseModel):
    titular: str
    fuente: str
    fecha: datetime
    compound: float
    clasificacion: str


class SentimientoResponse(BaseModel):
    ticker: str
    promedio_compound: float
    conteo: dict[str, int]
    noticias: list[NoticiaSentimiento]
