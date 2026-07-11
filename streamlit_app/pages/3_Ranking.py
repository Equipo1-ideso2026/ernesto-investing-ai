"""Pagina de Ranking: los 5 tickers ordenados por fuerza de senal consolidada."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="Ranking — Ernesto Investing AI", page_icon="🏆", layout="wide")
st.title("🏆 Ranking de señales")
st.caption("Los 5 tickers ordenados por consenso de los 5 modelos de clasificación (SVC + 4 RNNs).")

if not api_configurada():
    st.warning("Configura la URL de la API en la página principal (barra lateral).")
    st.stop()

try:
    respuesta = get("/api/ranking")
except RuntimeError as error:
    st.error(str(error))
    st.stop()

ranking = respuesta["ranking"]
if not ranking:
    st.info("Aún no hay predicciones. Ejecuta los notebooks de modelos.")
    st.stop()

for indice, item in enumerate(ranking, start=1):
    columnas = st.columns([0.5, 1.5, 3, 1.5])
    columnas[0].markdown(f"**#{indice}**")
    columnas[1].markdown(f"**{item['ticker']}**")

    modelos_texto = " · ".join(f"{m.upper()}: {s}" for m, s in item["modelos"].items())
    columnas[2].caption(modelos_texto)

    if item["senal_consenso"] == "BUY":
        columnas[3].success(f"BUY · {item['fuerza_senal']:.2f}")
    else:
        columnas[3].error(f"SELL · {item['fuerza_senal']:.2f}")

    st.divider()
