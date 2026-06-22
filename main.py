from fastapi import FastAPI
from routes.clientes import clientes_router
from routes.auth import auth_router
from db import init_db


app = FastAPI()

init_db()

app.include_router(clientes_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


