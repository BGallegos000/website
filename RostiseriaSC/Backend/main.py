from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

from database import db_client
from routes import auth, products, orders, contact

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.close()

app = FastAPI(title="Rostiseria API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(contact.router)

@app.get("/")
def root():
    return {"msg": "API Rostiseria Online"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)