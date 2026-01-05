# Troubleshooting Guide

## Common Issues

### Installation Issues

#### Issue: `pip install` fails with permission error

**Solution**:

```bash
# Use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Issue: Playwright browsers won't install

**Solution**:

```bash
# Reinstall with system dependencies
playwright install --with-deps

# Or install browsers only
playwright install chromium
```

#### Issue: `npm install` fails

**Solution**:

```bash
# Clear cache and retry
cd ai-engine-ui
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

---

### Configuration Issues

#### Issue: "GITHUB_TOKEN not found"

**Symptoms**: API calls fail, PRs not created

**Solution**:

1. Check `.env` file exists in project root
2. Verify `GITHUB_TOKEN=ghp_xxx` is set
3. Ensure no quotes around value
4. Restart server after editing `.env`

```bash
# Verify .env is loaded
cd src
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('GITHUB_TOKEN'))"
```

#### Issue: "Invalid GitHub credentials"

**Solution**:

1. Generate new personal access token
2. Ensure `repo` scope is selected
3. Token hasn't expired
4. Update `.env` with new token

#### Issue: "Gemini API error: 429 Rate Limit"

**Solution**:

- Wait 1 minute and retry
- Upgrade to paid Gemini API tier
- Reduce frequency of `/run` calls

---

### Runtime Issues

#### Issue: Server won't start - "Address already in use"

**Symptoms**:

```
Error: [Errno 48] Address already in use
```

**Solution**:

```bash
# Find process on port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn main_with_config:app --port 8001
```

#### Issue: UI won't load - "Connection refused"

**Symptoms**: Frontend shows blank page or error

**Solution**:

1. Check backend is running: `curl http://localhost:8000/health`
2. Check frontend is running: Visit http://localhost:3000
3. Check CORS settings in `main_with_config.py`
4. Clear browser cache

#### Issue: WebSocket logs not streaming

**Symptoms**: Real-time logs not appearing in UI

**Solution**:

1. Check WebSocket connection in browser DevTools
2. Verify backend WebSocket endpoint: `ws://localhost:8000/ws/logs`
3. Check firewall isn't blocking WebSockets
4. Try refreshing page

---

### Feature Issues

#### Issue: Competitive analysis returns empty results

**Symptoms**:

```json
{ "feature_gaps": [], "total_gaps": 0 }
```

**Possible Causes**:

1. **Gemini Vision API not working**: Check API key
2. **Competitor sites blocking scraping**: Use different sites
3. **Your site already has all features**: This is good!

**Solution**:

```bash
# Test Gemini Vision manually
python3 -c "
from ai_vision_api import analyze_screenshot
result = analyze_screenshot('screenshot.png')
print(result)
"

# Try with more/different competitors
COMPETITOR_URLS=https://amazon.com,https://ebay.com,https://walmart.com
```

#### Issue: No bugs detected but site has issues

**Possible Causes**:

1. Bug detector couldn't access site
2. Site requires authentication
3. JavaScript errors only appear in specific flows

**Solution**:

```bash
# Check site accessibility
curl -I https://yoursite.com

# Run Lighthouse manually
lighthouse https://yoursite.com --view

# Check specific URL path
# Edit analyzer.py to test specific pages
```

#### Issue: Fixes rejected by validator

**Symptoms**:

```
[VALIDATOR] ❌ Fix rejected: Dangerous pattern
```

**Solution**:

1. Check `validation_log.json` for details
2. Review fix content - may be false positive
3. Adjust validation rules in `validator.py` if needed
4. Use `USE_IMPROVED_FIXER=true` for better fixes

---

### API Issues

#### Issue: `/run` endpoint hangs

**Symptoms**: Request never completes

**Solution**:

```bash
# Check logs for errors
tail -f src/logs.txt

# Increase timeouts
# Edit main_with_config.py:
# uvicorn.run(..., timeout_keep_alive=300)
```

#### Issue: GitHub PR creation fails

**Symptoms**:

```
[ERROR] Failed to create PR: 401 Unauthorized
```

**Solution**:

1. Verify GitHub token permissions
2. Check repository exists and is accessible
3. Ensure token hasn't expired
4. Verify `GITHUB_REPO` format: `username/repo`

```bash
# Test GitHub access
python3 -c "
from github import Github
import os
g = Github(os.getenv('GITHUB_TOKEN'))
print(g.get_user().login)
"
```

---

### Performance Issues

#### Issue: Analysis takes too long

**Symptoms**: `/analyze-competitors` takes >5 minutes

**Causes**:

- Too many competitors
- Large/slow websites
- Gemini API rate limits

**Solution**:

```bash
# Reduce competitors
COMPETITOR_URLS=https://site1.com,https://site2.com  # Max 3-5

# Use faster model
GEMINI_MODEL=gemini-1.5-flash
```

#### Issue: High memory usage

**Solution**:

```bash
# Monitor memory
top -p $(pgrep -f python3)

# Restart service periodically
# Clear browser instances:
playwright install --force
```

---

### Testing Issues

#### Issue: Fix tests fail with "Node.js not found"

**Solution**:

```bash
# Install Node.js
# Ubuntu/Debian:
sudo apt install nodejs npm

# macOS:
brew install node

# Verify:
node --version
```

#### Issue: Playwright tests fail

**Error**:

```
Browser was closed unexpectedly
```

**Solution**:

```bash
# Reinstall browsers
playwright install chromium --with-deps

# Run with headed mode for debugging
# Edit fix_tester.py:
# browser = await p.chromium.launch(headless=False)
```

---

### UI Issues

#### Issue: Components not rendering

**Symptoms**: Blank spaces or missing UI elements

**Solution**:

```bash
cd ai-engine-ui

# Reinstall shadcn components
npx shadcn@latest add card button badge

# Clear Next.js cache
rm -rf .next
npm run dev
```

#### Issue: TypeScript errors in UI

**Solution**:

```bash
cd ai-engine-ui

# Check types
npx tsc --noEmit

# Update type definitions
npm install --save-dev @types/react @types/node
```

---

## Debug Mode

Enable verbose logging:

```python
# In main_with_config.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check all dependencies
curl http://localhost:8000/status | jq '.dependencies'

# Test database connectivity (if applicable)
# Test API keys
curl http://localhost:8000/status | jq '.environment'
```

## Log Files

Check logs for detailed error information:

```bash
# Backend logs (if configured)
tail -f src/logs/app.log

# Validation log
cat src/validation_log.json | jq '.'

# Rollback history
cat src/rollback_history.json | jq '.'
```

## Getting Help

1. **Check Logs**: Most issues show details in logs
2. **Search Issues**: GitHub Issues might have solution
3. **Read Docs**: Review [ARCHITECTURE.md](./ARCHITECTURE.md) and [API.md](./API.md)
4. **Enable Debug**: Turn on verbose logging
5. **Create Issue**: If still stuck, open GitHub issue with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)
   - Relevant logs

## Diagnostic Script

```bash
#!/bin/bash
# diagnose.sh - Check system health

echo "=== AI Engine Diagnostics ==="

echo "\n1. Python Version:"
python3 --version

echo "\n2. Node.js Version:"
node --version

echo "\n3. Backend Status:"
curl -s http://localhost:8000/health | jq '.'

echo "\n4. Environment Variables:"
grep -v "TOKEN\|KEY" .env

echo "\n5. Disk Space:"
df -h

echo "\n6. Memory:"
free -h

echo "\n7. Processes:"
ps aux | grep -E "(python3|node)"

echo "\n=== End Diagnostics ==="
```

Run with: `chmod +x diagnose.sh && ./diagnose.sh`
