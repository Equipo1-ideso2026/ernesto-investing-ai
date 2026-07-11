"""Pagina del Regresor LSTM: pronostico de precios con banda de confianza."""
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="Regresor LSTM — Ernesto Investing AI", page_icon="📉", layout="wide")
st.title("📉 Regresor LSTM — Pronóstico de precios")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

col1, col2 = st.columns([1, 1])
ticker = col1.selectbox("Ticker", ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"], index=3)
horizonte = col2.selectbox("Horizonte (días)", [7, 14, 30, 60], index=2)

try:
    mercado = get(f"/api/mercado/{ticker}", params={"periodo": 120})
    pronostico = get(f"/api/predicciones/lstm-regressor/{ticker}", params={"horizonte": horizonte})
    comparador = get(f"/api/metricas/comparador/{ticker}")["modelos"]
except RuntimeError as error:
    st.error(str(error))
    st.stop()

puntos = mercado["datos"]
if not puntos:
    st.info("No hay datos de mercado para este ticker.")
    st.stop()

fechas = [p["fecha"] for p in puntos]
precios = [p["close"] for p in puntos]

# Fecha futura real (no un texto concatenado), para que el eje X ubique
# el pronostico en su posicion correcta segun el horizonte elegido.
fecha_futura = (datetime.fromisoformat(fechas[-1]) + timedelta(days=horizonte)).strftime("%Y-%m-%d")

figura = go.Figure()
figura.add_trace(go.Scatter(x=fechas, y=precios, name="Precio real", line=dict(color="#8da3b0", width=2)))
figura.add_trace(go.Scatter(
    x=[fechas[-1], fecha_futura], y=[precios[-1], pronostico["precio_predicho"]],
    name=f"Pronóstico ({horizonte}d)", line=dict(color="#b5713c", width=2, dash="dash"), mode="lines+markers",
    marker=dict(size=9),
))
figura.add_trace(go.Scatter(
    x=[fechas[-1], fecha_futura], y=[precios[-1], pronostico["banda_confianza"]["superior"]],
    line=dict(width=0), showlegend=False, hoverinfo="skip",
))
figura.add_trace(go.Scatter(
    x=[fechas[-1], fecha_futura], y=[precios[-1], pronostico["banda_confianza"]["inferior"]],
    line=dict(width=0), fill="tonexty", fillcolor="rgba(181,113,60,0.15)",
    name="Banda de confianza (95%)",
))
figura.update_layout(template="plotly_dark", height=440, margin=dict(t=20, b=20), yaxis_title="Precio (USD)")
st.plotly_chart(figura, use_container_width=True)

st.info(
    f"Pronóstico a {horizonte} días: **${pronostico['precio_predicho']:.2f}** "
    f"(banda de confianza: ${pronostico['banda_confianza']['inferior']:.2f} — ${pronostico['banda_confianza']['superior']:.2f})"
)

metrica_regresor = next((m for m in comparador if m["modelo"] == "lstm_regressor"), None)
if metrica_regresor:
    m = metrica_regresor["metricas"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("RMSE (USD)", f"${m['rmse']:.3f}" if m.get("rmse") is not None else "—")
    c2.metric("RMSE (%)", f"{m['rmse_pct']:.2f}%" if m.get("rmse_pct") is not None else "—")
    c3.metric("MAE", f"{m['mae']:.3f}" if m.get("mae") is not None else "—")
    c4.metric("R²", f"{m['r2']:.3f}" if m.get("r2") is not None else "—")
