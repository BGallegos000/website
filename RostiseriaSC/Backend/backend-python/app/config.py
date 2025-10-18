from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGO_DB: str = "rostiseria"
    JWT_SECRET: str = "dev"
    JWT_EXPIRES: str = "8h"
    ADMIN_EMAIL: str = "admin@rostiseria.sc"
    ADMIN_PASS: str = "A1b2c3d4"

    class Config:
        env_file = ".env"

settings = Settings()
