"""
Punto de entrada del backend de Ernesto Investing AI.
Monta todos los routers y configura CORS para que el frontend
(HTML estatico en GitHub Pages o la app de Streamlit) pueda
consumir la API sin restricciones de origen.

Todos los routers leen exclusivamente de MongoDB (poblada por los
notebooks de Colab); ninguno recalcula ni entrena modelos en tiempo
de peticion, por eso la API responde en milisegundos.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import crear_indices
from backend.auth.routes import router as auth_router
from backend.routers.mercado import router as mercado_router
from backend.routers.predicciones import router as predicciones_router
from backend.routers.metricas import router as metricas_router
from backend.routers.ranking import router as ranking_router
from backend.routers.actividad import router as actividad_router
from backend.routers.historial import router as historial_router
from backend.routers.sentimiento import router as sentimiento_router
from backend.routers.salud import router as salud_router

app = FastAPI(
    title="Ernesto Investing AI - API",
    description="API REST del sistema de apoyo a decisiones de inversion bursatil con IA.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def iniciar_indices() -> None:
    """Crea los indices de MongoDB al arrancar el servidor (idempotente)."""
    crear_indices()


app.include_router(auth_router)
app.include_router(mercado_router)
app.include_router(predicciones_router)
app.include_router(metricas_router)
app.include_router(ranking_router)
app.include_router(actividad_router)
app.include_router(historial_router)
app.include_router(sentimiento_router)
app.include_router(salud_router)


@app.get("/")
def raiz():
    """Endpoint raiz simple para verificar que el servidor esta activo."""
    return {"sistema": "Ernesto Investing AI", "estado": "activo", "documentacion": "/docs"}
