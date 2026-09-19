// =============================================
// PROYECTO: Urban Kicks E-Commerce
// MÓDULO:   Catálogo NoSQL Completo y Enriquecido (Unidad 2)
// MOTOR:    MongoDB
// =============================================

// Seleccionar la base de datos
use('urban_kicks_db');

// 1. Limpiar la colección si existe para poder ejecutar el script desde cero
db.productos.drop();

// 2. Crear la colección con validación estricta de esquema (JSON Schema)
db.createCollection("productos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["nombre", "marca", "categoria", "precioBaseCop", "activo", "variantes"],
      properties: {
        nombre: {
          bsonType: "string",
          description: "Nombre del producto (obligatorio)"
        },
        marca: {
          bsonType: "object",
          required: ["nombre", "paisOrigen"],
          properties: {
            nombre: { bsonType: "string" },
            paisOrigen: { bsonType: "string" }
          }
        },
        categoria: {
          bsonType: "string",
          description: "Categoría principal (obligatorio, ej: Zapatillas, Ropa Urbana, Accesorios)"
        },
        precioBaseCop: {
          bsonType: "int",
          minimum: 0,
          description: "Precio base en pesos colombianos (obligatorio, >= 0)"
        },
        activo: {
          bsonType: "bool"
        },
        variantes: {
          bsonType: "array",
          description: "Lista de variantes de inventario (Obligatorio al menos un elemento)",
          minItems: 1,
          items: {
            bsonType: "object",
            required: ["sku", "talla", "color", "stock"],
            properties: {
              sku: { bsonType: "string", description: "Soft link hacia la base relacional SQL" },
              talla: { bsonType: "string" },
              color: {
                bsonType: "object",
                required: ["nombre", "hex"],
                properties: {
                  nombre: { bsonType: "string" },
                  hex: { bsonType: "string" }
                }
              },
              precioAdicionalCop: { bsonType: "int", minimum: 0 },
              stock: { bsonType: "int", minimum: 0 }
            }
          }
        }
      }
    }
  }
});

// 3. Insertar el catálogo robusto de productos (Mock Data Colombiano)
db.productos.insertMany([
  {
    "nombre": "Adidas Forum Low Bad Bunny",
    "marca": { "nombre": "Adidas", "paisOrigen": "Alemania" },
    "categoria": "Zapatillas",
    "descripcion": "Colección especial Bad Bunny x Adidas, suela gruesa y detalles en verde olivo.",
    "precioBaseCop": 950000,
    "imagenes": [
      "https://ejemplo.com/img/badbunny_1.jpg",
      "https://ejemplo.com/img/badbunny_2.jpg"
    ],
    "atributosEspecificos": { "colaboracion": "Bad Bunny", "cierre": "Cordones y velcro", "material": "Cuero y gamuza" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "AD-BB-FORUM-US8", "talla": "US 8", "color": { "nombre": "Verde Olivo", "hex": "#556B2F" }, "precioAdicionalCop": 0, "stock": 2 },
      { "sku": "AD-BB-FORUM-US9", "talla": "US 9", "color": { "nombre": "Verde Olivo", "hex": "#556B2F" }, "precioAdicionalCop": 0, "stock": 5 }
    ]
  },
  {
    "nombre": "Adidas Samba OG White Gum",
    "marca": { "nombre": "Adidas", "paisOrigen": "Alemania" },
    "categoria": "Zapatillas",
    "descripcion": "El clásico zapato de fútbol sala convertido en un ícono del streetwear.",
    "precioBaseCop": 520000,
    "imagenes": ["https://ejemplo.com/img/samba_wg.jpg"],
    "atributosEspecificos": { "estilo": "Retro", "material": "Cuero y punta de gamuza" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "AD-SAMBA-WG-US8", "talla": "US 8", "color": { "nombre": "Blanco Nube", "hex": "#FFFFFF" }, "precioAdicionalCop": 0, "stock": 10 },
      { "sku": "AD-SAMBA-WG-US9", "talla": "US 9", "color": { "nombre": "Blanco Nube", "hex": "#FFFFFF" }, "precioAdicionalCop": 0, "stock": 15 }
    ]
  },
  {
    "nombre": "Nike Air Force 1 '07",
    "marca": { "nombre": "Nike", "paisOrigen": "Estados Unidos" },
    "categoria": "Zapatillas",
    "descripcion": "La silueta más icónica de Nike, en su versión triple blanco inmaculado.",
    "precioBaseCop": 480000,
    "imagenes": ["https://ejemplo.com/img/af1_wht.jpg"],
    "atributosEspecificos": { "estilo": "Clásico", "corte": "Bajo (Low)", "material": "Cuero" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "NK-AF1-WHT-US8", "talla": "US 8", "color": { "nombre": "Blanco", "hex": "#FFFFFF" }, "precioAdicionalCop": 0, "stock": 20 },
      { "sku": "NK-AF1-WHT-US9", "talla": "US 9", "color": { "nombre": "Blanco", "hex": "#FFFFFF" }, "precioAdicionalCop": 0, "stock": 25 },
      { "sku": "NK-AF1-BLK-US9", "talla": "US 9", "color": { "nombre": "Negro", "hex": "#000000" }, "precioAdicionalCop": 0, "stock": 5 }
    ]
  },
  {
    "nombre": "Air Jordan 1 Retro High Chicago",
    "marca": { "nombre": "Jordan", "paisOrigen": "Estados Unidos" },
    "categoria": "Zapatillas",
    "descripcion": "El santo grial de las zapatillas. Edición Retro High OG en el colorway original de Chicago.",
    "precioBaseCop": 1200000,
    "imagenes": ["https://ejemplo.com/img/jordan1_chicago.jpg"],
    "atributosEspecificos": { "corte": "Alto (High)", "colaboracion": "Michael Jordan", "material": "Cuero premium" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "JD1-CHI-US8", "talla": "US 8", "color": { "nombre": "Rojo/Blanco/Negro", "hex": "#C8102E" }, "precioAdicionalCop": 100000, "stock": 2 },
      { "sku": "JD1-CHI-US9", "talla": "US 9", "color": { "nombre": "Rojo/Blanco/Negro", "hex": "#C8102E" }, "precioAdicionalCop": 200000, "stock": 1 }
    ]
  },
  {
    "nombre": "Hoodie Classics Adicolor",
    "marca": { "nombre": "Adidas", "paisOrigen": "Alemania" },
    "categoria": "Ropa Urbana",
    "descripcion": "Saco con capucha clásico, cómodo y con el logo del Trifolio bordado.",
    "precioBaseCop": 350000,
    "imagenes": ["https://ejemplo.com/img/hoodie_adidas_blk.jpg"],
    "atributosEspecificos": { "tipo_prenda": "Saco", "material": "Algodón francés", "fit": "Regular" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "AD-HD-BLK-S", "talla": "S", "color": { "nombre": "Negro", "hex": "#000000" }, "precioAdicionalCop": 0, "stock": 10 },
      { "sku": "AD-HD-BLK-M", "talla": "M", "color": { "nombre": "Negro", "hex": "#000000" }, "precioAdicionalCop": 0, "stock": 15 },
      { "sku": "AD-HD-BLK-L", "talla": "L", "color": { "nombre": "Negro", "hex": "#000000" }, "precioAdicionalCop": 0, "stock": 5 }
    ]
  },
  {
    "nombre": "Jogger Nike Sportswear Tech Fleece",
    "marca": { "nombre": "Nike", "paisOrigen": "Estados Unidos" },
    "categoria": "Ropa Urbana",
    "descripcion": "Pantalón para uso diario con un diseño cálido sin peso adicional gracias al tejido Tech Fleece.",
    "precioBaseCop": 420000,
    "imagenes": ["https://ejemplo.com/img/nike_tech_fleece_gry.jpg"],
    "atributosEspecificos": { "tipo_prenda": "Pantalón", "material": "Algodón/Poliéster", "fit": "Slim" },
    "activo": true,
    "fechaCreacion": new Date(),
    "variantes": [
      { "sku": "NK-TF-GRY-M", "talla": "M", "color": { "nombre": "Gris Jaspeado", "hex": "#808080" }, "precioAdicionalCop": 0, "stock": 8 },
      { "sku": "NK-TF-GRY-L", "talla": "L", "color": { "nombre": "Gris Jaspeado", "hex": "#808080" }, "precioAdicionalCop": 0, "stock": 12 }
    ]
  }
]);

// 4. Crear índices de alto rendimiento
// Índice de texto para barra de búsqueda rápida (buscar "Jordan", "Nike", etc.)
db.productos.createIndex({ "nombre": "text", "descripcion": "text" });

// Índices regulares para filtrado en el frontend
db.productos.createIndex({ "marca.nombre": 1 });
db.productos.createIndex({ "categoria": 1 });

// Índice único en las variantes embebidas para que no haya dos SKUs repetidos en toda la base
db.productos.createIndex({ "variantes.sku": 1 }, { unique: true });

print("¡Base de datos NoSQL inicializada con éxito!");
