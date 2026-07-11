"""
Esquemas Pydantic del modulo de mercado: datos OHLCV, correlacion
entre tickers y comparacion multi-ticker.
"""
from pydantic import BaseModel


class IndicadoresTecnicos(BaseModel):
    sma_20: float | None = None
    sma_50: float | None = None
    ema_12: float | None = None
    ema_26: float | None = None
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    macd_hist: float | None = None
    bb_upper: float | None = None
    bb_lower: float | None = None


class PuntoOhlcv(BaseModel):
    fecha: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    volume: float | None = None
    indicadores: IndicadoresTecnicos


class MercadoResponse(BaseModel):
    ticker: str
    total_dias: int
    datos: list[PuntoOhlcv]


class CorrelacionResponse(BaseModel):
    tickers: list[str]
    matriz: list[list[float | None]]


class SerieTicker(BaseModel):
    ticker: str
    datos: list[PuntoOhlcv]


class ComparacionResponse(BaseModel):
    tickers: list[str]
    series: list[SerieTicker]
