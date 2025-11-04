from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from typing import Optional

# --- Configuración de Entorno ---
# (Se asume que estas variables de entorno son inyectadas en el entorno Canvas)
class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "rostiseria_db"
    SECRET_KEY: str = "super-secreto-para-jwt-no-compartir"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300 # 5 horas

    class Config:
        # Permite cargar variables de entorno desde un archivo .env si se usa localmente
        # En Canvas, se cargarán directamente del entorno.
        pass

settings = Settings()

# --- Cliente de Base de Datos ---
class DatabaseClient:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        """Inicializa la conexión con MongoDB."""
        try:
            print(f"Conectando a MongoDB en: {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            await self.client.admin.command('ping') # Prueba de conexión
            self.db = self.client[settings.MONGO_DB_NAME]
            print("Conexión a MongoDB exitosa.")

            # Crear índices únicos (buena práctica)
            await self.db["users"].create_index("email", unique=True)
            await self.db["products"].create_index("name", unique=True)

        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            self.client = None
            self.db = None

    async def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")

db_client = DatabaseClient()

# Función de dependencia para obtener la colección
def get_collection(collection_name: str):
    """Devuelve la colección de MongoDB."""
    if db_client.db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
    return db_client.db[collection_name]
