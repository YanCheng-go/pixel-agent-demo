import os
import pytest
from httpx import ASGITransport, AsyncClient

# Point the database to a test file before importing the app
os.environ.setdefault("DATABASE_URL", "test.db")

import src.database as database

# Override DB_PATH so all tests use the test database
database.DB_PATH = "test.db"

from src.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture()
async def short_code(client: AsyncClient) -> str:
    """Create a shortened URL and return its short code."""
    resp = await client.post("/shorten", json={"url": "https://example.com/test-fixture"})
    assert resp.status_code == 201
    return resp.json()["short_code"]


@pytest.fixture(scope="session", autouse=True)
async def cleanup():
    """Remove test database after the test session."""
    yield
    if os.path.exists("test.db"):
        os.remove("test.db")
