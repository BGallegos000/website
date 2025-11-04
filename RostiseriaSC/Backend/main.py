from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from database import db_client
from routes import auth, products, orders, contact

# --- Context Manager para conexión a DB ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar la aplicación:
    await db_client.connect()
    yield
    # Al cerrar la aplicación:
    await db_client.close()

# --- Inicialización de FastAPI ---
app = FastAPI(
    title="Rostiseria SC API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None
)

# --- Configuración CORS (Obligatorio para frontend web) ---
origins = [
    # Permitir al frontend que se ejecuta en el mismo dominio acceder a la API
    "*", 
    # Agrega otros dominios si es necesario (ej: tu dominio de producción)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Registro de Routers ---
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(contact.router)

# --- Ruta Raíz ---
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "API de Rostiseria Sabores Caseros. Visita /docs para la documentación."}

# --- Ejecución (Para desarrollo local) ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    # En entornos de producción (como el Canvas), uvicorn se ejecutará por separado.
    # Esta línea es para probar localmente con `python main.py`
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
