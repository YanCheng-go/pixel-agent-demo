# Product Requirements Document: URL Shortener Microservice

**Version:** 1.0
**Date:** 2026-03-04
**Status:** Approved

---

## Project Overview

A lightweight URL shortener microservice. Users submit a long URL via a REST API and receive a short alphanumeric code. Visiting the short URL via a browser or HTTP client results in a redirect to the original URL. Basic analytics track how many times each short link has been accessed.

The service is stateless except for a persistent store (database or in-memory map with file persistence). It exposes three HTTP endpoints and requires no authentication in v1.

---

## User Stories

### US-1: Shorten a URL
> As a user, I want to submit a long URL and receive a short code so I can share it easily.

### US-2: Redirect via Short Code
> As a user, I want to visit a short link and be automatically redirected to the original URL.

### US-3: View Click Statistics
> As a user, I want to query how many times a short link has been clicked so I can track its reach.

---

## API Endpoints

### POST /shorten
- **Request body:** `{ "url": "https://example.com/some/long/path" }`
- **Response (201):** `{ "code": "aB3xY7", "short_url": "http://localhost:8000/aB3xY7" }`
- **Response (400):** Invalid or missing URL
- **Behavior:** Generates a unique short code (6 alphanumeric characters), stores the mapping, returns the short URL.

### GET /:code
- **Response (307):** Temporary redirect to the original URL (`Location` header set)
- **Response (404):** Code not found
- **Behavior:** Looks up the code, increments the click counter, issues an HTTP 307 redirect.

### GET /:code/stats
- **Response (200):** `{ "code": "aB3xY7", "original_url": "https://...", "clicks": 42, "created_at": "2026-03-04T10:00:00Z" }`
- **Response (404):** Code not found
- **Behavior:** Returns metadata and the current click count without incrementing it.

---

## Acceptance Criteria

### AC-1 (US-1: Shorten a URL)
- `POST /shorten` with a valid URL returns HTTP 201 and a JSON body containing `code` and `short_url`.
- `short_url` is a fully-qualified URL using the server's base URL and the generated `code`.
- The `code` is 6 alphanumeric characters (a–z, A–Z, 0–9).
- `POST /shorten` with a missing or malformed URL returns HTTP 400 with an error message.
- Shortening the same URL twice produces two separate codes (no deduplication in v1).

### AC-2 (US-2: Redirect)
- `GET /:code` for a valid code returns HTTP 307 with a `Location` header pointing to the original URL.
- `GET /:code` for an unknown code returns HTTP 404.
- Each successful redirect increments the click counter by 1.

### AC-3 (US-3: Click Statistics)
- `GET /:code/stats` returns HTTP 200 with `code`, `original_url`, `clicks`, and `created_at` fields.
- `clicks` reflects the exact number of times `GET /:code` has been called successfully.
- `GET /:code/stats` does not increment `clicks`.
- `GET /:code/stats` for an unknown code returns HTTP 404.

---

## MVP Scope

### In Scope (v1)
- `POST /shorten` — create a short URL mapping
- `GET /:code` — redirect to original URL with click tracking
- `GET /:code/stats` — retrieve click count and metadata
- In-memory or file-backed persistence (no external database required)
- JSON request/response bodies
- Basic input validation (URL format check)

### Out of Scope (v1)
- Authentication or API keys
- Custom aliases (user-specified short codes)
- Rate limiting
- Link expiration / TTL
- Bulk shortening
- Dashboard or UI
- Persistent database (PostgreSQL, Redis, etc.) — optional stretch goal only
- HTTPS termination (assumed to be handled by a reverse proxy)
- Analytics beyond click count (e.g., referrer, geo, device)
