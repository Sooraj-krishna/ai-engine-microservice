# Celery Worker Auto-Start Setup

This guide provides two methods to automatically start the Celery worker, eliminating the need to manually run it every time.

## 🎯 Choose Your Approach

### Option 1: Systemd Service (Recommended for Local Development)

**Pros:**

- ✅ Native Linux integration
- ✅ Starts automatically on boot
- ✅ Auto-restarts on failure
- ✅ Easy to manage with `systemctl`
- ✅ Lightweight (no containers)

**Cons:**

- ❌ Linux-only
- ❌ Requires manual Redis installation
- ❌ Less portable

### Option 2: Docker Compose (Recommended for Production)

**Pros:**

- ✅ Fully containerized (Redis, Celery, API, UI)
- ✅ Portable across environments
- ✅ Isolated dependencies
- ✅ Easy to scale
- ✅ Built-in orchestration

**Cons:**

- ❌ Requires Docker and Docker Compose
- ❌ Slightly more resource-intensive
- ❌ Requires rebuilding on code changes

---

## 📦 Option 1: Systemd Service Setup

### Prerequisites

- Redis server installed (already done ✅)
- Python virtual environment created (already done ✅)

### Installation

1. **Install the service:**

   ```bash
   cd /home/devils_hell/ai-engine-microservice
   sudo bash scripts/install-celery-service.sh
   ```

2. **Verify it's running:**
   ```bash
   sudo systemctl status celery-worker
   ```

### Managing the Service

```bash
# Check status
sudo systemctl status celery-worker

# View live logs
sudo journalctl -u celery-worker -f

# Restart service
sudo systemctl restart celery-worker

# Stop service
sudo systemctl stop celery-worker

# Start service
sudo systemctl start celery-worker

# Disable auto-start on boot
sudo systemctl disable celery-worker

# Enable auto-start on boot
sudo systemctl enable celery-worker
```

### What Happens on Reboot?

- ✅ Redis starts automatically
- ✅ Celery worker starts automatically
- ✅ You only need to manually start your FastAPI app and UI

---

## 🐳 Option 2: Docker Compose Setup

### Prerequisites

- Docker installed
- Docker Compose installed

### Installation

1. **Start all services:**

   ```bash
   cd /home/devils_hell/ai-engine-microservice
   bash scripts/start-docker.sh -d
   ```

   This starts:
   - Redis (message broker)
   - Celery Worker (background tasks)
   - FastAPI API (backend)
   - UI (frontend)

2. **Check status:**
   ```bash
   docker-compose ps
   ```

### Managing Docker Services

```bash
# Start all services (detached)
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f celery-worker
docker-compose logs -f api
docker-compose logs -f redis

# Restart a specific service
docker-compose restart celery-worker

# Rebuild and restart (after code changes)
docker-compose up -d --build

# Check service status
docker-compose ps

# Stop a specific service
docker-compose stop celery-worker
```

### What Happens on Reboot?

If you want Docker services to auto-start on reboot, add `restart: always` to each service in `docker-compose.yml` (already included! ✅)

---

## 🧪 Testing Both Approaches

### Test Auto-Start

**Systemd:**

```bash
# Reboot system
sudo reboot

# After reboot, check if service started
sudo systemctl status celery-worker
```

**Docker:**

```bash
# Reboot system
sudo reboot

# After reboot, check if containers started
docker-compose ps
```

### Test Maintenance Cycle

1. Open UI: http://localhost:3000
2. Click "Start Maintenance Cycle"
3. Should work without errors!

---

## 🔧 Troubleshooting

### Systemd Service Issues

**Service won't start:**

```bash
# Check detailed logs
sudo journalctl -u celery-worker -n 50

# Check Redis is running
sudo systemctl status redis-server

# Check file permissions
ls -la /var/log/celery-worker.log
```

**Service keeps restarting:**

```bash
# View restart count
systemctl show celery-worker -p NRestarts

# View full logs
sudo journalctl -u celery-worker --since "1 hour ago"
```

### Docker Compose Issues

**Containers won't start:**

```bash
# Check container logs
docker-compose logs celery-worker
docker-compose logs redis

# Check if ports are available
sudo netstat -tulpn | grep -E '6379|8000|3000'
```

**Redis connection errors:**

```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
```

---

## 🎉 Success Indicators

You'll know it's working when:

- ✅ Celery worker starts automatically on boot
- ✅ Maintenance cycles run without manual intervention
- ✅ No "Connection refused" errors to Redis
- ✅ Tasks appear in Celery logs when triggered
- ✅ System continues working after reboot

---

## 📝 Current Setup Status

Based on your system:

- [x] Redis installed and running
- [x] Celery worker can connect to Redis
- [x] Systemd service file created
- [x] Docker Compose configuration created
- [ ] Choose and install one of the approaches above

**Recommendation:** For your local development setup, use the **Systemd Service** approach. It's simpler and more lightweight for a single developer machine.
