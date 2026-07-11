"""Pagina del Clasificador SVC: senal actual, metricas y matriz de confusion."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="SVC — Ernesto Investing AI", page_icon="🎯", layout="wide")
st.title("🎯 Clasificador SVC")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

ticker = st.selectbox("Ticker", ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"], index=3)

try:
    prediccion = get(f"/api/predicciones/svc/{ticker}")
    comparador = get(f"/api/metricas/comparador/{ticker}")
except RuntimeError as error:
    st.error(str(error))
    st.stop()

metrica_svc = next((m for m in comparador["modelos"] if m["modelo"] == "svc"), None)

col_senal, col_metricas = st.columns([1, 2])
with col_senal:
    if prediccion["senal"] == "BUY":
        st.success(f"### {prediccion['senal']}")
    else:
        st.error(f"### {prediccion['senal']}")
    st.metric("Confianza del modelo", f"{prediccion['probabilidad'] * 100:.1f}%")

if metrica_svc:
    with col_metricas:
        m = metrica_svc["metricas"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{m['accuracy'] * 100:.1f}%")
        c2.metric("Precision", f"{m['precision'] * 100:.1f}%")
        c3.metric("Recall", f"{m['recall'] * 100:.1f}%")
        c4.metric("F1-score", f"{m['f1'] * 100:.1f}%")

    st.markdown("**Hiperparámetros (GridSearchCV):** " + ", ".join(f"`{k}={v}`" for k, v in metrica_svc["hiperparametros"].items()))

    if metrica_svc.get("matriz_confusion"):
        matriz = metrica_svc["matriz_confusion"]
        figura = go.Figure(go.Heatmap(
            z=matriz, x=["Predicho SELL", "Predicho BUY"], y=["Real SELL", "Real BUY"],
            colorscale=[[0, "#1b2029"], [1, "#b5713c"]], texttemplate="%{z}", showscale=False,
        ))
        figura.update_layout(template="plotly_dark", height=320, margin=dict(t=20, b=20))
        st.plotly_chart(figura, use_container_width=True)
