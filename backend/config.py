"""
Configuracion centralizada del backend. Todas las variables sensibles
se leen de variables de entorno (o Secrets de Colab), nunca hardcodeadas.
"""
import os
from datetime import timedelta


class Settings:
    # MongoDB
    MONGO_URI: str = os.environ.get("MONGO_URI", "")
    MONGO_DB_NAME: str = os.environ.get("MONGO_DB_NAME", "ernesto_investing_ai")

    # JWT
    JWT_SECRET: str = os.environ.get("JWT_SECRET", "cambiar-este-secreto-en-produccion")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: timedelta = timedelta(days=7)

    # Tickers del proyecto (fuente unica de verdad para todo el backend)
    TICKERS: list[str] = ["FSM", "VOLCABC1.LM", "ABX.TO", "BVN", "BHP"]

    # Modelos de clasificacion y regresion soportados
    MODELOS_CLASIFICACION: list[str] = ["svc", "lstm", "bilstm", "gru", "simplernn"]
    MODELO_REGRESION: str = "lstm_regressor"

    # CORS (simplificado para proyecto academico; restringir en produccion real)
    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
