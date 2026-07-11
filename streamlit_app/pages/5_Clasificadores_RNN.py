"""Pagina de Clasificadores RNN: comparacion de LSTM, BiLSTM, GRU y SimpleRNN."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="RNNs — Ernesto Investing AI", page_icon="🧠", layout="wide")
st.title("🧠 Clasificadores RNN")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

NOMBRES = {"lstm": "LSTM", "bilstm": "BiLSTM", "gru": "GRU", "simplernn": "SimpleRNN"}

ticker = st.selectbox("Ticker", ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"], index=3)

try:
    predicciones = get(f"/api/predicciones/rnn/{ticker}")["predicciones"]
    comparador = get(f"/api/metricas/comparador/{ticker}")["modelos"]
except RuntimeError as error:
    st.error(str(error))
    st.stop()

if not predicciones:
    st.info("No hay predicciones RNN para este ticker. Ejecuta los Notebooks 03/03b.")
    st.stop()

columnas = st.columns(4)
for columna, clave in zip(columnas, NOMBRES):
    prediccion = next((p for p in predicciones if p["modelo"] == clave), None)
    metrica = next((m for m in comparador if m["modelo"] == clave), None)
    with columna:
        st.markdown(f"**{NOMBRES[clave]}**")
        if prediccion:
            if prediccion["senal"] == "BUY":
                st.success(prediccion["senal"])
            else:
                st.error(prediccion["senal"])
        if metrica:
            st.caption(f"Accuracy: {metrica['metricas']['accuracy'] * 100:.1f}%")

st.divider()

modelo_seleccionado = st.selectbox("Ver curva de entrenamiento de:", list(NOMBRES.keys()), format_func=lambda k: NOMBRES[k])
metrica_sel = next((m for m in comparador if m["modelo"] == modelo_seleccionado), None)

if metrica_sel and metrica_sel.get("historial_entrenamiento"):
    historial = metrica_sel["historial_entrenamiento"]
    figura = go.Figure()
    figura.add_trace(go.Scatter(x=[h["epoca"] for h in historial], y=[h["accuracy"] for h in historial], name="Accuracy (train)", line=dict(color="#3f9463")))
    figura.add_trace(go.Scatter(x=[h["epoca"] for h in historial], y=[h["val_accuracy"] for h in historial], name="Accuracy (val)", line=dict(color="#3f9463", dash="dot")))
    figura.update_layout(template="plotly_dark", height=380, xaxis_title="Época", yaxis_title="Accuracy", yaxis_range=[0, 1])
    st.plotly_chart(figura, use_container_width=True)
