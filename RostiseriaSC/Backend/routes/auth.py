# routes/auth.py
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr

from database import get_collection
from models import User, Role

# CONFIGURACIÓN (JWT)
SECRET_KEY = "tu_clave_secreta_super_segura_backend" # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Coincide/supera tu TiempoSesion.js

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Schemas para Auth ---
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    is_admin: bool  # Necesario para tu login.html

# --- Funciones ---
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Endpoints ---

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister):
    users_coll = get_collection("users")
    if await users_coll.find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=Role.USER # Por defecto es usuario normal
    )
    
    await users_coll.insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
    token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_email": new_user.email,
        "is_admin": False
    }

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin):
    users_coll = get_collection("users")
    user_doc = await users_coll.find_one({"email": user_in.email})
    
    if not user_doc or not verify_password(user_in.password, user_doc["hashed_password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    # Compatibilidad: Si no tiene rol en BD, asignamos basado en flag antigua
    if "role" not in user_doc:
        user_doc["role"] = Role.ADMIN if user_doc.get("is_admin") else Role.USER
        
    user = User(**user_doc)
    token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_email": user.email,
        "is_admin": user.is_admin # <--- Esto redirige tu frontend
    }