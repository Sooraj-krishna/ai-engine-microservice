#!/bin/bash
# Convenience script to start all services with Docker Compose

set -e

echo "🐳 Starting AI Engine Microservice with Docker Compose..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
# Prefer modern `docker compose` (plugin), but fall back to legacy `docker-compose`.
COMPOSE_CMD=()
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD=("docker-compose")
elif docker compose version &> /dev/null; then
    COMPOSE_CMD=("docker" "compose")
else
    echo "❌ Docker Compose is not installed (need `docker compose` or `docker-compose`)."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
COMPOSE_BIN="${COMPOSE_CMD[*]}"

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${YELLOW}📁 Project directory: $PROJECT_DIR${NC}"

# Check if config.env file exists (dotfiles may be blocked in some environments)
if [ ! -f "config.env" ]; then
    echo "❌ config.env file not found!"
    if [ -f "config.env.example" ]; then
        echo "📋 Copying config.env.example to config.env..."
        cp config.env.example config.env
        echo "⚠️  Please edit config.env file with your configuration before starting."
        exit 1
    else
        echo "Please create a config.env file first."
        exit 1
    fi
fi

# Parse command line arguments
DETACHED=""
if [ "$1" == "-d" ] || [ "$1" == "--detach" ]; then
    DETACHED="-d"
    echo "🔧 Running in detached mode..."
fi

# Build and start services
echo "🏗️  Building and starting services..."
"${COMPOSE_BIN}" up $DETACHED --build

if [ -n "$DETACHED" ]; then
    echo ""
    echo -e "${GREEN}✨ All services started successfully!${NC}"
    echo ""
    echo "📊 Service Status:"
    "${COMPOSE_BIN}" ps
    echo ""
    echo "🌐 Access points:"
    echo "  • Frontend UI:  http://localhost:3000"
    echo "  • Backend API:  http://localhost:8000"
    echo "  • API Docs:     http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  • View logs:           ${COMPOSE_BIN} logs -f"
    echo "  • View specific logs:  ${COMPOSE_BIN} logs -f celery-worker"
    echo "  • Stop all services:   ${COMPOSE_BIN} down"
    echo "  • Restart service:     ${COMPOSE_BIN} restart celery-worker"
    echo "  • Check status:        ${COMPOSE_BIN} ps"
fi
