# GHARMIND AI — Backend Dockerfile
# Multi-stage build for production

# ─── Stage 1: Builder ─────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Export dependencies to requirements.txt (no dev deps)
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Install dependencies
RUN pip install --no-cache-dir --target=/build/deps -r requirements.txt


# ─── Stage 2: Runtime ─────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /build/deps /usr/local/lib/python3.12/site-packages

# Create non-root user
RUN useradd --create-home --shell /bin/bash gharmind
USER gharmind

# Copy application code
COPY --chown=gharmind:gharmind ./app ./app
COPY --chown=gharmind:gharmind ./alembic ./alembic
COPY --chown=gharmind:gharmind alembic.ini .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/system/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
