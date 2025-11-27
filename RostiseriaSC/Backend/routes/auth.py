from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Annotated, List, Optional
from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field

from database import get_collection, settings
from models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "email": str(data["email"])})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("email")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_collection("users").find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403, detail="Se requieren permisos de administrador"
        )
    return current_user


# --------- Schemas locales ---------

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
    is_admin: bool


class UserOut(BaseModel):
    id: str = Field(alias="_id")
    name: str
    email: str
    is_admin: bool

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# --------- Endpoints ---------

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister):
    users = get_collection("users")
    if await users.find_one({"email": user_in.email}):
        raise HTTPException(status_code=400, detail="Email ya registrado")

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_admin=False,
    )
    await users.insert_one(new_user.model_dump(by_alias=True, exclude={"id"}))
    token = create_access_token({"email": new_user.email, "is_admin": False})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_email": new_user.email,
        "is_admin": False,
    }


@router.post("/login", response_model=Token)
async def login(form_data: UserLogin):
    user_doc = await get_collection("users").find_one({"email": form_data.email})
    if not user_doc or not verify_password(
        form_data.password, user_doc["hashed_password"]
    ):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    user = User(**user_doc)
    token = create_access_token({"email": user.email, "is_admin": user.is_admin})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_email": user.email,
        "is_admin": user.is_admin,
    }


@router.get("/admin/users", response_model=List[UserOut])
async def list_users(admin: Annotated[User, Depends(get_current_admin_user)]):
    users = await get_collection("users").find().to_list(100)
    return [UserOut(**u) for u in users]


@router.patch("/admin/users/{user_id}/role")
async def change_role(
    user_id: str, is_admin: bool, admin: Annotated[User, Depends(get_current_admin_user)]
):
    if str(admin.id) == user_id:
        raise HTTPException(status_code=400, detail="No puedes cambiar tu propio rol")

    res = await get_collection("users").update_one(
        {"_id": ObjectId(user_id)}, {"$set": {"is_admin": is_admin}}
    )
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"message": "Rol actualizado"}
