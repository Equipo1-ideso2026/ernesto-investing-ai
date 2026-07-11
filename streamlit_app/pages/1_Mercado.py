"""Pagina de Mercado: OHLCV real + indicadores tecnicos, usando Plotly."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="Mercado — Ernesto Investing AI", page_icon="📊", layout="wide")
st.title("📊 Mercado")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

col1, col2 = st.columns([1, 1])
ticker = col1.selectbox("Ticker", ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"], index=3)
periodo = col2.selectbox("Periodo (días)", [30, 90, 180, 365], index=1)

try:
    datos = get(f"/api/mercado/{ticker}", params={"periodo": periodo})
except RuntimeError as error:
    st.error(str(error))
    st.stop()

puntos = datos["datos"]
if not puntos:
    st.info("No hay datos de mercado para este ticker todavía. Ejecuta el Notebook 01.")
    st.stop()

fechas = [p["fecha"] for p in puntos]

figura = go.Figure()
figura.add_trace(go.Candlestick(
    x=fechas,
    open=[p["open"] for p in puntos], high=[p["high"] for p in puntos],
    low=[p["low"] for p in puntos], close=[p["close"] for p in puntos],
    name=ticker, increasing_line_color="#3f9463", decreasing_line_color="#c25b52",
))
figura.add_trace(go.Scatter(x=fechas, y=[p["indicadores"]["sma_20"] for p in puntos], name="SMA 20", line=dict(color="#8da3b0", width=1.3)))
figura.add_trace(go.Scatter(x=fechas, y=[p["indicadores"]["sma_50"] for p in puntos], name="SMA 50", line=dict(color="#d9925f", width=1.3)))
figura.update_layout(template="plotly_dark", height=480, margin=dict(t=20, b=20), xaxis_rangeslider_visible=False)

st.plotly_chart(figura, use_container_width=True)

ultimo = puntos[-1]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Cierre", f"${ultimo['close']:.2f}")
c2.metric("RSI (14)", f"{ultimo['indicadores']['rsi_14']:.1f}" if ultimo["indicadores"]["rsi_14"] else "—")
c3.metric("MACD", f"{ultimo['indicadores']['macd']:.3f}" if ultimo["indicadores"]["macd"] else "—")
c4.metric("SMA 20", f"${ultimo['indicadores']['sma_20']:.2f}" if ultimo["indicadores"]["sma_20"] else "—")
c5.metric("SMA 50", f"${ultimo['indicadores']['sma_50']:.2f}" if ultimo["indicadores"]["sma_50"] else "—")
