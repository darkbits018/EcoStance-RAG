# EcoStance Backend API Documentation

Base URL: `http://localhost:5000/api`

---

## Products API

### Get All Products
Retrieve all products with optional filtering and sorting.

**Endpoint:** `GET /api/products`

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `category` | string | Filter by category | `Carbon Offsets` |
| `location` | string | Filter by location | `Brazil` |
| `onSale` | boolean | Filter sale items only | `true` |
| `isNew` | boolean | Filter new items only | `true` |
| `tag` | string | Filter by tag | `REDD+` |
| `minPrice` | number | Minimum price filter | `500` |
| `maxPrice` | number | Maximum price filter | `1000` |
| `sortBy` | string | Sort results | `price-asc`, `price-desc`, `rating`, `reviews` |

**Example Request:**
```bash
GET /api/products?category=Carbon%20Offsets&maxPrice=600&sortBy=price-asc
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": "e1",
      "name": "Nitrous Gas Removal",
      "price": 540.00,
      "oldPrice": 640.00,
      "category": "Carbon Offsets",
      "image": "https://...",
      "rating": 4.5,
      "reviews": 12,
      "location": "Egypt",
      "onSale": true,
      "tags": ["VCS", "CDM"]
    }
  ]
}
```

---

### Get Product by ID
Retrieve a single product by its ID.

**Endpoint:** `GET /api/products/:id`

**Path Parameters:**
- `id` (string, required) - Product ID

**Example Request:**
```bash
GET /api/products/e1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "e1",
    "name": "Nitrous Gas Removal",
    "price": 540.00,
    "oldPrice": 640.00,
    "category": "Carbon Offsets",
    "image": "https://...",
    "rating": 4.5,
    "reviews": 12,
    "location": "Egypt",
    "onSale": true,
    "tags": ["VCS", "CDM"]
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Product not found"
}
```

---

### Search Products
Search products by name, location, or tags.

**Endpoint:** `GET /api/products/search/query`

**Query Parameters:**
- `q` (string, required) - Search query

**Example Request:**
```bash
GET /api/products/search/query?q=wind
```

**Response:**
```json
{
  "success": true,
  "count": 3,
  "data": [
    {
      "id": "e2",
      "name": "Piedra Wind Farm",
      "price": 515.00,
      "category": "Carbon Offsets",
      "location": "Mexico",
      "rating": 4.8,
      "reviews": 24,
      "tags": ["Gold Standard"]
    }
  ]
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Search query required"
}
```

---

## Projects API

### Get All Projects
Retrieve all environmental projects with optional filtering.

**Endpoint:** `GET /api/projects`

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `type` | string | Filter by project type | `REFORESTATION`, `RENEWABLE_ENERGY`, `OCEAN_CLEANUP` |
| `location` | string | Filter by location | `Brazil` |
| `maxCost` | number | Maximum offset cost | `15` |

**Example Request:**
```bash
GET /api/projects?type=REFORESTATION&maxCost=20
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": "1",
      "title": "Amazon Reforestation",
      "description": "Protecting and restoring critical habitats in the Amazon basin through community-led efforts.",
      "image": "https://...",
      "type": "REFORESTATION",
      "location": "Brazil",
      "offsetCost": 15
    }
  ]
}
```

---

### Get Project by ID
Retrieve a single project by its ID.

**Endpoint:** `GET /api/projects/:id`

**Path Parameters:**
- `id` (string, required) - Project ID

**Example Request:**
```bash
GET /api/projects/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "1",
    "title": "Amazon Reforestation",
    "description": "Protecting and restoring critical habitats in the Amazon basin through community-led efforts.",
    "image": "https://...",
    "type": "REFORESTATION",
    "location": "Brazil",
    "offsetCost": 15
  }
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Project not found"
}
```

---

## Health Check

### Server Health
Check if the API server is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok",
  "message": "EcoStance Backend API is running"
}
```

---

## Error Handling

All endpoints return consistent error responses:

**Format:**
```json
{
  "success": false,
  "message": "Error description"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (missing/invalid parameters)
- `404` - Resource Not Found
- `500` - Internal Server Error

---

## CORS

CORS is enabled for all origins. The API accepts requests from any domain.

---

## Data Models

### Product Model
```typescript
interface Product {
  id: string;
  name: string;
  price: number;
  oldPrice?: number;
  category: string;
  image: string;
  rating: number;
  reviews: number;
  location: string;
  onSale?: boolean;
  isNew?: boolean;
  tags: string[];
}
```

### Project Model
```typescript
interface Project {
  id: string;
  title: string;
  description: string;
  image: string;
  type: 'REFORESTATION' | 'RENEWABLE_ENERGY' | 'OCEAN_CLEANUP';
  location: string;
  offsetCost: number;
}
```

---

## Usage Examples

### JavaScript/TypeScript

```typescript
// Get all products
const response = await fetch('http://localhost:5000/api/products');
const { data } = await response.json();

// Get products with filters
const filtered = await fetch(
  'http://localhost:5000/api/products?category=Carbon%20Offsets&sortBy=price-asc'
);
const { data: products } = await filtered.json();

// Search products
const search = await fetch(
  'http://localhost:5000/api/products/search/query?q=wind'
);
const { data: results } = await search.json();

// Get single product
const product = await fetch('http://localhost:5000/api/products/e1');
const { data: productData } = await product.json();
```

### cURL

```bash
# Get all products
curl http://localhost:5000/api/products

# Get products with filters
curl "http://localhost:5000/api/products?category=Carbon%20Offsets&maxPrice=600"

# Search products
curl "http://localhost:5000/api/products/search/query?q=wind"

# Get single product
curl http://localhost:5000/api/products/e1

# Get all projects
curl http://localhost:5000/api/projects

# Get single project
curl http://localhost:5000/api/projects/1
```

---

## Rate Limiting

Currently, there are no rate limits implemented. This may be added in future versions.

---

## Authentication

No authentication is required for any endpoints. All endpoints are publicly accessible.

---

## Versioning

Current version: `v1.0.0`

The API does not currently use versioning in the URL path. Future versions may introduce `/api/v2/` endpoints.
