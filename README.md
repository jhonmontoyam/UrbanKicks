# Urban Kicks: E-commerce con Motor de Recomendación

## Participantes y Roles Iniciales
*   **[jhonmontoyam]** - Desarrollador
*   **[HugoAndres23]** - Desarrollador
*   **[Killingham]** - Lider

## Descripción del Problema
En el comercio electrónico actual, los usuarios se enfrentan a catálogos masivos que dificultan la toma de decisiones, lo que resulta en altas tasas de abandono de carritos y pérdida de fidelización. Además, las plataformas tradicionales basadas únicamente en bases de datos relacionales sufren cuellos de botella al intentar ofrecer catálogos con atributos dinámicos y analizar el comportamiento en tiempo real. 

Este proyecto propone una plataforma de comercio electrónico que no solo gestione el flujo transaccional de ventas, sino que utilice persistencia políglota para ofrecer recomendaciones personalizadas basadas en el historial de navegación y compras del consumidor.

## Posibles Usuarios del Sistema
1.  **Comprador:** Explora productos, interactúa con el carrito de compras, recibe recomendaciones personalizadas y realiza pedidos.
2.  **Administrador de Catálogo:** Gestiona el inventario rígido y agrega atributos dinámicos a nuevos productos sin alterar esquemas.
3.  **Analista de Ventas / Marketing:** Consulta paneles de inteligencia de negocios para evaluar la efectividad de las recomendaciones y las tasas de conversión.

## Lista Preliminar de Entidades
El sistema implementa persistencia políglota distribuida en tres unidades arquitectónicas:

**Unidad 1: Base de Datos Relacional (SQL)**
*   `Cliente` (Datos de facturación, autenticación)
*   `Orden_Compra` (Transacciones ACID)
*   `Detalle_Orden` (Líneas de facturación)
*   `Inventario_Base` (Stock estricto y SKU)

**Unidad 2: Base de Datos NoSQL (Documental / Clave-Valor)**
*   `Catalogo_Dinamico` (Productos con atributos variables en JSON)
*   `Carrito_Compra` (Gestión temporal y rápida en memoria)
*   `Interaccion_Usuario` (Logs de clics, vistas y reseñas)

**Unidad 3: Analítica (Data Warehouse / Data Mart)**
*   `Dim_Cliente` / `Dim_Producto` / `Dim_Tiempo`
*   `Fact_Ventas` (Hechos transaccionales consolidados)
*   `Perfil_Recomendacion` (Resultados del motor analítico)

## Reglas de Negocio
1.  **Integridad Transaccional:** Un cliente no puede finalizar una orden de compra si el motor relacional detecta que el stock del `Inventario_Base` es igual a cero en el momento exacto del *checkout*.
2.  **Recomendación Obligatoria:** Antes de proceder al pago, el sistema debe analizar la `Interaccion_Usuario` (NoSQL) y presentar al menos tres (3) productos sugeridos complementarios al contenido actual del carrito.
3.  **Auditoría de Abandono:** Todo `Carrito_Compra` que permanezca inactivo por más de 24 horas debe ser vaciado de la base de datos operativa y su registro debe enviarse al Data Lake para futuros análisis de tasa de abandono (*Churn Rate*).

## ¿Por qué el proyecto es suficientemente complejo?
Este proyecto supera un simple CRUD al requerir **persistencia políglota**. Exige garantizar transacciones ACID para las finanzas (SQL), manejar esquemas flexibles y alta velocidad de lectura/escritura para la experiencia del usuario (NoSQL), y finalmente, construir un pipeline de extracción y transformación de datos para alimentar un Data Mart (Analítica). Abarca el ciclo de vida completo del dato corporativo, integrando las tres unidades de evaluación en una solución técnica cohesiva.

## Política de Uso de IA
En el desarrollo de este proyecto, los asistentes de Inteligencia Artificial se utilizarán bajo la metodología de **"Copiloto Arquitectónico y de Código"**:
*   **Estructuración:** Apoyo en el diseño de los esquemas relacionales y documentales.
*   **Generación de Datos:** Creación de scripts de *mock data* (datos falsos) masivos para pruebas de carga en las bases de datos.
*   **Optimización:** Refactorización de consultas SQL complejas o pipelines de agregación NoSQL.
*   **Restricción:** Ningún bloque de código o consulta generada por IA será integrada en la rama principal (`main`) sin ser previamente auditada, entendida y probada por los miembros del equipo. Test