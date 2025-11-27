# database.py
import motor.motor_asyncio
from typing import Optional

# Configuración de conexión local
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "rostiseria_db"

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None

async def init_db():
    """Inicia la conexión a MongoDB al arrancar la app."""
    global _client, _db
    try:
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        _db = _client[DB_NAME]
        # Verificar conexión con un comando simple
        await _client.server_info()
        print(f"✅ Conectado exitosamente a MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")

async def close_db():
    """Cierra la conexión al apagar la app."""
    global _client
    if _client:
        _client.close()
        print("🔻 Conexión a MongoDB cerrada.")

def get_collection(name: str):
    """Obtiene una colección específica de la base de datos."""
    if _db is None:
        raise RuntimeError("La base de datos no está inicializada.")
    return _db[name]