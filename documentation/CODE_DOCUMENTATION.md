# Code Documentation

Detailed documentation for each file in the AI Engine Microservice project.

## Table of Contents

- [Backend Python Modules](#backend-python-modules)
- [Frontend React Components](#frontend-react-components)
- [Configuration Files](#configuration-files)

---

## Backend Python Modules

### `main_with_config.py`

**Purpose**: FastAPI application entry point with full feature set

**What it does**:

- Initializes FastAPI server with CORS middleware
- Defines all REST API endpoints
- Manages WebSocket connections for real-time logs
- Coordinates maintenance cycles
- Handles competitive analysis workflows

**Technologies**:

- **FastAPI**: Async web framework
- **uvicorn**: ASGI server
- **WebSockets**: Real-time log streaming
- **CORS**: Cross-origin resource sharing

**Key Endpoints**:

- `GET /` - Root health check
- `POST /run` - Trigger maintenance cycle
- `GET /status` - System status
- `POST /analyze-competitors` - Run competitive analysis
- `GET /feature-recommendations` - Get analysis results

**Implementation Details**:

```python
# Startup event for WebSocket broadcasting
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(log_streamer.broadcast_logs())

# Background task execution
@app.post("/run")
def run_engine(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_enhanced_maintenance_cycle)
```

---

### `enhanced_bug_detector.py`

**Purpose**: Comprehensive bug detection system

**What it does**:

- Runs Lighthouse performance audits
- Executes Axe accessibility tests
- Monitors JavaScript console errors
- Detects responsive design issues
- Aggregates and prioritizes bugs

**Technologies**:

- **Playwright**: Browser automation
- **Lighthouse**: Performance auditing
- **axe-core**: Accessibility testing

**Implementation**:

```python
async def detect_bugs_enhanced(url, repo_path=None):
    # Launch browser
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Performance audit
        lighthouse_results = await run_lighthouse_audit(url)

        # Accessibility scan
        axe_results = await run_axe_scan(page, url)

        # JavaScript errors
        console_errors = await monitor_console_errors(page, url)
```

**Output Format**:

```python
{
    "type": "performance",
    "severity": "high",
    "description": "Large Contentful Paint exceeds threshold",
    "target_file": "index.html",
    "details": {...}
}
```

---

### `competitive_analyzer.py`

**Purpose**: Analyzes competitor websites to identify feature gaps

**What it does**:

1. Scrapes competitor websites using Playwright
2. Takes screenshots of pages
3. Uses Gemini Vision API to extract features
4. Compares with your site's features
5. Calculates priority scores
6. Generates recommendations

**Technologies**:

- **Playwright**: Web scraping and screenshots
- **Google Gemini Vision API**: Visual feature detection
- **asyncio**: Asynchronous operations

**Implementation**:

```python
class CompetitiveAnalyzer:
    async def analyze_competitors(self, own_site_url, competitor_urls):
        # Extract features from own site
        own_features = await self.extract_features(own_site_url)

        # Extract features from competitors
        competitor_features = []
        for url in competitor_urls:
            features = await self.extract_features(url)
            competitor_features.append((url, features))

        # Find gaps
        gaps = self.find_feature_gaps(own_features, competitor_features)

        # Prioritize
        prioritized = self.prioritize_features(gaps)

        return {
            "feature_gaps": prioritized,
            "summary": self.generate_summary(prioritized)
        }
```

**Priority Scoring Algorithm**:

```python
def calculate_priority(feature):
    frequency_score = (feature.frequency / total_competitors) * 4
    impact_score = {"high": 3, "medium": 2, "low": 1}[feature.business_impact]
    effort_penalty = {"low": 0, "medium": -1, "high": -2}[feature.complexity]
    return frequency_score + impact_score + effort_penalty
```

---

### `feature_extractor.py`

**Purpose**: Extracts features from website screenshots using AI

**What it does**:

- Captures full-page screenshots
- Sends to Gemini Vision API
- Parses AI response for features
- Categories features by type
- Returns structured feature list

**Technologies**:

- **Google Gemini Vision**: Image analysis
- **Playwright**: Screenshot capture
- **JSON parsing**: Response processing

**Implementation**:

```python
async def extract_features(url):
    # Capture screenshot
    screenshot_path = await capture_screenshot(url)

    # Analyze with Vision API
    prompt = """
    Analyze this website screenshot and list ALL visible features.
    For each feature, provide:
    - name
    - category (UX, Performance, Accessibility, etc.)
    - description
    """

    response = await analyze_with_gemini_vision(screenshot_path, prompt)
    features = parse_features(response)
    return features
```

---

### `generator.py`

**Purpose**: AI-powered code fix generation

**What it does**:

- Separates bugs from optimizations
- Uses improved fixer for bug fixes
- Creates utility files for optimizations
- Generates AI fixes for complex issues
- Validates all generated code

**Technologies**:

- **Google Gemini API**: Code generation
- **Python asyncio**: Async processing
- **File I/O**: Code reading/writing

**Implementation**:

```python
async def prepare_fixes(issues, repo_path=None):
    all_fixes = []

    # Separate bug fixes from optimizations
    bugs = [i for i in issues if is_bug(i)]
    optimizations = [i for i in issues if not is_bug(i)]

    # Fix bugs first
    if USE_IMPROVED_FIXER:
        bug_fixes = incremental_fix_bugs(bugs, repo_path)
    else:
        bug_fixes = await generate_ai_fixes(bugs)

    all_fixes.extend(bug_fixes)

    # Create utility files for optimizations
    for opt in optimizations:
        utility = create_utility(opt)
        all_fixes.append(utility)

    # Validate all fixes
    safe_fixes = validator.validate_all_fixes(all_fixes)

    # Test fixes
    tested_fixes = await tester.test_fixes(safe_fixes)

    return tested_fixes
```

---

### `improved_fixer.py`

**Purpose**: Intelligent incremental bug fixing

**What it does**:

- Reads existing file content
- Analyzes context around bug
- Makes minimal, targeted changes
- Preserves existing functionality
- Returns modified code

**Technologies**:

- **AST parsing**: Code structure analysis
- **Regex**: Pattern matching
- **Google Gemini**: AI-assisted fixing

**Implementation**:

```python
def incremental_fix_bugs(bugs, repo_path):
    fixes = []

    for bug in bugs:
        # Read existing file
        file_path = os.path.join(repo_path, bug['target_file'])
        with open(file_path, 'r') as f:
            original_code = f.read()

        # Analyze context
        context = analyze_code_context(original_code, bug)

        # Generate minimal fix
        fix_prompt = f"""
        Fix this bug with minimal changes:
        Bug: {bug['description']}
        Context: {context}
        Original code: {original_code}

        Return ONLY the fixed code, no explanations.
        """

        fixed_code = query_ai(fix_prompt)

        fixes.append({
            'path': bug['target_file'],
            'content': fixed_code,
            'description': f"Fix: {bug['description']}"
        })

    return fixes
```

---

### `validator.py`

**Purpose**: Multi-layer code validation

**What it does**:

- Checks for dangerous patterns
- Validates file types
- Ensures utility files in safe locations
- Detects bug fixes vs utilities
- Maintains validation log

**Technologies**:

- **Regex**: Pattern matching
- **File path analysis**: Path validation
- **JSON logging**: Audit trail

**Implementation**:

```python
class CodeValidator:
    def validate_fix(self, fix):
        # Safety check
        if self.has_dangerous_patterns(fix['content']):
            return False, "Dangerous pattern detected"

        # File type check
        if not self.is_modifiable_file(fix['path']):
            return False, "Cannot modify framework files"

        # Utility file check
        if self.is_utility_file(fix['path']):
            if not self.is_safe_utility_location(fix['path']):
                return False, "Unsafe utility location"

        # All checks passed
        return True, None

    DANGEROUS_PATTERNS = [
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'rm\s+-rf',
        r'delete\s+from',
        r'Function\s*\('
    ]
```

---

### `fix_tester.py`

**Purpose**: Isolated testing of code fixes

**What it does**:

- Tests JavaScript syntax with Node.js
- Tests Python syntax with AST
- Runs execution tests in sandbox
- Tests browser compatibility
- Validates HTML structure

**Technologies**:

- **Node.js**: JavaScript validation
- **Python subprocess**: Isolated execution
- **Playwright**: Browser testing
- **AST**: Python parsing

**Implementation**:

```python
class FixTester:
    async def test_single_fix(self, fix):
        file_ext = Path(fix['path']).suffix

        if file_ext in ['.js', '.jsx', '.ts', '.tsx']:
            return await self.test_web_fix(fix)
        elif file_ext == '.py':
            return await self.test_python_fix(fix)
        elif file_ext == '.html':
            return await self.test_html_fix(fix)

    def check_javascript_syntax(self, code):
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix='.js') as f:
            f.write(code.encode())
            f.flush()

            # Run node --check
            result = subprocess.run(
                ['node', '--check', f.name],
                capture_output=True
            )

            return result.returncode == 0
```

**Special Handling**:

- Skips Node.js tests for browser-only code (window, document)
- Detects TypeScript/JSX and adjusts validation
- Skips execution tests for utility files (ES6 modules)

---

### `github_handler.py`

**Purpose**: GitHub repository integration

**What it does**:

- Clones/pulls repository
- Creates feature branches
- Commits and pushes changes
- Creates pull requests
- Generates PR descriptions

**Technologies**:

- **PyGithub**: GitHub API client
- **GitPython**: Git operations
- **subprocess**: Git commands

**Implementation**:

```python
def submit_fix_pr(fixes):
    # Clone repo
    repo_path = clone_or_pull_repo()

    # Create branch
    branch_name = f"ai-fix-{framework}-{timestamp}"
    create_branch(repo_path, branch_name)

    # Apply fixes
    for fix in fixes:
        file_path = os.path.join(repo_path, fix['path'])
        with open(file_path, 'w') as f:
            f.write(fix['content'])

    # Commit and push
    commit_message = generate_commit_message(fixes)
    push_changes(repo_path, branch_name, commit_message)

    # Create PR
    pr = create_pull_request(
        branch=branch_name,
        title=f"AI-Generated Fixes ({len(fixes)} changes)",
        body=generate_pr_description(fixes)
    )

    return pr.html_url
```

---

### `rollback_manager.py`

**Purpose**: Automatic rollback protection

**What it does**:

- Monitors site health after deployments
- Tracks change history
- Creates rollback PRs if issues detected
- Maintains audit trail

**Technologies**:

- **requests**: HTTP health checks
- **JSON**: History storage
- **PyGithub**: Rollback PR creation

**Implementation**:

```python
class RollbackManager:
    def perform_rollback_if_needed(self, site_data):
        # Check if recent changes caused issues
        if self.has_critical_errors(site_data):
            # Get last change
            last_change = self.get_last_change()

            # Create rollback PR
            pr_url = self.create_rollback_pr(
                reason="Critical errors detected",
                change_id=last_change['id']
            )

            return {
                "rollback_performed": True,
                "pr_url": pr_url,
                "reason": "Critical errors"
            }

        return {"rollback_performed": False}
```

---

### `analyzer.py`

**Purpose**: Central coordinator for all analysis types

**What it does**:

- Orchestrates bug detection
- Processes Google Analytics data
- Coordinates performance audits
- Manages data aggregation
- Prioritizes issues

**Technologies**:

- **asyncio**: Async coordination
- **Google Analytics API**: Metrics collection
- **modular imports**: Component integration

**Implementation**:

```python
async def analyze_data(site_data, repo_files, url, repo_path):
    all_issues = []

    # Enhanced bug detection
    bugs = await enhanced_bug_detector.detect_bugs_enhanced(url, repo_path)
    all_issues.extend(bugs)

    # GA analysis (if configured)
    if MONITORING_MODE in ['ga_only', 'ga_logs']:
        ga_issues = await analyze_ga_data(site_data)
        all_issues.extend(ga_issues)

    # Prioritize issues
    prioritized = prioritize_issues(all_issues)

    return prioritized
```

---

## Frontend React Components

### `FeatureRecommendations.tsx`

**Purpose**: Display competitive analysis results with natural language summary

**What it does**:

- Fetches feature recommendations from API
- Shows analysis summary in plain English
- Displays feature cards with priority scores
- Allows user to select features for implementation
- Triggers competitive analysis on demand

**Technologies**:

- **React**: Component framework
- **TypeScript**: Type safety
- **shadcn/ui**: UI components (Card, Button, Badge)
- **TailwindCSS**: Styling

**Implementation**:

```typescript
export default function FeatureRecommendations() {
  const [features, setFeatures] = useState<Feature[]>([]);
  const [analyzing, setAnalyzing] = useState(false);

  // Fetch recommendations
  const fetchRecommendations = async () => {
    const response = await fetch(
      "http://localhost:8000/feature-recommendations"
    );
    const data = await response.json();
    setFeatures(data.feature_gaps);
  };

  // Trigger analysis
  const triggerAnalysis = async () => {
    setAnalyzing(true);
    await fetch("http://localhost:8000/analyze-competitors", {
      method: "POST",
    });
    await fetchRecommendations();
    setAnalyzing(false);
  };

  return (
    <div>
      {/* Natural language summary */}
      <Card>
        <p>
          I analyzed {summary.total_competitors} competitors and found{" "}
          {summary.total_gaps} missing features...
        </p>
      </Card>

      {/* Feature cards */}
      {features.map((feature) => (
        <FeatureCard key={feature.id} feature={feature} />
      ))}
    </div>
  );
}
```

**State Management**:

- `features`: List of feature recommendations
- `analyzing`: Loading state during analysis
- `error`: Error messages
- `summary`: Analysis summary data

---

### `ConfigurationForm.tsx`

**Purpose**: System configuration interface

**What it does**:

- Manages environment configuration
- Tests API connections
- Updates backend settings
- Validates configuration

**Technologies**:

- **React Hook Form**: Form management
- **shadcn/ui**: Form components
- **TailwindCSS**: Styling

---

### `StatusMonitor.tsx`

**Purpose**: Real-time system status display

**What it does**:

- Shows health indicators
- Displays environment status
- Shows dependency connectivity
- Updates in real-time

**Technologies**:

- **React**: Component framework
- **useEffect**: Data fetching
- **Polling**: Periodic status updates

---

### `LogsDisplay.tsx`

**Purpose**: Real-time log streaming viewer

**What it does**:

- Connects to WebSocket endpoint
- Streams logs in real-time
- Color-codes log levels
- Auto-scrolls to latest

**Technologies**:

- **WebSocket API**: Real-time communication
- **React**: Component rendering
- **useEffect**: Connection lifecycle

**Implementation**:

```typescript
useEffect(() => {
  const ws = new WebSocket("ws://localhost:8000/ws/logs");

  ws.onmessage = (event) => {
    setLogs((prevLogs) => [...prevLogs, event.data]);
  };

  return () => ws.close();
}, []);
```

---

## Configuration Files

### `.env`

**Purpose**: Environment variable storage  
**Security**: Never committed to git  
**Contents**: API keys, URLs, configuration flags

### `requirements.txt`

**Purpose**: Python dependencies specification  
**Format**: Package names with versions  
**Usage**: `pip install -r requirements.txt`

### `package.json`

**Purpose**: Node.js project configuration  
**Contains**: Frontend dependencies, scripts  
**Usage**: `npm install`

### `tsconfig.json`

**Purpose**: TypeScript compiler configuration  
**Features**: Path aliases (`@/`), JSX support, strict mode

---

## Testing Files

### `tests/test_validator.py`

**Purpose**: Validator unit tests  
**Framework**: pytest  
**Coverage**: Validation rules, safety checks

### `tests/test_fix_tester.py`

**Purpose**: Fix tester unit tests  
**Tests**: Syntax validation, execution testing

---

## Utility Files

### `log_streamer.py`

**Purpose**: WebSocket log broadcasting  
**Technology**: FastAPI WebSocket  
**Pattern**: Producer-consumer

### `log_summary.py`

**Purpose**: Log aggregation and summarization  
**Output**: Error/warning/info counts

### `model_router.py`

**Purpose**: Gemini API proxy for frontend  
**Security**: Backend API key management  
**Benefit**: Keeps API keys server-side

---

For questions about specific implementation details, see the inline code comments in each file.
