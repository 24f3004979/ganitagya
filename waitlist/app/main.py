import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config import settings
from .storage import build_storage


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.storage = build_storage(settings)
    yield


app = FastAPI(
    title="Ganitagya Waitlist",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url=None,
    openapi_url="/openapi.json" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


# --- Errors use {"error": "..."} so the Vue form can show them directly ---
@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, __: RequestValidationError):
    return JSONResponse({"error": "Enter a valid email address."}, status_code=400)


@app.exception_handler(StarletteHTTPException)
async def http_error(_: Request, exc: StarletteHTTPException):
    return JSONResponse({"error": exc.detail}, status_code=exc.status_code)


# --- Tiny per-IP rate limit (in memory, per instance) ---
_hits: dict[str, list[float]] = {}


def rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window = settings.rate_limit_window_seconds
    recent = [t for t in _hits.get(ip, []) if now - t < window]
    if len(recent) >= settings.rate_limit_max:
        raise HTTPException(429, "Too many attempts. Try again later.")
    recent.append(now)
    _hits[ip] = recent
    if len(_hits) > 10_000:  # keep memory bounded
        _hits.clear()


class JoinRequest(BaseModel):
    email: EmailStr = Field(max_length=254)
    website: str = ""  # honeypot: real users never fill this


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/waitlist", dependencies=[Depends(rate_limit)])
def join_waitlist(body: JoinRequest, request: Request):
    if body.website:  # bot filled the hidden field; pretend it worked
        return {"ok": True}

    email = str(body.email).strip().lower()
    try:
        request.app.state.storage.add(email)
    except Exception:
        raise HTTPException(500, "Something went wrong. Please try again.")

    # Same response whether new or already on the list, so nobody can probe who has joined
    return {"ok": True}