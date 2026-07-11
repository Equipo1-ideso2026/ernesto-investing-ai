"""
Cliente HTTP para que la app de Streamlit consuma la misma API REST
que el frontend HTML. Ninguna logica de negocio vive aqui: solo
llamadas a los endpoints ya definidos en backend/routers/.
"""
import requests
import streamlit as st


def _base_url() -> str:
    return st.session_state.get("api_url", "").rstrip("/")


def _headers() -> dict:
    encabezados = {"ngrok-skip-browser-warning": "true"}
    token = st.session_state.get("token")
    if token:
        encabezados["Authorization"] = f"Bearer {token}"
    return encabezados


def api_configurada() -> bool:
    return bool(_base_url())


def get(ruta: str, params: dict | None = None) -> dict:
    """GET generico. Lanza RuntimeError con mensaje legible si algo falla."""
    if not api_configurada():
        raise RuntimeError("Configura la URL de la API en la barra lateral antes de continuar.")
    try:
        respuesta = requests.get(f"{_base_url()}{ruta}", headers=_headers(), params=params, timeout=15)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"No se pudo conectar con la API: {error}") from error

    if respuesta.status_code == 401:
        st.session_state.pop("token", None)
        st.session_state.pop("usuario", None)
        raise RuntimeError("Tu sesion expiro. Inicia sesion nuevamente.")

    if not respuesta.ok:
        detalle = respuesta.json().get("detail", respuesta.text) if respuesta.content else respuesta.text
        raise RuntimeError(f"Error {respuesta.status_code}: {detalle}")

    return respuesta.json()


def post(ruta: str, cuerpo: dict) -> dict:
    if not api_configurada():
        raise RuntimeError("Configura la URL de la API en la barra lateral antes de continuar.")
    try:
        respuesta = requests.post(f"{_base_url()}{ruta}", headers=_headers(), json=cuerpo, timeout=15)
    except requests.exceptions.RequestException as error:
        raise RuntimeError(f"No se pudo conectar con la API: {error}") from error

    if not respuesta.ok:
        detalle = respuesta.json().get("detail", respuesta.text) if respuesta.content else respuesta.text
        raise RuntimeError(f"Error {respuesta.status_code}: {detalle}")

    return respuesta.json()


def put(ruta: str, cuerpo: dict) -> dict:
    if not api_configurada():
        raise RuntimeError("Configura la URL de la API en la barra lateral antes de continuar.")
    respuesta = requests.put(f"{_base_url()}{ruta}", headers=_headers(), json=cuerpo, timeout=15)
    if not respuesta.ok:
        detalle = respuesta.json().get("detail", respuesta.text) if respuesta.content else respuesta.text
        raise RuntimeError(f"Error {respuesta.status_code}: {detalle}")
    return respuesta.json()
