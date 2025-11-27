from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
import pytz

# Zona horaria de Chile
CHILE_TIMEZONE = pytz.timezone("Chile/Continental")


# ------------------------
#   MODELOS DE DOMINIO
# ------------------------

class ProductBase(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str 
    price: float 
    category: str
    description: str
    img_url: str
    active: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: str 

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class User(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    hashed_password: str
    is_admin: bool = False

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class OrderItem(BaseModel):
    product_id: str
    name: str
    price: float
    quantity: int


# Estados del pedido (string normal para guardar en Mongo)
class OrderStatus:
    PENDING = "Pendiente"
    PREPARING = "En preparación"
    READY = "Listo"
    DELIVERING = "En camino"
    DELIVERED = "Entregado"
    CANCELED = "Anulado"


class Order(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    user_email: Optional[EmailStr] = None
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    total: float
    status: str = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))
    cancel_until: datetime = Field(
        default_factory=lambda: datetime.now(CHILE_TIMEZONE) + timedelta(minutes=10)
    )

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }


class ContactMessage(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda dt: dt.isoformat(),
        }
