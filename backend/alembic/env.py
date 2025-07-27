"""
Alembic environment configuration for SweetShop TDD project.

This file configures the Alembic migration environment with proper
database connection handling and model metadata registration.
"""
from logging.config import fileConfig
import sys
import os
from typing import Optional

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import database configuration and models
from app.database import Base
from app.config import settings

# Import all models to ensure they're registered with Base.metadata
# This is crucial for autogenerate to detect model changes
from app.models.user import User
from app.models.role import Role  
from app.models.category import Category
from app.models.sweet import Sweet
from app.models.sweet_inventory import SweetInventory
from app.models.purchase import Purchase
from app.models.restock import Restock
from app.models.review import Review
from app.models.revoked_token import RevokedToken
from app.models.audit_log import AuditLog

# Alembic Config object - provides access to .ini file values
config = context.config

# Set database URL from application configuration
# This ensures consistency between app and migration database connections
database_url = settings.DATABASE_URL
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

# Configure Python logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata from models for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the 
    Engine creation we don't even need a DBAPI to be available.
    
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine and associate 
    a connection with the context. This is the typical mode
    used when running migrations against a live database.
    """
    # Create engine with connection pooling disabled for migrations
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Enable transaction per migration for safety
            transaction_per_migration=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Determine migration mode and execute
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
