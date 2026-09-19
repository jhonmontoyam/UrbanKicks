# ============================================================
# ARCHIVO: app/schemas/auth.py
# PROPÓSITO: Modelos Pydantic para el módulo de autenticación.
#            Define las estructuras de entrada y salida del endpoint
#            de login y el payload del token JWT.
# ============================================================

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Cuerpo del POST /api/v1/auth/login.
    username puede ser correo o nombre de usuario.
    """
    username: str
    password: str


class TokenResponse(BaseModel):
    """
    Respuesta exitosa del endpoint de login.
    Devuelve el JWT y el tipo de token (siempre 'bearer').
    """
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Payload decodificado del JWT.
    'sub' (subject) identifica al usuario autenticado.
    """
    sub: str | None = None
