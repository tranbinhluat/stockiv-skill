FROM python:3.12-slim

# Copy uv from the official Astral image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation and keep uv cache purely ephemeral
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first (leverage Docker layer caching)
COPY pyproject.toml uv.lock ./
# We don't want to install the project itself yet, just dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy ONLY the bare minimum code needed to run the API
# We skip docs, tests, memory, and raw data
COPY README.md ./
COPY src ./src

# Install the project itself
RUN uv sync --frozen --no-dev

# Ensure the UV bin path is in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI server via uvicorn
CMD ["uvicorn", "stockiv.api:app", "--host", "0.0.0.0", "--port", "8000"]
