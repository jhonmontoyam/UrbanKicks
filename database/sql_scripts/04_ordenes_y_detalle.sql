-- =============================================
-- PROYECTO: Urban Kicks E-Commerce
-- MÓDULO:   Órdenes de Compra y Detalle
-- MOTOR:    Microsoft SQL Server
-- =============================================

USE urban_kicks_db;
GO

-- =============================================
-- TABLA 1: estados_orden
-- Catálogo maestro de estados posibles de un pedido.
-- =============================================
IF OBJECT_ID('dbo.estados_orden', 'U') IS NOT NULL
    DROP TABLE dbo.estados_orden;
GO

CREATE TABLE dbo.estados_orden (
    estado_id   INT            NOT NULL IDENTITY(1,1),
    nombre      NVARCHAR(50)   NOT NULL,
    descripcion NVARCHAR(200)  NULL,

    CONSTRAINT pk_estados_orden        PRIMARY KEY (estado_id),
    CONSTRAINT uq_estados_orden_nombre UNIQUE      (nombre)
);
GO

-- =============================================
-- TABLA 2: ordenes
-- Cabecera del pedido: quién compró, dónde enviar,
-- en qué estado está y cuánto pagó en total.
-- =============================================
IF OBJECT_ID('dbo.ordenes', 'U') IS NOT NULL
    DROP TABLE dbo.ordenes;
GO

CREATE TABLE dbo.ordenes (
    orden_id      INT            NOT NULL IDENTITY(1,1),
    cliente_id    INT            NOT NULL,
    direccion_id  INT            NOT NULL,
    estado_id     INT            NOT NULL,
    total_cop     BIGINT         NOT NULL,
    notas         NVARCHAR(500)  NULL,
    fecha_orden   DATETIME2      NOT NULL CONSTRAINT df_ordenes_fecha DEFAULT GETDATE(),

    CONSTRAINT pk_ordenes           PRIMARY KEY (orden_id),
    CONSTRAINT fk_ordenes_cliente   FOREIGN KEY (cliente_id)   REFERENCES dbo.clientes(cliente_id),
    CONSTRAINT fk_ordenes_direccion FOREIGN KEY (direccion_id) REFERENCES dbo.direcciones(direccion_id),
    CONSTRAINT fk_ordenes_estado    FOREIGN KEY (estado_id)    REFERENCES dbo.estados_orden(estado_id),
    CONSTRAINT ck_ordenes_total     CHECK       (total_cop >= 0)
);
GO

-- =============================================
-- TABLA 3: orden_detalle
-- Líneas del pedido con precio congelado (histórico).
-- =============================================
IF OBJECT_ID('dbo.orden_detalle', 'U') IS NOT NULL
    DROP TABLE dbo.orden_detalle;
GO

CREATE TABLE dbo.orden_detalle (
    detalle_id          INT   NOT NULL IDENTITY(1,1),
    orden_id            INT   NOT NULL,
    variante_id         INT   NOT NULL,
    cantidad            INT   NOT NULL,
    precio_unitario_cop INT   NOT NULL,  -- Precio congelado al momento de la compra (histórico)
    subtotal_cop        INT   NOT NULL,  -- = cantidad × precio_unitario_cop

    CONSTRAINT pk_orden_detalle           PRIMARY KEY (detalle_id),
    CONSTRAINT uq_orden_detalle_linea     UNIQUE      (orden_id, variante_id),
    CONSTRAINT fk_orden_detalle_orden     FOREIGN KEY (orden_id)    REFERENCES dbo.ordenes(orden_id),
    CONSTRAINT fk_orden_detalle_variante  FOREIGN KEY (variante_id) REFERENCES dbo.producto_variantes(variante_id),
    CONSTRAINT ck_detalle_cantidad        CHECK       (cantidad >= 1),
    CONSTRAINT ck_detalle_precio_unitario CHECK       (precio_unitario_cop >= 0)
);
GO

-- =============================================
-- DATOS DE PRUEBA (Mock Data - Urban Kicks)
-- =============================================

-- Estados del pedido
INSERT INTO dbo.estados_orden (nombre, descripcion) VALUES
    ('Pendiente',  'Orden recibida, esperando confirmación de pago'),
    ('Pagado',     'Pago confirmado, en preparación para envío'),
    ('Enviado',    'Paquete en camino con la transportadora'),
    ('Entregado',  'Paquete recibido por el cliente en su dirección'),
    ('Cancelado',  'Orden anulada por el cliente o por falta de stock');
GO

-- =============================================
-- ÓRDENES DE PRUEBA
-- Referencia de clientes (script 03):
--   cliente_id 1 → Santiago Restrepo  (direccion_id 1 = Casa Niquía)
--   cliente_id 2 → Valeria Múnera     (direccion_id 3 = Casa La Madera)
--   cliente_id 3 → Juan David Ospina  (direccion_id 4 = Apto Niquía)
--   cliente_id 5 → Andrés Marulanda   (direccion_id 6 = Casa Tierradentro)
-- Referencia de variantes (script 02):
--   variante_id 2  → AD-BB-FORUM-US9   ($950.000 base)
--   variante_id 6  → AD-SAMBA-WG-US9   ($520.000 base)
--   variante_id 10 → NK-AF1-WHT-US9    ($480.000 base)
--   variante_id 14 → JD1-CHI-US9       ($1.200.000 + $200.000 adicional)
--   variante_id 19 → AD-HD-BLK-M       ($350.000 base)
--   variante_id 22 → NK-TF-GRY-M       ($420.000 base)
-- =============================================

-- Orden 1: Santiago compra Adidas Forum Bad Bunny + Hoodie Adidas
-- Total: 950.000 + 350.000 = 1.300.000 COP → estado: Entregado
INSERT INTO dbo.ordenes (cliente_id, direccion_id, estado_id, total_cop, notas) VALUES
    (1, 1, 4, 1300000, 'Dejar con el portero del edificio si no hay nadie');
GO

INSERT INTO dbo.orden_detalle (orden_id, variante_id, cantidad, precio_unitario_cop, subtotal_cop) VALUES
    (1, 2,  1, 950000, 950000),   -- Forum Bad Bunny US9
    (1, 19, 1, 350000, 350000);   -- Hoodie Adidas Negro M
GO

-- Orden 2: Valeria compra Samba OG + Nike Tech Fleece Jogger
-- Total: 520.000 + 420.000 = 940.000 COP → estado: Enviado
INSERT INTO dbo.ordenes (cliente_id, direccion_id, estado_id, total_cop) VALUES
    (2, 3, 3, 940000);
GO

INSERT INTO dbo.orden_detalle (orden_id, variante_id, cantidad, precio_unitario_cop, subtotal_cop) VALUES
    (2, 6,  1, 520000, 520000),   -- Samba OG White Gum US9
    (2, 22, 1, 420000, 420000);   -- Nike Tech Fleece Jogger M
GO

-- Orden 3: Juan David compra 2x Air Force 1 (regalo) + Jordan 1 Chicago cotizada
-- Jordan 1 US9: precio_base 1.200.000 + precio_adicional 200.000 = 1.400.000
-- Total: (480.000 × 2) + 1.400.000 = 2.360.000 COP → estado: Pagado
INSERT INTO dbo.ordenes (cliente_id, direccion_id, estado_id, total_cop, notas) VALUES
    (3, 4, 2, 2360000, 'Empaque especial para regalo por favor');
GO

INSERT INTO dbo.orden_detalle (orden_id, variante_id, cantidad, precio_unitario_cop, subtotal_cop) VALUES
    (3, 10, 2, 480000,  960000),   -- Air Force 1 US9 × 2
    (3, 14, 1, 1400000, 1400000);  -- Jordan 1 Chicago US9 (precio histórico con adicional incluido)
GO

-- Orden 4: Andrés cancela una orden (stock insuficiente)
-- Total: 950.000 COP → estado: Cancelado
INSERT INTO dbo.ordenes (cliente_id, direccion_id, estado_id, total_cop) VALUES
    (5, 6, 5, 950000);
GO

INSERT INTO dbo.orden_detalle (orden_id, variante_id, cantidad, precio_unitario_cop, subtotal_cop) VALUES
    (4, 2, 1, 950000, 950000);   -- Forum Bad Bunny US9 (cancelado)
GO
