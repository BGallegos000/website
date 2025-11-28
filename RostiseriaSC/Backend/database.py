import motor.motor_asyncio
from typing import Optional

MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "rostiseria_db"

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None

async def init_db():
    global _client, _db
    try:
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        _db = _client[DB_NAME]
        await _client.server_info()
        print(f"✅ Conectado a MongoDB: {DB_NAME}")
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")

async def close_db():
    global _client
    if _client:
        _client.close()
        print("🔻 Conexión cerrada.")

def get_collection(name: str):
    if _db is None:
        raise RuntimeError("BD no inicializada.")
    return _db[name]