erDiagram

    marcas {
        INT marca_id PK
        NVARCHAR nombre
        NVARCHAR pais_origen
        NVARCHAR logo_url
        BIT activo
        DATETIME2 fecha_creacion
    }

    categorias {
        INT categoria_id PK
        NVARCHAR nombre
        NVARCHAR descripcion
        BIT activo
        DATETIME2 fecha_creacion
    }

    productos {
        INT producto_id PK
        INT marca_id FK
        INT categoria_id FK
        NVARCHAR nombre
        NVARCHAR descripcion
        INT precio_base
        NVARCHAR imagen_url
        BIT activo
        DATETIME2 fecha_creacion
    }

    tallas {
        INT talla_id PK
        NVARCHAR nombre
        NVARCHAR descripcion
    }

    colores {
        INT color_id PK
        NVARCHAR nombre
        VARCHAR codigo_hex
    }

    producto_variantes {
        INT variante_id PK
        INT producto_id FK
        INT talla_id FK
        INT color_id FK
        VARCHAR sku
        INT precio_adicional
        INT stock_disponible
        BIT activo
        DATETIME2 fecha_creacion
    }

    clientes {
        INT cliente_id PK
        NVARCHAR nombre
        NVARCHAR apellido
        NVARCHAR email
        VARCHAR telefono
        DATE fecha_nacimiento
        BIT activo
        DATETIME2 fecha_registro
    }

    direcciones {
        INT direccion_id PK
        INT cliente_id FK
        NVARCHAR alias
        NVARCHAR calle
        NVARCHAR barrio
        NVARCHAR municipio
        NVARCHAR departamento
        NVARCHAR pais
        VARCHAR codigo_postal
        BIT es_predeterminada
    }

    estados_orden {
        INT estado_id PK
        NVARCHAR nombre
        NVARCHAR descripcion
    }

    ordenes {
        INT orden_id PK
        INT cliente_id FK
        INT direccion_id FK
        INT estado_id FK
        BIGINT total_cop
        NVARCHAR notas
        DATETIME2 fecha_orden
    }

    orden_detalle {
        INT detalle_id PK
        INT orden_id FK
        INT variante_id FK
        INT cantidad
        INT precio_unitario_cop
        INT subtotal_cop
    }

    marcas           ||--o{ productos          : "tiene"
    categorias       ||--o{ productos          : "clasifica"
    productos        ||--o{ producto_variantes  : "tiene"
    tallas           ||--o{ producto_variantes  : "define"
    colores          ||--o{ producto_variantes  : "define"
    clientes         ||--o{ direcciones         : "registra"
    clientes         ||--o{ ordenes             : "genera"
    direcciones      ||--o{ ordenes             : "entrega en"
    estados_orden    ||--o{ ordenes             : "clasifica"
    ordenes          ||--o{ orden_detalle       : "contiene"
    producto_variantes ||--o{ orden_detalle     : "es comprada en"
