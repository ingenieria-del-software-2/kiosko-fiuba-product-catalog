#!/bin/bash

# Script para popular la base de datos con productos de ejemplo

API_URL="http://localhost:8000/api"
CATEGORIES_URL="$API_URL/categories/categories"
BRANDS_URL="$API_URL/brands/brands"
PRODUCTS_URL="$API_URL/products"

echo "Populando la base de datos..."

# Crear categorías
echo "Creando categorías..."

ELECTRONICS_ID=$(curl -s -X POST "$CATEGORIES_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electrónicos",
    "slug": "electronicos",
    "description": "Productos electrónicos y gadgets"
  }' | jq -r '.id')

echo "Categoría Electrónicos creada con ID: $ELECTRONICS_ID"

LAPTOPS_ID=$(curl -s -X POST "$CATEGORIES_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptops",
    "slug": "laptops",
    "description": "Computadoras portátiles y notebooks",
    "parent_id": "'"$ELECTRONICS_ID"'"
  }' | jq -r '.id')

echo "Categoría Laptops creada con ID: $LAPTOPS_ID"

HOME_ID=$(curl -s -X POST "$CATEGORIES_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hogar",
    "slug": "hogar",
    "description": "Productos para el hogar"
  }' | jq -r '.id')

echo "Categoría Hogar creada con ID: $HOME_ID"

KITCHEN_ID=$(curl -s -X POST "$CATEGORIES_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cocina",
    "slug": "cocina",
    "description": "Productos para la cocina",
    "parent_id": "'"$HOME_ID"'"
  }' | jq -r '.id')

echo "Categoría Cocina creada con ID: $KITCHEN_ID"

# Validar IDs
if [[ -z "$ELECTRONICS_ID" || "$ELECTRONICS_ID" == "null" ||
      -z "$LAPTOPS_ID" || "$LAPTOPS_ID" == "null" ||
      -z "$HOME_ID" || "$HOME_ID" == "null" ||
      -z "$KITCHEN_ID" || "$KITCHEN_ID" == "null" ]]; then
  echo "❌ Error: Uno o más IDs de categoría son inválidos."
  exit 1
fi

# Crear marcas
echo "Creando marcas..."

HP_ID=$(curl -s -X POST "$BRANDS_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HP",
    "logo": "https://example.com/hp-logo.png",
    "description": "Hewlett-Packard Company"
  }' | jq -r '.id')

echo "Marca HP creada con ID: $HP_ID"

THERMOS_ID=$(curl -s -X POST "$BRANDS_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Thermos",
    "logo": "https://example.com/thermos-logo.png",
    "description": "Especialistas en productos térmicos"
  }' | jq -r '.id')

echo "Marca Thermos creada con ID: $THERMOS_ID"

# Crear productos
echo "Creando productos..."

# Producto Laptop
echo "Creando laptop..."
curl -s -X POST "$PRODUCTS_URL/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop HP Pavilion 15",
    "slug": "laptop-hp-pavilion-15",
    "description": "Laptop HP Pavilion 15 con procesador Intel Core i7, 16GB de RAM y 512GB SSD",
    "summary": "Laptop potente y versátil para trabajo y entretenimiento",
    "price": 12999.99,
    "compareAtPrice": 13999.99,
    "currency": "ARS",
    "brand_id": "'$HP_ID'",
    "model": "Pavilion 15-eg1xxx",
    "sku": "HP-PAV-15-2023",
    "stock": 50,
    "isAvailable": true,
    "isNew": true,
    "condition": "new",
    "category_ids": ["'$LAPTOPS_ID'"],
    "tags": ["laptop", "hp", "computadora", "intel", "oferta"],
    "images": [
      {
        "url": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-DpbgguUV1vH8YkXMYntRtDcxSDx5yn.png",
        "alt": "Dell Inspiron 15 3520 - Vista frontal",
        "isMain": true,
        "order": 1
      },
      {
        "url": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-GUEvjUnZPMsMUbPbAWOFohlOSV2iZE.png",
        "alt": "Dell Inspiron 15 3520 - Vista en ángulo con teclado",
        "isMain": false,
        "order": 2
      },
      {
        "url": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-OydAoInnWHSLmTn7Xyf4ikcIPUwbcc.png",
        "alt": "Dell Inspiron 15 3520 - Vista lateral",
        "isMain": false,
        "order": 3
      },
      {
        "url": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-ntNRI6gVMYfiY1t6INIiKmpdKcEPtQ.png",
        "alt": "Dell Inspiron 15 3520 - Vista superior cerrada",
        "isMain": false,
        "order": 4
      },
      {
        "url": "https://hebbkx1anhila5yf.public.blob.vercel-storage.com/image-NctTXYhGw0i625k1ZpJ8Jhsp9l8TMs.png",
        "alt": "Dell Inspiron 15 3520 - Vista de perfil",
        "isMain": false,
        "order": 5
      }
    ],
    "attributes": [
      {
        "name": "Procesador",
        "value": "Intel Core i7-1165G7",
        "displayValue": "Intel Core i7 11a Gen",
        "isHighlighted": true
      },
      {
        "name": "Memoria RAM",
        "value": "16GB",
        "displayValue": "16GB DDR4",
        "isHighlighted": true
      },
      {
        "name": "Almacenamiento",
        "value": "512GB",
        "displayValue": "512GB SSD NVMe",
        "isHighlighted": true
      },
      {
        "name": "Pantalla",
        "value": "15.6 pulgadas FHD",
        "displayValue": "15.6\" Full HD IPS",
        "isHighlighted": false
      },
      {
        "name": "Tarjeta Gráfica",
        "value": "Intel Iris Xe",
        "displayValue": "Intel Iris Xe Graphics",
        "isHighlighted": false
      }
    ],
    "highlightedFeatures": [
      "Procesador Intel Core i7 de 11a generación",
      "16GB de memoria RAM DDR4",
      "Disco SSD de 512GB ultrarrápido",
      "Pantalla Full HD de 15.6 pulgadas",
      "Windows 11 Home"
    ]
  }'

# Producto Thermos
echo "Creando termo..."
curl -s -X POST "$PRODUCTS_URL/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Termo Stanley Clásico 1.4lts Negro",
    "slug": "termo-stanley-clasico-1.4lts-negro",
    "description": "Termo Stanley de acero inoxidable con capacidad de 1.4 litros",
    "summary": "Termo de alta calidad para mantener tus bebidas a la temperatura ideal",
    "price": 4999.99,
    "compareAtPrice": 5999.99,
    "currency": "ARS",
    "brand_id": "'$THERMOS_ID'",
    "model": "Stanley Clásico 1.4lts Negro",
    "sku": "THERMOS-STANLEY-1.4L-NEGRO",
    "stock": 100,
    "isAvailable": true,
    "isNew": false,
    "condition": "new",
    "category_ids": ["'$KITCHEN_ID'"],
    "tags": ["termo", "thermos", "acero inoxidable", "cocina", "mate"],
    "images": [
      {
        "url": "/images/stanley-black.png",
        "alt": "Termo Stanley Clásico 1.4lts Negro - Vista principal",
        "isMain": true,
        "order": 1
      },
      {
        "url": "/images/stanley-black-specs.png",
        "alt": "Termo Stanley Clásico 1.4lts Negro - Especificaciones",
        "isMain": false,
        "order": 2
      },
      {
        "url": "/images/stanley-black-open.png",
        "alt": "Termo Stanley Clásico 1.4lts Negro - Con tapa abierta",
        "isMain": false,
        "order": 3
      }
    ],
    "attributes": [
      {
        "name": "Material",
        "value": "acero-inoxidable",
        "displayValue": "Acero Inoxidable",
        "isHighlighted": true
      },
      {
        "name": "Capacidad",
        "value": "1.4L",
        "displayValue": "1.4 Litros",
        "isHighlighted": true
      },
      {
        "name": "Tiempo Conservación Calor",
        "value": "24h",
        "displayValue": "24 horas",
        "isHighlighted": true
      },
      {
        "name": "Tiempo Conservación Frío",
        "value": "36h",
        "displayValue": "36 horas",
        "isHighlighted": false
      },
      {
        "name": "Color",
        "value": "negro",
        "displayValue": "Negro",
        "isHighlighted": false
      }
    ],
    "highlightedFeatures": [
      "Fabricado en acero inoxidable de alta calidad",
      "Mantiene bebidas calientes por 24 horas",
      "Mantiene bebidas frías por 36 horas",
      "Tapa que sirve como vaso",
      "Diseño ergonómico y antideslizante"
    ]
  }'

echo "✅ Base de datos populada con éxito."
