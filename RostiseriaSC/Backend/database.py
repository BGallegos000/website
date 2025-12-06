import motor.motor_asyncio
from typing import Optional

# --- CONFIGURACIÓN DIRECTA (PARA ASEGURAR CONEXIÓN) ---
# Copia y pega esto tal cual. Apunta a tu Cluster en la Nube.
MONGODB_URI = "mongodb+srv://admin_rostiseria:Majinb00420-@cluster0.gimrz8i.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "rostiseria_db"

_client: Optional[motor.motor_asyncio.AsyncIOMotorClient] = None
_db = None

async def init_db():
    global _client, _db
    try:
        print("Intentando conectar a la Nube 🍄 (Atlas)...")
        # Creamos el cliente
        _client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        _db = _client[DB_NAME]
        
        # Prueba de fuego: Pedir información al servidor de Atlas
        info = await _client.server_info()
        print(f"CONEXIÓN EXITOSA Estás en M🍄 Atlas v{info.get('version')}")
        
    except Exception as e:
        print(f"ERROR FATAL DE CONEXIÓN: {e}")

async def close_db():
    global _client
    if _client:
        _client.close()
        print("Conexión cerrada. 💀")

def get_collection(name: str):
    if _db is None:
        # Recuperación de emergencia si _db no se asignó
        if _client:
            return _client[DB_NAME][name]
        raise RuntimeError("BD no inicializada.")
    return _db[name]