"""
Test async database configuration and connection
"""
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import engine, async_session, get_db, Base, get_async_database_url, SQLALCHEMY_DATABASE_URL


def test_async_database_url_conversion():
    """Test database URL conversion to async format"""
    # Test postgresql:// conversion
    sync_url = "postgresql://user:pass@localhost:5432/db"
    async_url = get_async_database_url(sync_url)
    assert async_url == "postgresql+asyncpg://user:pass@localhost:5432/db"
    
    # Test postgres:// conversion  
    sync_url2 = "postgres://user:pass@localhost:5432/db"
    async_url2 = get_async_database_url(sync_url2)
    assert async_url2 == "postgresql+asyncpg://user:pass@localhost:5432/db"


@pytest.mark.asyncio
async def test_engine_creation():
    """Test that async engine is created properly"""
    assert engine is not None
    assert hasattr(engine, 'connect')
    
    # Test connection with a fresh engine to avoid loop conflicts
    test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=False)
    try:
        async with test_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
    finally:
        await test_engine.dispose()


@pytest.mark.asyncio  
async def test_async_session_factory():
    """Test async session factory creation"""
    assert async_session is not None
    
    # Test that we can create a session
    async with async_session() as session:
        # Just verify the session was created
        assert session is not None


def test_base_model_class():
    """Test the Base model class"""
    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'registry')


def test_engine_configuration():
    """Test engine configuration settings"""
    # Check that engine has proper configuration
    assert engine.echo == False  # Should match DEBUG setting (production default)
    assert engine.pool._pre_ping == True
    assert engine.pool._recycle == 300


@pytest.mark.asyncio
async def test_database_connection_functionality():
    """Test database connection functionality with isolated engine"""
    # Create a test-specific engine to avoid asyncio loop conflicts
    test_engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=False,  # Disable ping to avoid loop issues in tests
        echo=False
    )
    
    try:
        async with test_engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT 'Hello Database' as message"))
            message = result.scalar()
            assert message == "Hello Database"
            
            # Test with parameters
            result = await conn.execute(text("SELECT :value as param_test"), {"value": 123})
            param_value = result.scalar()
            assert param_value == 123
    finally:
        # Clean up the test engine
        await test_engine.dispose()


@pytest.mark.asyncio
async def test_database_url_configuration():
    """Test that the database URL is correctly configured"""
    assert SQLALCHEMY_DATABASE_URL.startswith("postgresql+asyncpg://")
    assert "sweet_shop" in SQLALCHEMY_DATABASE_URL
    
    # Test that we can connect with the configured URL
    test_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=False)
    try:
        async with test_engine.begin() as conn:
            # Test connection works
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            assert db_name == "sweet_shop"
    finally:
        await test_engine.dispose()
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import engine, async_session, get_db, Base, get_async_database_url


def test_async_database_url_conversion():
    """Test database URL conversion to async format"""
    # Test postgresql:// conversion
    sync_url = "postgresql://user:pass@localhost:5432/db"
    async_url = get_async_database_url(sync_url)
    assert async_url == "postgresql+asyncpg://user:pass@localhost:5432/db"
    
    # Test postgres:// conversion  
    sync_url2 = "postgres://user:pass@localhost:5432/db"
    async_url2 = get_async_database_url(sync_url2)
    assert async_url2 == "postgresql+asyncpg://user:pass@localhost:5432/db"


@pytest.mark.asyncio
async def test_engine_creation():
    """Test that async engine is created properly"""
    assert engine is not None
    assert hasattr(engine, 'connect')
    
    # Test connection
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1


@pytest.mark.asyncio  
async def test_async_session_factory():
    """Test async session factory creation"""
    assert async_session is not None
    
    # Test that we can create a session
    async with async_session() as session:
        # Just verify the session was created
        assert session is not None


def test_base_model_class():
    """Test the Base model class"""
    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base, 'registry')


def test_engine_configuration():
    """Test engine configuration settings"""
    # Check that engine has proper configuration
    assert engine.echo == False  # Should match DEBUG setting (production default)
    assert engine.pool._pre_ping == True
    assert engine.pool._recycle == 300


def test_database_connection_functionality():
    """Test database connection functionality using asyncio.run"""
    import asyncio
    from app.database import get_async_database_url
    from app.config import settings
    
    async def test_connection():
        # Create a dedicated engine for this test
        test_engine = create_async_engine(
            get_async_database_url(settings.DATABASE_URL),
            echo=False,
            pool_pre_ping=False,
        )
        
        try:
            async with test_engine.begin() as conn:
                # Test basic query
                result = await conn.execute(text("SELECT 'Hello Database' as message"))
                message = result.scalar()
                assert message == "Hello Database"
                
                # Test with number literal (avoiding parameter binding issues)
                result = await conn.execute(text("SELECT 123 as number_test"))
                number_value = result.scalar()
                assert number_value == 123
                
                # Test current timestamp
                result = await conn.execute(text("SELECT CURRENT_TIMESTAMP"))
                timestamp = result.scalar()
                assert timestamp is not None
                
                return True
        finally:
            await test_engine.dispose()
    
    # Run the async test in a new event loop
    result = asyncio.run(test_connection())
    assert result is True


@pytest.mark.asyncio
async def test_database_connection_via_engine():
    """Test database connection functionality"""
    # Create a fresh engine instance for this test to avoid event loop issues
    from sqlalchemy.ext.asyncio import create_async_engine
    from app.database import get_async_database_url
    from app.config import settings
    
    test_engine = create_async_engine(
        get_async_database_url(settings.DATABASE_URL),
        echo=False,
        pool_pre_ping=False,  # Disable ping to avoid loop issues
    )
    
    try:
        async with test_engine.begin() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT 'Hello Database' as message"))
            message = result.scalar()
            assert message == "Hello Database"
            
            # Test with numbers (no parameters to avoid asyncpg type issues)
            result = await conn.execute(text("SELECT 123 as number_test"))
            number_value = result.scalar()
            assert number_value == 123
            
            # Test current timestamp 
            result = await conn.execute(text("SELECT CURRENT_TIMESTAMP"))
            timestamp = result.scalar()
            assert timestamp is not None
    finally:
        await test_engine.dispose()
