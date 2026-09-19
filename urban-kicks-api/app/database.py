# ============================================================
# ARCHIVO: app/database.py
# PROPÓSITO: Gestionar la conexión a Microsoft SQL Server con pyodbc.
#            Este archivo es el único lugar del proyecto que sabe
#            "cómo hablar" con la base de datos.
# ============================================================

import pyodbc
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

# Variable global para mantener el pool de conexiones a MongoDB en FastAPI
mongo_client = None

def get_mongo_db():
    """
    Retorna la instancia asíncrona de la base de datos MongoDB.
    Si el cliente no existe, lo inicializa.
    """
    global mongo_client
    if mongo_client is None:
        mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    return mongo_client[settings.mongo_db]

def get_connection() -> pyodbc.Connection:
    """
    Crea y retorna una conexión activa a SQL Server.

    Soporta dos modalidades automáticamente:
    1. Autenticación de Windows (Integrated Security / Trusted Connection):
       Si DB_USER está vacío en el .env, se conecta con la cuenta de Windows actual.
    2. Autenticación SQL:
       Si DB_USER tiene un valor, usa usuario y contraseña (UID/PWD).
    """
    # Si hay usuario definido, usamos Autenticación SQL
    if settings.db_user and settings.db_user.strip():
        connection_string = (
            f"DRIVER={{{settings.db_driver}}};"
            f"SERVER={settings.db_server};"
            f"DATABASE={settings.db_name};"
            f"UID={settings.db_user};"
            f"PWD={settings.db_password};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
    else:
        # Autenticación de Windows (Integrated Security / Trusted Connection)
        connection_string = (
            f"DRIVER={{{settings.db_driver}}};"
            f"SERVER={settings.db_server};"
            f"DATABASE={settings.db_name};"
            "Trusted_Connection=yes;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

    connection = pyodbc.connect(connection_string)
    return connection
