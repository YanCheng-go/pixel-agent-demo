# Product Requirements Document: URL Shortener Microservice

## Project Overview

A lightweight URL shortener microservice that provides three core capabilities:

1. **Shorten** — Accept a long URL and return a unique short code.
2. **Redirect** — Resolve a short code back to the original URL and redirect the caller.
3. **Analytics** — Track and expose per-link click counts.

The service exposes a simple REST API. Data is stored in-process (SQLite or in-memory) for the MVP — no external database dependency. The target audience is developers integrating via HTTP calls or curl.

---

## User Stories

### US-1: Shorten a URL

**As a** user, **I want to** submit a long URL **so that** I receive a short, shareable code.

**Details:**
- The service generates a unique alphanumeric code (6–8 characters).
- The response includes the short code and the fully-qualified short URL.
- Submitting the same long URL multiple times may produce different codes (no deduplication required in MVP).

### US-2: Redirect via Short Link

**As a** user, **I want to** visit a short link **so that** I am redirected to the original URL.

**Details:**
- The service responds with HTTP 307 (Temporary Redirect) and a `Location` header pointing to the original URL.
- Each successful redirect increments the link's click counter.
- If the code does not exist, the service returns HTTP 404 with a JSON error body.

### US-3: View Link Statistics

**As a** user, **I want to** view click statistics for a short link **so that** I know how often it has been used.

**Details:**
- The response includes: original URL, short code, click count, and creation timestamp.
- Click count reflects all redirects processed up to the time of the request.

---

## API Endpoints

### `POST /shorten`

| Field        | Value                              |
|--------------|------------------------------------|
| Request body | `{ "url": "https://example.com" }` |
| Response 201 | `{ "short_code": "abc123", "short_url": "http://host/abc123", "url": "https://example.com", "created_at": "..." }` |
| Response 400 | `{ "error": "Invalid URL" }`       |

- Validates that the input is a well-formed HTTP/HTTPS URL.

### `GET /:code`

| Field        | Value                                   |
|--------------|-----------------------------------------|
| Response 307 | Redirects via `Location` header         |
| Response 404 | `{ "error": "Short link not found" }`   |

### `GET /:code/stats`

| Field        | Value                                   |
|--------------|-----------------------------------------|
| Response 200 | `{ "short_code": "abc123", "url": "https://example.com", "clicks": 42, "created_at": "..." }` |
| Response 404 | `{ "error": "Short link not found" }`   |

---

## Acceptance Criteria

### AC-1 (US-1: Shorten)

- [ ] `POST /shorten` with a valid URL returns HTTP 201 and a JSON body containing `short_code`, `short_url`, and `url`.
- [ ] `POST /shorten` with an invalid or missing URL returns HTTP 400 with an error message.
- [ ] Generated short codes are alphanumeric and 6–8 characters long.

### AC-2 (US-2: Redirect)

- [ ] `GET /:code` with a valid code returns HTTP 307 with the correct `Location` header.
- [ ] `GET /:code` with a nonexistent code returns HTTP 404 with a JSON error body.
- [ ] Each redirect increments the click counter by exactly 1.

### AC-3 (US-3: Stats)

- [ ] `GET /:code/stats` returns HTTP 200 with `short_code`, `url`, `clicks`, and `created_at`.
- [ ] Click count accurately reflects the number of redirects served.
- [ ] Requesting stats for a nonexistent code returns HTTP 404.

---

## MVP Scope

### In Scope (v1)

- Three endpoints: `/shorten`, `/:code`, `/:code/stats`.
- In-process data storage (SQLite or in-memory dictionary).
- Input validation for URLs.
- JSON request/response format.
- Basic error handling with appropriate HTTP status codes.

### Out of Scope (v1)

- **Authentication / authorization** — no API keys or user accounts.
- **Custom aliases** — users cannot choose their own short codes.
- **Rate limiting** — no request throttling.
- **Link expiration** — short links live forever.
- **Bulk operations** — one URL per request.
- **Persistent storage migration** — no external DB setup.

---

## Technical Notes for Downstream Agents

- **Architect**: Use this PRD to produce an OpenAPI spec and data model. The three endpoints and their request/response shapes are defined above.
- **Developer**: Implement against the Architect's spec. Python/FastAPI or Node/Express are both acceptable.
- **QA**: Write tests that verify every acceptance criterion listed above. Test both happy paths and error cases.
- **DevOps**: The service should run as a single container with no external dependencies.
