from motor.motor_asyncio import AsyncIOMotorClient
from pydantic_settings import BaseSettings
from typing import Optional
from fastapi import HTTPException

class Settings(BaseSettings):
    # Ajusta la URI si tu MongoDB está en otro lado
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "rostiseria_db"
    SECRET_KEY: str = "super-secreto-para-jwt-no-compartir"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300 

settings = Settings()

class DatabaseClient:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None

    async def connect(self):
        try:
            print(f"Conectando a MongoDB en: {settings.MONGODB_URI}...")
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            await self.client.admin.command('ping')
            self.db = self.client[settings.MONGO_DB_NAME]
            print("Conexión a MongoDB exitosa.")
            
            # Índices únicos
            await self.db["users"].create_index("email", unique=True)

        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")
            self.client = None
            self.db = None

    async def close(self):
        if self.client:
            self.client.close()
            print("Conexión a MongoDB cerrada.")

db_client = DatabaseClient()

def get_collection(collection_name: str):
    if db_client.db is None:
        raise HTTPException(status_code=500, detail="Database connection not initialized")
    return db_client.db[collection_name]