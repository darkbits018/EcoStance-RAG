# API Documentation

Base URL: `http://localhost:3000`

## Categories

### Get All Categories
Retrieves a list of all product categories.

- **Endpoint**: `/api/categories`
- **Method**: `GET`
- **Response**: `200 OK`
- **Content-Type**: `application/json`

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Audio",
    "slug": "audio",
    "image": "https://images.unsplash.com/..."
  },
  {
    "id": 2,
    "name": "Photography",
    "slug": "photography",
    "image": "https://images.unsplash.com/..."
  }
]
```

---

## Products

### Get All Products
Retrieves a list of all products.

- **Endpoint**: `/api/products`
- **Method**: `GET`
- **Response**: `200 OK`
- **Content-Type**: `application/json`

**Query Parameters:**

| Parameter  | Type   | Description                                      | Example              |
|Link        | link   | link                                             | link                 |
|------------|--------|--------------------------------------------------|----------------------|
| `category` | string | (Optional) Filter products by category slug.     | `?category=gaming`   |
| `search`   | string | (Optional) Search products by name (partial match). | `?search=sony`       |

**Example Response (All Products):**
```json
[
  {
    "id": 1,
    "category_id": 1,
    "name": "Sony WH-1000XM5",
    "description": "Industry-leading noise canceling headphones...",
    "price": 348.00,
    "image": "https://images.unsplash.com/...",
    "rating": 4.8,
    "categoryId": 1
  },
  ...
]
```

**Example Response (Filtered by Category):**
`GET /api/products?category=gaming`

```json
[
  {
    "id": 5,
    "category_id": 3,
    "name": "PlayStation 5",
    "description": "Play Has No Limits...",
    "price": 499.00,
    ...
  }
]
```

**Example Response (Search):**
`GET /api/products?search=watch`

```json
[
  {
    "id": 7,
    "name": "Apple Watch Ultra",
    ...
  },
  {
    "id": 8,
    "name": "Galaxy Watch 6",
    ...
  }
]
```

## Database Schema

**Categories Table**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL
- `slug`: TEXT NOT NULL UNIQUE
- `image`: TEXT

**Products Table**
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `category_id`: INTEGER (Foreign Key -> categories.id)
- `name`: TEXT NOT NULL
- `description`: TEXT
- `price`: REAL NOT NULL
- `image`: TEXT
- `rating`: REAL
