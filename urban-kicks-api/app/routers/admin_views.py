# ============================================================
# ARCHIVO: app/routers/admin_views.py
# PROPÓSITO: Router de vistas HTML (Jinja2) para el panel admin.
#            Sirve las páginas de login y dashboard.
#            El dashboard valida el JWT via cookie para proteger
#            el acceso desde el navegador.
# ============================================================

from fastapi import APIRouter, Cookie, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.auth_service import get_current_user
from app.schemas.auth import TokenData
from jose import JWTError, jwt
from app.config import settings

# ----------------------------------------------------------
# Configuración de plantillas Jinja2.
# La carpeta templates se resuelve relativa al directorio app/.
# ----------------------------------------------------------
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

router = APIRouter(tags=["Admin Views"])


# ----------------------------------------------------------
# GET /admin/login — Sirve la página de login
# ----------------------------------------------------------
@router.get("/admin/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    """
    Renderiza la plantilla login.html con el sistema de diseño Urban Kicks.
    Si ya hay un token válido en la cookie, redirige al dashboard.
    """
    token = request.cookies.get("uk_admin_token")
    if token:
        try:
            jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        except JWTError:
            pass  # Token inválido → mostrar login

    return templates.TemplateResponse("login.html", {"request": request})


# ----------------------------------------------------------
# GET /admin/dashboard — Ruta protegida, requiere JWT en cookie
# ----------------------------------------------------------
@router.get("/admin/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard_page(request: Request, uk_admin_token: str | None = Cookie(default=None)):
    """
    Renderiza el dashboard admin. Requiere cookie 'uk_admin_token' con JWT válido.
    Si no hay token o es inválido, redirige a /admin/login.
    """
    if not uk_admin_token:
        return RedirectResponse(url="/admin/login", status_code=302)

    try:
        payload = jwt.decode(
            uk_admin_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username: str = payload.get("sub", "Admin")
    except JWTError:
        response = RedirectResponse(url="/admin/login", status_code=302)
        response.delete_cookie("uk_admin_token")
        return response

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "username": username},
    )


# ----------------------------------------------------------
# GET /admin/logout — Elimina la cookie y redirige al login
# ----------------------------------------------------------
@router.get("/admin/logout", include_in_schema=False)
def logout():
    """
    Cierra la sesión eliminando la cookie del token JWT.
    """
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("uk_admin_token")
    return response
