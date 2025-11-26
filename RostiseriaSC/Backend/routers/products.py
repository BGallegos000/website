from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Annotated
from bson import ObjectId
from pydantic import BaseModel

from database import get_collection
from models import Product
from routes.auth import get_current_admin_user, User

router = APIRouter(prefix="/products", tags=["Products"])

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    img_url: Optional[str] = None
    active: Optional[bool] = None

@router.get("/", response_model=List[Product])
async def get_products(category: str = None, search: str = None):
    query = {"active": True}
    if category: query["category"] = category
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    return await get_collection("products").find(query).to_list(100)

@router.get("/admin/list", response_model=List[Product])
async def get_all_products_admin(admin: Annotated[User, Depends(get_current_admin_user)]):
    return await get_collection("products").find().to_list(100)

@router.post("/", response_model=Product, status_code=201)
async def create_product(product: Product, admin: Annotated[User, Depends(get_current_admin_user)]):
    new_prod = product.model_dump(by_alias=True, exclude={'id'})
    res = await get_collection("products").insert_one(new_prod)
    created = await get_collection("products").find_one({"_id": res.inserted_id})
    return Product(**created)

@router.put("/{id}", response_model=Product)
async def update_product(id: str, p_in: ProductUpdate, admin: Annotated[User, Depends(get_current_admin_user)]):
    if not ObjectId.is_valid(id): raise HTTPException(400, "ID inválido")
    data = {k:v for k,v in p_in.model_dump(exclude_unset=True).items() if v is not None}
    
    await get_collection("products").update_one({"_id": ObjectId(id)}, {"$set": data})
    updated = await get_collection("products").find_one({"_id": ObjectId(id)})
    if not updated: raise HTTPException(404, "Producto no encontrado")
    return Product(**updated)

@router.delete("/{id}", status_code=204)
async def delete_product(id: str, admin: Annotated[User, Depends(get_current_admin_user)]):
    if not ObjectId.is_valid(id): raise HTTPException(400, "ID inválido")
    res = await get_collection("products").delete_one({"_id": ObjectId(id)})
    if res.deleted_count == 0: raise HTTPException(404, "Producto no encontrado")