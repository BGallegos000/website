from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Annotated
from bson import ObjectId

from database import get_collection, settings
from models import User, PyObjectId, OrderStatus, CHILE_TIMEZONE

router = APIRouter(prefix="/auth", tags=["Auth & Users"])

# --- Configuración de Seguridad ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "sub": str(data["email"])})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Función de dependencia para obtener el usuario actual
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email: str = payload.get("email")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    users_col = get_collection("users")
    user_doc = await users_col.find_one({"email": user_email})
    if user_doc is None:
        raise credentials_exception
    return User(**user_doc)

# Función de dependencia para requerir admin
async def get_current_admin_user(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado. Se requiere rol de administrador.")
    return current_user

# --- Modelos de Entrada/Salida ---
class UserIn(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: EmailStr
    is_admin: bool

class UserOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    email: EmailStr
    is_admin: bool

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# --- Rutas ---

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserIn):
    users_col = get_collection("users")
    user_doc = await users_col.find_one({"email": user_in.email})
    if user_doc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado.")

    hashed_password = get_password_hash(user_in.password)
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        is_admin=False  # Por defecto no es admin
    )

    inserted = await users_col.insert_one(new_user.model_dump(by_alias=True, exclude_none=True, exclude={'id'}))
    
    # Crear token JWT
    access_token = create_access_token(data={"email": user_in.email, "is_admin": False})
    
    return Token(
        access_token=access_token,
        user_email=user_in.email,
        is_admin=False
    )

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: UserLogin):
    users_col = get_collection("users")
    user_doc = await users_col.find_one({"email": form_data.email})

    if not user_doc or not verify_password(form_data.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo y/o contraseña inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = User(**user_doc)
    access_token = create_access_token(data={"email": user.email, "is_admin": user.is_admin})
    
    return Token(
        access_token=access_token,
        user_email=user.email,
        is_admin=user.is_admin
    )

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

# Ruta para que el admin pueda ver todos los usuarios
@router.get("/admin/users", response_model=List[UserOut])
async def list_all_users(admin_user: Annotated[User, Depends(get_current_admin_user)]):
    users_col = get_collection("users")
    users = await users_col.find().to_list(100)
    return [UserOut(**u) for u in users]

# Ruta para gestionar el rol de admin
@router.patch("/admin/users/{user_id}/role")
async def update_user_role(user_id: str, is_admin: bool, admin_user: Annotated[User, Depends(get_current_admin_user)]):
    users_col = get_collection("users")
    
    if user_id == str(admin_user.id):
        raise HTTPException(status_code=400, detail="No puedes modificar tu propio rol de administrador.")

    result = await users_col.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_admin": is_admin}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    return {"message": f"Rol de administrador actualizado para el usuario {user_id}."}
