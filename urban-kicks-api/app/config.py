# ============================================================
# ARCHIVO: app/config.py
# PROPÓSITO: Leer y centralizar las variables de entorno del archivo .env.
#            Cualquier parte del proyecto que necesite configuración
#            la importa desde aquí, no directamente del .env.
# ============================================================

import os
from dotenv import load_dotenv

# load_dotenv() busca el archivo .env en la raíz del proyecto
# y carga cada variable como si fuera una variable de sistema operativo.
load_dotenv()


class Settings:
    """
    Clase que agrupa toda la configuración del proyecto.
    Al usar una clase, podemos acceder a los valores con
    autocompletado en el IDE: settings.db_server
    """
    db_server: str   = os.getenv("DB_SERVER", "localhost")
    db_name: str     = os.getenv("DB_NAME",   "urban_kicks_db")
    db_user: str     = os.getenv("DB_USER",   "")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_driver: str   = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")

    # Configuración de MongoDB
    mongo_uri: str   = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_db: str    = os.getenv("MONGO_DB", "urban_kicks_db")

    # ----------------------------------------------------------
    # Configuración JWT — Módulo de Autenticación Admin
    # ----------------------------------------------------------
    jwt_secret_key: str     = os.getenv("JWT_SECRET_KEY", "dev-secret-key-CHANGE-ME")
    jwt_algorithm: str      = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # ----------------------------------------------------------
    # Credenciales Admin (temporal — migrar a BD cuando exista admin_users)
    # ----------------------------------------------------------
    admin_username: str      = os.getenv("ADMIN_USERNAME", "admin@urbankicks.co")
    admin_password_hash: str = os.getenv("ADMIN_PASSWORD_HASH", "")


# Instancia única de Settings que todo el proyecto importará.
# Patrón conocido como "Singleton de configuración".
settings = Settings()
