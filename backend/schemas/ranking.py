"""
Esquemas Pydantic para el ranking de senales por ticker y el feed
de actividad reciente del sistema.
"""
from datetime import datetime

from pydantic import BaseModel


class RankingItem(BaseModel):
    ticker: str
    senal_consenso: str
    fuerza_senal: float
    modelos: dict[str, str]


class RankingResponse(BaseModel):
    ranking: list[RankingItem]


class ActividadItem(BaseModel):
    ticker: str
    modelo: str
    tipo: str
    senal: str | None = None
    precio_predicho: float | None = None
    fecha_generacion: datetime


class ActividadResponse(BaseModel):
    actividad: list[ActividadItem]
