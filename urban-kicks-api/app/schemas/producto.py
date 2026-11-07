# ============================================================
# ARCHIVO: app/schemas/producto.py
# PROPÓSITO: Definir los esquemas Pydantic para los documentos
#            del catálogo en MongoDB (lectura, creación, edición
#            y ajuste de stock).
# ============================================================

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MarcaSchema(BaseModel):
    nombre: str
    paisOrigen: str


class ColorSchema(BaseModel):
    nombre: str
    hex: str


class VarianteSchema(BaseModel):
    sku: str
    talla: str
    color: ColorSchema
    precioAdicionalCop: int = 0
    stock: int = 0


class ProductoResumen(BaseModel):
    """
    Esquema simplificado para el listado general (vitrina).
    Omite la descripción larga, atributos extras e inventario profundo.
    """
    id: str = Field(alias="_id")  # MongoDB usa _id como llave primaria
    nombre: str
    marca: MarcaSchema
    categoria: str
    precioBaseCop: int
    imagenes: List[str] = []
    activo: bool

    class Config:
        populate_by_name = True  # Permite mapear _id a id


class ProductoDetalle(ProductoResumen):
    """
    Hereda del Resumen y añade los campos completos para ver 
    el detalle de un producto específico.
    """
    descripcion: Optional[str] = None
    atributosEspecificos: Optional[dict] = None
    variantes: List[VarianteSchema]
    fechaCreacion: Optional[datetime] = None


class ProductoCreate(BaseModel):
    """
    Esquema para crear un nuevo producto en MongoDB.
    Garantiza que cumpla con las reglas del validator JSON Schema de MongoDB.
    """
    nombre: str = Field(..., min_length=2, description="Nombre comercial del producto")
    marca: MarcaSchema
    categoria: str = Field(..., description="Categoría (ej: Zapatillas, Ropa Urbana, Accesorios)")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la prenda/calzado")
    precioBaseCop: int = Field(..., ge=0, description="Precio base en pesos colombianos (entero >= 0)")
    imagenes: List[str] = Field(default_factory=list, description="Lista de URLs de fotos")
    atributosEspecificos: Optional[dict] = Field(default_factory=dict, description="Atributos libres NoSQL")
    variantes: List[VarianteSchema] = Field(..., min_length=1, description="Al menos una variante con SKU y stock")
    activo: bool = Field(True, description="Si el producto está publicado en catálogo")


class ProductoUpdate(BaseModel):
    """
    Esquema para actualizar datos de un producto existente.
    Todos los campos son opcionales para permitir actualizaciones parciales.
    """
    nombre: Optional[str] = None
    marca: Optional[MarcaSchema] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    precioBaseCop: Optional[int] = Field(None, ge=0)
    imagenes: Optional[List[str]] = None
    atributosEspecificos: Optional[dict] = None
    variantes: Optional[List[VarianteSchema]] = None
    activo: Optional[bool] = None


class AjusteStockRequest(BaseModel):
    """
    Esquema exclusivo para que el rol GestorInventario ajuste
    el stock físico de una variante específica mediante su SKU.
    """
    sku: str = Field(..., description="Código SKU de la variante a modificar")
    nuevoStock: int = Field(..., ge=0, description="Cantidad física real en inventario (>= 0)")
    motivo: Optional[str] = Field(None, description="Motivo del ajuste (ej: Conteo físico, Recepción lote, Devolución)")
