from fastapi import APIRouter, HTTPException, status
from typing import List
from bson import ObjectId

from database import get_collection
from models import ContactMessage, User # Importa User para la dependencia de Admin

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_contact_message(message: ContactMessage):
    messages_col = get_collection("messages")
    
    # Excluir el ID para que MongoDB lo genere
    message_data = message.model_dump(by_alias=True, exclude_none=True, exclude={'id'})
    inserted = await messages_col.insert_one(message_data)
    
    return {"message": "Mensaje de contacto enviado con éxito.", "id": str(inserted.inserted_id)}