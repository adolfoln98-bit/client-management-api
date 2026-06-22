# FastAPI Client Management API

API REST desarrollada con FastAPI para gestionar clientes, usuarios, autenticación JWT, roles y ownership de recursos.

## Tecnologías

- Python
- FastAPI
- SQLite
- Pydantic
- JWT
- Pytest
- TestClient
- dotenv

## Funcionalidades

- Registro de usuarios
- Login con JWT
- Protección de rutas mediante token
- Roles de usuario (`user` / `admin`)
- Gestión CRUD de clientes
- Ownership: cada usuario solo puede acceder a sus propios clientes
- Filtros, paginación y ordenación
- Validaciones con Pydantic
- Tests automatizados con Pytest
- Variables de entorno con `.env`

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt