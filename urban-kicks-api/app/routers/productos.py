# ============================================================
# ARCHIVO: app/routers/productos.py
# PROPÓSITO: Rutas asíncronas para leer el catálogo de MongoDB.
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.database import get_mongo_db
from app.schemas.producto import ProductoResumen, ProductoDetalle

router = APIRouter(
    prefix="/productos",
    tags=["Catálogo (MongoDB)"],
)


@router.get(
    "/",
    response_model=List[ProductoResumen],
    summary="Listar catálogo con filtros",
    description="Retorna los productos activos desde MongoDB. Soporta filtrado opcional por categoría y marca."
)
async def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría (ej. Zapatillas)"),
    marca: Optional[str] = Query(None, description="Filtrar por nombre de marca (ej. Nike)")
):
    """
    Endpoint Asíncrono (async/await)
    Usa 'motor' para hacer consultas a MongoDB sin bloquear el servidor.
    """
    try:
        db = get_mongo_db()
        coleccion = db["productos"]

        # 1. Construir la consulta dinámicamente
        query = {"activo": True}
        if categoria:
            query["categoria"] = categoria
        if marca:
            query["marca.nombre"] = marca

        # 2. Ejecutar la búsqueda en Mongo (usando índices si existen)
        cursor = coleccion.find(query)
        
        # 3. Convertir el cursor asíncrono a una lista de Python
        productos_lista = await cursor.to_list(length=100)
        
        # MongoDB retorna el ID como '_id' de tipo ObjectId.
        # Pydantic mapeará esto mágicamente al campo 'id' string 
        # gracias a populate_by_name = True, pero necesitamos convertir el ObjectId a string.
        for prod in productos_lista:
            prod["_id"] = str(prod["_id"])

        return productos_lista

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error consultando MongoDB: {str(e)}")


@router.get(
    "/buscar",
    response_model=List[ProductoResumen],
    summary="Búsqueda por texto",
    description="Busca en el nombre y descripción utilizando el índice '$text' de MongoDB."
)
async def buscar_productos(
    q: str = Query(..., min_length=2, description="Término a buscar (ej. Jordan)")
):
    try:
        db = get_mongo_db()
        # Aprovechamos el índice { "nombre": "text", "descripcion": "text" }
        query = {
            "activo": True,
            "$text": { "$search": q }
        }
        
        cursor = db["productos"].find(query)
        productos_lista = await cursor.to_list(length=100)

        for prod in productos_lista:
            prod["_id"] = str(prod["_id"])

        return productos_lista

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en búsqueda de texto: {str(e)}")
