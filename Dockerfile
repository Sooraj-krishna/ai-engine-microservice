# Build Stage for Frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/ui
COPY ./ai-engine-ui/package*.json ./
RUN npm install
COPY ./ai-engine-ui ./
# Fix for potential memory issues during build on low-resource machines
ENV NODE_OPTIONS="--max-old-space-size=4096"
RUN npm run build

# Final Stage for Backend
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps chromium

# Install Playwright browser binaries + OS deps.
# Without this, any runtime usage of Playwright (Lighthouse/e2e/a11y tests) fails.
RUN python -m playwright install --with-deps chromium

# Copy source code
# Copy backend source code
COPY ./src ./src
COPY ./tests ./tests

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /app/ui/out ./ui_dist

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose port (Render sets PORT env var, but we expose 8000 default)
EXPOSE 8000

# Default entrypoint (compose overrides the command).
CMD ["uvicorn", "main_with_config:app", "--host", "0.0.0.0", "--port", "8000"]
