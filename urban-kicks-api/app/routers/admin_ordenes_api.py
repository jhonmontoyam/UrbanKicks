# ============================================================
# ARCHIVO: app/routers/admin_ordenes_api.py
# PROPÓSITO: Rutas de API para el módulo administrativo de órdenes
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.database import get_connection
from app.services.auth_service import get_current_user
from app.schemas.auth import TokenData

class EstadoUpdate(BaseModel):
    estado: str
    notas: str | None = None

router = APIRouter(
    prefix="/admin/ordenes",
    tags=["Admin Órdenes"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
def listar_ordenes():
    """
    Obtiene el listado de órdenes con detalles de cliente.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            o.orden_id AS id, 
            o.cliente_id, 
            c.nombre + ' ' + c.apellido AS cliente_nombre, 
            c.email AS cliente_email,
            o.total_cop, 
            e.nombre AS estado, 
            o.fecha_orden AS fecha_creacion
        FROM dbo.ordenes o
        JOIN dbo.clientes c ON o.cliente_id = c.cliente_id
        JOIN dbo.estados_orden e ON o.estado_id = e.estado_id
        ORDER BY o.fecha_orden DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        ordenes = []
        for row in rows:
            ordenes.append({
                "id": row.id,
                "cliente_id": row.cliente_id,
                "cliente_nombre": row.cliente_nombre,
                "cliente_email": row.cliente_email,
                "total_cop": float(row.total_cop) if row.total_cop else 0,
                "estado": row.estado,
                "fecha_creacion": row.fecha_creacion.isoformat() if row.fecha_creacion else None
            })
            
        return ordenes

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar órdenes: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.get("/{orden_id}")
def detalle_orden(orden_id: int):
    """
    Obtiene el detalle específico de una orden.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Primero obtenemos la orden base para confirmar que existe
        query_orden = """
        SELECT o.orden_id AS id, e.nombre AS estado, o.total_cop, o.notas, o.fecha_orden AS fecha_creacion,
               c.nombre + ' ' + c.apellido as cliente_nombre, c.email as cliente_email,
               d.calle as direccion, d.municipio as ciudad, d.departamento
        FROM dbo.ordenes o
        JOIN dbo.clientes c ON o.cliente_id = c.cliente_id
        LEFT JOIN dbo.direcciones d ON o.direccion_id = d.direccion_id
        JOIN dbo.estados_orden e ON o.estado_id = e.estado_id
        WHERE o.orden_id = ?
        """
        cursor.execute(query_orden, (orden_id,))
        orden_row = cursor.fetchone()
        
        if not orden_row:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        # Obtenemos los ítems de la orden
        query_items = """
        SELECT detalle_id AS id, variante_sku, cantidad, precio_unitario_cop, subtotal_cop
        FROM dbo.orden_detalle
        WHERE orden_id = ?
        """
        cursor.execute(query_items, (orden_id,))
        items_rows = cursor.fetchall()
        
        items = []
        for item in items_rows:
            items.append({
                "id": item.id,
                "variante_sku": item.variante_sku,
                "cantidad": item.cantidad,
                "precio_unitario_cop": float(item.precio_unitario_cop) if item.precio_unitario_cop else 0,
                "subtotal_cop": float(item.subtotal_cop) if item.subtotal_cop else 0
            })

        return {
            "orden": {
                "id": orden_row.id,
                "estado": orden_row.estado,
                "total_cop": float(orden_row.total_cop) if orden_row.total_cop else 0,
                "notas": orden_row.notas,
                "fecha_creacion": orden_row.fecha_creacion.isoformat() if orden_row.fecha_creacion else None,
                "cliente": {
                    "nombre": orden_row.cliente_nombre,
                    "email": orden_row.cliente_email
                },
                "direccion": {
                    "direccion": orden_row.direccion,
                    "ciudad": orden_row.ciudad,
                    "departamento": orden_row.departamento
                }
            },
            "items": items
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar detalle de orden: {str(e)}")
    finally:
        if conn:
            conn.close()

@router.put("/{orden_id}/estado")
def actualizar_estado_orden(
    orden_id: int, 
    payload: EstadoUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Actualiza el estado y notas de una orden.
    Solo permitido para roles SuperAdmin y Vendedor.
    """
    # 1. Validación de Roles
    roles_permitidos = {"SuperAdmin", "Vendedor"}
    user_roles = set(current_user.roles)
    if not user_roles.intersection(roles_permitidos):
        raise HTTPException(
            status_code=403, 
            detail="Permisos insuficientes. Requiere rol SuperAdmin o Vendedor."
        )

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 2. Buscar el estado_id correspondiente al nombre enviado
        cursor.execute("SELECT estado_id FROM dbo.estados_orden WHERE nombre = ?", (payload.estado,))
        estado_row = cursor.fetchone()
        
        if not estado_row:
            raise HTTPException(status_code=400, detail=f"El estado '{payload.estado}' no es válido.")
        
        nuevo_estado_id = estado_row.estado_id

        # 3. Actualizar la orden
        if payload.notas is not None:
            query = "UPDATE dbo.ordenes SET estado_id = ?, notas = ? WHERE orden_id = ?"
            cursor.execute(query, (nuevo_estado_id, payload.notas, orden_id))
        else:
            query = "UPDATE dbo.ordenes SET estado_id = ? WHERE orden_id = ?"
            cursor.execute(query, (nuevo_estado_id, orden_id))
            
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        conn.commit()
        return {"mensaje": "Estado de la orden actualizado exitosamente."}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la orden: {str(e)}")
    finally:
        if conn:
            conn.close()
