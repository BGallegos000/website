# routes/products.py
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId

from database import get_products_collection
from models import Product, ProductCreate  # ajusta si tus nombres son distintos

router = APIRouter(
    prefix="/products",      # Quedará /products/... desde main.py sin prefix extra
    tags=["products"],
)


@router.get("/", response_model=List[Product])
async def list_products(
    category: Optional[str] = Query(None, description="Filtrar por categoría exacta"),
    search: Optional[str] = Query(None, description="Texto a buscar en el nombre"),
):
    """
    Lista productos desde MongoDB.

    - `category`: filtra por categoría exacta (ej: 'Pollo').
    - `search`: busca texto parcial en el nombre (case-insensitive).
    """
    coll = get_products_collection()

    query: dict = {"active": True}

    if category:
        query["category"] = category

    if search:
        # Búsqueda por nombre, sin distinguir mayúsculas/minúsculas
        query["name"] = {"$regex": search, "$options": "i"}

    cursor = coll.find(query)
    products: list[Product] = []
    async for doc in cursor:
        # Convertimos ObjectId a str para que Pydantic no se queje
        doc["id"] = str(doc["_id"])
        products.append(Product(**doc))

    return products


@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Obtiene un producto por su _id de Mongo."""
    coll = get_products_collection()

    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    doc = await coll.find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    doc["id"] = str(doc["_id"])
    return Product(**doc)


@router.post("/", response_model=Product, status_code=201)
async def create_product(product_in: ProductCreate):
    """Crea un producto nuevo en MongoDB."""
    coll = get_products_collection()

    data = product_in.model_dump()
    res = await coll.insert_one(data)
    doc = await coll.find_one({"_id": res.inserted_id})

    if not doc:
        raise HTTPException(status_code=500, detail="Error al crear el producto")

    doc["id"] = str(doc["_id"])
    return Product(**doc)
