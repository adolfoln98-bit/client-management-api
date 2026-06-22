from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Depends
#from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from dotenv import load_dotenv

#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")
bearer_scheme = HTTPBearer()

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


pwd_context= CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashear_password(password: str)->str:
    return pwd_context.hash(password)

def verificar_password(password: str, hashed_password: str)-> bool:
    return pwd_context.verify(password, hashed_password)

def crear_access_token(user_id: int, rol:str):
    expiracion= datetime.now(timezone.utc)+timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)


    payload ={
        "sub": str(user_id),
        "rol": rol,
        "exp": expiracion
    }

    token= jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

def verificar_access_token(token: str):

    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Token invalido")
    
    user_id= payload.get("sub")
    user_rol= payload.get("rol")

    if user_id is None:
        raise ValueError("Token invalido")
    
    if user_rol is None:
        raise ValueError("Token invalido")

    return {
        "id": user_id,
        "rol": user_rol
    }

def get_usuario_actual(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials

    try:
        return verificar_access_token(token)
    except ValueError as error:
        raise HTTPException(status_code = 401, detail= str(error))

def get_admin_user(usuario_actual: dict):
    
    if usuario_actual.get("rol") != "admin":
        raise PermissionError("Permisos insuficientes")
    
    return usuario_actual
