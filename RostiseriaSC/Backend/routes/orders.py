from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from database import get_collection
from models import Order, OrderStatus
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["Orders"])

# --- 1. CREAR PEDIDO (POST) ---
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Order)
async def create_order(order: Order):
    coll = get_collection("orders")
    
    # Asignar valores por defecto del servidor
    order.status = OrderStatus.PENDING
    order.created_at = datetime.now()
    
    # Convertir a formato diccionario para MongoDB
    order_dict = order.model_dump(by_alias=True, exclude={"id"})
    
    try:
        # Insertar en la base de datos
        result = await coll.insert_one(order_dict)
        
        # Recuperar el documento recién creado
        created_order = await coll.find_one({"_id": result.inserted_id})
        return created_order
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno al procesar el pedido")


# --- 2. OBTENER PEDIDOS (GET) ---
@router.get("/", response_model=List[Order])
async def get_orders(email: Optional[str] = Query(None)):
    coll = get_collection("orders")
    filtro = {}
    
    # Si se envía email, filtrar por usuario. Si no, devuelve todo
    if email:
        filtro["user_email"] = email

    try:
        # Ordenar por fecha descendente (más reciente primero)
        cursor = coll.find(filtro).sort("created_at", -1)
        orders = await cursor.to_list(length=100)
        return orders
    except Exception as e:
         raise HTTPException(status_code=500, detail="Error al recuperar el historial")


# --- 3. ACTUALIZAR ESTADO (PATCH) ---
@router.patch("/{id}/status", response_model=Order)
async def update_order_status(id: str, status_update: dict):
    new_status = status_update.get("status")
    
    if not new_status:
        raise HTTPException(status_code=400, detail="El campo 'status' es obligatorio")

    coll = get_collection("orders")

    try:
        # Validar formato de ID de MongoDB
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="ID de pedido inválido")
            
        mongo_id = ObjectId(id) 

        # Ejecutar actualización
        result = await coll.update_one(
            {"_id": mongo_id}, 
            {"$set": {"status": new_status}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")

        # Devolver el documento actualizado
        updated_order = await coll.find_one({"_id": mongo_id})
        return updated_order

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))