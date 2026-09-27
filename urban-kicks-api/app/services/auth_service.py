# ============================================================
# ARCHIVO: app/services/auth_service.py
# PROPÓSITO: Capa de servicio para la autenticación.
#            Contiene toda la lógica de negocio relacionada con:
#            - Verificación de contraseñas con bcrypt
#            - Autenticación de usuarios admin
#            - Generación y validación de tokens JWT
#            - Dependencia de seguridad reutilizable para rutas protegidas
# ============================================================

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
import bcrypt

from app.config import settings
from app.schemas.auth import TokenData
from app.database import get_connection

# ----------------------------------------------------------
# Esquema de seguridad HTTP Bearer.
# FastAPI lo expone en /docs como candado de autorización.
# ----------------------------------------------------------
bearer_scheme = HTTPBearer()


# ----------------------------------------------------------
# FUNCIÓN: verify_password
# Compara la contraseña en texto plano con el hash almacenado.
# ----------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Retorna True si la contraseña coincide con el hash bcrypt.
    """
    try:
        # Asegurar que el hash de la BD no tenga espacios extra (strip)
        # bcrypt.checkpw requiere que ambos parámetros sean bytes
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.strip().encode('utf-8'))
    except Exception as e:
        print(f"Error en verify_password: {e}")
        return False


# ----------------------------------------------------------
# FUNCIÓN: authenticate_user
# Verifica que username y password sean válidos para el admin.
# Actualmente consulta .env; migrar a BD cuando exista admin_users.
# ----------------------------------------------------------
def authenticate_user(username: str, password: str) -> bool:
    """
    Retorna True si las credenciales son correctas (consultando la base de datos).
    El username corresponde al email del empleado.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT password_hash, activo FROM dbo.empleados WHERE email = ?"
        cursor.execute(query, (username,))
        row = cursor.fetchone()
        
        if not row:
            return False
            
        password_hash_db, activo = row
        
        if not activo:
            return False
            
        is_valid = verify_password(password, password_hash_db)
        
        # Opcional: Actualizar el último acceso si fue exitoso
        if is_valid:
            update_query = "UPDATE dbo.empleados SET ultimo_login = GETDATE() WHERE email = ?"
            cursor.execute(update_query, (username,))
            conn.commit()
            
        return is_valid
        
    except Exception as e:
        print(f"Error en authenticate_user: {e}")
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# ----------------------------------------------------------
# FUNCIÓN: get_user_roles
# Obtiene la lista de nombres de roles de un usuario
# ----------------------------------------------------------
def get_user_roles(email: str) -> list[str]:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT r.nombre 
        FROM dbo.roles r
        JOIN dbo.empleados_roles er ON r.rol_id = er.rol_id
        JOIN dbo.empleados e ON er.empleado_id = e.empleado_id
        WHERE e.email = ?
        """
        cursor.execute(query, (email,))
        rows = cursor.fetchall()
        return [row.nombre for row in rows]
    except Exception as e:
        print(f"Error en get_user_roles: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()


# ----------------------------------------------------------
# FUNCIÓN: create_access_token
# Genera un token JWT firmado con HS256 y una fecha de expiración.
# ----------------------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Crea y retorna un JWT firmado.
    'data' debe contener al menos {'sub': username}.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.jwt_expire_minutes)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# ----------------------------------------------------------
# DEPENDENCIA: get_current_user
# Se inyecta en rutas protegidas con Depends(get_current_user).
# Decodifica el Bearer token y retorna el payload TokenData.
# Lanza HTTP 401 si el token es inválido o expirado.
# ----------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    """
    Dependencia de seguridad FastAPI.
    Extrae y valida el JWT del header Authorization: Bearer <token>.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Vuelve a iniciar sesión.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject: str | None = payload.get("sub")
        roles: list[str] = payload.get("roles", [])
        if subject is None:
            raise credentials_exception
        return TokenData(sub=subject, roles=roles)
    except JWTError:
        raise credentials_exception
