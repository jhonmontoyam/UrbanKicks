-- =============================================
-- PROYECTO: Urban Kicks E-Commerce
-- MÓDULO:   Gestión de Inventario y Variantes
-- MOTOR:    Microsoft SQL Server
-- =============================================

USE urban_kicks_db;
GO

-- =============================================
-- TABLA 1: tallas
-- Catálogo maestro de tallas (calzado y ropa).
-- =============================================
IF OBJECT_ID('dbo.tallas', 'U') IS NOT NULL
    DROP TABLE dbo.tallas;
GO

CREATE TABLE dbo.tallas (
    talla_id    INT           NOT NULL IDENTITY(1,1),
    nombre      NVARCHAR(20)  NOT NULL,
    descripcion NVARCHAR(100) NULL,

    CONSTRAINT pk_tallas        PRIMARY KEY (talla_id),
    CONSTRAINT uq_tallas_nombre UNIQUE      (nombre)
);
GO

-- =============================================
-- TABLA 2: colores
-- Catálogo maestro de colores disponibles.
-- =============================================
IF OBJECT_ID('dbo.colores', 'U') IS NOT NULL
    DROP TABLE dbo.colores;
GO

CREATE TABLE dbo.colores (
    color_id   INT          NOT NULL IDENTITY(1,1),
    nombre     NVARCHAR(50) NOT NULL,
    codigo_hex VARCHAR(7)   NULL,

    CONSTRAINT pk_colores        PRIMARY KEY (color_id),
    CONSTRAINT uq_colores_nombre UNIQUE      (nombre)
);
GO

-- =============================================
-- TABLA 3: producto_variantes
-- Une producto + talla + color con stock real.
-- Una misma zapatilla puede tener muchas variantes.
-- =============================================
IF OBJECT_ID('dbo.producto_variantes', 'U') IS NOT NULL
    DROP TABLE dbo.producto_variantes;
GO

CREATE TABLE dbo.producto_variantes (
    variante_id      INT            NOT NULL IDENTITY(1,1),
    producto_id      INT            NOT NULL,
    talla_id         INT            NOT NULL,
    color_id         INT            NOT NULL,
    sku              VARCHAR(50)    NOT NULL,
    precio_adicional INT            NOT NULL CONSTRAINT df_variantes_precio_add DEFAULT 0,  -- Sobreprecio en COP por talla/demanda
    stock_disponible INT            NOT NULL CONSTRAINT df_variantes_stock       DEFAULT 0,
    activo           BIT            NOT NULL CONSTRAINT df_variantes_activo      DEFAULT 1,
    fecha_creacion   DATETIME2      NOT NULL CONSTRAINT df_variantes_fecha       DEFAULT GETDATE(),

    CONSTRAINT pk_producto_variantes         PRIMARY KEY (variante_id),
    CONSTRAINT uq_variantes_sku              UNIQUE      (sku),
    CONSTRAINT uq_variantes_prod_talla_color UNIQUE      (producto_id, talla_id, color_id),
    CONSTRAINT fk_variantes_producto         FOREIGN KEY (producto_id) REFERENCES dbo.productos(producto_id),
    CONSTRAINT fk_variantes_talla            FOREIGN KEY (talla_id)    REFERENCES dbo.tallas(talla_id),
    CONSTRAINT fk_variantes_color            FOREIGN KEY (color_id)    REFERENCES dbo.colores(color_id),
    CONSTRAINT ck_variantes_stock            CHECK       (stock_disponible >= 0)
);
GO

-- =============================================
-- DATOS DE PRUEBA (Mock Data - Urban Kicks)
-- =============================================

-- Tallas
INSERT INTO dbo.tallas (nombre, descripcion) VALUES
    ('US 8',  'Talla calzado americano (26 cm)'),
    ('US 9',  'Talla calzado americano (27 cm)'),
    ('US 10', 'Talla calzado americano (28 cm)'),
    ('US 11', 'Talla calzado americano (29 cm)'),
    ('S',     'Talla prenda Small'),
    ('M',     'Talla prenda Medium'),
    ('L',     'Talla prenda Large'),
    ('Única', 'Talla estándar para accesorios');
GO

-- Colores
INSERT INTO dbo.colores (nombre, codigo_hex) VALUES
    ('Verde Olivo',  '#556B2F'),
    ('Blanco Gum',   '#F5F0E8'),
    ('Triple White', '#FFFFFF'),
    ('Chicago Red',  '#CE1126'),
    ('Negro',        '#000000'),
    ('Gris Carbón',  '#2F2F2F'),
    ('Blanco Verde', '#F0FFF0');
GO

-- =============================================
-- VARIANTES POR PRODUCTO
-- Referencia IDs del script 01_catalogo_inicial:
--   producto_id 1 → Adidas Forum Low Bad Bunny
--   producto_id 2 → Adidas Samba OG White Gum
--   producto_id 3 → Nike Air Force 1 Low Triple White
--   producto_id 4 → Jordan 1 Retro High OG Chicago
--   producto_id 6 → Adidas Originals Hoodie Essentials
--   producto_id 7 → Nike Tech Fleece Jogger
--   producto_id 8 → Puma x Pleasures Cap
-- =============================================

-- Producto 1: Adidas Forum Low Bad Bunny (color_id 1 = Verde Olivo)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (1, 1, 1, 'AD-BB-FORUM-US8',  5),
    (1, 2, 1, 'AD-BB-FORUM-US9',  8),
    (1, 3, 1, 'AD-BB-FORUM-US10', 3),
    (1, 4, 1, 'AD-BB-FORUM-US11', 2);
GO

-- Producto 2: Adidas Samba OG White Gum (color_id 2 = Blanco Gum)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (2, 1, 2, 'AD-SAMBA-WG-US8',  10),
    (2, 2, 2, 'AD-SAMBA-WG-US9',  14),
    (2, 3, 2, 'AD-SAMBA-WG-US10', 9),
    (2, 4, 2, 'AD-SAMBA-WG-US11', 6);
GO

-- Producto 3: Nike Air Force 1 Low Triple White (color_id 3 = Triple White)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (3, 1, 3, 'NK-AF1-WHT-US8',  15),
    (3, 2, 3, 'NK-AF1-WHT-US9',  20),
    (3, 3, 3, 'NK-AF1-WHT-US10', 12),
    (3, 4, 3, 'NK-AF1-WHT-US11',  8);
GO

-- Producto 4: Jordan 1 Retro High OG Chicago (color_id 4 = Chicago Red)
-- precio_adicional en COP por alta demanda en tallas cotizadas
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, precio_adicional, stock_disponible) VALUES
    (4, 1, 4, 'JD1-CHI-US8',  120000, 3),
    (4, 2, 4, 'JD1-CHI-US9',  200000, 2),
    (4, 3, 4, 'JD1-CHI-US10', 200000, 1),
    (4, 4, 4, 'JD1-CHI-US11', 100000, 4);
GO

-- Producto 6: Adidas Originals Hoodie Essentials (color_id 5 = Negro)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (6, 5, 5, 'AD-HD-BLK-S', 6),
    (6, 6, 5, 'AD-HD-BLK-M', 10),
    (6, 7, 5, 'AD-HD-BLK-L',  7);
GO

-- Producto 7: Nike Tech Fleece Jogger (color_id 6 = Gris Carbón)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (7, 5, 6, 'NK-TF-GRY-S', 8),
    (7, 6, 6, 'NK-TF-GRY-M', 12),
    (7, 7, 6, 'NK-TF-GRY-L',  9);
GO

-- Producto 8: Puma x Pleasures Cap (color_id 5 = Negro, talla_id 8 = Única)
INSERT INTO dbo.producto_variantes (producto_id, talla_id, color_id, sku, stock_disponible) VALUES
    (8, 8, 5, 'PM-PLSR-CAP-NEG', 20);
GO
