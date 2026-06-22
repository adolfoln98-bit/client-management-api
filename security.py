import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

bearer_scheme = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashear_password(password: str) -> str:
    return pwd_context.hash(password)


def verificar_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def crear_access_token(user_id: int, rol: str) -> str:
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "rol": rol,
        "exp": expiracion,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verificar_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")

    user_id = payload.get("sub")
    user_rol = payload.get("rol")

    if user_id is None or user_rol is None:
        raise ValueError("Invalid token")

    return {
        "id": user_id,
        "rol": user_rol,
    }


def get_usuario_actual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    token = credentials.credentials

    try:
        return verificar_access_token(token)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))


def get_admin_user(usuario_actual: dict) -> dict:
    if usuario_actual.get("rol") != "admin":
        raise PermissionError("Insufficient permissions")

    return usuario_actual