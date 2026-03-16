# Redis & Queue Management

We use **Redis** and **Celery** to manage background tasks, ensuring the API remains responsive even during heavy AI processing.

## Core Functions

### 1. Task Queue (Celery)

Long-running operations are offloaded to background workers:

- **Maintenance Cycles**: The core "fix loop" runs asynchronously.
- **Analysis Tasks**: Competitive analysis, which involves scraping multiple sites, is processed in the background.
- **Notifications**: Sending emails or alerts happens without blocking the main thread.

### 2. State Management

Redis acts as the shared state/memory for the microservice:

- **Real-time Logs**: Using Redis Pub/Sub, we broadcast backend logs to the frontend via WebSockets.
- **Progress Tracking**: The status of multi-step AI tasks (e.g., "Step 3/5: Validating Fix") is stored in Redis.
- **Distributed Locking**: Prevents two maintenance cycles from running simultaneously and conflicting.

### 3. Caching

We use Redis to cache expensive operations:

- **API Responses**: Results from competitive analysis are cached.
- **AI Responses**: To save costs, identical prompts sent to Gemini are cached (using SHA-256 hashing).

## Configuration

The Redis connection is configured via the `REDIS_URL` environment variable.

```env
REDIS_URL=redis://localhost:6379/0
```

It supports SSL/TLS for secure production environments.
