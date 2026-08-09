-- =============================================
-- PROYECTO: Urban Kicks E-Commerce
-- MÓDULO:   Gestión de Clientes y Direcciones
-- MOTOR:    Microsoft SQL Server
-- =============================================

USE urban_kicks_db;
GO

-- =============================================
-- TABLA 1: clientes
-- =============================================
IF OBJECT_ID('dbo.clientes', 'U') IS NOT NULL
    DROP TABLE dbo.clientes;
GO

CREATE TABLE dbo.clientes (
    cliente_id        INT            NOT NULL IDENTITY(1,1),
    nombre            NVARCHAR(100)  NOT NULL,
    apellido          NVARCHAR(100)  NOT NULL,
    email             NVARCHAR(200)  NOT NULL,
    telefono          VARCHAR(20)    NULL,
    fecha_nacimiento  DATE           NULL,
    activo            BIT            NOT NULL CONSTRAINT df_clientes_activo    DEFAULT 1,
    fecha_registro    DATETIME2      NOT NULL CONSTRAINT df_clientes_registro  DEFAULT GETDATE(),

    CONSTRAINT pk_clientes       PRIMARY KEY (cliente_id),
    CONSTRAINT uq_clientes_email UNIQUE      (email)
);
GO

-- =============================================
-- TABLA 2: direcciones
-- Un cliente puede tener N direcciones guardadas.
-- =============================================
IF OBJECT_ID('dbo.direcciones', 'U') IS NOT NULL
    DROP TABLE dbo.direcciones;
GO

CREATE TABLE dbo.direcciones (
    direccion_id      INT            NOT NULL IDENTITY(1,1),
    cliente_id        INT            NOT NULL,
    alias             NVARCHAR(50)   NOT NULL,
    calle             NVARCHAR(200)  NOT NULL,
    barrio            NVARCHAR(100)  NULL,
    municipio         NVARCHAR(100)  NOT NULL,
    departamento      NVARCHAR(100)  NOT NULL CONSTRAINT df_dir_depto DEFAULT 'Antioquia',
    pais              NVARCHAR(100)  NOT NULL CONSTRAINT df_dir_pais  DEFAULT 'Colombia',
    codigo_postal     VARCHAR(10)    NULL,
    es_predeterminada BIT            NOT NULL CONSTRAINT df_dir_predeterminada DEFAULT 0,

    CONSTRAINT pk_direcciones         PRIMARY KEY (direccion_id),
    CONSTRAINT fk_direcciones_cliente FOREIGN KEY (cliente_id) REFERENCES dbo.clientes(cliente_id)
);
GO

-- =============================================
-- DATOS DE PRUEBA (Mock Data - Urban Kicks)
-- Contexto: Clientes de Antioquia, enfoque en Bello
-- =============================================

-- Clientes
INSERT INTO dbo.clientes (nombre, apellido, email, telefono, fecha_nacimiento) VALUES
    ('Santiago',   'Restrepo',  'santiago.restrepo@gmail.com',  '3042156789', '2000-03-14'),
    ('Valeria',    'Múnera',    'vale.munera@hotmail.com',       '3118874321', '1998-09-22'),
    ('Juan David', 'Ospina',    'juandavid.ospina@gmail.com',    '3204431287', NULL        ),
    ('Daniela',    'Cano',      'dani.cano@outlook.com',         '3015567890', '2001-07-05'),
    ('Andrés',     'Marulanda', 'andres.marulanda@gmail.com',    NULL,         '1995-11-30');
GO

-- =============================================
-- DIRECCIONES
-- Nomenclatura urbana real de Antioquia / Bello
-- =============================================

-- Santiago Restrepo (cliente_id 1): vive en Niquía, trabaja en Bello centro
INSERT INTO dbo.direcciones (cliente_id, alias, calle, barrio, municipio, codigo_postal, es_predeterminada) VALUES
    (1, 'Casa',    'Cra 51B # 44-120',         'Niquía',          'Bello',    '051051', 1),
    (1, 'Trabajo', 'Cl 49 # 50-80, Local 3',   'Centro de Bello', 'Bello',    '051001', 0);

-- Valeria Múnera (cliente_id 2): vive en La Madera
INSERT INTO dbo.direcciones (cliente_id, alias, calle, barrio, municipio, codigo_postal, es_predeterminada) VALUES
    (2, 'Casa',    'Cra 55 # 38-15, Apto 201', 'La Madera',       'Bello',    '051020', 1);

-- Juan David Ospina (cliente_id 3): Niquía principal + casa de sus papás en Zamora
INSERT INTO dbo.direcciones (cliente_id, alias, calle, barrio, municipio, codigo_postal, es_predeterminada) VALUES
    (3, 'Mi Apto',       'Cl 43 # 52-30, Apto 404', 'Niquía',  'Bello',    '051051', 1),
    (3, 'Casa de papás', 'Cra 48 # 12-55',           'Zamora',  'Medellín', '050015', 0);

-- Daniela Cano (cliente_id 4): vive en Prado, Bello
INSERT INTO dbo.direcciones (cliente_id, alias, calle, barrio, municipio, codigo_postal, es_predeterminada) VALUES
    (4, 'Casa',    'Cl 52 # 46-18',              'Prado',          'Bello',   '051030', 1);

-- Andrés Marulanda (cliente_id 5): vive en Tierradentro + bodega de su negocio en París
INSERT INTO dbo.direcciones (cliente_id, alias, calle, barrio, municipio, codigo_postal, es_predeterminada) VALUES
    (5, 'Casa',   'Cra 57 # 40-90, Casa 2',    'Tierradentro',  'Bello',   '051040', 1),
    (5, 'Bodega', 'Cra 52A # 62-10, Bodega 8', 'París',         'Bello',   '051060', 0);
GO
