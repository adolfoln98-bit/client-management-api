import pytest
import uuid
import os
from dotenv import load_dotenv

load_dotenv(".env.test", override=True)

TEST_DB_PATH = os.getenv("DATABASE_URL")

if TEST_DB_PATH and os.path.exists(TEST_DB_PATH):
    os.remove(TEST_DB_PATH)

from db import init_db, conn

init_db()

from fastapi.testclient import TestClient
from main import app



@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_registrado(client):
    email = f"test_{uuid.uuid4()}@test.com"
    password = "abcd12345"
    
    response_registro= client.post("/api/auth/register", json={
        "email":email,
        "password": password
    })
    
    return {
        "id":response_registro.json()["id"],
        "email":email,
        "password": password
    }

@pytest.fixture
def crear_usuario_test(client):
    def _crear_usuario_test():
        email = f"test_{uuid.uuid4()}@test.com"
        password = "abcd12345"
    
        response_registro = client.post("/api/auth/register", json={
            "email": email,
            "password": password

    })
        data_registro= response_registro.json()
        #Se realiza el inicio de sesion
        response_login= client.post("/api/auth/login", json={
            "email": email,
            "password": password
        })

        data_login = response_login.json()

        return {
            "id": data_registro["id"],
            "email": email,
            "password": password,
            "access_token": data_login["access_token"]
        }
    
    return _crear_usuario_test

@pytest.fixture(autouse=True)
def borrar_db():
    yield

    with conn() as conexion:
        cursor = conexion.cursor()

        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM usuarios")

        conexion.commit()