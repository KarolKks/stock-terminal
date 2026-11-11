import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.main import app
from app.db.database import get_db
from app.core.config import settings

# Construct DB URL from application settings
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)


@pytest_asyncio.fixture
async def db_session():
    """
    Creates a dedicated async engine and isolated transaction session for a single test.
    Executed entirely within the test's own asyncio event loop to avoid loop mismatch errors.
    """
    engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
    connection = await engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )

    yield session

    # Teardown: Roll back all SQL operations and dispose of the engine
    await session.close()
    await transaction.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def ac(db_session: AsyncSession):
    """
    Provides an AsyncClient bound to FastAPI with overriden get_db dependency.
    """
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()