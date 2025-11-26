from fastapi import APIRouter, status
from database import get_collection
from models import ContactMessage

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/", status_code=201)
async def send_message(msg: ContactMessage):
    data = msg.model_dump(by_alias=True, exclude={'id'})
    await get_collection("messages").insert_one(data)
    return {"message": "Enviado correctamente"}