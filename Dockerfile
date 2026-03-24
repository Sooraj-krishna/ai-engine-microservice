FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries + OS deps.
# Without this, any runtime usage of Playwright (Lighthouse/e2e/a11y tests) fails.
RUN python -m playwright install --with-deps chromium

# Copy source code
COPY ./src ./src
COPY ./tests ./tests

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

WORKDIR /app/src

EXPOSE 8000

# Default entrypoint (compose overrides the command).
CMD ["uvicorn", "main_with_config:app", "--host", "0.0.0.0", "--port", "8000"]
