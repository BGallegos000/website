from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from database import get_collection
from models import User, Role

SECRET_KEY = "tu_clave_secreta"
ALGORITHM = "HS256"
router = APIRouter(prefix="/auth", tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserReg(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLog(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    is_admin: bool

def get_password_hash(password): return pwd_context.hash(password)
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_token(data):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=60)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/register", response_model=Token)
async def register(u: UserReg):
    if await get_collection("users").find_one({"email": u.email}):
        raise HTTPException(400, "Email registrado")
    new_user = User(name=u.name, email=u.email, hashed_password=get_password_hash(u.password))
    await get_collection("users").insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
    return {"access_token": create_token({"sub": u.email}), "token_type": "bearer", "user_email": u.email, "is_admin": False}

@router.post("/login", response_model=Token)
async def login(u: UserLog):
    user = await get_collection("users").find_one({"email": u.email})
    if not user or not verify_password(u.password, user["hashed_password"]):
        raise HTTPException(401, "Credenciales inválidas")
    
    # Compatibilidad rol antiguo
    if "role" not in user: user["role"] = Role.ADMIN if user.get("is_admin") else Role.USER
    u_obj = User(**user)
    
    return {"access_token": create_token({"sub": u_obj.email}), "token_type": "bearer", "user_email": u_obj.email, "is_admin": u_obj.is_admin}