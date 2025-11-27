# routes/orders.py
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Optional
from bson import ObjectId
from models import Order, OrderItem
from database import get_collection
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Orders"])

# Schema específico para recibir el JSON de carrito.html
class OrderCreate(BaseModel):
    customer_name: str
    email: str
    phone: str
    address: str
    note: Optional[str] = ""
    # El front envía items con claves en español, el modelo OrderItem lo maneja
    items: List[OrderItem] 
    total: float

@router.post("/", response_model=Order, status_code=201)
async def create_order(order_in: OrderCreate):
    if not order_in.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío")
    
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

# Endpoint para GestionPedidos.html (Búsqueda por email)
@router.get("/", response_model=List[Order])
async def get_orders(email: Optional[str] = Query(None)):
    query = {}
    if email:
        query["user_email"] = email
        
    coll = get_collection("orders")
    cursor = coll.find(query).sort("created_at", -1)
    
    results = []
    async for doc in cursor:
        results.append(Order(**doc))
    return results

# Endpoint para GestionPedidos.html (Búsqueda por ID)
@router.get("/{order_id}", response_model=Order)
async def get_order_by_id(order_id: str):
    coll = get_collection("orders")
    try:
        oid = ObjectId(order_id)
        doc = await coll.find_one({"_id": oid})
    except:
        raise HTTPException(404, "Formato de ID inválido")

    if not doc:
        raise HTTPException(404, "Pedido no encontrado")
    return Order(**doc)