from fastapi import FastAPI

from db import init_db
from routes.auth import auth_router
from routes.clientes import clientes_router


app = FastAPI(
    title="Client Management API",
    description="REST API built with FastAPI featuring JWT authentication, roles, ownership and automated tests.",
    version="1.0.0",
)

init_db()

app.include_router(clientes_router, prefix="/api")
app.include_router(auth_router, prefix="/api")