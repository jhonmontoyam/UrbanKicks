# ============================================================
# ARCHIVO: app/schemas/orden.py
# PROPÓSITO: Definir los esquemas de validación (Pydantic) 
#            para procesar nuevas órdenes que irán a SQL Server.
# ============================================================

from pydantic import BaseModel, Field
from typing import List, Optional


class OrdenItemCreate(BaseModel):
    """
    Representa una línea (detalle) dentro del carrito de compras.
    """
    variante_sku: str = Field(..., description="El SKU exacto de la variante comprada en MongoDB.")
    cantidad: int = Field(..., gt=0, description="Cantidad comprada (debe ser mayor a 0).")
    precio_unitario_cop: int = Field(..., ge=0, description="Precio unitario al momento de la compra (histórico).")


class OrdenCreate(BaseModel):
    """
    Payload principal que envía el Frontend cuando un cliente da clic en 'Pagar'.
    """
    cliente_id: int
    direccion_id: int
    total_cop: int = Field(..., ge=0, description="Suma total a cobrar.")
    notas: Optional[str] = None
    items: List[OrdenItemCreate] = Field(..., min_length=1, description="El pedido debe tener al menos un ítem.")
