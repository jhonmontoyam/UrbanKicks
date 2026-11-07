# ============================================================
# ARCHIVO: app/routers/storefront_views.py
# PROPÓSITO: Vistas HTML (Jinja2) del storefront público para
#            usuarios comunes y compradores de Urban Kicks.
#            Consume exclusivamente los productos desde MongoDB.
# ============================================================

from datetime import datetime
import json
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import get_mongo_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def format_cop(value: int | float | None) -> str:
    """Formatea valores numéricos a formato de moneda colombiana COP."""
    if value is None:
        return "$0 COP"
    try:
        formatted = f"{int(value):,}".replace(",", ".")
        return f"${formatted} COP"
    except Exception:
        return f"${value} COP"


def clean_doc_for_json(doc: dict) -> dict:
    """
    Limpia recursivamente un documento de MongoDB para que sea 100% serializable
    a JSON (convirtiendo ObjectId y datetime a cadenas de texto).
    """
    clean = {}
    for k, v in doc.items():
        if isinstance(v, datetime):
            clean[k] = v.isoformat()
        elif isinstance(v, list):
            clean[k] = [
                clean_doc_for_json(item) if isinstance(item, dict)
                else (item.isoformat() if isinstance(item, datetime)
                      else str(item) if hasattr(item, "__str__") and type(item).__name__ == "ObjectId"
                      else item)
                for item in v
            ]
        elif isinstance(v, dict):
            clean[k] = clean_doc_for_json(v)
        else:
            clean[k] = str(v) if hasattr(v, "__str__") and type(v).__name__ == "ObjectId" else v
    return clean


templates.env.filters["cop"] = format_cop
templates.env.filters["safe_json"] = lambda obj: json.dumps(obj, default=str)

router = APIRouter(tags=["Storefront (Público)"])


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_page(request: Request):
    """
    Endpoint principal del E-Commerce (Home / Catálogo para clientes).
    Consulta exclusivamente los productos activos directamente desde MongoDB.
    """
    productos = []
    try:
        db = get_mongo_db()
        cursor = db["productos"].find({"activo": True}).sort("fechaCreacion", -1)
        db_productos = await cursor.to_list(length=100)

        for p in db_productos:
            p["_id"] = str(p["_id"])
            productos.append(clean_doc_for_json(p))
    except Exception as e:
        print(f"Error consultando productos en MongoDB: {e}")
        productos = []

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "productos": productos,
            "total_productos": len(productos),
        },
    )
