from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
import pytz

CHILE_TIMEZONE = pytz.timezone('Chile/Continental')

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# --- Modelos ---

class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    category: str
    description: str
    img_url: str
    active: bool = True

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    hashed_password: str
    is_admin: bool = False

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class OrderItem(BaseModel):
    product_id: str 
    name: str
    price: float
    quantity: int

class OrderStatus(str):
    PENDING = "Pendiente"
    PREPARING = "En preparación"
    READY = "Listo"
    DELIVERING = "En camino"
    DELIVERED = "Entregado"
    CANCELED = "Anulado"

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_email: Optional[EmailStr] = None
    customer_name: str
    phone: str
    address: str
    items: List[OrderItem]
    total: float
    status: str = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))
    cancel_until: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE) + timedelta(minutes=10))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}

class ContactMessage(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}