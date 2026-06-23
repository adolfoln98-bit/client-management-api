from db import conn
from models import ClienteBase, UsuarioCreate, UsuarioLogin
from security import (
    crear_access_token,
    hashear_password,
    verificar_password,
)



def fila_a_cliente(fila):
    return dict(fila)

#Funcion para trasformar los datos de la base de datos a json lejible por el codigo
def db_a_json (lista_db):
    return [fila_a_cliente(cliente) for cliente in lista_db]


def construir_metadatos(data: list, total: int, limit: int, offset: int):
    return {
        "data": db_a_json(data),
        "total": total,
        "limit": limit,
        "offset": offset,
    }

def construir_filtro_nombre(nombre: str):
    #Limpiamos los nombres pasados de posibles errores como comas duplicadas o espacios tanto al inicio como en medio como al final del string
    valores_limpios = [v.strip() for v in nombre.split(",") if v.strip()]
    
    #Si no hay datos salvables devolvemos None y una lista vacia
    if not valores_limpios:
        return None, []

    condiciones_nombre = []
    valores_nombre = []

    for valor in valores_limpios:
        valor = valor.lower()

        if valor.startswith("*") and valor.endswith("*"):
            patron = f"%{valor[1:-1]}%"
        elif valor.startswith("*"):
            patron = "%"+valor[1:]
        elif valor.endswith("*"):
            patron = valor[:-1]+"%"
        else:
            patron = "%"+valor+"%"

        condiciones_nombre.append("LOWER(nombre) LIKE ?")
        valores_nombre.append(patron)

    condicion_nombre = " OR ".join(condiciones_nombre)
    condicion_nombre = f"({condicion_nombre})"

    return condicion_nombre, valores_nombre


def construir_filtro_edad(edades):
    #Limpiamos las edeades pasadoa de posibles errores como comas duplicadas o espacios tanto al inicio como en medio como al final del string
    try:
        edades_filtradas = [int(v.strip()) for v in edades.split(",") if v.strip()]
    except ValueError:
        raise ValueError("Valores introducidos no validos")

    
    if not edades_filtradas:
        return None, []
    
    condiciones_edad = []

    for edad in edades_filtradas:
        if edad <0:
            raise ValueError("La edad no puede ser menor que 0")
        if edad >120:
            raise ValueError("La edad no puede ser mayor que 120")
        
        condiciones_edad.append("edad = ?")

    condicion_edad = " OR ".join(condiciones_edad)
    condicion_edad = f"({condicion_edad})"

    return condicion_edad, edades_filtradas



def listar_clientes(
        usuario_id: int,
        nombre: str = None,
        edades: str = None,
        edad_min: int = None,
        edad_max: int = None,
        limit: int = 10,
        offset: int = 0,
        sort_by: str = "id",
        order: str = "asc",
    ):

    query = "SELECT * FROM clientes"
    count_query = "SELECT COUNT(*) FROM clientes"
    condiciones = ["usuario_id = ?"]
    valores = [usuario_id]
    campos_validos = ["id", "nombre", "edad"]
    orden_valido = ["asc", "desc"]
    order = order.lower()

    if sort_by not in campos_validos:
        raise ValueError("Campo de ordenación no válido")
    
    if order not in orden_valido:
        raise ValueError("Campo de orden no valido")
    
    if nombre:
        condicion_nombre, valores_nombre = construir_filtro_nombre(nombre)
        if condicion_nombre:
            condiciones.append(condicion_nombre)
            valores.extend(valores_nombre)


    if edades is not None and (edad_min is not None or edad_max is not None):
        raise ValueError("No se pueden combinar edades exactas con rango de edad")

    if edad_min is not None and edad_max is not None:
        if edad_min > edad_max:
            raise ValueError("La edad minima no puede ser mayor a la edad maxima")
    
    if edad_min is not None:
        condiciones.append("edad >= ?")
        valores.append(edad_min)

    if edad_max is not None:
        condiciones.append("edad <= ?")
        valores.append(edad_max)


    if edades is not None:
        condicion_edad, valores_edad = construir_filtro_edad(edades)
        
        if condicion_edad:
            condiciones.append(condicion_edad)
            valores.extend(valores_edad)

    if condiciones:
        query += " WHERE "+" AND ".join(condiciones)
        count_query += " WHERE "+" AND ".join(condiciones)
    
    query += " ORDER BY "+sort_by+" "+order+" LIMIT ? OFFSET ?"
    valores_finales = valores + [limit, offset]
    
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute(count_query, valores)
        total_respuestas = cursor.fetchone()[0]

        cursor.execute(query, valores_finales)
        respuesta_db = cursor.fetchall()

    resultado = construir_metadatos(respuesta_db, total_respuestas, limit, offset)
    return resultado

def buscar_cliente_id(cliente_id: int, id_usuario: int):
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        Select * from clientes where id = ? AND usuario_id = ?
        """, (cliente_id, id_usuario))
        cliente = cursor.fetchone()
    if cliente:
        resultado = fila_a_cliente(cliente)
    else:
        return None
    return resultado

def crear_nuevo_cliente_db(cliente: ClienteBase, usuario_id: int):
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        Insert into clientes (nombre, edad, usuario_id) values(?,?,?)
        """, (cliente.nombre, cliente.edad, usuario_id))
        conexion.commit()
        ultimo_id = cursor.lastrowid
        cliente_added = cursor.rowcount
    if cliente_added > 0:
        return {
            "id": ultimo_id,
            "nombre": cliente.nombre,
            "edad": cliente.edad
        }
    else:
        return None

def actualizar_cliente_db(cliente_id: int, usuario_id: int, cliente:ClienteBase):
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        UPDATE clientes
        SET nombre = ?, edad= ?
        WHERE id = ? AND usuario_id = ?
        """, (cliente.nombre, cliente.edad, cliente_id, usuario_id))
        conexion.commit()
        cliente_actualizado = cursor.rowcount
    if cliente_actualizado > 0:
        with conn() as conexion:
            cursor = conexion.cursor()
            cursor.execute("""
                Select * from clientes WHERE id = ? AND usuario_id = ?
            """, (cliente_id, usuario_id))
            actualizado = cursor.fetchone()
        if actualizado:
            datos_actualizados = fila_a_cliente(actualizado)
        else:
            return None
    else:
        return None
    return datos_actualizados
    
def borrar_cliente_db(cliente_id, usuario_id: int):
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
            Delete from clientes WHERE id = ? AND usuario_id = ?  
            """, (cliente_id, usuario_id))
        conexion.commit()
        filas_borradas = cursor.rowcount

    if filas_borradas == 0:
        raise ValueError("Cliente no encontrado")

    return True

def registrar_usuario(usuario: UsuarioCreate):

    hashed_pass = hashear_password(usuario.password)

    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT id FROM usuarios WHERE email = ?
        """, (usuario.email,))
        existe_usuario = cursor.fetchone()
        if existe_usuario:
            raise ValueError("Ya existe un usuario registrado para este email.")
        cursor.execute("""
        INSERT INTO usuarios (email, password_hash) values (?,?)
        """, (usuario.email, hashed_pass))
        ultimo_id = cursor.lastrowid
    return {
        "id": ultimo_id,
        "email": usuario.email
    }

def login(usuario: UsuarioLogin):
    with conn() as conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        SELECT id, password_hash, rol FROM usuarios WHERE email = ?
        """, (usuario.email,))
        resultado = cursor.fetchone()
        if not resultado:
            raise ValueError("Credenciales incorrectas")
        password_hash = resultado[1]
        if not verificar_password(usuario.password, password_hash):
            raise ValueError("Credenciales incorrectas")
        
        token = crear_access_token(resultado[0], resultado[2])
        return {
            "access_token": token,
            "token_type": "bearer"
        }