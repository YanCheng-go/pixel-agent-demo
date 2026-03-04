import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


# ── POST /shorten ──────────────────────────────────────────────


class TestPostShorten:
    async def test_shorten_valid_url(self, client: AsyncClient):
        resp = await client.post("/shorten", json={"url": "https://example.com/hello"})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_code" in data
        assert "short_url" in data
        assert data["short_url"].endswith(data["short_code"])
        assert "created_at" in data

    async def test_shorten_invalid_url(self, client: AsyncClient):
        resp = await client.post("/shorten", json={"url": "not-a-url"})
        assert resp.status_code == 422


# ── GET /{code} (redirect) ─────────────────────────────────────


class TestGetRedirect:
    async def test_redirect_valid_code(self, client: AsyncClient, short_code: str):
        resp = await client.get(f"/{short_code}", follow_redirects=False)
        assert resp.status_code == 307
        assert "location" in resp.headers
        assert resp.headers["location"] == "https://example.com/test-fixture"

    async def test_redirect_nonexistent_code(self, client: AsyncClient):
        resp = await client.get("/zzzzzz", follow_redirects=False)
        assert resp.status_code == 404
        assert resp.json()["error"] == "Short link not found"


# ── GET /{code}/stats ──────────────────────────────────────────


class TestGetStats:
    async def test_stats_valid_code(self, client: AsyncClient, short_code: str):
        resp = await client.get(f"/{short_code}/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["short_code"] == short_code
        assert "clicks" in data
        assert "url" in data
        assert "created_at" in data

    async def test_click_count_increments(self, client: AsyncClient):
        # Create a fresh short URL
        create_resp = await client.post("/shorten", json={"url": "https://example.com/counter"})
        code = create_resp.json()["short_code"]

        # Check initial click count
        stats_resp = await client.get(f"/{code}/stats")
        assert stats_resp.json()["clicks"] == 0

        # Perform a redirect
        await client.get(f"/{code}", follow_redirects=False)

        # Click count should be 1
        stats_resp = await client.get(f"/{code}/stats")
        assert stats_resp.json()["clicks"] == 1

    async def test_stats_nonexistent_code(self, client: AsyncClient):
        resp = await client.get("/zzzzzz/stats")
        assert resp.status_code == 404
        assert resp.json()["error"] == "Short link not found"


# ── Edge cases ─────────────────────────────────────────────────


class TestEdgeCases:
    async def test_health_endpoint(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
