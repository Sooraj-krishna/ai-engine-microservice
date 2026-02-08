#!/bin/bash
# Installation script for Celery Worker systemd service

set -e

echo "🚀 Installing Celery Worker as systemd service..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run with sudo${NC}"
    exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
PROJECT_DIR="/home/$ACTUAL_USER/ai-engine-microservice"

echo -e "${YELLOW}📁 Project directory: $PROJECT_DIR${NC}"

# Create log directory
echo "📝 Creating log directory..."
mkdir -p /var/log
touch /var/log/celery-worker.log
chown $ACTUAL_USER:$ACTUAL_USER /var/log/celery-worker.log

# Copy service file to systemd directory
echo "📋 Copying service file..."
cp "$PROJECT_DIR/celery-worker.service" /etc/systemd/system/

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service to start on boot
echo "✅ Enabling service to start on boot..."
systemctl enable celery-worker.service

# Start the service
echo "▶️  Starting Celery worker service..."
systemctl start celery-worker.service

# Wait a moment for service to start
sleep 2

# Show status
echo ""
echo -e "${GREEN}✨ Installation complete!${NC}"
echo ""
echo "📊 Service Status:"
systemctl status celery-worker.service --no-pager

echo ""
echo -e "${GREEN}🎉 Celery worker is now running as a system service!${NC}"
echo ""
echo "Useful commands:"
echo "  • Check status:     sudo systemctl status celery-worker"
echo "  • View logs:        sudo journalctl -u celery-worker -f"
echo "  • Restart service:  sudo systemctl restart celery-worker"
echo "  • Stop service:     sudo systemctl stop celery-worker"
echo "  • Disable service:  sudo systemctl disable celery-worker"
