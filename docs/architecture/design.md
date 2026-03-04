# Architecture Design Document: URL Shortener Microservice

## 1. Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Modern async support, wide ecosystem |
| Framework | FastAPI | Async-native, automatic OpenAPI docs, Pydantic validation |
| Database | SQLite via `aiosqlite` | Zero-config, in-process — no external dependencies (per PRD MVP scope) |
| Server | Uvicorn | ASGI server, production-quality, works seamlessly with FastAPI |

## 2. Component Overview

The service is a **single FastAPI application** backed by **one SQLite database file** (`urls.db`). There are no external service dependencies — the entire microservice runs in a single process.

```
┌─────────────────────────────────────────┐
│              FastAPI App                │
│                                         │
│  POST /shorten ──► create_short_url()   │
│  GET /{code}   ──► redirect_to_url()    │
│  GET /{code}/stats ──► get_stats()      │
│                                         │
│         ┌──────────────┐                │
│         │  SQLite DB   │                │
│         │  (urls.db)   │                │
│         └──────────────┘                │
└─────────────────────────────────────────┘
```

## 3. Data Model

### `urls` Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal row ID |
| `short_code` | TEXT | UNIQUE NOT NULL | The 6-character base62 code |
| `original_url` | TEXT | NOT NULL | The long URL submitted by the user |
| `created_at` | TIMESTAMP | NOT NULL DEFAULT CURRENT_TIMESTAMP | When the link was created |
| `click_count` | INTEGER | NOT NULL DEFAULT 0 | Number of redirects served |

```sql
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    click_count INTEGER NOT NULL DEFAULT 0
);
```

Per PRD US-1, submitting the same URL multiple times may produce different codes — there is no unique constraint on `original_url`.

## 4. Short Code Generation

- **Alphabet**: `0-9`, `a-z`, `A-Z` (62 characters — base62).
- **Length**: 6 characters, yielding 62^6 ≈ 56.8 billion possible codes.
- **Method**: Generate 6 random characters from the base62 alphabet using `secrets.choice()`.
- **Collision handling**: On `UNIQUE` constraint violation, regenerate and retry (up to 5 attempts). At low volumes this is effectively instant.

Per PRD AC-1, codes must be alphanumeric and 6–8 characters. We use a fixed length of 6.

## 5. Project Structure

```
src/
├── main.py        # FastAPI app, endpoint definitions, startup/shutdown hooks
├── models.py      # Pydantic request/response schemas
├── database.py    # SQLite connection management, CRUD functions
```

### `database.py`
- `init_db()` — creates the `urls` table if it doesn't exist (called on app startup).
- `insert_url(short_code, original_url)` — inserts a new row.
- `get_url_by_code(code)` — retrieves a row by `short_code`.
- `increment_click_count(code)` — atomically increments `click_count` by 1.

### `models.py`
- `ShortenRequest` — Pydantic model validating the incoming `url` field (must be a valid HTTP/HTTPS URL, per PRD AC-1).
- `ShortenResponse` — fields: `short_code`, `short_url`, `url`, `created_at`.
- `StatsResponse` — fields: `short_code`, `url`, `clicks`, `created_at`.
- `ErrorResponse` — field: `error`.

### `main.py`
- Mounts the three endpoints per the API spec.
- On startup, calls `init_db()`.
- Generates short codes using the base62 strategy described above.
- Returns 307 redirects using FastAPI's `RedirectResponse` (per PRD US-2).

## 6. Key Design Decisions

### Why SQLite?
Per PRD MVP scope, the service uses "in-process data storage (SQLite or in-memory dictionary)." SQLite gives us real SQL, persistence across restarts, and zero configuration — ideal for a demo. Using `aiosqlite` keeps it async-compatible with FastAPI.

### Why FastAPI?
FastAPI provides automatic OpenAPI/Swagger UI documentation out of the box, which makes the demo visually impressive. Its Pydantic integration handles input validation (PRD AC-1: invalid URL → 400) with minimal code.

### Redirect Status Code: 307
Per PRD US-2, the service uses HTTP 307 (Temporary Redirect). This preserves the request method and signals that the short link mapping is not permanent (important since link expiration may be added later, per PRD out-of-scope notes).

### No Deduplication
Per PRD US-1, "submitting the same long URL multiple times may produce different codes." Each `POST /shorten` creates a new row regardless of whether the URL has been shortened before. This keeps the logic simple.

### URL Validation
Per PRD AC-1, the `POST /shorten` endpoint validates that the input is a well-formed HTTP or HTTPS URL. This is handled via Pydantic's `AnyHttpUrl` type in the request model. Invalid or missing URLs return HTTP 400 with `{"error": "Invalid URL"}`.
