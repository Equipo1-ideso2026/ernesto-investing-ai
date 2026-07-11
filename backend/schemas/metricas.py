"""
Esquemas Pydantic para las metricas de entrenamiento, el comparador
de modelos por ticker y la analitica global agregada.
"""
from datetime import datetime

from pydantic import BaseModel


class MetricasValores(BaseModel):
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1: float | None = None
    rmse: float | None = None
    mae: float | None = None
    r2: float | None = None
    rmse_pct: float | None = None


class EpocaEntrenamiento(BaseModel):
    epoca: int
    loss: float
    accuracy: float
    val_loss: float
    val_accuracy: float


class MetricaModelo(BaseModel):
    modelo: str
    fecha_entrenamiento: datetime
    metricas: MetricasValores
    hiperparametros: dict
    matriz_confusion: list[list[int]] | None = None
    historial_entrenamiento: list[EpocaEntrenamiento] | None = None


class ComparadorResponse(BaseModel):
    ticker: str
    modelos: list[MetricaModelo]


class GlobalPorModelo(BaseModel):
    modelo: str
    tickers_evaluados: int
    accuracy_promedio: float | None = None
    f1_promedio: float | None = None
    rmse_promedio: float | None = None


class GlobalResponse(BaseModel):
    resultados: list[GlobalPorModelo]
