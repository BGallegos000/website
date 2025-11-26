from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Annotated
from bson import ObjectId
from datetime import datetime, timedelta
from pydantic import BaseModel

from database import get_collection
from models import Order, OrderItem, OrderStatus, CHILE_TIMEZONE
from routes.auth import get_current_user, get_current_admin_user, User

router = APIRouter(prefix="/orders", tags=["Orders"])

class OrderIn(BaseModel):
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: str

@router.post("/", response_model=Order, status_code=201)
async def create_order(order_in: OrderIn, user: Optional[User] = Depends(get_current_user)):
    if not order_in.items: raise HTTPException(400, "El carrito está vacío")
    
    # Recalcular total en backend por seguridad
    total = sum(item.price * item.quantity for item in order_in.items) + 3000 # + Envío
    
    new_order = Order(
        user_email=user.email if user else None,
        customer_name=order_in.customer_name,
        phone=order_in.phone,
        address=order_in.address,
        items=order_in.items,
        total=total,
        status=OrderStatus.PENDING,
        created_at=datetime.now(CHILE_TIMEZONE),
        cancel_until=datetime.now(CHILE_TIMEZONE) + timedelta(minutes=10)
    )
    
    res = await get_collection("orders").insert_one(new_order.model_dump(by_alias=True, exclude={'id'}))
    created = await get_collection("orders").find_one({"_id": res.inserted_id})
    return Order(**created)

@router.get("/mine", response_model=List[Order])
async def my_orders(user: Annotated[User, Depends(get_current_user)]):
    return await get_collection("orders").find({"user_email": user.email}).sort("created_at", -1).to_list(100)

@router.get("/{id}", response_model=Order)
async def get_order(id: str):
    if not ObjectId.is_valid(id): raise HTTPException(400, "ID inválido")
    order = await get_collection("orders").find_one({"_id": ObjectId(id)})
    if not order: raise HTTPException(404, "Pedido no encontrado")
    return Order(**order)

@router.patch("/{id}/cancel", response_model=Order)
async def cancel_order(id: str):
    if not ObjectId.is_valid(id): raise HTTPException(400, "ID inválido")
    order_doc = await get_collection("orders").find_one({"_id": ObjectId(id)})
    if not order_doc: raise HTTPException(404, "No encontrado")
    
    order = Order(**order_doc)
    if order.status in [OrderStatus.CANCELED, OrderStatus.DELIVERED]:
        raise HTTPException(400, "No se puede anular en este estado")
    
    if datetime.now(CHILE_TIMEZONE) > order.cancel_until:
        raise HTTPException(400, "Tiempo de anulación expirado")
        
    await get_collection("orders").update_one({"_id": ObjectId(id)}, {"$set": {"status": OrderStatus.CANCELED}})
    updated = await get_collection("orders").find_one({"_id": ObjectId(id)})
    return Order(**updated)

# --- Admin ---
@router.get("/admin/list", response_model=List[Order])
async def list_orders_admin(admin: Annotated[User, Depends(get_current_admin_user)], status_filter: Optional[str] = None):
    q = {"status": status_filter} if status_filter else {}
    return await get_collection("orders").find(q).sort("created_at", -1).to_list(100)

@router.patch("/admin/list/{id}/status", response_model=Order)
async def update_status(id: str, status_in: OrderStatusUpdate, admin: Annotated[User, Depends(get_current_admin_user)]):
    if not ObjectId.is_valid(id): raise HTTPException(400, "ID inválido")
    res = await get_collection("orders").update_one({"_id": ObjectId(id)}, {"$set": {"status": status_in.status}})
    if res.matched_count == 0: raise HTTPException(404, "Pedido no encontrado")
    updated = await get_collection("orders").find_one({"_id": ObjectId(id)})
    return Order(**updated)