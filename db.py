import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_URL", "data/clientes.db")

def conn():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion
def init_db():
    with conn() as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'user'
        )
        """)

        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cliente_usuario_id
        ON clientes(usuario_id)
        """)
        conexion.commit()