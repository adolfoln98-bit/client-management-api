from fastapi import APIRouter, Depends, HTTPException, Query

from dependencies.auth import requerir_admin
from models import (
    ClienteBase,
    ClienteOut,
    ClientesResponse,
    OrderBy,
    SortBy,
)
from security import get_usuario_actual
from services.clientes_service import (
    actualizar_cliente_db,
    borrar_cliente_db,
    buscar_cliente_id,
    crear_nuevo_cliente_db,
    listar_clientes,
)


clientes_router = APIRouter(
    prefix="/clientes",
    tags=["clientes"]
)

@clientes_router.get("", response_model=ClientesResponse)
def get_clientes(
                nombre: str = None,
                edades: str | None = None,
                edad_min: int = Query(None, ge=0, le=120),
                edad_max: int = Query(None, ge=0, le=120),
                limit: int = Query(10, ge=1, le=100),
                page: int = Query(1, ge=1),
                sort_by: SortBy = SortBy.id,
                order: OrderBy = OrderBy.asc,
                usuario_actual: dict = Depends(get_usuario_actual)
    ):
    offset= (page-1) * limit
    usuario_id= int(usuario_actual["id"])
    try:
        resultado = listar_clientes (usuario_id= usuario_id,
                                     nombre = nombre,
                                     edades = edades,
                                     edad_min = edad_min, 
                                     edad_max = edad_max, 
                                     limit = limit, 
                                     offset = offset, 
                                     sort_by = sort_by, 
                                     order = order)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    
    resultado["page"] = page
    resultado["total_pages"] = (resultado["total"]+ resultado["limit"] -1) // resultado["limit"]
    return resultado

@clientes_router.get("/admin-test")
def admin_test(admin: dict= Depends(requerir_admin)):
        return {"mensaje": "Acceso admin permitido"}
    


@clientes_router.get("/{id_cliente}", response_model=ClienteOut)
def busca_cliente(
    id_cliente: int,
    usuario_actual: dict = Depends(get_usuario_actual)
    ):
    usuario_id= int(usuario_actual["id"])
    cliente = buscar_cliente_id(id_cliente, usuario_id)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente


@clientes_router.post("", status_code=201, response_model=ClienteOut)
def crea_cliente(
                cliente: ClienteBase,
                usuario_actual: dict = Depends(get_usuario_actual)
                ):
    
    usuario_id = int(usuario_actual["id"])
    nuevo_cliente = crear_nuevo_cliente_db(cliente, usuario_id)
    if nuevo_cliente is None:
        raise HTTPException(status_code=400, detail="No se pudo añadir al cliente")
    return nuevo_cliente
        
       
@clientes_router.put("/{id_cliente}", response_model=ClienteOut)
def actualiza_cliente(
                        id_cliente: int,
                        cliente: ClienteBase,
                        usuario_actual:dict = Depends(get_usuario_actual)
                    ): 
    usuario_id = int(usuario_actual["id"])  
    actualiza = actualizar_cliente_db(id_cliente, usuario_id, cliente)   
    if actualiza is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return actualiza

@clientes_router.delete("/{id_cliente}")
def borra_cliente(
                    id_cliente: int,
                    usuario_actual: dict = Depends(get_usuario_actual)
                ):
    usuario_id = int(usuario_actual["id"])
    try:
        borrar_cliente_db(id_cliente, usuario_id)
        return {"mensaje": "Cliente borrado"}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))




        
