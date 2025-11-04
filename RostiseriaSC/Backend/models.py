from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
import pytz

# Configuración de zona horaria (Chile)
CHILE_TIMEZONE = pytz.timezone('Chile/Continental')

# --- Mapeo de ObjectId para Pydantic ---
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

# --- Modelos del Diagrama de Clases ---

# 1. Producto (Product)
class Product(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=3, description="Nombre del producto.")
    price: float = Field(..., gt=0, description="Precio unitario.")
    category: str = Field(..., description="Categoría del producto (e.g., 'Pollos', 'Agregados').")
    description: str = Field(..., min_length=10, description="Descripción detallada.")
    img_url: str = Field(..., description="URL de la imagen del producto.")
    active: bool = Field(default=True, description="Indica si el producto está disponible.")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        # Ejemplo de producto para OpenAPI
        schema_extra = {
            "example": {
                "name": "Pollo Asado Clásico",
                "price": 9990.00,
                "category": "Pollos",
                "description": "Pollo entero marinado con hierbas frescas, asado a la perfección.",
                "img_url": "/imagenes/pollo.jpg",
                "active": True
            }
        }

# 2. Usuario (User)
class User(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=2)
    email: EmailStr = Field(..., description="Email único, usado para login.")
    hashed_password: str = Field(..., description="Contraseña hasheada (no el texto plano).")
    is_admin: bool = Field(default=False, description="Rol de administrador.")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 3. Item en Pedido (OrderItem)
class OrderItem(BaseModel):
    product_id: PyObjectId = Field(..., description="ID del producto en el catálogo.")
    name: str = Field(..., description="Nombre del producto al momento de la compra.")
    price: float = Field(..., gt=0, description="Precio al momento de la compra.")
    quantity: int = Field(..., gt=0, description="Cantidad comprada.")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# 4. Pedido (Order)
class OrderStatus(str):
    PENDING = "Pendiente"
    PREPARING = "En preparación"
    READY = "Listo"
    DELIVERING = "En camino"
    DELIVERED = "Entregado"
    CANCELED = "Anulado"

class Order(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    # user_id o email asociado, si el usuario estaba logueado
    user_email: Optional[EmailStr] = Field(default=None, description="Email del usuario si estaba logueado.")
    
    # Datos del cliente para la entrega (incluidos en carrito.html)
    customer_name: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=8)
    address: str = Field(..., min_length=10, description="Dirección de entrega (ej: Calle Falsa 123, Santiago).")
    
    items: List[OrderItem] = Field(..., description="Lista de productos y cantidades.")
    total: float = Field(..., gt=0, description="Costo total del pedido.")
    
    # Gestión de estado (similar a GestionPedidos.html)
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Estado actual del pedido.")
    
    # Fechas
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))
    # Fecha límite para anulación (10 min como en carrito.html)
    cancel_until: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE) + timedelta(minutes=10))

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}


# 5. Mensaje de Contacto (ContactMessage)
class ContactMessage(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(..., min_length=2)
    email: EmailStr
    message: str = Field(..., min_length=10)
    created_at: datetime = Field(default_factory=lambda: datetime.now(CHILE_TIMEZONE))
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, datetime: lambda dt: dt.isoformat()}
