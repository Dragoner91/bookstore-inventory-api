# Bookstore Inventory API

API REST para la gestión de inventario de una cadena de librerías, con cálculo de precio de
venta sugerido a partir de la tasa de cambio USD → Bolívares en tiempo real.

## Requisitos previos

**Opción recomendada:** Docker y Docker Compose. No hace falta nada más.

**Sin Docker:**

- Python 3.12 o superior
- Una base de datos PostgreSQL accesible
- Dependencias del proyecto, listadas en `requirements.txt`: FastAPI, SQLModel, asyncpg,
  httpx, pydantic-settings y uvicorn

## Instalación y ejecución

### Con Docker

Levanta la API junto a una base PostgreSQL, sin configuración adicional:

```bash
git clone https://github.com/Dragoner91/bookstore-inventory-api.git
cd bookstore-inventory-api
docker compose up --build
```

La API queda disponible en http://localhost:8000 y la documentación en
http://localhost:8000/docs. Las tablas se crean automáticamente al arrancar.

### Sin Docker

```bash
git clone https://github.com/Dragoner91/bookstore-inventory-api.git
cd bookstore-inventory-api

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.template .env      # y ajustar DATABASE_URL

uvicorn app.main:app --reload
```

### Variables de entorno

| Variable | Obligatoria | Por defecto | Descripción |
|---|---|---|---|
| `DATABASE_URL` | Sí | — | Cadena de conexión. El driver debe ser `postgresql+asyncpg://` |
| `DEFAULT_USD_RATE` | No | `750.00` | Tasa USD → VES usada si la API de cambio falla |
| `MARGIN_PERCENTAGE` | No | `40` | Margen de ganancia aplicado sobre el costo |
| `EXCHANGE_API_URL` | No | `https://api.exchangerate-api.com/v4/latest/USD` | API de tasas de cambio |
| `EXCHANGE_TIMEOUT_SECONDS` | No | `5.0` | Tiempo máximo de espera de esa API |

## Ejemplos de uso de los endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/books` | Crear libro |
| `GET` | `/books?limit=&offset=` | Listar libros paginados |
| `GET` | `/books/search?category=` | Buscar por categoría |
| `GET` | `/books/low-stock?threshold=` | Libros con stock bajo |
| `GET` | `/books/{id}` | Obtener libro por ID |
| `PUT` | `/books/{id}` | Actualizar libro |
| `DELETE` | `/books/{id}` | Eliminar libro |
| `POST` | `/books/{id}/calculate-price` | Calcular precio de venta sugerido |

En los ejemplos, reemplazar `$URL` por
`https://bookstore-inventory-api-w36d.onrender.com` o por `http://localhost:8000`.

### Crear un libro

```bash
curl -X POST $URL/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "El Quijote",
    "author": "Miguel de Cervantes",
    "isbn": "978-84-376-0494-7",
    "cost_usd": 15.99,
    "stock_quantity": 25,
    "category": "Literatura Clasica",
    "supplier_country": "ES"
  }'
```

```json
{
  "title": "El Quijote",
  "author": "Miguel de Cervantes",
  "isbn": "9788437604947",
  "cost_usd": "15.99",
  "stock_quantity": 25,
  "category": "Literatura Clasica",
  "supplier_country": "ES",
  "id": 1,
  "selling_price_local": null,
  "created_at": "2026-08-12T21:45:11.955368Z",
  "updated_at": "2026-08-12T21:45:11.955368Z"
}
```

`selling_price_local` nace en `null`: solo se completa al invocar `calculate-price`.

### Calcular el precio de venta sugerido

```bash
curl -X POST $URL/books/1/calculate-price
```

```json
{
  "book_id": 1,
  "cost_usd": "15.99",
  "exchange_rate": "764.35",
  "cost_local": "12221.96",
  "margin_percentage": "40",
  "selling_price_local": "17110.74",
  "currency": "Bs",
  "rate_source": "api",
  "rate_notice": null,
  "calculation_timestamp": "2026-08-12T21:45:32.907232Z"
}
```

Si la API de tasas no responde, el cálculo se completa con la tasa por defecto y la
respuesta lo indica en `rate_source` y `rate_notice`.

### Consultar y filtrar

```bash
curl "$URL/books?limit=10&offset=0"
curl "$URL/books/1"
curl "$URL/books/search?category=Literatura%20Clasica"
curl "$URL/books/low-stock?threshold=10"
```

### Actualizar y eliminar

```bash
curl -X PUT $URL/books/1 \
  -H "Content-Type: application/json" \
  -d '{"stock_quantity": 7}'

curl -X DELETE $URL/books/1
```

### Respuestas de error

```
409 → {"detail": "Ya existe un libro con ese ISBN"}
400 → {"detail": "El ISBN debe tener 10 o 13 dígitos"}
400 → {"detail": "cost_usd debe ser mayor a 0"}
404 → {"detail": "No existe un libro con id 999999"}
```
