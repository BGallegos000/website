from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import List, Optional
from bson import ObjectId
from models import Order, OrderItem, OrderStatus
from database import get_collection
from pydantic import BaseModel

router = APIRouter(prefix="/orders", tags=["Orders"])

# --- SCHEMAS DE ENTRADA ---

# Schema para recibir el pedido desde el carrito
class OrderCreate(BaseModel):
    customer_name: str
    email: str
    phone: str
    address: str
    note: Optional[str] = ""
    items: List[OrderItem] 
    total: float

# Schema para actualizar el estado (SOLUCIÓN DEL ERROR)
class OrderStatusUpdate(BaseModel):
    status: str

# --- ENDPOINTS ---

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

# Endpoint para obtener pedidos (Búsqueda por email o todos)
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

# Endpoint para obtener un solo pedido por ID
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

# --- ENDPOINT NUEVO: CAMBIAR ESTADO (CORREGIDO) ---
@router.patch("/{order_id}/status", response_model=Order)
async def update_order_status(order_id: str, status_update: OrderStatusUpdate):
    coll = get_collection("orders")
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(400, "ID inválido")
        
    # Validar que el estado sea correcto
    valid_statuses = [
        OrderStatus.PENDING, 
        OrderStatus.PREPARING, 
        OrderStatus.READY, 
        OrderStatus.EN_CAMINO, 
        OrderStatus.DELIVERED, 
        OrderStatus.CANCELED
    ]
    
    if status_update.status not in valid_statuses:
        raise HTTPException(400, f"Estado no permitido. Opciones: {valid_statuses}")

    # Actualizar en base de datos
    result = await coll.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status_update.status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(404, "Pedido no encontrado")
        
    # Devolver el pedido actualizado
    updated_doc = await coll.find_one({"_id": ObjectId(order_id)})
    return Order(**updated_doc)