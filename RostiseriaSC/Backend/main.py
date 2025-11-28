from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, close_db
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.contact import router as contact_router

app = FastAPI(title="Rostisería SC API", version="1.0.0")

# 1. Protección de Host (Evita ataques de host header)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

# 2. Compresión GZip (Mejora rendimiento en respuestas grandes)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Permitir acceso desde el Frontend (Live Server)
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PATCH, OPTIONS
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(contact_router)

@app.get("/health")
def health():
    return {"status": "ok"}