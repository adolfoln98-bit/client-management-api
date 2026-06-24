import uuid

def test_register_usuario_correcto(client):
    email = f"test_{uuid.uuid4()}@test.com"

    response = client.post("/api/auth/register", json = {
        "email": email,
        "password": "abc12345"
    })
    print(response.status_code)
    print(response.json())
    assert response.status_code in (200, 201)

    data = response.json()

    #Compruebo si los datos del test son correctos
    assert "id" in data
    assert isinstance (data["id"], int)
    assert data["email"] == email

    

def test_register_usuario_duplicado(client, usuario_registrado):
    #Con el usuario ya registrado en usuario_registrado intento registrarlo otra vez

    response = client.post("/api/auth/register", json = {
        "email": usuario_registrado["email"],
        "password": usuario_registrado["password"]
    })

#Compruebo si el test lanza un error si el correo ya existe
    assert response.status_code == 400
    assert response.json()["detail"] == "Ya existe un usuario registrado para este email."

def test_login_usuario_correcto(client, usuario_registrado):
    
    #inicio de sesion con el usuario creado en usuario_registrado
    response = client.post("/api/auth/login", json = {
        "email": usuario_registrado["email"],
        "password": usuario_registrado["password"]
    })

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["access_token"], str)
    assert response.json()["token_type"] == "bearer"

def test_login_password_incorrecto(client, usuario_registrado):

    #inicio de sesion con contraseña incorrecta
    response = client.post("/api/auth/login", json = {
        "email": usuario_registrado["email"],
        "password": "wrong1234"
    })

    assert response.status_code == 400

    assert response.json()["detail"] == "Credenciales incorrectas"

def test_login_usuario_incorrecto(client):
    #al no necesitar crear un usuario vamos directamente con la comprobacion ante un usuario inexistente
    response = client.post("/api/auth/login", json = {
        "email": "wrongemail@test.com",
        "password": "abc12345"
    })

    assert response.status_code==400
    assert response.json()["detail"]=="Credenciales incorrectas"

def test_get_cliente_sin_token(client):
    response = client.get("/api/clientes")

    
    assert response.status_code in (401, 403)

def test_get_cliente_token_valido(client, crear_usuario_test):

    usuario = crear_usuario_test()
    #accedemos con el token del usuario generado a la ruta protegida
    response = client.get("/api/clientes", headers = {
        "Authorization": f"Bearer {usuario['access_token']}"
    })

    assert response.status_code == 200

def test_crear_cliente_token_valido(client, crear_usuario_test):
    #Guardamos en una variable el usuario generado para usar sus datos
    usuario = crear_usuario_test()

    #ahora probamos a crear un cliente

    response= client.post("/api/clientes", json = {
        "nombre": "Ana",
        "edad": 25
    },headers = {
        "Authorization": f"Bearer {usuario['access_token']}"
    })

    #comprobamos si se ha creado correctamente el cliente
    assert response.status_code == 201

    data = response.json()

    #comprobamos que los datos se han guardado correctamente 
    assert "id" in data
    assert data["nombre"] == "Ana"
    assert data["edad"] == 25


def test_ownership_cliente(client, crear_usuario_test):
    #creamos el usuario A e iniciamos sesion, con este cliente crearemos un usuario
    usuario_a = crear_usuario_test()

    response_a= client.post("/api/clientes", json = {
        "nombre": "Juan",
        "edad": 35
    }, headers = {
        "Authorization": f"Bearer {usuario_a['access_token']}"
    })

    #comprobamos si se ha creado el cliente correctamente y guardamos el id del usuario creado
    assert response_a.status_code == 201
    id_cliente= response_a.json()["id"]

    #A continuacion creamos el usuario B, con el que intentaremos acceder al cliente creado anteriormente
    usuario_b = crear_usuario_test()

    response_b = client.get(f"/api/clientes/{id_cliente}", headers = {
        "Authorization": f"Bearer {usuario_b['access_token']}"
    })

    assert response_b.status_code == 404

def test_ownership_actualiza_cliente(client, crear_usuario_test):
    #Guardamos en una variable el usuario generado para usar sus datos
    usuario = crear_usuario_test()

    #ahora probamos a crear un cliente

    response= client.post("/api/clientes", json = {
        "nombre": "Ana",
        "edad": 25
    },headers = {
        "Authorization": f"Bearer {usuario['access_token']}"
    })

    #comprobamos si se ha creado correctamente el cliente
    assert response.status_code == 201

    #comprobamos que los datos se han guardado correctamente 
    data = response.json()
    assert "id" in data
    assert data["nombre"] == "Ana"
    assert data["edad"] == 25


def test_ownership_modifica_cliente(client, crear_usuario_test):

    #creamos el usuario A e iniciamos sesion, con este cliente crearemos un usuario
    usuario_a = crear_usuario_test()

    response_a = client.post("/api/clientes", json = {
        "nombre": "Juan",
        "edad": 35
    }, headers = {
        "Authorization": f"Bearer {usuario_a['access_token']}"
    })

    #comprobamos si se ha creado el cliente correctamente y guardamos el id del usuario creado
    assert response_a.status_code == 201
    id_cliente = response_a.json()["id"]

    #A continuacion creamos el usuario B, con el que intentaremos actualizar al cliente creado anteriormente
    usuario_b = crear_usuario_test()

    response_b= client.put(f"/api/clientes/{id_cliente}",json = {
        "nombre": "Roberto",
        "edad": 45,
        "id_cliente": id_cliente
    }, headers = {
        "Authorization": f"Bearer {usuario_b['access_token']}"
    })
    
    assert response_b.status_code == 404

    #A continucacion comprobamos si efectivamente no se ha modificado el cliente
    response_get= client.get(f"/api/clientes/{id_cliente}", headers={
        "Authorization": f"Bearer {usuario_a['access_token']}"
    })

    assert response_get.status_code == 200

    data= response_get.json()
    assert data["nombre"] == "Juan"
    assert data["edad"] == 35

def test_ownership_borra_cliente(client, crear_usuario_test):
    #creamos el usuario A con el que crearemos un cliente
    usuario_a= crear_usuario_test()
    response_a= client.post("/api/clientes", json = {
        "nombre": "Juan",
        "edad": 35
    }, headers = {
        "Authorization": f"Bearer {usuario_a['access_token']}"
    })

    #comprobamos si se ha creado el cliente correctamente y guardamos el id del cliente creado
    assert response_a.status_code == 201
    id_cliente = response_a.json()["id"]

    #A continuacion creamos el usuario B, con el que intentaremos actualizar al cliente creado anteriormente
    usuario_b = crear_usuario_test()

    response_b = client.delete(f"/api/clientes/{id_cliente}", headers={
        "Authorization": f"Bearer {usuario_b['access_token']}"
    })
    
    assert response_b.status_code == 404

    #A continucacion comprobamos si efectivamente no se ha modificado el cliente
    response_get = client.get(f"/api/clientes/{id_cliente}", headers = {
        "Authorization": f"Bearer {usuario_a['access_token']}"
    })

    assert response_get.status_code == 200
    data = response_get.json()

    assert data["nombre"] == "Juan"
    assert data["edad"] == 35
    

def test_filtrar_nombre(client, crear_usuario_test):
    #Creamos el usuario  y guardamos su token
    usuario= crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    clientes = [
    {"nombre": "Ana", "edad": 25},
    {"nombre": "Anabel", "edad": 45},
    {"nombre": "Mariana", "edad": 50},
    {"nombre": "Rossy", "edad": 30},
    ]
    
    #Creamos los clientes con los que realizaremos la comprobacion
    for cliente_data in clientes:
        client.post("/api/clientes", json=cliente_data, headers=header)

    
    #Realizamos la busqueda
    response= client.get("/api/clientes?nombre=ana", headers = {
        "Authorization": f"Bearer {usuario['access_token']}"
    })

    data= response.json()["data"]
    nombre_clientes=[cliente["nombre"] for cliente in data]

    assert set(nombre_clientes) == {"Ana", "Anabel", "Mariana"}

def test_filtrar_edad(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    clientes=[
    {"nombre": "Ana", "edad": 25},
    {"nombre": "Anabel", "edad": 45},
    {"nombre": "Mariana", "edad": 50},
    {"nombre": "Rossy", "edad": 30},
    ]
    
    #Creamos los clientes con los que realizaremos la comprobacion
    for cliente_data in clientes:
        client.post("/api/clientes", json = cliente_data, headers = header)

    
    #Realizamos la busqueda
    response = client.get("/api/clientes?edades=25,50", headers = header)

    #Guardamos el resultado de la busqueda y guardamos el resultado de la busqueda
    data = response.json()["data"]
    edad_clientes=[cliente["edad"] for cliente in data]

    assert set(edad_clientes) == {25, 50}

def test_filtrar_edad_erronea(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    response = client.get("/api/clientes?edades=abc", headers = header)

    data= response.json()

    assert response.status_code == 400
    assert data["detail"] == "Valores introducidos no validos"

def test_filtrar_rango_edad(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    clientes=[
    {"nombre": "Ana", "edad": 30},
    {"nombre": "Anabel", "edad": 45},
    {"nombre": "Mariana", "edad": 50},
    {"nombre": "Rossy", "edad": 60},
    ]

    for cliente_data in clientes:
        client.post("/api/clientes", json = cliente_data, headers = header)
    
    response = client.get("/api/clientes?edad_min=30&edad_max=50", headers = header)

    data= response.json()["data"]
    edad_en_rango = [cliente["edad"] for cliente in data]

    assert set(edad_en_rango) == {30, 45, 50}

def test_filtrar_rango_edad_erroneo(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    response= client.get("/api/clientes?edades=25,50&edad_min=30", headers = header)

    assert response.status_code == 400
    assert response.json()["detail"] == "No se pueden combinar edades exactas con rango de edad"


def test_get_cliente_token_invalido(client):
    response = client.get("/api/clientes", headers={
        "Authorization": f"Bearer token_invalido"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalido"

def test_usuario_admin_error(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }
    #Intentamos acceder a un end-point solo para admins con un usuario que no lo es
    response = client.get("/api/clientes/admin-test", headers = header)

    assert response.status_code == 403
    assert response.json()["detail"] == "Permisos insuficientes"

def test_paginacion(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    clientes = [
    {"nombre": "Ana", "edad": 30},
    {"nombre": "Anabel", "edad": 45},
    {"nombre": "Mariana", "edad": 50},
    {"nombre": "Rossy", "edad": 60},
    {"nombre": "Jose", "edad":23}
    ]

    for cliente_data in clientes:
        client.post("/api/clientes", json=cliente_data, headers=header)

    response= client.get("/api/clientes?limit=2&page=2", headers=header)

    assert response.status_code == 200

    data= response.json()

    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["page"] == 2
    assert data["offset"] == 2
    assert data["total_pages"] == 3
    assert len(data["data"]) == 2

def test_sort_by(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }
    clientes = [
    {"nombre": "Ana", "edad": 30},
    {"nombre": "Anabel", "edad": 45},
    {"nombre": "Mariana", "edad": 50},
    {"nombre": "Rossy", "edad": 60},
    {"nombre": "Jose", "edad":23}
    ]

    for cliente_data in clientes:
        client.post("/api/clientes", json = cliente_data, headers = header)

    response = client.get("/api/clientes?sort_by=edad&order=desc", headers = header)

    data = response.json()["data"]

    edades_clientes = [cliente["edad"] for cliente in data]

    assert edades_clientes == sorted(edades_clientes, reverse = True)

def test_edad_min_mayor_edad_max(client, crear_usuario_test):
    usuario = crear_usuario_test()
    header = {
        "Authorization": f"Bearer {usuario['access_token']}"
    }

    response = client.get("/api/clientes?edad_min=50&edad_max=30", headers=header)

    assert response.status_code == 400
    assert response.json()["detail"] == "La edad minima no puede ser mayor a la edad maxima"