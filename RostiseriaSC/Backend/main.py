# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, close_db
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router

app = FastAPI(title="Rostisería Sabores Caseros API", version="1.0.0")

# --- CONFIGURACIÓN CORS BLINDADA ---
# Definimos exactamente quién tiene permiso para hablar con el backend
origins = [
    "http://127.0.0.1:5500",    # Tu Live Server actual
    "http://localhost:5500",    # Alternativa común
    "http://localhost",         # Por si corres sin puerto
    "*"                         # Comodín para desarrollo (opcional)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Usamos la lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

# Registrar rutas
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "system": "Rostisería API Online"}