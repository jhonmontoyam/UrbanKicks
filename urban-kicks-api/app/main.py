# ============================================================
# ARCHIVO: app/main.py
# PROPÓSITO: Punto de entrada principal de la aplicación FastAPI.
#            Configura la app, middlewares, archivos estáticos,
#            templates Jinja2 y registra todos los routers.
# ============================================================

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import productos, ordenes, auth, admin_views

# -------------------------------------------------------
# Creación de la instancia principal de FastAPI.
# -------------------------------------------------------
app = FastAPI(
    title="Urban Kicks API",
    description=(
        "API Backend del E-Commerce Urban Kicks. "
        "Gestión de catálogo de zapatillas, inventario, "
        "clientes y órdenes en Pesos Colombianos (COP). "
        "Construida con FastAPI + Microsoft SQL Server + MongoDB."
    ),
    version="2.4.0",
    contact={"name": "Equipo Urban Kicks"},
)


# -------------------------------------------------------
# Middleware CORS — permite llamadas desde el frontend
# durante el desarrollo local. Restringir en producción.
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# Archivos estáticos: CSS, JS, imágenes del admin panel.
# Accesibles en http://127.0.0.1:8000/static/...
# -------------------------------------------------------
_static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(_static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


# -------------------------------------------------------
# Registro de routers
# -------------------------------------------------------
# — API REST (prefijo /api/v1)
app.include_router(productos.router,   prefix="/api/v1")
app.include_router(ordenes.router,     prefix="/api/v1")
app.include_router(auth.router,        prefix="/api/v1")

# — Vistas HTML admin (sin prefijo — rutas: /admin/login, /admin/dashboard)
app.include_router(admin_views.router)


# -------------------------------------------------------
# Endpoint raíz: redirige al login del panel admin.
# -------------------------------------------------------
@app.get("/", include_in_schema=False)
def root():
    """
    Redirige la raíz al panel de login de administración.
    """
    return RedirectResponse(url="/admin/login")
