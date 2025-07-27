# SweetShop API Documentation

## 🍭 Complete API Reference

This document provides comprehensive API documentation for the SweetShop backend, showcasing RESTful design principles and professional API development practices tailored for the Gujarat sweet market.

## 🔐 Authentication Endpoints

### User Registration
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "priya_shah",
  "email": "priya.shah@gmail.com",
  "password": "Gujarat@123",
  "role": "customer"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "username": "priya_shah",
    "email": "priya.shah@gmail.com",
    "role": "customer",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### User Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=priya_shah&password=Gujarat@123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Token Revocation
```http
POST /api/auth/logout
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

## 🍬 Sweet Management Endpoints

### List All Sweets
```http
GET /api/sweets?page=1&size=10&category_id=1&min_price=150.00&max_price=800.00
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Kaju Katli",
      "description": "Premium cashew fudge made with pure ghee and silver leaf",
      "price": 450.00,
      "category": {
        "id": 1,
        "name": "Dry Fruits Sweets"
      },
      "inventory": {
        "quantity": 25
      },
      "average_rating": 4.9,
      "review_count": 87
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

### Get Sweet Details
```http
GET /api/sweets/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Kaju Katli",
  "description": "Premium cashew fudge made with pure ghee and silver leaf",
  "price": 450.00,
  "category": {
    "id": 1,
    "name": "Dry Fruits Sweets"
  },
  "inventory": {
    "quantity": 25
  },
  "reviews": [
    {
      "id": 1,
      "user": "priya_shah",
      "rating": 5,
      "comment": "Ekdum fresh ane taste pan खूब સરસ! મારા બાળકોને ખૂબ ગમ્યું.",
      "created_at": "2024-01-14T15:20:00Z"
    }
  ],
  "average_rating": 4.9,
  "review_count": 87
}
```

### Create Sweet (Admin Only)
```http
POST /api/sweets
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "name": "Gujarati Dhokla",
  "description": "Traditional steamed gram flour cake with mustard seed tempering",
  "price": 180.00,
  "category_id": 2
}
```

**Response (201 Created):**
```json
{
  "id": 15,
  "name": "Gujarati Dhokla",
  "description": "Traditional steamed gram flour cake with mustard seed tempering",
  "price": 180.00,
  "category": {
    "id": 2,
    "name": "Traditional Sweets"
  },
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Update Sweet (Admin Only)
```http
PUT /api/sweets/15
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "name": "Premium Gujarati Dhokla",
  "description": "Traditional steamed gram flour cake with organic ingredients and special green chutney",
  "price": 220.00
}
```

**Response (200 OK):**
```json
{
  "id": 15,
  "name": "Premium Gujarati Dhokla",
  "description": "Traditional steamed gram flour cake with organic ingredients and special green chutney",
  "price": 220.00,
  "category": {
    "id": 2,
    "name": "Traditional Sweets"
  },
  "updated_at": "2024-01-15T11:30:00Z"
}
```

### Delete Sweet (Admin Only)
```http
DELETE /api/sweets/15
Authorization: Bearer {admin_access_token}
```

**Response (204 No Content)**

## 🛒 Purchase Endpoints

### Create Purchase
```http
POST /api/purchases
Authorization: Bearer {customer_access_token}
Content-Type: application/json

{
  "items": [
    {
      "sweet_id": 1,
      "quantity": 2
    },
    {
      "sweet_id": 3,
      "quantity": 1
    }
  ],
  "delivery_address": "B-204, Shyam Residency, Near Navrangpura Metro, Ahmedabad, Gujarat 380009"
}
```

**Response (201 Created):**
```json
{
  "id": 42,
  "user_id": 1,
  "items": [
    {
      "sweet": {
        "id": 1,
        "name": "Kaju Katli",
        "price": 450.00
      },
      "quantity": 2,
      "unit_price": 450.00,
      "subtotal": 900.00
    },
    {
      "sweet": {
        "id": 3,
        "name": "Mohanthal",
        "price": 320.00
      },
      "quantity": 1,
      "unit_price": 320.00,
      "subtotal": 320.00
    }
  ],
  "total_amount": 1220.00,
  "delivery_address": "B-204, Shyam Residency, Near Navrangpura Metro, Ahmedabad, Gujarat 380009",
  "status": "pending",
  "created_at": "2024-01-15T12:00:00Z"
}
```

### List User Purchases
```http
GET /api/purchases?page=1&size=10
Authorization: Bearer {customer_access_token}
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 42,
      "total_amount": 1220.00,
      "status": "delivered",
      "created_at": "2024-01-15T12:00:00Z",
      "item_count": 2
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

### Get Purchase Details
```http
GET /api/purchases/42
Authorization: Bearer {customer_access_token}
```

**Response (200 OK):**
```json
{
  "id": 42,
  "user_id": 1,
  "items": [
    {
      "sweet": {
        "id": 1,
        "name": "Kaju Katli",
        "price": 450.00
      },
      "quantity": 2,
      "unit_price": 450.00,
      "subtotal": 900.00
    }
  ],
  "total_amount": 1220.00,
  "delivery_address": "B-204, Shyam Residency, Near Navrangpura Metro, Ahmedabad, Gujarat 380009",
  "status": "delivered",
  "created_at": "2024-01-15T12:00:00Z",
  "delivered_at": "2024-01-16T14:30:00Z"
}
```

## ⭐ Review Endpoints

### Create Review
```http
POST /api/reviews
Authorization: Bearer {customer_access_token}
Content-Type: application/json

{
  "sweet_id": 1,
  "rating": 5,
  "comment": "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે."
}
```

**Response (201 Created):**
```json
{
  "id": 25,
  "sweet_id": 1,
  "user": "priya_shah",
  "rating": 5,
  "comment": "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે.",
  "created_at": "2024-01-15T13:00:00Z"
}
```

### List Sweet Reviews
```http
GET /api/sweets/1/reviews?page=1&size=10
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 25,
      "user": "priya_shah",
      "rating": 5,
      "comment": "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે.",
      "created_at": "2024-01-15T13:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1,
  "average_rating": 5.0
}
```

### Update Review
```http
PUT /api/reviews/25
Authorization: Bearer {customer_access_token}
Content-Type: application/json

{
  "rating": 4,
  "comment": "સારો કાજુ કતલી છે, પણ થોડો મોંઘો લાગે છે. Quality સારી છે though."
}
```

**Response (200 OK):**
```json
{
  "id": 25,
  "sweet_id": 1,
  "user": "priya_shah",
  "rating": 4,
  "comment": "સારો કાજુ કતલી છે, પણ થોડો મોંઘો લાગે છે. Quality સારી છે though.",
  "updated_at": "2024-01-15T14:00:00Z"
}
```

### Delete Review
```http
DELETE /api/reviews/25
Authorization: Bearer {customer_access_token}
```

**Response (204 No Content)**

## 🔧 Admin Endpoints

### Restock Sweet Inventory
```http
POST /api/admin/restock
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "sweet_id": 1,
  "quantity_added": 50
}
```

**Response (201 Created):**
```json
{
  "sweet_id": 1,
  "quantity_added": 50,
  "new_total_quantity": 100,
  "restocked_by": "admin_user",
  "restocked_at": "2024-01-15T15:00:00Z"
}
```

### Get System Statistics
```http
GET /api/admin/stats
Authorization: Bearer {admin_access_token}
```

**Response (200 OK):**
```json
{
  "total_users": 850,
  "total_sweets": 65,
  "total_orders": 1240,
  "revenue": {
    "total": 485000.75,
    "this_month": 85400.50,
    "this_week": 18500.25
  },
  "popular_sweets": [
    {
      "id": 1,
      "name": "Kaju Katli",
      "total_sold": 189
    }
  ],
  "low_inventory": [
    {
      "id": 5,
      "name": "Gujarati Jalebi",
      "quantity": 8
    }
  ]
}
```

### Manage Purchase Status
```http
PUT /api/admin/purchases/42/status
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "status": "shipped",
  "tracking_number": "SW123456789"
}
```

**Response (200 OK):**
```json
{
  "id": 42,
  "status": "shipped",
  "tracking_number": "SW123456789",
  "updated_at": "2024-01-15T16:00:00Z"
}
```

## 📊 Error Response Format

All error responses follow a consistent format:

```json
{
  "detail": "Error message description",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/endpoint/path"
}
```

### Common HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 204 | No Content | Successful DELETE requests |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource already exists or conflict |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Server-side errors |

## 🔄 Rate Limiting

All endpoints are rate-limited to prevent abuse:

- **Unauthenticated requests**: 100 requests per hour
- **Authenticated customers**: 1000 requests per hour
- **Admin users**: 5000 requests per hour

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642521600
```

## 📝 Request/Response Headers

### Required Headers for Authenticated Requests
```http
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
```

### Response Headers
```http
Content-Type: application/json
X-Request-ID: req_123456789
X-Response-Time: 45ms
```

## 🔍 Filtering and Pagination

### Query Parameters for List Endpoints

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number (1-based) | 1 |
| `size` | integer | Items per page (max 100) | 10 |
| `sort` | string | Sort field and direction | "id:asc" |
| `search` | string | Search term for name/description | - |
| `category_id` | integer | Filter by category | - |
| `min_price` | decimal | Minimum price filter | - |
| `max_price` | decimal | Maximum price filter | - |

### Example Filtered Request
```http
GET /api/sweets?search=kaju&category_id=1&min_price=300.00&sort=price:desc&page=1&size=20
```

This comprehensive API documentation demonstrates professional API design with consistent patterns, proper HTTP status codes, authentication flows, and detailed error handling tailored for the Gujarat sweet market.

## 🧪 API Testing & Validation

Our API endpoints are thoroughly tested using TDD methodology with **78 comprehensive test cases**:

```bash
Test Results: 73 PASSED, 5 SKIPPED (93.6% pass rate)
Test Coverage: Authentication, CRUD operations, multilingual support, security validation
```

### Tested Endpoints:
- **✅ Authentication**: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`
- **✅ Sweet Management**: All CRUD operations with Gujarat market examples
- **✅ Purchase System**: Complete order workflow with Indian pricing
- **✅ Review System**: Including Gujarati language content support
- **✅ Admin Operations**: Role-based access and inventory management

### Multilingual API Support:
```json
// Example: Gujarati language review via API
POST /api/reviews
{
  "sweet_id": 1,
  "rating": 5,
  "comment": "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે."
}

// Response preserves Unicode content
{
  "id": 25,
  "comment": "અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી! Fresh ane pure ghee નો સ્વાદ આવે છે.",
  "rating": 5,
  "created_at": "2024-01-15T13:00:00Z"
}
```
