from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum

class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50)
    edad: int = Field(..., ge=0, le=120)
    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str):
        value= value.strip()
        if not value:
            raise ValueError("El nombe debe tener al menos un caracter")
        return value

class ClienteOut(ClienteBase):
    id: int

class ClientesResponse(BaseModel):
    data: list[ClienteOut]
    total: int
    limit: int
    offset: int
    page: int
    total_pages: int

class UsuarioBase(BaseModel):
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: str):
        if not any(caracter.isalpha() for caracter in value):
            raise ValueError("La contraseña debe tener al menos una letra")
        if not any(caracter.isdigit() for caracter in value):
            raise ValueError("La contraseña debe tener al menos un numero")
        
        return value

class UsuarioOut(UsuarioBase):
    id: int

class UsuarioLogin(UsuarioBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class OrderBy(str, Enum):
    asc = "asc"
    desc = "desc"

class SortBy(str, Enum):
    id = "id"
    nombre = "nombre"
    edad = "edad"