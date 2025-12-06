from fastapi import APIRouter
from database import get_collection
from models import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", status_code=201)
async def send_message(msg: ContactMessage):
    """
    Recibe un mensaje del formulario de contacto y lo guarda en MongoDB.
    """
    coll = get_collection("messages")
    
    # Convertir modelo a diccionario para Mongo
    msg_data = msg.model_dump()
    
    # Insertar en la base de datos
    await coll.insert_one(msg_data)
    
    return {"message": "Mensaje recibido correctamente"}