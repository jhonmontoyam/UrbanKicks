# ============================================================
# ARCHIVO: app/schemas/producto.py
# PROPÓSITO: Definir los esquemas Pydantic para los documentos
#            del catálogo en MongoDB.
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
    imagenes: List[str]
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
