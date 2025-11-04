from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Annotated
from bson import ObjectId

from database import get_collection
from models import Product, PyObjectId
from routes.auth import get_current_admin_user, User # Importa las dependencias de Auth

router = APIRouter(prefix="/products", tags=["Products"])

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    img_url: Optional[str] = None
    active: Optional[bool] = None

# --- Rutas Públicas (Catálogo) ---
@router.get("/", response_model=List[Product])
async def get_all_products(category: str = None, search: str = None):
    products_col = get_collection("products")
    query = {"active": True}
    
    if category:
        query["category"] = category
    
    if search:
        # Búsqueda insensible a mayúsculas y minúsculas en nombre y descripción
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]

    products = await products_col.find(query).to_list(100)
    return products

@router.get("/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str):
    products_col = get_collection("products")
    
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")

    product = await products_col.find_one({"_id": ObjectId(product_id)})
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return Product(**product)

# --- Rutas de Administración (Requiere Admin) ---
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(product: Product, admin_user: Annotated[User, Depends(get_current_admin_user)]):
    products_col = get_collection("products")
    
    # Excluir el ID para que MongoDB lo genere
    product_data = product.model_dump(by_alias=True, exclude_none=True, exclude={'id'})
    inserted_product = await products_col.insert_one(product_data)
    
    created_product = await products_col.find_one({"_id": inserted_product.inserted_id})
    return Product(**created_product)

@router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, admin_user: Annotated[User, Depends(get_current_admin_user)]):
    products_col = get_collection("products")

    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")
    
    # Filtrar solo los campos que tienen un valor
    update_data = {k: v for k, v in product_update.model_dump(exclude_unset=True).items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    result = await products_col.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Devolver el producto actualizado
    updated_product = await products_col.find_one({"_id": ObjectId(product_id)})
    return Product(**updated_product)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, admin_user: Annotated[User, Depends(get_current_admin_user)]):
    products_col = get_collection("products")

    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="ID de producto inválido")
        
    result = await products_col.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None

# Ruta para el panel de administración
@router.get("/admin/list", response_model=List[Product])
async def admin_list_products(admin_user: Annotated[User, Depends(get_current_admin_user)]):
    products_col = get_collection("products")
    products = await products_col.find().to_list(100)
    return products
