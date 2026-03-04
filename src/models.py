from datetime import datetime

from pydantic import BaseModel, AnyHttpUrl


class ShortenRequest(BaseModel):
    url: AnyHttpUrl


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    url: str
    created_at: datetime


class StatsResponse(BaseModel):
    short_code: str
    url: str
    clicks: int
    created_at: datetime


class ErrorResponse(BaseModel):
    error: str
