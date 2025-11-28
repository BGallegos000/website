from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from bson import ObjectId
from models import Order, OrderItem, OrderStatus
from database import get_collection
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Orders"])

class OrderCreate(BaseModel):
    customer_name: str
    email: str
    phone: str
    address: str
    note: Optional[str] = ""
    items: List[OrderItem] 
    total: float

class OrderStatusUpdate(BaseModel):
    status: str

@router.post("/", response_model=Order, status_code=201)
async def create_order(order_in: OrderCreate):
    if not order_in.items:
        raise HTTPException(400, "Carrito vacío")
    
    new_order = Order(
        user_email=order_in.email,
        customer_name=order_in.customer_name,
        phone=order_in.phone,
        address=order_in.address,
        note=order_in.note,
        items=order_in.items,
        total=order_in.total
    )
    coll = get_collection("orders")
    res = await coll.insert_one(new_order.model_dump(by_alias=True, exclude={"id"}))
    created = await coll.find_one({"_id": res.inserted_id})
    return Order(**created)

@router.get("/", response_model=List[Order])
async def get_orders(email: Optional[str] = Query(None)):
    query = {}
    if email: query["user_email"] = email
    coll = get_collection("orders")
    return await coll.find(query).sort("created_at", -1).to_list(100)

@router.patch("/{order_id}/status", response_model=Order)
async def update_status(order_id: str, status_update: OrderStatusUpdate):
    if not ObjectId.is_valid(order_id): raise HTTPException(400, "ID inválido")
    
    coll = get_collection("orders")
    res = await coll.update_one(
        {"_id": ObjectId(order_id)}, 
        {"$set": {"status": status_update.status}}
    )
    if res.matched_count == 0: raise HTTPException(404, "No encontrado")
    
    doc = await coll.find_one({"_id": ObjectId(order_id)})
    return Order(**doc)