"""
Conexion a MongoDB Atlas para el backend de Ernesto Investing AI.
Se usa pymongo de forma sincrona (consistente con los notebooks del curso,
que tambien usan pymongo sincrono desde Google Colab).
"""
from pymongo import MongoClient
from pymongo.database import Database

from backend.config import settings

_client: MongoClient | None = None
_db: Database | None = None


def get_db() -> Database:
    """
    Devuelve la instancia de la base de datos, creando la conexion
    una sola vez (patron singleton) para reutilizarla en toda la app.
    """
    global _client, _db
    if _db is None:
        if not settings.MONGO_URI:
            raise RuntimeError(
                "MONGO_URI no esta configurada. Define la variable de entorno "
                "o el Secret de Colab antes de iniciar el servidor."
            )
        _client = MongoClient(settings.MONGO_URI)
        _db = _client[settings.MONGO_DB_NAME]
    return _db


def crear_indices() -> None:
    """
    Crea los indices necesarios en cada coleccion. Se ejecuta una vez
    al iniciar el servidor. create_index es idempotente: no falla si
    el indice ya existe.
    """
    db = get_db()

    # usuarios: email y username deben ser unicos
    db.usuarios.create_index("email", unique=True)
    db.usuarios.create_index("username", unique=True)

    # precios_ohlcv: un solo documento por ticker + fecha
    db.precios_ohlcv.create_index([("ticker", 1), ("fecha", 1)], unique=True)

    # predicciones: log append-only, se consulta por ticker+modelo ordenado por fecha
    db.predicciones.create_index([("ticker", 1), ("modelo", 1), ("fecha_generacion", -1)])

    # metricas_modelos: una entrada por ticker + modelo
    db.metricas_modelos.create_index([("ticker", 1), ("modelo", 1)])

    # sentimiento_noticias: consultas por ticker ordenadas por fecha
    db.sentimiento_noticias.create_index([("ticker", 1), ("fecha", -1)])
