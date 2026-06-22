from fastapi import APIRouter, HTTPException

from models import Token, UsuarioCreate, UsuarioLogin, UsuarioOut
from services.clientes_service import login, registrar_usuario


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UsuarioOut)
def register(usuario: UsuarioCreate):
    try:
        return registrar_usuario(usuario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@auth_router.post("/login", response_model=Token)
def user_login(usuario: UsuarioLogin):
    try:
        return login(usuario)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))