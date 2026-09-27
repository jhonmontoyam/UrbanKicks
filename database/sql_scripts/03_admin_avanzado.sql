-- =============================================
-- PROYECTO: Urban Kicks E-Commerce
-- MÓDULO:   Centro Administrativo y T-SQL Avanzado (Unidad Cierre SQL)
-- MOTOR:    Microsoft SQL Server
-- =============================================

USE urban_kicks_db;
GO

-- =============================================
-- 1. MÓDULO DE ROLES Y SEGURIDAD (Centro Administrativo)
-- =============================================
IF OBJECT_ID('dbo.empleados_roles', 'U') IS NOT NULL DROP TABLE dbo.empleados_roles;
IF OBJECT_ID('dbo.roles', 'U') IS NOT NULL DROP TABLE dbo.roles;
IF OBJECT_ID('dbo.empleados', 'U') IS NOT NULL DROP TABLE dbo.empleados;

CREATE TABLE dbo.roles (
    rol_id      INT IDENTITY(1,1) PRIMARY KEY,
    nombre      NVARCHAR(50) NOT NULL UNIQUE,
    descripcion NVARCHAR(200) NULL
);

CREATE TABLE dbo.empleados (
    empleado_id   INT IDENTITY(1,1) PRIMARY KEY,
    nombre        NVARCHAR(100) NOT NULL,
    email         NVARCHAR(200) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Almacenará el hash de bcrypt
    activo        BIT DEFAULT 1,
    ultimo_login  DATETIME NULL,         -- Registro del último acceso
    creado_en     DATETIME DEFAULT GETDATE()
);

CREATE TABLE dbo.empleados_roles (
    empleado_id INT NOT NULL,
    rol_id      INT NOT NULL,
    PRIMARY KEY (empleado_id, rol_id),
    CONSTRAINT fk_er_empleado FOREIGN KEY (empleado_id) REFERENCES dbo.empleados(empleado_id),
    CONSTRAINT fk_er_rol      FOREIGN KEY (rol_id)      REFERENCES dbo.roles(rol_id)
);
GO

-- Datos de prueba
INSERT INTO dbo.roles (nombre, descripcion) VALUES 
('SuperAdmin', 'Acceso total al centro administrativo'), 
('GestorInventario', 'Administra productos en MongoDB y ajusta stock'), 
('Vendedor', 'Gestiona órdenes, despachos y atención al cliente');

-- Insertamos empleados con una contraseña por defecto: "admin12345"
-- El hash bcrypt para "admin12345" (ejemplo): $2b$12$ewkxdRSKOn9eEVUzPLuTDuIvHeSxnpN29HaXwclGhhT3x.9vqS8TS
INSERT INTO dbo.empleados (nombre, email, password_hash) VALUES 
('Hugo Andrés Casas', 'hcasas@urbankicks.com', '$2b$12$ewkxdRSKOn9eEVUzPLuTDuIvHeSxnpN29HaXwclGhhT3x.9vqS8TS'), 
('Carlos Andrés Moreno', 'cmoreno@urbankicks.com', '$2b$12$ewkxdRSKOn9eEVUzPLuTDuIvHeSxnpN29HaXwclGhhT3x.9vqS8TS'),
('Jhon Alexander Montoya', 'jmontoya@urbankicks.com', '$2b$12$ewkxdRSKOn9eEVUzPLuTDuIvHeSxnpN29HaXwclGhhT3x.9vqS8TS');

INSERT INTO dbo.empleados_roles (empleado_id, rol_id) VALUES 
(1, 1), -- Hugo Andrés Casas es SuperAdmin
(2, 2), -- Carlos Andrés Moreno es GestorInventario
(3, 3); -- Jhon Alexander Montoya es Vendedor
GO


-- =============================================
-- 2. JERARQUÍAS CON CTEs RECURSIVAS
-- Soporte para una estructura departamental jerárquica
-- =============================================
IF OBJECT_ID('dbo.departamentos_internos', 'U') IS NOT NULL DROP TABLE dbo.departamentos_internos;
CREATE TABLE dbo.departamentos_internos (
    depto_id   INT IDENTITY(1,1) PRIMARY KEY,
    nombre     NVARCHAR(100) NOT NULL,
    padre_id   INT NULL CONSTRAINT fk_depto_padre FOREIGN KEY REFERENCES dbo.departamentos_internos(depto_id)
);

INSERT INTO dbo.departamentos_internos (nombre, padre_id) VALUES
('Gerencia General', NULL),         -- 1
('Operaciones', 1),                 -- 2
('Ventas', 1),                      -- 3
('Logística', 2),                   -- 4
('Servicio al Cliente', 3);         -- 5
GO

-- Vista analítica con CTE Recursiva
IF OBJECT_ID('dbo.vw_arbol_organizacional', 'V') IS NOT NULL DROP VIEW dbo.vw_arbol_organizacional;
GO
CREATE VIEW dbo.vw_arbol_organizacional AS
WITH ArbolCTE AS (
    -- Miembro Ancla: Los nodos raíz (padre_id es NULL)
    SELECT depto_id, nombre, padre_id, 1 AS Nivel, CAST(nombre AS NVARCHAR(MAX)) AS Ruta
    FROM dbo.departamentos_internos
    WHERE padre_id IS NULL

    UNION ALL

    -- Miembro Recursivo: Llama repetidamente a ArbolCTE hasta llegar a las hojas
    SELECT d.depto_id, d.nombre, d.padre_id, a.Nivel + 1, a.Ruta + ' > ' + d.nombre
    FROM dbo.departamentos_internos d
    INNER JOIN ArbolCTE a ON d.padre_id = a.depto_id
)
SELECT depto_id, nombre, Nivel, Ruta FROM ArbolCTE;
GO


-- =============================================
-- 3. VISTAS Y FUNCIONES DE VENTANA (Analítica de Ventas)
-- =============================================
IF OBJECT_ID('dbo.vw_ranking_ventas_municipio', 'V') IS NOT NULL DROP VIEW dbo.vw_ranking_ventas_municipio;
GO
CREATE VIEW dbo.vw_ranking_ventas_municipio AS
SELECT 
    d.municipio,
    d.departamento,
    COUNT(o.orden_id) AS total_ordenes,
    SUM(o.total_cop) AS total_ingresos_cop,
    -- Función de Ventana: Calcula el ranking dinámicamente particionado por departamento
    RANK() OVER(PARTITION BY d.departamento ORDER BY SUM(o.total_cop) DESC) AS ranking_en_depto
FROM dbo.ordenes o
INNER JOIN dbo.direcciones d ON o.direccion_id = d.direccion_id
WHERE o.estado_id IN (2, 3, 4) -- Solo contabilizar Pagado, Enviado, Entregado
GROUP BY d.municipio, d.departamento;
GO


-- =============================================
-- 4. PROCEDIMIENTOS ALMACENADOS Y TRANSACCIONES
-- =============================================
IF OBJECT_ID('dbo.sp_procesar_nueva_orden', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_procesar_nueva_orden;
GO
CREATE PROCEDURE dbo.sp_procesar_nueva_orden
    @cliente_id INT,
    @direccion_id INT,
    @total_cop BIGINT,
    @notas NVARCHAR(500),
    @variante_sku VARCHAR(50),
    @cantidad INT,
    @precio_unitario_cop INT
AS
BEGIN
    SET NOCOUNT ON; -- Mejora el rendimiento al no devolver "1 row affected" repetitivamente

    BEGIN TRY
        -- Iniciamos el bloque transaccional: O se guarda TODO o no se guarda NADA.
        BEGIN TRANSACTION;

        DECLARE @nueva_orden_id INT;

        -- Paso A: Crear la Orden (Cabecera)
        INSERT INTO dbo.ordenes (cliente_id, direccion_id, estado_id, total_cop, notas)
        VALUES (@cliente_id, @direccion_id, 1, @total_cop, @notas); -- 1 = Estado "Pendiente"

        -- Obtenemos el ID generado autoincremental
        SET @nueva_orden_id = SCOPE_IDENTITY();

        -- Paso B: Crear el Detalle (Línea) usando Soft-Link a MongoDB
        INSERT INTO dbo.orden_detalle (orden_id, variante_sku, cantidad, precio_unitario_cop, subtotal_cop)
        VALUES (@nueva_orden_id, @variante_sku, @cantidad, @precio_unitario_cop, @cantidad * @precio_unitario_cop);

        -- Confirmamos cambios
        COMMIT TRANSACTION;
        PRINT 'Exito: Orden procesada correctamente con ID ' + CAST(@nueva_orden_id AS VARCHAR);

    END TRY
    BEGIN CATCH
        -- En caso de error (ej: cliente_id inválido), deshacemos la operación
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        PRINT 'Error CRÍTICO al procesar la orden. Se aplicó Rollback.';
        PRINT 'Detalle del Error: ' + ERROR_MESSAGE();
        
        -- Relanzamos el error hacia la aplicación (FastAPI)
        THROW; 
    END CATCH
END;
GO


-- =============================================
-- 5. TRIGGERS DE AUDITORÍA
-- =============================================
IF OBJECT_ID('dbo.log_auditoria_ordenes', 'U') IS NOT NULL DROP TABLE dbo.log_auditoria_ordenes;
CREATE TABLE dbo.log_auditoria_ordenes (
    log_id          INT IDENTITY(1,1) PRIMARY KEY,
    orden_id        INT NOT NULL,
    estado_anterior INT NOT NULL,
    estado_nuevo    INT NOT NULL,
    fecha_cambio    DATETIME2 DEFAULT GETDATE(),
    usuario_db      NVARCHAR(100) DEFAULT SYSTEM_USER
);
GO

IF OBJECT_ID('dbo.tr_auditoria_estado_orden', 'TR') IS NOT NULL DROP TRIGGER dbo.tr_auditoria_estado_orden;
GO
CREATE TRIGGER dbo.tr_auditoria_estado_orden
ON dbo.ordenes
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- UPDATE() verifica si la columna especificada fue parte del comando UPDATE
    IF UPDATE(estado_id)
    BEGIN
        INSERT INTO dbo.log_auditoria_ordenes (orden_id, estado_anterior, estado_nuevo)
        SELECT 
            i.orden_id, 
            d.estado_id, -- Tabla lógica 'deleted' contiene el valor viejo
            i.estado_id  -- Tabla lógica 'inserted' contiene el valor nuevo
        FROM inserted i
        INNER JOIN deleted d ON i.orden_id = d.orden_id
        WHERE i.estado_id <> d.estado_id; -- Solo insertar si el estado REALMENTE cambió
    END
END;
GO

-- =============================================
-- PRUEBA DE LOS COMPONENTES
-- =============================================

-- Prueba del Procedimiento Almacenado
EXEC dbo.sp_procesar_nueva_orden 
    @cliente_id = 1, 
    @direccion_id = 1, 
    @total_cop = 520000, 
    @notas = 'Entregar en portería', 
    @variante_sku = 'AD-SAMBA-WG-US9', 
    @cantidad = 1, 
    @precio_unitario_cop = 520000;

-- Prueba del Trigger de Auditoría (Cambiamos el estado de la nueva orden)
DECLARE @ultima_orden INT = SCOPE_IDENTITY(); -- o usar MAX(orden_id)
UPDATE dbo.ordenes SET estado_id = 2 WHERE orden_id = 5; -- Pasamos a estado "Pagado"

-- SELECT * FROM dbo.vw_arbol_organizacional;
-- SELECT * FROM dbo.vw_ranking_ventas_municipio;
-- SELECT * FROM dbo.log_auditoria_ordenes;
