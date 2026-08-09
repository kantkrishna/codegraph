# Dockerfile

# This Dockerfile uses a multi-stage build to create a lightweight runtime image
#for a Python application.

FROM python:3.12-slim

# Copy the uv executable directly from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Set uv to compile bytecode for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy dependency manifests first to leverage Docker layer caching
COPY pyproject.toml uv.lock* ./

# Install dependencies (uv will automatically create the .venv here)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the actual application code
COPY backend/ /app/backend/

EXPOSE 8000

# Let uv handle the execution and environment activation safely
CMD ["uv", "run", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]