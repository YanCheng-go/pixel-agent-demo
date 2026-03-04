import secrets
import string
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from src.database import init_db, close_db, insert_url, get_url_by_code, increment_click_count
from src.models import ShortenRequest, ShortenResponse, StatsResponse, ErrorResponse

BASE62 = string.digits + string.ascii_lowercase + string.ascii_uppercase
CODE_LENGTH = 6
MAX_RETRIES = 5


def generate_short_code() -> str:
    return "".join(secrets.choice(BASE62) for _ in range(CODE_LENGTH))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="URL Shortener API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/shorten", response_model=ShortenResponse, status_code=201)
async def create_short_url(body: ShortenRequest, request: Request):
    original_url = str(body.url)

    for _ in range(MAX_RETRIES):
        short_code = generate_short_code()
        try:
            row = await insert_url(short_code, original_url)
            base_url = str(request.base_url).rstrip("/")
            return ShortenResponse(
                short_code=row["short_code"],
                short_url=f"{base_url}/{row['short_code']}",
                url=row["original_url"],
                created_at=row["created_at"],
            )
        except Exception:
            continue

    return JSONResponse(status_code=500, content={"error": "Failed to generate unique short code"})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/{code}/stats", response_model=StatsResponse, responses={404: {"model": ErrorResponse}})
async def get_stats(code: str):
    row = await get_url_by_code(code)
    if not row:
        return JSONResponse(status_code=404, content={"error": "Short link not found"})
    return StatsResponse(
        short_code=row["short_code"],
        url=row["original_url"],
        clicks=row["click_count"],
        created_at=row["created_at"],
    )


@app.get("/{code}", responses={404: {"model": ErrorResponse}})
async def redirect_to_url(code: str):
    row = await get_url_by_code(code)
    if not row:
        return JSONResponse(status_code=404, content={"error": "Short link not found"})
    await increment_click_count(code)
    return RedirectResponse(url=row["original_url"], status_code=307)
