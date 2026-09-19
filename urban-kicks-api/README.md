# Urban Kicks API - Guía de Inicio Rápido

Backend para el E-Commerce **Urban Kicks** construido con **FastAPI** y **Microsoft SQL Server**.

## Requisitos Previos

1. **Python 3.10+** instalado en tu sistema.
2. **Microsoft SQL Server** instalado y corriendo localmente con la base de datos `urban_kicks_db` (creada con los scripts de la carpeta `database/sql_scripts/`).
3. **ODBC Driver for SQL Server** (por ejemplo, *ODBC Driver 17 for SQL Server* o *ODBC Driver 18 for SQL Server*).

---

## Pasos para Poner a Correr el Proyecto

### 1. Abrir la terminal en la carpeta del proyecto
```bash
cd urban-kicks-api
```

### 2. Crear y activar el entorno virtual en Python

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(Si PowerShell te da un error de permisos de ejecución de scripts, puedes usar la consola CMD normal):*
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

### 3. Instalar las dependencias del proyecto
```bash
pip install -r requirements.txt
```

### 4. Configurar tus credenciales en el archivo `.env`
Abre el archivo [`.env`](file:urban-kicks-api/.env) y ajusta tus datos reales:

```ini
DB_SERVER=localhost
DB_NAME=urban_kicks_db
DB_USER=sa
DB_PASSWORD=tu_contraseña_real_aqui
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### 5. Iniciar el servidor local
```bash
uvicorn app.main:app --reload
```

---

## Probar la API en el Navegador

Una vez iniciado el servidor, verás un mensaje en consola indicando que está corriendo en `http://127.0.0.1:8000`.

Abre tu navegador y entra a:

* **Documentación Interactiva (Swagger UI)**:  
  [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
  *(Aquí podrás probar los endpoints de forma visual con el botón "Try it out")*.

* **Catálogo de Productos (JSON en COP)**:  
  [http://127.0.0.1:8000/api/v1/productos/](http://127.0.0.1:8000/api/v1/productos/)

* **Detalle de un Producto Específico (ej. ID 1)**:  
  [http://127.0.0.1:8000/api/v1/productos/1](http://127.0.0.1:8000/api/v1/productos/1)
