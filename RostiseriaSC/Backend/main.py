from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, close_db
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.contact import router as contact_router

app = FastAPI(title="Rostisería SC API", version="1.0.0")

# Permitir acceso desde el Frontend (Live Server)
origins = ["*"] # Puedes restringirlo a ["http://127.0.0.1:5500"] en producción

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