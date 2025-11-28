from typing import List, Optional
from fastapi import APIRouter, Query
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