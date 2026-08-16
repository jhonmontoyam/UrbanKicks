-- =============================================
-- PROYECTO: Urban Kicks E-Commerce
-- MÓDULO:   Catálogo de Productos (Unidad 1)
-- MOTOR:    Microsoft SQL Server
-- =============================================

-- =============================================
-- CREACIÓN DE BASE DE DATOS
-- =============================================

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'urban_kicks_db')
BEGIN
    CREATE DATABASE urban_kicks_db;
END
GO

USE urban_kicks_db;
GO

-- =============================================
-- TABLA 1: marcas
-- Almacena los fabricantes/diseñadores de los productos.
-- =============================================
IF OBJECT_ID('dbo.marcas', 'U') IS NOT NULL
    DROP TABLE dbo.marcas;
GO

CREATE TABLE dbo.marcas (
    marca_id        INT             NOT NULL IDENTITY(1,1),
    nombre          NVARCHAR(100)   NOT NULL,
    pais_origen     NVARCHAR(100)   NULL,
    logo_url        NVARCHAR(500)   NULL,
    activo          BIT             NOT NULL CONSTRAINT df_marcas_activo DEFAULT 1,
    fecha_creacion  DATETIME2       NOT NULL CONSTRAINT df_marcas_fecha  DEFAULT GETDATE(),

    CONSTRAINT pk_marcas        PRIMARY KEY (marca_id),
    CONSTRAINT uq_marcas_nombre UNIQUE      (nombre)
);
GO

-- =============================================
-- TABLA 2: categorias
-- Clasifica los productos en grandes grupos.
-- =============================================
IF OBJECT_ID('dbo.categorias', 'U') IS NOT NULL
    DROP TABLE dbo.categorias;
GO

CREATE TABLE dbo.categorias (
    categoria_id    INT             NOT NULL IDENTITY(1,1),
    nombre          NVARCHAR(100)   NOT NULL,
    descripcion     NVARCHAR(500)   NULL,
    activo          BIT             NOT NULL CONSTRAINT df_categorias_activo DEFAULT 1,
    fecha_creacion  DATETIME2       NOT NULL CONSTRAINT df_categorias_fecha  DEFAULT GETDATE(),

    CONSTRAINT pk_categorias        PRIMARY KEY (categoria_id),
    CONSTRAINT uq_categorias_nombre UNIQUE      (nombre)
);
GO

-- =============================================
-- TABLA 3: productos
-- Detalle general de cada artículo del catálogo.
-- Depende de marcas y categorias.
-- =============================================
IF OBJECT_ID('dbo.productos', 'U') IS NOT NULL
    DROP TABLE dbo.productos;
GO

CREATE TABLE dbo.productos (
    producto_id     INT             NOT NULL IDENTITY(1,1),
    marca_id        INT             NOT NULL,
    categoria_id    INT             NOT NULL,
    nombre          NVARCHAR(200)   NOT NULL,
    descripcion     NVARCHAR(1000)  NULL,
    precio_base     INT             NOT NULL,  -- Precio en Pesos Colombianos (COP), sin decimales
    imagen_url      NVARCHAR(500)   NULL,
    activo          BIT             NOT NULL CONSTRAINT df_productos_activo DEFAULT 1,
    fecha_creacion  DATETIME2       NOT NULL CONSTRAINT df_productos_fecha  DEFAULT GETDATE(),

    CONSTRAINT pk_productos             PRIMARY KEY (producto_id),
    CONSTRAINT fk_productos_marca       FOREIGN KEY (marca_id)     REFERENCES dbo.marcas(marca_id),
    CONSTRAINT fk_productos_categoria   FOREIGN KEY (categoria_id) REFERENCES dbo.categorias(categoria_id),
    CONSTRAINT ck_productos_precio      CHECK       (precio_base >= 0)
);
GO

-- =============================================
-- DATOS DE PRUEBA (Mock Data - Urban Kicks)
-- =============================================

-- Marcas
INSERT INTO dbo.marcas (nombre, pais_origen) VALUES
    ('Nike',    'Estados Unidos'),
    ('Adidas',  'Alemania'),
    ('Jordan',  'Estados Unidos'),
    ('New Balance', 'Estados Unidos'),
    ('Puma',    'Alemania');
GO

-- Categorías
INSERT INTO dbo.categorias (nombre, descripcion) VALUES
    ('Zapatillas',   'Calzado deportivo y urbano de edición limitada y general'),
    ('Ropa',         'Prendas urbanas: hoodies, joggers, camisetas y más'),
    ('Accesorios',   'Gorras, calcetines, mochilas y complementos de moda urbana');
GO

-- Productos (precios en COP - Pesos Colombianos)
INSERT INTO dbo.productos (marca_id, categoria_id, nombre, descripcion, precio_base) VALUES
    (2, 1, 'Adidas Forum Low Bad Bunny',         'Colección especial Bad Bunny x Adidas, suela gruesa y detalles en verde olivo',  950000),
    (2, 1, 'Adidas Samba OG White Gum',          'Ícono del streetwear europeo, cuero blanco con suela gum clásica',               520000),
    (1, 1, 'Nike Air Force 1 Low Triple White',  'El clásico silhouette en colorway todo blanco, versátil y atemporal',            480000),
    (3, 1, 'Jordan 1 Retro High OG Chicago',     'El legendario colorway Chicago en cuero premium rojo, negro y blanco',          1200000),
    (4, 1, 'New Balance 550 White Green',         'Retro basketball sneaker con upper en cuero y colorway minimalista',             580000),
    (2, 2, 'Adidas Originals Hoodie Essentials', 'Hoodie urban en fleece pesado con logo Trefoil bordado en pecho',                350000),
    (1, 2, 'Nike Tech Fleece Jogger',            'Pantalón de corte slim en tejido Tech Fleece, ideal para el look street',        420000),
    (5, 3, 'Puma x Pleasures Cap',               'Gorra de colaboración Puma x Pleasures, bordado frontal y correa ajustable',     180000);
GO
