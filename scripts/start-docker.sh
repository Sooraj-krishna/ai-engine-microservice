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
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo -e "${YELLOW}📁 Project directory: $PROJECT_DIR${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    if [ -f ".env.example" ]; then
        echo "📋 Copying .env.example to .env..."
        cp .env.example .env
        echo "⚠️  Please edit .env file with your configuration before starting."
        exit 1
    else
        echo "Please create a .env file first."
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
docker-compose up $DETACHED --build

if [ -n "$DETACHED" ]; then
    echo ""
    echo -e "${GREEN}✨ All services started successfully!${NC}"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 Access points:"
    echo "  • Frontend UI:  http://localhost:3000"
    echo "  • Backend API:  http://localhost:8000"
    echo "  • API Docs:     http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  • View logs:           docker-compose logs -f"
    echo "  • View specific logs:  docker-compose logs -f celery-worker"
    echo "  • Stop all services:   docker-compose down"
    echo "  • Restart service:     docker-compose restart celery-worker"
    echo "  • Check status:        docker-compose ps"
fi
