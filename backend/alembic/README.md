# Alembic Database Migrations - SweetShop TDD

This directory contains database migration scripts for the SweetShop TDD project using Alembic, SQLAlchemy's lightweight database migration tool.

## Overview

Alembic provides version control for your database schema, allowing you to:
- Track database schema changes over time
- Apply incremental updates to database structure
- Rollback problematic migrations
- Maintain consistency across development, staging, and production environments

## Directory Structure

```
alembic/
├── README.md           # This file
├── env.py             # Migration environment configuration
├── script.py.mako     # Template for generating migration scripts
└── versions/          # Directory containing migration scripts
    └── *.py          # Individual migration files
```

## Common Commands

### Check Current Migration Status
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

### Generate New Migration (Auto-detect Changes)
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Create Empty Migration
```bash
alembic revision -m "Description of changes"
```

### Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Apply next migration only
alembic upgrade +1
```

### Rollback Migrations
```bash
# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base
```

### Verify Schema Consistency
```bash
alembic check
```

## Migration Workflow

1. **Make Model Changes**: Modify your SQLAlchemy models in `app/models/`
2. **Generate Migration**: Run `alembic revision --autogenerate -m "description"`
3. **Review Migration**: Check the generated migration file for accuracy
4. **Test Migration**: Apply migration to development database
5. **Apply to Production**: Run migration in production environment

## Important Notes

- **Always review auto-generated migrations** before applying them
- **Test migrations** on a copy of production data when possible
- **Backup database** before applying migrations in production
- **Never edit applied migrations** - create new ones instead
- **Use descriptive messages** for migration descriptions

## Current Models

The following models are tracked by migrations:
- User (authentication and user management)
- Role (user roles: admin, customer)
- Category (sweet categories)
- Sweet (sweet products)
- SweetInventory (stock management)
- Purchase (purchase transactions)
- Restock (admin restocking operations)
- Review (customer reviews)
- RevokedToken (JWT token management)
- AuditLog (system audit trail)

## Configuration

- Database URL is automatically configured from `app/config.py`
- Migration files include timestamps for better organization
- Logging is configured for development and production use
- Type comparison and server default comparison are enabled for accurate change detection
