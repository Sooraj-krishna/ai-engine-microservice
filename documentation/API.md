# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, all endpoints are open. Future versions will include API key authentication.

## Endpoints

### Core Endpoints

#### GET `/`

**Description**: Root endpoint, health check

**Response**:

```json
{
  "status": "AI Engine running",
  "timestamp": "2026-01-05T20:00:00",
  "version": "2.0.0 - Enhanced Safety Edition",
  "website_monitored": "https://yoursite.com",
  "monitoring_mode": "simple",
  "safety_features": {
    "validation_enabled": true,
    "rollback_enabled": true,
    "safe_mode_only": true
  }
}
```

#### GET `/health`

**Description**: Comprehensive health check

**Response**:

```json
{
  "status": "healthy",
  "last_check": "2026-01-05T20:00:00",
  "dependencies": {
    "github_api": true,
    "gemini_api": true,
    "all_healthy": true
  },
  "version": "2.0.0"
}
```

#### GET `/status`

**Description**: Detailed system status including validation and rollback history

**Response**:

```json
{
  "health": {...},
  "environment": {
    "website_url": "https://yoursite.com",
    "github_repo": "user/repo",
    "monitoring_mode": "simple",
    "has_github_token": true,
    "has_gemini_token": true
  },
  "safety_systems": {
    "validation": {...},
    "rollback": {...}
  },
  "issues": [],
  "timestamp": "2026-01-05T20:00:00"
}
```

---

### Maintenance Endpoints

#### POST `/run`

**Description**: Trigger AI maintenance cycle

**Request**: No body required

**Response**:

```json
{
  "message": "Enhanced AI maintenance cycle started",
  "timestamp": "2026-01-05T20:00:00",
  "website": "https://yoursite.com",
  "safety_features": {
    "validation_enabled": true,
    "rollback_enabled": true
  }
}
```

**Process**:

1. Collects site data
2. Analyzes for bugs/issues
3. Generates fixes using AI
4. Validates all fixes
5. Tests fixes in sandbox
6. Creates GitHub PR

**Logs**: Stream via `/ws/logs` WebSocket

#### POST `/manual-rollback`

**Description**: Manually trigger rollback of recent changes

**Request**: No body required

**Response**:

```json
{
  "message": "Manual rollback initiated",
  "timestamp": "2026-01-05T20:00:00"
}
```

---

### Competitive Analysis Endpoints

#### POST `/analyze-competitors`

**Description**: Analyze competitor websites and generate feature recommendations

**Request Body** (optional):

```json
{
  "competitor_urls": ["https://competitor1.com", "https://competitor2.com"]
}
```

If not provided, uses `COMPETITOR_URLS` from `.env`

**Response**:

```json
{
  "analysis_date": "2026-01-05T20:00:00",
  "summary": {
    "total_competitors": 3,
    "total_gaps_identified": 12,
    "high_priority": 4,
    "medium_priority": 5,
    "low_priority": 3
  },
  "feature_gaps": [
    {
      "id": "feature_001",
      "name": "Dark Mode",
      "category": "User Experience",
      "description": "Theme toggle for dark/light modes",
      "found_in": ["competitor1.com", "competitor2.com"],
      "frequency": "2/3",
      "frequency_percentage": "67%",
      "complexity": "medium",
      "priority_score": 8.5,
      "estimated_effort": "1-2 days",
      "business_impact": "high",
      "implementation_notes": "Add theme provider and toggle component"
    }
  ]
}
```

**Duration**: 30-60 seconds depending on number of competitors

#### GET `/feature-recommendations`

**Description**: Get prioritized feature recommendations from last analysis

**Response**:

```json
{
  "analysis_date": "2026-01-05T20:00:00",
  "feature_gaps": [...],
  "summary": {...}
}
```

**Error Response** (if no analysis run):

```json
{
  "error": "No competitive analysis results available. Run /analyze-competitors first"
}
```

#### POST `/select-feature`

**Description**: User selects which feature to implement next

**Request Body**:

```json
{
  "feature_id": "feature_001"
}
```

**Response**:

```json
{
  "message": "Feature 'Dark Mode' selected for future implementation",
  "feature": {...},
  "note": "Feature selection logged. Implementation planning will be added in future updates."
}
```

---

### Configuration Endpoints

#### POST `/configure`

**Description**: Update system configuration

**Request Body**:

```json
{
  "website_url": "https://newsite.com",
  "monitoring_mode": "ga_logs",
  "enable_competitive_analysis": true
}
```

**Response**:

```json
{
  "status": "Configuration updated successfully",
  "config": {...}
}
```

#### GET `/config`

**Description**: Get current configuration

**Response**:

```json
{
  "website_url": "https://yoursite.com",
  "monitoring_mode": "simple",
  "enable_competitive_analysis": true,
  "auto_run_competitive_analysis": false
}
```

---

### Logging & Monitoring

#### WebSocket `/ws/logs`

**Description**: Real-time log streaming

**Connection**:

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/logs");

ws.onmessage = (event) => {
  console.log("Log:", event.data);
};
```

**Messages**: Timestamped log entries from all operations

#### GET `/log-summary`

**Description**: Compact summary of logs for AI consumption

**Response**:

```json
{
  "error_count": 2,
  "warning_count": 5,
  "info_count": 42,
  "recent_errors": [...],
  "recent_warnings": [...]
}
```

---

### Gemini API Proxy

#### POST `/api/gemini`

**Description**: Backend endpoint for Gemini API calls (used by frontend)

**Request Body**:

```json
{
  "messages": [{ "role": "user", "content": "Generate a button component" }],
  "model": "gemini-1.5-flash",
  "timeoutMs": 60000
}
```

**Response**:

```json
{
  "text": "Generated response...",
  "model": "gemini-1.5-flash"
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

**Success** (2xx):

```json
{
  "message": "Operation successful",
  "data": {...}
}
```

**Client Error** (4xx):

```json
{
  "error": "Error description",
  "status_code": 400
}
```

**Server Error** (5xx):

```json
{
  "error": "Internal server error",
  "details": "Stack trace or details"
}
```

## Rate Limiting

Currently no rate limiting. Future versions will implement:

- 100 requests/minute per IP
- 10 maintenance cycles/hour
- 5 competitive analyses/hour

## API Examples

### cURL Examples

```bash
# Trigger maintenance
curl -X POST http://localhost:8000/run

# Get system status
curl http://localhost:8000/status

# Run competitive analysis
curl -X POST http://localhost:8000/analyze-competitors \
  -H "Content-Type: application/json" \
  -d '{"competitor_urls": ["https://competitor.com"]}'

# Get feature recommendations
curl http://localhost:8000/feature-recommendations

# Select feature for implementation
curl -X POST http://localhost:8000/select-feature \
  -H "Content-Type: application/json" \
  -d '{"feature_id": "feature_001"}'
```

### JavaScript/TypeScript Examples

```typescript
// Trigger maintenance cycle
const response = await fetch("http://localhost:8000/run", {
  method: "POST",
});
const data = await response.json();

// Get feature recommendations
const recommendations = await fetch(
  "http://localhost:8000/feature-recommendations"
);
const features = await recommendations.json();

// WebSocket connection
const ws = new WebSocket("ws://localhost:8000/ws/logs");
ws.onmessage = (event) => {
  console.log("Log:", event.data);
};
```

### Python Examples

```python
import requests

# Trigger maintenance
response = requests.post('http://localhost:8000/run')
print(response.json())

# Run competitive analysis
response = requests.post(
    'http://localhost:8000/analyze-competitors',
    json={'competitor_urls': ['https://competitor.com']}
)
analysis = response.json()

# Get status
status = requests.get('http://localhost:8000/status').json()
```

## Interactive API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation with live testing capabilities.
