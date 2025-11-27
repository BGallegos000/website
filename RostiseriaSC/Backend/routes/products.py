# routes/products.py
from typing import List, Optional
from fastapi import APIRouter, Query
from database import get_collection
from models import Product, PyObjectId

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None
):
    query = {"active": True}
    if category:
        query["category"] = category
    if search:
        # Búsqueda case-insensitive
        query["name"] = {"$regex": search, "$options": "i"}

    coll = get_collection("products")
    cursor = coll.find(query)
    
    products = []
    async for doc in cursor:
        products.append(Product(**doc))
    return products

# Endpoint auxiliar para crear productos (puedes usar Postman para llenar la BD)
@router.post("/", response_model=Product)
async def create_product_manual(product: Product):
    coll = get_collection("products")
    res = await coll.insert_one(product.model_dump(by_alias=True, exclude={"id"}))
    new_doc = await coll.find_one({"_id": res.inserted_id})
    return Product(**new_doc)