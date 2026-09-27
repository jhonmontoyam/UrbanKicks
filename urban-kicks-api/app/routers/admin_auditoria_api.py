# ============================================================
# ARCHIVO: app/routers/admin_auditoria_api.py
# PROPÓSITO: Rutas de API para el log de auditoría.
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.database import get_connection
from app.services.auth_service import get_current_user
from app.schemas.auth import TokenData

router = APIRouter(
    prefix="/admin/auditoria",
    tags=["Admin Auditoría"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/ordenes")
def listar_auditoria_ordenes(current_user: TokenData = Depends(get_current_user)):
    """
    Obtiene el historial de cambios de estado de las órdenes.
    Solo permitido para el rol SuperAdmin.
    """
    if "SuperAdmin" not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado. Se requiere rol SuperAdmin."
        )

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            l.log_id,
            l.orden_id,
            e1.nombre AS estado_anterior,
            e2.nombre AS estado_nuevo,
            l.fecha_cambio,
            l.usuario_db
        FROM dbo.log_auditoria_ordenes l
        JOIN dbo.estados_orden e1 ON l.estado_anterior = e1.estado_id
        JOIN dbo.estados_orden e2 ON l.estado_nuevo = e2.estado_id
        ORDER BY l.fecha_cambio DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        logs = []
        for row in rows:
            logs.append({
                "log_id": row.log_id,
                "orden_id": row.orden_id,
                "estado_anterior": row.estado_anterior,
                "estado_nuevo": row.estado_nuevo,
                "fecha_cambio": row.fecha_cambio.isoformat() if row.fecha_cambio else None,
                "usuario_db": row.usuario_db
            })

        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar auditoría: {str(e)}")
    finally:
        if conn:
            conn.close()
