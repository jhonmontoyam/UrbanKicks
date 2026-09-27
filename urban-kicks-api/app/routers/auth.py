# ============================================================
# ARCHIVO: app/routers/auth.py
# PROPÓSITO: Router REST para autenticación.
#            Expone el endpoint POST /api/v1/auth/login que
#            verifica credenciales y emite un token JWT Bearer.
# ============================================================

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, create_access_token
from app.config import settings

# ----------------------------------------------------------
# Creación del router con prefijo y tag para la documentación.
# Se monta en main.py bajo /api/v1, quedando:
#   POST /api/v1/auth/login
# ----------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Inicio de sesión admin",
    description=(
        "Recibe credenciales de administrador y devuelve un token JWT Bearer. "
        "El token debe enviarse en el header `Authorization: Bearer <token>` "
        "para acceder a rutas protegidas."
    ),
)
def login(credentials: LoginRequest) -> TokenResponse:
    """
    Endpoint de autenticación para el panel de administración Urban Kicks.

    - Verifica username y password contra las credenciales configuradas en .env.
    - En caso de éxito, emite un JWT firmado con HS256.
    - En caso de fallo, devuelve HTTP 401 con mensaje descriptivo.
    """
    # 1. Verificar credenciales
    is_valid = authenticate_user(credentials.username, credentials.password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas. Acceso denegado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Obtener roles y crear token JWT con el username como subject
    from app.services.auth_service import get_user_roles
    roles = get_user_roles(credentials.username)
    
    access_token = create_access_token(
        data={"sub": credentials.username, "roles": roles},
        expires_delta=timedelta(minutes=settings.jwt_expire_minutes),
    )

    return TokenResponse(access_token=access_token, token_type="bearer")
