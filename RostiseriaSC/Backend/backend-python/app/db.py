from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.MONGO_DB]

# Colecciones “alias”
col_users = db["users"]
col_products = db["products"]
col_orders = db["orders"]
col_resets = db["resetTokens"]
col_logs = db["logs"]
