# Configuration Guide

## Environment Variables

All configuration is managed via the `.env` file in the project root. Copy `.env.example` to `.env` and configure as needed.

## Required Variables

### Website Configuration

```bash
# The URL of the website to monitor
WEBSITE_URL=https://yourwebsite.com
```

**Purpose**: Target website for bug detection and analysis  
**Example**: `https://buggy-cart.vercel.app`

### GitHub Integration

```bash
# GitHub personal access token
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# Target repository (format: username/repo)
GITHUB_REPO=yourusername/yourrepo
```

**Purpose**: Automated PR creation for fixes  
**Token Permissions**: `repo` (full repository access)  
**How to get**: GitHub → Settings → Developer settings → Personal access tokens

### AI Configuration

```bash
# Google Gemini API key
GEMINI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxx

# AI model to use
GEMINI_MODEL=gemini-1.5-flash
```

**Purpose**: AI-powered code generation  
**Models Available**:

- `gemini-1.5-flash` (recommended, faster)
- `gemini-1.5-pro` (more accurate, slower)
- `gemini-pro` (legacy)

**How to get**: [Google AI Studio](https://makersuite.google.com/app/apikey)

## Optional Variables

### Monitoring Mode

```bash
# Monitoring strategy
MONITORING_MODE=simple
```

**Options**:

- `simple` - Basic monitoring (default)
- `ga_only` - Google Analytics only
- `ga_logs` - GA + server logs (requires log file paths)

### Google Analytics (Optional)

```bash
GA4_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

**Required for**: `ga_only` or `ga_logs` monitoring modes  
**Setup**: Create service account in Google Cloud, enable Analytics Data API

### Competitive Analysis

```bash
# Competitor URLs (comma-separated)
COMPETITOR_URLS=https://competitor1.com,https://competitor2.com,https://competitor3.com

# Enable competitive analysis feature
ENABLE_COMPETITIVE_ANALYSIS=true

# Auto-run on startup (not recommended)
AUTO_RUN_COMPETITIVE_ANALYSIS=false
```

### Advanced Features

```bash
# Use improved incremental fixer
USE_IMPROVED_FIXER=true

# Test fixes before applying
TEST_FIXES_BEFORE_APPLY=true

# Application environment
ENVIRONMENT=development  # or production
```

### Log File Paths (For ga_logs mode)

```bash
ACCESS_LOG_PATH=/var/log/nginx/access.log
ERROR_LOG_PATH=/var/log/nginx/error.log
APP_LOG_PATH=logs/app.log
```

**Note**: Only needed if `MONITORING_MODE=ga_logs`

## Configuration Examples

### Minimal Setup (Development)

```bash
WEBSITE_URL=https://yoursite.com
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_REPO=user/repo
GEMINI_API_KEY=xxxxxxxxxxxxx
MONITORING_MODE=simple
```

### Full Setup (Production)

```bash
# Website
WEBSITE_URL=https://production-site.com
MONITORING_MODE=ga_logs

# GitHub
GITHUB_TOKEN=ghp_xxxxxxx
GITHUB_REPO=company/production-repo

# AI
GEMINI_API_KEY=xxxxxxx
GEMINI_MODEL=gemini-1-5-pro

# Google Analytics
GA4_PROPERTY_ID=123456789
GOOGLE_APPLICATION_CREDENTIALS=/keys/ga-service-account.json

# Competitive Analysis
COMPETITOR_URLS=https://competitor1.com,https://competitor2.com
ENABLE_COMPETITIVE_ANALYSIS=true

# Features
USE_IMPROVED_FIXER=true
TEST_FIXES_BEFORE_APPLY=true
ENVIRONMENT=production

# Logs
ACCESS_LOG_PATH=/var/log/nginx/access.log
ERROR_LOG_PATH=/var/log/nginx/error.log
```

### Competitive Analysis Only

```bash
WEBSITE_URL=https://yoursite.com
GITHUB_TOKEN=ghp_xxxx
GITHUB_REPO=user/repo
GEMINI_API_KEY=xxxxx
MONITORING_MODE=simple

# Focus on competitive analysis
COMPETITOR_URLS=https://amazon.com,https://flipkart.com,https://myntra.com
ENABLE_COMPETITIVE_ANALYSIS=true
```

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use `.env.example`** for templates (without real values)
3. **Rotate tokens regularly** (every 90 days)
4. **Use separate tokens** for development and production
5. **Limit GitHub token scope** to specific repositories
6. **Store service account keys** outside project directory

## Validation

The system validates configuration on startup. Check logs for:

```
[DEBUG] Loading environment variables...
[DEBUG] WEBSITE_URL: https://yoursite.com
[DEBUG] GITHUB_REPO: user/repo
[DEBUG] MONITORING_MODE: simple
```

Missing required variables will show warnings:

```
[WARNING] GITHUB_TOKEN not found
[WARNING] GEMINI_API_KEY not configured
```

## Environment-Specific Configuration

### Development

```bash
ENVIRONMENT=development
GEMINI_MODEL=gemini-1.5-flash  # Faster
TEST_FIXES_BEFORE_APPLY=true
```

### Staging

```bash
ENVIRONMENT=staging
GEMINI_MODEL=gemini-1.5-pro  # More accurate
TEST_FIXES_BEFORE_APPLY=true
```

### Production

```bash
ENVIRONMENT=production
GEMINI_MODEL=gemini-1.5-pro
TEST_FIXES_BEFORE_APPLY=true
USE_IMPROVED_FIXER=true
MONITORING_MODE=ga_logs
```

## Loading Configuration

The system loads configuration in this order:

1. `.env` file in project root
2. Environment variables from system
3. Default values (if not specified)

To override .env values temporarily:

```bash
WEBSITE_URL=https://test.com python3 main_with_config.py
```

## Troubleshooting Configuration

### Check Loaded Values

```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"WEBSITE_URL: {os.getenv('WEBSITE_URL')}")
print(f"GITHUB_REPO: {os.getenv('GITHUB_REPO')}")
```

### Common Issues

**Issue**: "Environment variable not found"  
**Solution**: Ensure `.env` exists and variable is set

**Issue**: "Invalid GitHub token"
**Solution**: Check token has correct permissions and isn't expired

**Issue**: "Gemini API error"  
**Solution**: Verify API key is correct and has quota remaining

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for more solutions.
