# ============================================================
# ARCHIVO: app/routers/admin_productos_api.py
# PROPÓSITO: Rutas de API para la gestión de productos y stock en MongoDB.
#            Protegido para usuarios con rol 'GestorInventario' y 'SuperAdmin'.
# ============================================================

from datetime import datetime, timezone
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_mongo_db
from app.schemas.auth import TokenData
from app.services.auth_service import get_current_user
from app.schemas.producto import (
    ProductoCreate,
    ProductoUpdate,
    ProductoDetalle,
    ProductoResumen,
    AjusteStockRequest,
)

router = APIRouter(
    prefix="/admin/productos",
    tags=["Admin Productos (MongoDB)"],
    dependencies=[Depends(get_current_user)],
)


def verificar_gestor_inventario(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Dependencia de autorización:
    Verifica que el usuario autenticado tenga el rol GestorInventario o SuperAdmin.
    """
    roles_permitidos = {"SuperAdmin", "GestorInventario"}
    user_roles = set(current_user.roles)
    if not user_roles.intersection(roles_permitidos):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permisos insuficientes. Requiere rol GestorInventario o SuperAdmin.",
        )
    return current_user


@router.get(
    "/",
    response_model=List[ProductoDetalle],
    summary="Listar todos los productos para administración",
    description="Retorna productos de MongoDB incluyendo activos e inactivos, con detalle de variantes y stock.",
)
async def listar_productos_admin(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo"),
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    try:
        db = get_mongo_db()
        coleccion = db["productos"]

        query = {}
        if categoria:
            query["categoria"] = categoria
        if activo is not None:
            query["activo"] = activo

        cursor = coleccion.find(query).sort("fechaCreacion", -1)
        productos = await cursor.to_list(length=300)

        for prod in productos:
            prod["_id"] = str(prod["_id"])

        return productos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar productos: {str(e)}")


@router.get(
    "/{producto_id}",
    response_model=ProductoDetalle,
    summary="Consultar producto por ID",
    description="Retorna el documento completo de un producto por su ObjectId.",
)
async def obtener_producto_admin(
    producto_id: str,
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="El ID del producto no es un ObjectId válido.")

    db = get_mongo_db()
    producto = await db["productos"].find_one({"_id": ObjectId(producto_id)})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    producto["_id"] = str(producto["_id"])
    return producto


@router.post(
    "/",
    response_model=ProductoDetalle,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
    description="Inserta un producto en la colección 'productos' de MongoDB con sus variantes iniciales.",
)
async def crear_producto_admin(
    payload: ProductoCreate,
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    try:
        db = get_mongo_db()
        coleccion = db["productos"]

        doc = payload.model_dump()
        doc["fechaCreacion"] = datetime.now(timezone.utc)

        resultado = await coleccion.insert_one(doc)
        doc["_id"] = str(resultado.inserted_id)

        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando producto en MongoDB: {str(e)}")


@router.put(
    "/{producto_id}",
    response_model=ProductoDetalle,
    summary="Actualizar un producto",
    description="Actualiza datos generales o variantes de un producto existente en MongoDB.",
)
async def actualizar_producto_admin(
    producto_id: str,
    payload: ProductoUpdate,
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="El ID del producto no es un ObjectId válido.")

    db = get_mongo_db()
    coleccion = db["productos"]

    datos_actualizar = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not datos_actualizar:
        raise HTTPException(status_code=400, detail="No se enviaron campos válidos para actualizar.")

    resultado = await coleccion.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": datos_actualizar},
    )

    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    producto_actualizado = await coleccion.find_one({"_id": ObjectId(producto_id)})
    producto_actualizado["_id"] = str(producto_actualizado["_id"])
    return producto_actualizado


@router.patch(
    "/{producto_id}/stock",
    summary="Ajustar stock de una variante específica",
    description="Modifica de forma atómica la cantidad de existencias de un SKU dentro del array de variantes.",
)
async def ajustar_stock_variante(
    producto_id: str,
    payload: AjusteStockRequest,
    current_user: TokenData = Depends(verificar_gestor_inventario),
):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="El ID del producto no es un ObjectId válido.")

    db = get_mongo_db()
    coleccion = db["productos"]

    # 1. Comprobar existencia del producto
    producto = await coleccion.find_one({"_id": ObjectId(producto_id)})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    # 2. Localizar variante por SKU
    variante_actual = next((v for v in producto.get("variantes", []) if v.get("sku") == payload.sku), None)
    if not variante_actual:
        raise HTTPException(
            status_code=404,
            detail=f"La variante con SKU '{payload.sku}' no existe en este producto.",
        )

    stock_anterior = variante_actual.get("stock", 0)

    # 3. Actualizar de forma atómica en MongoDB usando el operador posicional $
    resultado = await coleccion.update_one(
        {"_id": ObjectId(producto_id), "variantes.sku": payload.sku},
        {"$set": {"variantes.$.stock": payload.nuevoStock}},
    )

    if resultado.modified_count == 0 and stock_anterior == payload.nuevoStock:
        mensaje = f"El stock de la variante {payload.sku} ya se encontraba en {payload.nuevoStock} unidades."
    else:
        mensaje = f"Stock actualizado exitosamente para {payload.sku}: {stock_anterior} -> {payload.nuevoStock} unidades."

    return {
        "status": "success",
        "mensaje": mensaje,
        "producto_id": producto_id,
        "sku": payload.sku,
        "stock_anterior": stock_anterior,
        "nuevo_stock": payload.nuevoStock,
        "motivo": payload.motivo,
        "actualizado_por": current_user.sub,
        "fecha": datetime.now(timezone.utc).isoformat(),
    }


@router.patch(
    "/{producto_id}/toggle-activo",
    summary="Cambiar visibilidad (activo/inactivo)",
    description="Alterna el estado activo de un producto para publicarlo o despublicarlo del catálogo.",
)
async def toggle_activo_producto(
    producto_id: str,
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="El ID del producto no es un ObjectId válido.")

    db = get_mongo_db()
    coleccion = db["productos"]

    producto = await coleccion.find_one({"_id": ObjectId(producto_id)})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    nuevo_estado = not producto.get("activo", True)

    await coleccion.update_one(
        {"_id": ObjectId(producto_id)},
        {"$set": {"activo": nuevo_estado}},
    )

    return {
        "producto_id": producto_id,
        "activo": nuevo_estado,
        "mensaje": f"Producto {'activado' if nuevo_estado else 'desactivado'} exitosamente.",
    }


@router.delete(
    "/{producto_id}",
    summary="Eliminar producto (lógico o físico)",
    description="Por defecto realiza baja lógica (activo: false). Si permanente=True, elimina el documento de MongoDB.",
)
async def eliminar_producto_admin(
    producto_id: str,
    permanente: bool = Query(False, description="Si es True, elimina físicamente el documento de MongoDB"),
    _user: TokenData = Depends(verificar_gestor_inventario),
):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=400, detail="El ID del producto no es un ObjectId válido.")

    db = get_mongo_db()
    coleccion = db["productos"]

    if permanente:
        resultado = await coleccion.delete_one({"_id": ObjectId(producto_id)})
        if resultado.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        return {"status": "success", "mensaje": "Producto eliminado físicamente de la base de datos."}
    else:
        resultado = await coleccion.update_one(
            {"_id": ObjectId(producto_id)},
            {"$set": {"activo": False}},
        )
        if resultado.matched_count == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado.")
        return {"status": "success", "mensaje": "Producto desactivado lógicamente (Soft Delete)."}

