from typing import List, Optional
from fastapi import APIRouter, Query,HTTPException, status
from database import get_collection
from models import Product

router = APIRouter(prefix="/products", tags=["Products"])

@router.get("/", response_model=List[Product])
async def list_products(search: Optional[str] = None, category: Optional[str] = None):
    query = {"active": True}
    if category: query["category"] = category
    if search: query["name"] = {"$regex": search, "$options": "i"}
    
    cursor = get_collection("products").find(query)
    return [Product(**doc) async for doc in cursor]

@router.post("/", status_code=201)
async def create_product(product: Product):
    """
    Permite al administrador agregar un nuevo producto al catálogo.
    """
    coll = get_collection("products")
    
    # Validar si ya existe un producto con el mismo nombre (opcional pero recomendado)
    existing = await coll.find_one({"name": product.name})
    if existing:
        raise HTTPException(status_code=400, detail="El producto ya existe")

    # Convertir el modelo Pydantic a diccionario
    product_dict = product.model_dump(by_alias=True, exclude={"id"})
    
    # Insertar en MongoDB
    result = await coll.insert_one(product_dict)
    
    # Retornar el producto creado con su nuevo ID
    return {**product_dict, "_id": str(result.inserted_id)}