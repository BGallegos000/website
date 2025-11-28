from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, BeforeValidator
from typing_extensions import Annotated

PyObjectId = Annotated[str, BeforeValidator(str)]

class Role:
    USER = "user"
    ADMIN = "admin"

class OrderStatus:
    PENDING = "Pendiente"
    PREPARING = "En preparación"
    READY = "Listo"
    EN_CAMINO = "En camino"
    DELIVERED = "Entregado"
    CANCELED = "Anulado"

class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    price: float
    category: str
    description: str
    img_url: str = Field(alias="img")
    stock: int = 100
    active: bool = True

    class Config:
        populate_by_name = True
        json_encoders = {str: str}

class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str
    email: EmailStr
    hashed_password: str
    role: str = Role.USER
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    class Config:
        populate_by_name = True

class OrderItem(BaseModel):
    product_id: str = Field(alias="productoId")
    name: str = Field(alias="nombre")
    price: float = Field(alias="precio")
    quantity: int = Field(alias="cantidad")

    class Config:
        populate_by_name = True

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_email: Optional[EmailStr] = None
    customer_name: str
    phone: str
    address: str
    note: Optional[str] = None
    items: List[OrderItem]
    total: float
    status: str = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}
        
        
# ... (Todo lo anterior igual) ...

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_email: Optional[EmailStr] = None
    customer_name: str
    phone: str
    address: str
    note: Optional[str] = None
    items: List[OrderItem]
    total: float
    status: str = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda dt: dt.isoformat()}

# --- NUEVO MODELO PARA CONTACTO ---
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    created_at: datetime = Field(default_factory=datetime.now)