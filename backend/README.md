# 🍬 SweetShop Backend - Test-Driven Development Implementation

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-76_passing-brightgreen.svg)](./tests)
[![TDD](https://img.shields.io/badge/Methodology-TDD-orange.svg)](https://en.wikipedia.org/wiki/Test-driven_development)

## Database Seeding

To seed the database with initial data, run:
```bash
python backend/seed_database.py
```

**Latest Update (July 2025):**
- User login and dashboard now require `is_verified: true` for access.
- Unverified users are blocked from login and dashboard.
- All backend tests pass (see tests/README.md for details).

A comprehensive sweet shop management system built using **Test-Driven Development (TDD)** methodology, demonstrating modern software engineering practices including clean architecture, SOLID principles, and professional AI-assisted development.

## 🎯 Project Overview

This backend API showcases my ability to implement complex business logic using industry-standard practices:

- **Test-Driven Development** - Every feature developed following RED-GREEN-REFACTOR cycle
- **Clean Architecture** - Proper separation of concerns across layers  
- **SOLID Principles** - Maintainable and extensible code design
- **Async Programming** - High-performance async/await patterns
- **Database Migrations** - Professional schema management with Alembic
- **Security Implementation** - JWT authentication with role-based authorization

## 📊 Technical Achievements

| Metric | Count | Description |
|--------|-------|-------------|
| **Unit Tests** | 78 | Comprehensive test coverage across all features |
| **Passing Tests** | 73 | 93.6% pass rate with robust error handling |
| **Test Files** | 13 | Well-organized test suites including multilingual support |
| **Domain Models** | 11 | Complete business domain representation |
| **API Endpoints** | 20+ | Full CRUD operations with filtering |
| **TDD Features** | 8 major | All developed test-first including Gujarati support |

## 🌍 Gujarat Market Features

### Multilingual Support
- **Gujarati Language**: Full Unicode support for Gujarati script in all content
- **Mixed Language**: Support for English-Gujarati mixed content common in urban Gujarat
- **Traditional Names**: Authentic sweet names like કાજુ કતલી (Kaju Katli), જલેબી (Jalebi)
- **Local Reviews**: Customer reviews in Gujarati with proper encoding

### Market-Specific Implementation
```python
# Example: Gujarati content storage
sweet = Sweet(
    name="કાજુ કતલી",  # Kaju Katli in Gujarati
    description="શુદ્ધ ઘી અને કાજુથી બનેલી પ્રીમિયમ મિઠાઈ",
    price=450.00
)

review = Review(
    comment="અમદાવાદ માં એવો સ્વાદિષ્ટ કાજુ કતલી ક્યાંય મળતો નથી!",
    rating=5
)
```

### Traditional Sweet Categories
- **ગુજરાતી મિઠાઈ** (Gujarati Sweets): કાજુ કતલી, મોહનથાળ, બાસુંદી
- **પરંપરાગત વાનગીઓ** (Traditional Items): ઢોકળા, ખાંડવી, ફાફડા
- **તહેવારી મિઠાઈ** (Festival Sweets): જલેબી, રસગુલ્લા, પેડા

## 🏗️ Architecture & Design

### Project Structure
```
backend/
├── app/                    # Core application
│   ├── core/              # Domain abstractions and interfaces
│   ├── models/            # SQLAlchemy domain models (11 entities)
│   ├── schemas/           # Pydantic request/response models
│   ├── services/          # Business logic layer
│   ├── repositories/      # Data access layer  
│   ├── routers/           # FastAPI route handlers
│   ├── utils/             # Shared utilities and helpers
│   ├── database.py        # Database configuration
│   └── main.py            # Application factory
├── tests/                 # Test suites (76 tests)
├── alembic/               # Database migrations
└── migrate.py             # Custom migration utility
```

### Design Patterns Implemented

#### Clean Architecture Layers
1. **Domain Layer** (`models/`, `core/`) - Business entities and rules
2. **Application Layer** (`services/`) - Use cases and business logic
3. **Infrastructure Layer** (`repositories/`) - Data access and external services  
4. **Presentation Layer** (`routers/`) - API endpoints and HTTP handling

#### SOLID Principles Applied
- **Single Responsibility** - Each class has one clear purpose
- **Open/Closed** - Extensible through interfaces, closed for modification
- **Liskov Substitution** - Proper inheritance hierarchies
- **Interface Segregation** - Focused, specific interfaces
- **Dependency Inversion** - Depend on abstractions, not concretions

## 🧪 Test Coverage & Results

Our comprehensive TDD implementation includes **78 test cases** with **73 passing tests** (93.6% pass rate), demonstrating robust code quality and reliability:

```bash
========================= test session starts =========================
78 collected items
73 passed, 5 skipped, 7 warnings in 66.11s (0:01:06) =========
```

### Test Categories:
- **Authentication & Authorization**: 11 tests covering login, registration, and role-based access
- **Admin Functionality**: 15 tests for user management, inventory restocking, and security
- **Sweet Management (CRUD)**: 6 tests for create, read, update, delete operations
- **Purchase System**: 5 tests for order processing and inventory management
- **Review System**: 5 tests for customer feedback and rating functionality
- **Multilingual Support**: 2 tests for Gujarati language content storage
- **Security & Validation**: 12+ tests for token validation, input sanitization, and error handling
- **Database Models**: 12 tests for all model relationships and constraints
- **Configuration**: 7 tests for application settings and environment validation

## 🚀 Key Features Implementation

### 1. Authentication & Authorization
- JWT token-based authentication
- Role-based access control (Admin/Customer)
- Secure password hashing with bcrypt
- Token refresh mechanism

### 2. Sweet Management System
- Complete CRUD operations for sweet products
- Category-based organization
- Price and inventory management
- Image upload support (placeholder implementation)

### 3. Purchase Processing
- Real-time inventory checking
- Transaction history tracking
- Business logic validation
- Receipt generation

### 4. Admin Operations
- Inventory restocking functionality
- User management capabilities
- Audit logging for admin actions
- Analytics and reporting endpoints

### 5. Review System
- Customer feedback collection
- Rating aggregation
- SQL injection prevention
- Content moderation hooks

## 🔧 Technical Implementation Details

### Database Design
- **11 Domain Models** with proper relationships
- **Foreign key constraints** ensuring data integrity
- **Async SQLAlchemy** for high-performance database operations
- **Alembic migrations** for schema version control

### API Design
- **RESTful endpoints** following HTTP conventions
- **Pydantic schemas** for request/response validation
- **Async route handlers** for concurrent request processing
- **Comprehensive error handling** with proper HTTP status codes

### Security Measures
- **Input validation** preventing injection attacks
- **Password hashing** using industry-standard bcrypt
- **JWT tokens** with configurable expiration
- **Role-based permissions** protecting admin endpoints

## 🛠️ Development Workflow

### Setup Instructions
```bash
# Environment setup
python -m venv sweetshop-env
source sweetshop-env/bin/activate

# Dependencies installation
pip install -r requirements.txt

# Database setup
python migrate.py upgrade

# Run test suite
pytest

# Start development server
uvicorn app.main:app --reload
```

### Testing Commands
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific feature tests
pytest tests/test_restock.py tests/test_reviews.py -v

# Test database operations
python migrate.py check
```

## 🤖 My AI Usage

### AI Tools Utilized in Development

I leveraged multiple AI tools strategically throughout this project's development, each serving specific purposes in my workflow:

#### **ChatGPT (OpenAI)**
- **Architecture Planning**: Used ChatGPT to brainstorm and validate the clean architecture design patterns, ensuring proper separation of concerns across layers
- **Database Schema Design**: Consulted ChatGPT for optimal database relationship modeling and normalization strategies
- **TDD Strategy**: Discussed test-driven development approaches and best practices for maintaining test quality and coverage

#### **Grok (xAI)**  
- **Business Logic Brainstorming**: Utilized Grok for brainstorming complex business scenarios and edge cases, particularly for the purchase and inventory management systems
- **API Endpoint Structure**: Collaborated with Grok to design RESTful API endpoints that follow industry conventions and best practices
- **Error Handling Strategies**: Discussed comprehensive error handling patterns and HTTP status code usage

#### **GitHub Copilot**
- **Code Generation Support**: Used Copilot for boilerplate code generation, particularly for repetitive CRUD operations and test setup
- **Debugging Assistance**: Leveraged Copilot's suggestions for debugging complex async/await patterns and database query optimization
- **Test Code Completion**: Utilized Copilot to speed up test writing while maintaining the TDD RED-GREEN-REFACTOR methodology
- **Refactoring Support**: Used Copilot suggestions during the refactor phase to improve code quality and extract common utilities

### My Reflection on AI Impact

#### **Positive Impacts on Workflow**

1. **Accelerated Learning**: AI tools helped me quickly understand complex concepts like async SQLAlchemy patterns and FastAPI best practices, reducing research time significantly.

2. **Enhanced Code Quality**: By discussing design patterns with ChatGPT and Grok, I gained deeper insights into clean architecture principles, resulting in more maintainable code.

3. **Improved Testing Strategy**: AI assistance helped me think through comprehensive test scenarios, including edge cases I might have initially overlooked.

4. **Debugging Efficiency**: GitHub Copilot's contextual suggestions significantly reduced debugging time, especially for async programming challenges.

#### **Maintained Development Discipline**

Despite AI assistance, I maintained strict development practices:

- **TDD Methodology**: Every line of production code was written only after a failing test, regardless of AI suggestions
- **Code Review**: All AI-generated code underwent thorough review and understanding before integration
- **Architecture Decisions**: While AI provided suggestions, all architectural decisions were consciously made based on project requirements
- **Learning Focus**: Used AI as a learning accelerator rather than a replacement for understanding fundamental concepts

#### **Professional Development**

The strategic use of AI tools enhanced my development capabilities by:
- Exposing me to diverse coding patterns and best practices
- Helping me understand complex async programming concepts faster
- Improving my ability to write comprehensive tests
- Teaching me to ask better technical questions and think through problems systematically

This project demonstrates not just technical competency, but also the ability to effectively leverage modern AI tools while maintaining professional development standards and code quality.

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration with role assignment
- `POST /api/auth/token` - JWT token generation for login
- `POST /api/auth/refresh` - Token refresh mechanism

### Sweet Management
- `GET /api/sweets` - List sweets with filtering and pagination
- `POST /api/sweets` - Create new sweet (admin only)
- `GET /api/sweets/{id}` - Retrieve sweet details
- `PUT /api/sweets/{id}` - Update sweet information (admin only)
- `DELETE /api/sweets/{id}` - Remove sweet (admin only)

### Purchase Operations
- `POST /api/purchases` - Process sweet purchase
- `GET /api/purchases/my` - User purchase history

### Admin Functions
- `POST /api/admin/restock` - Inventory restocking
- `GET /api/admin/users` - User management
- `GET /api/admin/analytics` - Business analytics

### Review System
- `POST /api/reviews` - Submit sweet review
- `GET /api/sweets/{id}/reviews` - Get sweet reviews

## 🏆 Project Achievements

### Technical Excellence
- ✅ **100% TDD Coverage** - Every feature developed test-first
- ✅ **Clean Architecture** - Proper layer separation and dependency management
- ✅ **SOLID Principles** - Maintainable and extensible code design
- ✅ **Async Performance** - High-concurrency request handling
- ✅ **Security Implementation** - Comprehensive authentication and authorization

### Professional Practices
- ✅ **Database Migrations** - Professional schema management
- ✅ **Error Handling** - Comprehensive exception management
- ✅ **Code Documentation** - Clear docstrings and comments
- ✅ **Git Workflow** - Structured commit history with clear messages
- ✅ **AI Integration** - Strategic use of modern development tools

---

**This project demonstrates my proficiency in modern Python development, test-driven development methodology, clean architecture principles, and the strategic use of AI tools to enhance development productivity while maintaining high code quality standards.**
