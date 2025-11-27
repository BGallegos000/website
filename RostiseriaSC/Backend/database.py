from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "rostiseria_db"

client: AsyncIOMotorClient | None = None
db = None

async def init_db():
    global client, db
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    print("Conectado a MongoDB:", MONGO_URL, "/", DB_NAME)

async def close_db():
    global client
    if client:
        client.close()

def get_collection(name: str):
    return db[name]
