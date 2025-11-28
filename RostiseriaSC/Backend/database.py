import os
import motor.motor_asyncio
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "rostiseria_db")

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None

async def init_db():
    global _client, _db
    try:
        # Atlas fuerza la conexión segura automáticamente
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        _db = _client[DB_NAME]
        
        # Verificar conexión
        await _client.server_info()
        print(f"✅ Base de Datos Conectada: {DB_NAME} (Atlas Cloud)")
    except Exception as e:
        print(f"❌ Error de Conexión: {e}")

async def close_db():
    global _client
    if _client:
        _client.close()
        print("🔻 Conexión cerrada.")

def get_collection(name: str):
    if _db is None:
        raise RuntimeError("BD no inicializada.")
    return _db[name]