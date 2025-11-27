from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, close_db
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.contact import router as contact_router

app = FastAPI(title="Rostisería Sabores Caseros API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

app.include_router(auth_router, prefix="/auth")
app.include_router(products_router)          # <--- SIN prefix extra
app.include_router(orders_router, prefix="/orders")
app.include_router(contact_router, prefix="/contact")
