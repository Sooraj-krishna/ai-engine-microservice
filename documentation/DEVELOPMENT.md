# Development Guide

## Development Environment Setup

### 1. Fork and Clone

```bash
git clone https://github.com/yourusername/ai-engine-microservice.git
cd ai-engine-microservice
git remote add upstream https://github.com/originaluser/ai-engine-microservice.git
```

### 2. Install Dependencies

```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install

# Frontend
cd ai-engine-ui
npm install
cd ..
```

### 3. Development Configuration

Create `.env` for development:

```bash
cp .env.example .env
# Edit with test credentials
```

## Project Structure

```
src/
├── main_with_config.py       # FastAPI entry point
├── analyzer.py                # Central analysis coordinator
├── enhanced_bug_detector.py   # Bug detection system
├── improved_fixer.py          # Incremental fixing
├── generator.py               # AI fix generation
├── validator.py               # Code validation
├── fix_tester.py              # Isolated testing
├── competitive_analyzer.py    # Competitor analysis
├── feature_extractor.py       # Feature detection
├── github_handler.py          # GitHub automation
├── rollback_manager.py        # Rollback system
└── ...

ai-engine-ui/
├── src/
│   ├── app/
│   │   └── page.tsx           # Main page
│   └── components/
│       ├── ConfigurationForm.tsx
│       ├── StatusMonitor.tsx
│       ├── FeatureRecommendations.tsx
│       └── ...
```

## Running in Development Mode

### Backend (with auto-reload)

```bash
cd src
python3 main_with_config.py
```

Changes to Python files will auto-reload the server.

### Frontend (with hot-reload)

```bash
cd ai-engine-ui
npm run dev
```

Changes will hot-reload in browser.

## Adding New Features

### Backend Feature

1. **Create new module** in `src/`
2. **Import in `main_with_config.py`**
3. **Add endpoint** to FastAPI app
4. **Update validation** in `validator.py` if needed
5. **Write tests** in `tests/`

Example:

```python
# src/my_feature.py
def analyze_something():
    return {"result": "data"}

# src/main_with_config.py
from my_feature import analyze_something

@app.get("/my-feature")
def get_my_feature():
    return analyze_something()
```

### Frontend Feature

1. **Create component** in `ai-engine-ui/src/components/`
2. **Add to page** in `ai-engine-ui/src/app/page.tsx`
3. **Style with Tailwind** classes
4. **Connect to API** via fetch

Example:

```tsx
// src/components/MyFeature.tsx
export function MyFeature() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/my-feature")
      .then((r) => r.json())
      .then(setData);
  }, []);

  return <div>{data?.result}</div>;
}
```

## Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validator.py

# Run with coverage
pytest --cov=src tests/
```

### Frontend Tests

```bash
cd ai-engine-ui
npm test
```

### Manual Testing

```bash
# Test API endpoints
curl http://localhost:8000/status

# Test competitive analysis
curl -X POST http://localhost:8000/analyze-competitors

# Test maintenance cycle
curl -X POST http://localhost:8000/run
```

## Code Style

### Python

Follow PEP 8:

```bash
# Format with black
black src/

# Lint with flake8
flake8 src/

# Type checking (optional)
mypy src/
```

### TypeScript/React

```bash
cd ai-engine-ui

# Lint
npm run lint

# Format
npx prettier --write "src/**/*.{ts,tsx}"
```

## Debugging

### Backend Debugging

Add breakpoints with `pdb`:

```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger with `.vscode/launch.json`:

```json
{
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main_with_config:app", "--reload"],
      "cwd": "${workspaceFolder}/src"
    }
  ]
}
```

### Frontend Debugging

Use browser DevTools:

- Console for logs
- Network tab for API calls
- React DevTools for component inspection

## Common Development Tasks

### Reset Database/State

```bash
# Clear rollback history
rm src/rollback_history.json

# Clear validation log
rm src/validation_log.json
```

### Update Dependencies

```bash
# Backend
pip install --upgrade -r requirements.txt

# Frontend
cd ai-engine-ui
npm update
```

### Generate API Documentation

FastAPI auto-generates docs at:

- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Contributing

### 1. Create Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Make Changes

- Write code
- Add tests
- Update documentation

### 3. Commit

```bash
git add .
git commit -m "feat: add my new feature"
```

Follow conventional commits:

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `refactor:` code refactoring
- `test:` tests
- `chore:` maintenance

### 4. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Create PR on GitHub with:

- Clear description
- Screenshots if UI changes
- Test results

## Release Process

1. Update version in `main_with_config.py`
2. Update CHANGELOG
3. Create git tag: `git tag v2.1.0`
4. Push tag: `git push --tags`
5. Create GitHub release

## Architecture Decisions

Document significant decisions in `/documentation/ARCHITECTURE.md`.

## Performance Optimization

### Backend

- Use async/await for I/O operations
- Cache frequently accessed data
- Batch API calls to external services
- Use connection pooling

### Frontend

- Code splitting
- Lazy loading components
- Memoization with useMemo/useCallback
- Optimize re-renders

## Security Checklist

- [ ] No hardcoded credentials
- [ ] All user input validated
- [ ] API rate limiting implemented
- [ ] CORS properly configured
- [ ] Dependencies scanned for vulnerabilities
- [ ] Secrets in environment variables only

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Playwright Docs](https://playwright.dev/)
- [Google Gemini API](https://ai.google.dev/docs)
