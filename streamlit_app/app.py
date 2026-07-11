"""
Ernesto Investing AI — App Streamlit (version 100% Python).
Punto de entrada: configura la URL de la API (compartida en
st.session_state para todas las paginas) y muestra un resumen general.
La logica de negocio vive unicamente en el backend FastAPI; esta app
solo consume los mismos endpoints que el frontend HTML.
"""
import streamlit as st

from utils.api_client import get, api_configurada

st.set_page_config(page_title="Ernesto Investing AI", page_icon="📈", layout="wide")

if "api_url" not in st.session_state:
    st.session_state["api_url"] = ""

with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    nueva_url = st.text_input(
        "URL de la API",
        value=st.session_state["api_url"],
        placeholder="https://xxxx.ngrok-free.app",
        help="La URL cambia cada vez que reinicias el Notebook 06 en Colab.",
    )
    if nueva_url != st.session_state["api_url"]:
        st.session_state["api_url"] = nueva_url.rstrip("/")

    if api_configurada():
        try:
            salud = get("/api/salud")
            st.success("Conectado a la API")
            st.caption(f"MongoDB: {salud.get('mongodb', 'desconocido')}")
        except RuntimeError as error:
            st.error(str(error))
    else:
        st.warning("Configura la URL de la API para comenzar.")

st.title("📈 Ernesto Investing AI")
st.caption("Sistema de apoyo a decisiones de inversión bursátil con IA — versión Streamlit")

st.markdown("""
Esta es la version alternativa **100% Python** del sistema, pensada para
desplegarse en **Streamlit Community Cloud** con una URL permanente que
no depende de que Google Colab este activo.

Usa el menu de la izquierda para navegar entre los modulos:
- **Mercado** — precios OHLCV e indicadores tecnicos reales.
- **Comparador de Modelos** — metricas de los 5 clasificadores + regresor.
- **Ranking** — consenso de senales de los 5 tickers.
- **Clasificador SVC**, **Clasificadores RNN**, **Regresor LSTM** — detalle de cada modelo.
""")

if api_configurada():
    st.markdown("### Resumen rápido")
    try:
        salud = get("/api/salud")
        columnas = st.columns(5)
        colecciones = salud.get("colecciones", {})
        etiquetas = {
            "precios_ohlcv": "Días de precios",
            "predicciones": "Predicciones",
            "metricas_modelos": "Modelos entrenados",
            "sentimiento_noticias": "Noticias analizadas",
            "usuarios": "Usuarios registrados",
        }
        for columna, (clave, etiqueta) in zip(columnas, etiquetas.items()):
            columna.metric(etiqueta, colecciones.get(clave, "—"))
    except RuntimeError as error:
        st.error(str(error))
else:
    st.info("Ingresa la URL de la API en la barra lateral para ver datos en tiempo real.")
