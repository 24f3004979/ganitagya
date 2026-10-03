FROM python:3.12-slim

# uv, copied from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
WORKDIR /srv

# Install dependencies first so Docker caches this layer
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app ./app

# Cloud Run is stateless, so production uses Firestore
ENV PATH="/srv/.venv/bin:$PATH" STORAGE=firestore

# --proxy-headers lets us see the real client IP behind Google's proxy
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} \
    --proxy-headers --forwarded-allow-ips="*"
