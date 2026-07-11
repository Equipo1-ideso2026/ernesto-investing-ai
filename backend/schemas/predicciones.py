"""
Esquemas Pydantic para las predicciones de los modelos de clasificacion
(SVC, LSTM, BiLSTM, GRU, SimpleRNN) y del regresor LSTM.
"""
from datetime import datetime

from pydantic import BaseModel


class BandaConfianza(BaseModel):
    inferior: float | None = None
    superior: float | None = None


class PrediccionClasificacion(BaseModel):
    ticker: str
    modelo: str
    fecha_generacion: datetime
    senal: str
    probabilidad: float


class PrediccionRegresion(BaseModel):
    ticker: str
    modelo: str
    fecha_generacion: datetime
    precio_predicho: float
    horizonte_dias: int
    banda_confianza: BandaConfianza


class RnnComparacionResponse(BaseModel):
    ticker: str
    predicciones: list[PrediccionClasificacion]
