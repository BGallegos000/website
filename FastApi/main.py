# main.py
from typing import List, Optional, Sequence, Generic, TypeVar
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# =========================
# Configuración MongoDB
# =========================
MONGODB_URI = "mongodb://localhost:27017"
DB_NAME = "bdunab"
COLL_NAME = "items"

client: AsyncIOMotorClient | None = None
coll = None

app = FastAPI(title="FastAPI 8156", version="1.0.0")

# =========================
# Modelos Pydantic (v2)
# =========================
class ItemIn(BaseModel):
    nombre: str = Field(min_length=1, description="Nombre Producto")
    precio: float = Field(gt=0, description="Precio > 0")
    tags: List[str] = Field(default_factory=list)
    activo: bool = True

class ItemOut(ItemIn):
    id: str

def doc_to_itemout(doc) -> ItemOut:
    return ItemOut(
        id=str(doc["_id"]),
        nombre=doc["nombre"],
        precio=doc["precio"],
        tags=doc.get("tags", []),
        activo=doc.get("activo", True),
    )

# =========================
# Wrapper {status, mensaje, data}
# =========================
T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    status: int = 200
    mensaje: str = "ok"
    data: Optional[T] = None

def ok(data: Optional[T] = None, mensaje: str = "ok", status: int = 200) -> ApiResponse[T]:
    return ApiResponse[T](status=status, mensaje=mensaje, data=data)

# =========================
# Ciclo de vida de la app
# =========================
@app.on_event("startup")
async def startup():
    global client, coll
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    coll = db[COLL_NAME]
    # Índice útil (opcional)
    # await coll.create_index("nombre")

@app.on_event("shutdown")
async def shutdown():
    if client:
        client.close()

# =========================
# Sistema / Health
# =========================
@app.get("/health", response_model=ApiResponse[dict], tags=["sistema"])
async def health():
    await client.admin.command("ping")
    total = await coll.estimated_document_count()
    return ok({"db": "up", "collection": COLL_NAME, "count": total})

# =========================
# CRUD Items (envueltos en ApiResponse)
# =========================

@app.get("/items", response_model=ApiResponse[List[ItemOut]], tags=["items"])
async def listar_items(
    q: Optional[str] = Query(None, description="Filtro por nombre que contenga 'q'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """
    Lista items con filtros básicos y paginación.
    Filtra solo documentos válidos (con 'nombre' y 'precio').
    """
    query: dict = {
        "nombre": {"$exists": True, "$type": "string"},
        "precio": {"$exists": True, "$type": ["double", "int", "long", "decimal"]},
    }
    if q:
        query["nombre"]["$regex"] = q
        query["nombre"]["$options"] = "i"

    cursor = coll.find(query).skip(skip).limit(limit)
    items: list[ItemOut] = []
    async for doc in cursor:
        items.append(doc_to_itemout(doc))
    return ok(items)

@app.post("/items", response_model=ApiResponse[ItemOut], status_code=201, tags=["items"])
async def crear_item(item: ItemIn):
    """
    Crea un item (un documento por request).
    """
    res = await coll.insert_one(item.model_dump())
    doc = await coll.find_one({"_id": res.inserted_id})
    return ok(doc_to_itemout(doc), mensaje="creado", status=201)

@app.post("/items/bulk", response_model=ApiResponse[List[ItemOut]], status_code=201, tags=["items"])
async def crear_items_bulk(items: Sequence[ItemIn]):
    """
    Inserta varios items en una sola llamada.
    """
    payload = [it.model_dump() for it in items]
    res = await coll.insert_many(payload)
    cursor = coll.find({"_id": {"$in": res.inserted_ids}})
    out: list[ItemOut] = []
    async for d in cursor:
        out.append(doc_to_itemout(d))
    return ok(out, mensaje="creados", status=201)

@app.get("/items/{item_id}", response_model=ApiResponse[ItemOut], tags=["items"])
async def obtener_item(item_id: str):
    """
    Obtiene un item por su id.
    """
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="id invalido")
    doc = await coll.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return ok(doc_to_itemout(doc))

@app.put("/items/{item_id}", response_model=ApiResponse[ItemOut], tags=["items"])
async def actualizar_item(item_id: str, item: ItemIn):
    """
    Reemplazo total del item (PUT).
    """
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="id invalido")
    res = await coll.update_one({"_id": ObjectId(item_id)}, {"$set": item.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    doc = await coll.find_one({"_id": ObjectId(item_id)})
    return ok(doc_to_itemout(doc), mensaje="actualizado")

@app.delete("/items/{item_id}", response_model=ApiResponse[bool], tags=["items"])
async def eliminar_item(item_id: str):
    """
    Elimina un item por id.
    (Se devuelve 200 con {status, mensaje, data:true} para mantener el wrapper)
    """
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="id invalido")
    res = await coll.delete_one({"_id": ObjectId(item_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return ok(True, mensaje="eliminado")
