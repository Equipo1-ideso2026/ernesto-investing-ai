"""Pagina de Comparador de Modelos: tabla de metricas + radar de F1-score."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="Comparador — Ernesto Investing AI", page_icon="🧮", layout="wide")
st.title("🧮 Comparador de modelos")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

NOMBRES = {"svc": "SVC", "lstm": "LSTM", "bilstm": "BiLSTM", "gru": "GRU", "simplernn": "SimpleRNN", "lstm_regressor": "Regresor LSTM"}

ticker = st.selectbox("Ticker", ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"], index=3)

try:
    respuesta = get(f"/api/metricas/comparador/{ticker}")
except RuntimeError as error:
    st.error(str(error))
    st.stop()

modelos = respuesta["modelos"]
if not modelos:
    st.info("No hay métricas entrenadas para este ticker. Ejecuta los notebooks de modelos.")
    st.stop()

tabla = pd.DataFrame([{
    "Modelo": NOMBRES.get(m["modelo"], m["modelo"]),
    "Accuracy": m["metricas"].get("accuracy"),
    "Precision": m["metricas"].get("precision"),
    "Recall": m["metricas"].get("recall"),
    "F1": m["metricas"].get("f1"),
    "RMSE": m["metricas"].get("rmse"),
} for m in modelos])

st.dataframe(tabla, use_container_width=True, hide_index=True)

clasificadores = [m for m in modelos if m["metricas"].get("f1") is not None]
if clasificadores:
    etiquetas = [NOMBRES[m["modelo"]] for m in clasificadores] + [NOMBRES[clasificadores[0]["modelo"]]]
    valores = [m["metricas"]["f1"] for m in clasificadores] + [clasificadores[0]["metricas"]["f1"]]

    figura = go.Figure(go.Scatterpolar(r=valores, theta=etiquetas, fill="toself", line=dict(color="#b5713c")))
    figura.update_layout(template="plotly_dark", height=420, polar=dict(radialaxis=dict(range=[0, 1])), showlegend=False)
    st.plotly_chart(figura, use_container_width=True)
