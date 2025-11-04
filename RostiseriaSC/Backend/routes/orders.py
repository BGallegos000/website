from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated, Optional
from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, EmailStr

from database import get_collection
from models import Order, OrderItem, OrderStatus, PyObjectId, CHILE_TIMEZONE
from routes.auth import get_current_user, get_current_admin_user, User # Importa las dependencias de Auth

router = APIRouter(prefix="/orders", tags=["Orders"])

# --- Modelos de Entrada/Salida ---

class OrderIn(BaseModel):
    # Campos que el cliente envía en el checkout
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem] # La lista de items del carrito
    
# Clase para el cuerpo de la actualización de estado (Admin)
class OrderStatusUpdate(BaseModel):
    status: OrderStatus

# --- Rutas Públicas (Creación y Consulta del Cliente) ---

@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order_in: OrderIn, current_user: Optional[User] = Depends(get_current_user)):
    orders_col = get_collection("orders")
    
    # 1. Validación de Lógica de Negocio
    if not order_in.items:
        raise HTTPException(status_code=400, detail="El pedido debe contener al menos un artículo.")

    # Simulación de cálculo de total
    total_calculated = sum(item.price * item.quantity for item in order_in.items)

    # El usuario logueado se asocia al pedido
    user_email = current_user.email if current_user else None

    # 2. Creación del objeto Order
    new_order = Order(
        user_email=user_email,
        customer_name=order_in.customer_name,
        phone=order_in.phone,
        address=order_in.address,
        items=order_in.items,
        total=total_calculated,
        status=OrderStatus.PENDING,
        created_at=datetime.now(CHILE_TIMEZONE),
        # 10 minutos para cancelar, como en carrito.html
        cancel_until=datetime.now(CHILE_TIMEZONE) + timedelta(minutes=10)
    )

    # 3. Inserción en MongoDB
    inserted = await orders_col.insert_one(new_order.model_dump(by_alias=True, exclude_none=True, exclude={'id'}))
    
    created_order = await orders_col.find_one({"_id": inserted.inserted_id})
    return Order(**created_order)

@router.get("/mine", response_model=List[Order])
async def get_my_orders(current_user: Annotated[User, Depends(get_current_user)]):
    orders_col = get_collection("orders")
    
    # Solo mostrar pedidos asociados al email del usuario logueado
    orders = await orders_col.find({"user_email": current_user.email}).sort("created_at", -1).to_list(100)
    return orders

@router.get("/{order_id}", response_model=Order)
async def get_order_details(order_id: str):
    orders_col = get_collection("orders")

    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

    order = await orders_col.find_one({"_id": ObjectId(order_id)})
    if order is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return Order(**order)

@router.patch("/{order_id}/cancel", response_model=Order)
async def cancel_order(order_id: str):
    orders_col = get_collection("orders")
    
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

    order_doc = await orders_col.find_one({"_id": ObjectId(order_id)})
    if order_doc is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    order = Order(**order_doc)

    # Validación de cancelación (Lógica de carrito.html y GestionPedidos.html)
    if order.status == OrderStatus.CANCELED or order.status == OrderStatus.DELIVERED:
        raise HTTPException(status_code=400, detail=f"El pedido ya está en estado '{order.status}' y no puede ser anulado.")
    
    now_in_chile = datetime.now(CHILE_TIMEZONE)
    if now_in_chile > order.cancel_until:
        raise HTTPException(status_code=403, detail="El tiempo límite para anular el pedido ha expirado.")

    # Actualizar estado a Anulado
    await orders_col.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": OrderStatus.CANCELED}}
    )
    
    updated_order = await orders_col.find_one({"_id": ObjectId(order_id)})
    return Order(**updated_order)

# --- Rutas de Administración (Requiere Admin) ---

@router.get("/admin/list", response_model=List[Order])
async def admin_list_orders(admin_user: Annotated[User, Depends(get_current_admin_user)], status_filter: Optional[OrderStatus] = None):
    orders_col = get_collection("orders")
    
    query = {}
    if status_filter:
        query["status"] = status_filter
        
    # Ordenar por fecha de creación descendente
    orders = await orders_col.find(query).sort("created_at", -1).to_list(100)
    return orders

@router.patch("/admin/list/{order_id}/status", response_model=Order)
async def admin_update_order_status(order_id: str, status_update: OrderStatusUpdate, admin_user: Annotated[User, Depends(get_current_admin_user)]):
    orders_col = get_collection("orders")

    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

    result = await orders_col.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": status_update.status}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    updated_order = await orders_col.find_one({"_id": ObjectId(order_id)})
    return Order(**updated_order)