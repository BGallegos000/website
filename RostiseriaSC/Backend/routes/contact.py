from fastapi import APIRouter, HTTPException
from database import get_collection
from models import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", status_code=201)
async def send_message(msg: ContactMessage):
    """
    Guarda un mensaje de contacto en la base de datos.
    """
    coll = get_collection("messages")
    
    # Convertir a diccionario y guardar
    msg_data = msg.model_dump()
    await coll.insert_one(msg_data)
    
    return {"message": "Mensaje recibido correctamente"}