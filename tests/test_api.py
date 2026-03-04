"""
test_api.py — Comprehensive tests for the URL shortener REST API.

Tests are organized by endpoint and cover success paths, error paths,
and edge cases as defined in docs/architecture/api-spec.yaml.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# POST /shorten
# ---------------------------------------------------------------------------


class TestShortenEndpoint:
    """Tests for POST /shorten."""

    @pytest.mark.asyncio
    async def test_shorten_valid_url_returns_201(self, client: AsyncClient):
        """Successfully shorten a valid HTTPS URL — expect 201 Created."""
        response = await client.post(
            "/shorten",
            json={"url": "https://www.example.com/some/long/path?foo=bar"},
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_shorten_valid_url_response_contains_short_code(self, client: AsyncClient):
        """Response body must include a non-empty short_code field."""
        response = await client.post(
            "/shorten",
            json={"url": "https://www.example.com/path-for-code-check"},
        )
        assert response.status_code == 201
        body = response.json()
        assert "short_code" in body
        assert len(body["short_code"]) == 6

    @pytest.mark.asyncio
    async def test_shorten_valid_url_response_contains_short_url(self, client: AsyncClient):
        """Response body must include a non-empty short_url field."""
        response = await client.post(
            "/shorten",
            json={"url": "https://www.example.com/path-for-short-url-check"},
        )
        assert response.status_code == 201
        body = response.json()
        assert "short_url" in body
        assert body["short_code"] in body["short_url"]

    @pytest.mark.asyncio
    async def test_shorten_valid_url_response_contains_original_url(self, client: AsyncClient):
        """Response body must echo back the original_url."""
        original = "https://www.example.com/original-url-echo"
        response = await client.post("/shorten", json={"url": original})
        assert response.status_code == 201
        body = response.json()
        assert "original_url" in body
        # Pydantic may normalise trailing slashes; the domain must be present.
        assert "example.com" in body["original_url"]

    @pytest.mark.asyncio
    async def test_shorten_http_url_is_accepted(self, client: AsyncClient):
        """HTTP (non-HTTPS) URLs must also be accepted."""
        response = await client.post(
            "/shorten",
            json={"url": "http://www.example.com/plain-http"},
        )
        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_shorten_same_url_twice_generates_distinct_codes(self, client: AsyncClient):
        """Each call to POST /shorten must return a NEW short code."""
        url = "https://www.example.com/repeated-url"
        r1 = await client.post("/shorten", json={"url": url})
        r2 = await client.post("/shorten", json={"url": url})
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["short_code"] != r2.json()["short_code"]

    @pytest.mark.asyncio
    async def test_shorten_invalid_url_returns_422(self, client: AsyncClient):
        """A plain string that is not a URL must be rejected with 422."""
        response = await client.post(
            "/shorten",
            json={"url": "not-a-valid-url"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_shorten_missing_url_field_returns_422(self, client: AsyncClient):
        """A request body that omits the required 'url' field must be rejected with 422."""
        response = await client.post("/shorten", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_shorten_non_http_scheme_returns_422(self, client: AsyncClient):
        """A URL with a non-HTTP/HTTPS scheme (e.g. ftp://) must be rejected."""
        response = await client.post(
            "/shorten",
            json={"url": "ftp://files.example.com/resource"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /{code} — redirect
# ---------------------------------------------------------------------------


class TestRedirectEndpoint:
    """Tests for GET /{code}."""

    @pytest.mark.asyncio
    async def test_redirect_valid_code_returns_307(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """A valid short code must produce a 307 Temporary Redirect."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}")
        assert response.status_code == 307

    @pytest.mark.asyncio
    async def test_redirect_location_header_matches_original_url(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """The Location header must point to the original URL."""
        code = existing_short_code["short_code"]
        original_url = existing_short_code["original_url"]
        response = await client.get(f"/{code}")
        assert response.status_code == 307
        location = response.headers.get("location", "")
        # The Location header should contain the original host/path.
        assert "example.com" in location
        # Verify location matches what was stored (Pydantic may normalise trailing slash).
        assert location.rstrip("/") == original_url.rstrip("/")

    @pytest.mark.asyncio
    async def test_redirect_nonexistent_code_returns_404(self, client: AsyncClient):
        """A short code that was never created must return 404."""
        response = await client.get("/zzz999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_redirect_404_response_has_detail_field(self, client: AsyncClient):
        """The 404 error response must include a 'detail' field."""
        response = await client.get("/zzz000")
        assert response.status_code == 404
        body = response.json()
        assert "detail" in body


# ---------------------------------------------------------------------------
# GET /{code}/stats
# ---------------------------------------------------------------------------


class TestStatsEndpoint:
    """Tests for GET /{code}/stats."""

    @pytest.mark.asyncio
    async def test_stats_valid_code_returns_200(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """A valid short code must return 200 OK from the stats endpoint."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}/stats")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_stats_response_contains_click_count(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """Stats response must include a non-negative integer click_count."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}/stats")
        assert response.status_code == 200
        body = response.json()
        assert "click_count" in body
        assert isinstance(body["click_count"], int)
        assert body["click_count"] >= 0

    @pytest.mark.asyncio
    async def test_stats_response_contains_original_url(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """Stats response must echo the original_url."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}/stats")
        assert response.status_code == 200
        body = response.json()
        assert "original_url" in body
        assert "example.com" in body["original_url"]

    @pytest.mark.asyncio
    async def test_stats_response_contains_created_at(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """Stats response must include a created_at ISO-8601 timestamp."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}/stats")
        assert response.status_code == 200
        body = response.json()
        assert "created_at" in body
        assert body["created_at"]  # non-empty

    @pytest.mark.asyncio
    async def test_stats_response_contains_short_code(
        self, client: AsyncClient, existing_short_code: dict
    ):
        """Stats response must include the short_code itself."""
        code = existing_short_code["short_code"]
        response = await client.get(f"/{code}/stats")
        assert response.status_code == 200
        body = response.json()
        assert "short_code" in body
        assert body["short_code"] == code

    @pytest.mark.asyncio
    async def test_stats_click_count_increments_after_redirect(self, client: AsyncClient):
        """
        Click count in stats must increase by exactly 1 after one redirect.

        Creates a fresh URL to avoid interference from other test fixtures.
        """
        # Create a fresh short URL.
        create_resp = await client.post(
            "/shorten",
            json={"url": "https://www.example.com/click-count-test"},
        )
        assert create_resp.status_code == 201
        code = create_resp.json()["short_code"]

        # Capture baseline click count.
        stats_before = await client.get(f"/{code}/stats")
        count_before = stats_before.json()["click_count"]

        # Trigger one redirect.
        await client.get(f"/{code}")

        # Verify click count increased by 1.
        stats_after = await client.get(f"/{code}/stats")
        count_after = stats_after.json()["click_count"]
        assert count_after == count_before + 1

    @pytest.mark.asyncio
    async def test_stats_nonexistent_code_returns_404(self, client: AsyncClient):
        """A short code that was never created must return 404 from the stats endpoint."""
        response = await client.get("/zzz111/stats")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_stats_404_response_has_detail_field(self, client: AsyncClient):
        """The 404 stats error response must include a 'detail' field."""
        response = await client.get("/zzz222/stats")
        assert response.status_code == 404
        body = response.json()
        assert "detail" in body


# ---------------------------------------------------------------------------
# Edge cases / miscellaneous
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Miscellaneous edge-case and operational tests."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self, client: AsyncClient):
        """GET /health must return 200 OK."""
        response = await client.get("/health")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_health_response_body(self, client: AsyncClient):
        """GET /health must return a body confirming the service is up."""
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body.get("status") == "ok"

    @pytest.mark.asyncio
    async def test_multiple_redirects_increment_count_correctly(self, client: AsyncClient):
        """
        Firing N redirects must raise click_count by exactly N.
        """
        create_resp = await client.post(
            "/shorten",
            json={"url": "https://www.example.com/multi-click-test"},
        )
        assert create_resp.status_code == 201
        code = create_resp.json()["short_code"]

        n_clicks = 3
        for _ in range(n_clicks):
            await client.get(f"/{code}")

        stats = await client.get(f"/{code}/stats")
        assert stats.json()["click_count"] == n_clicks
