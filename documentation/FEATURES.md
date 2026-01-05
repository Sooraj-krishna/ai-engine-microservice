# Features Documentation

## Core Features

### 1. Automated Bug Detection

Comprehensive multi-layered bug detection system.

#### What It Detects

**Performance Issues**:

- Slow First Contentful Paint (FCP > 1.8s)
- Large Contentful Paint (LCP > 2.5s)
- Cumulative Layout Shift (CLS > 0.1)
- First Input Delay (FID > 100ms)

**Accessibility Violations**:

- Missing ARIA labels
- Color contrast issues
- Keyboard navigation problems
- Screen reader incompatibility

**JavaScript Errors**:

- Console errors
- Unhandled promise rejections
- Runtime exceptions
- Network failures

**Responsive Design**:

- Mobile viewport issues
- Touch target sizing
- Text readability on mobile

#### How It Works

1. Playwright launches headless browser
2. Lighthouse runs performance audit
3. Axe-core scans for accessibility issues
4. Console logs monitored for errors
5. Results aggregated and prioritized

#### Usage

```bash
# Automatic (via /run endpoint)
curl -X POST http://localhost:8000/run

# Results in system status
curl http://localhost:8000/status
```

---

### 2. AI-Powered Fix Generation

Intelligent code generation using Google Gemini.

#### Fix Types

**Bug Fixes**:

- Modifies existing code to fix bugs
- Context-aware changes
- Preserves existing functionality

**Utility Creation**:

- Creates new utility files for optimizations
- Never modifies existing critical files
- Additive improvements only

#### AI Models

- **gemini-1.5-flash**: Fast, cost-effective (recommended)
- **gemini-1.5-pro**: More accurate, slower

#### Example Fixes

**Before** (Accessibility bug):

```html
<button>Submit</button>
```

**After**:

```html
<button aria-label="Submit form">Submit</button>
```

---

### 3. Code Validation & Safety

Multi-layer validation ensures all fixes are safe.

#### Validation Layers

**1. Safety Validation**:

- No dangerous patterns (eval, exec, rm -rf)
- No modification of framework files
- No deletion of existing functions

**2. Syntax Validation**:

- JavaScript/TypeScript syntax check
- Python AST validation
- HTML structure validation

**3. Execution Testing**:

- Isolated sandbox testing
- Browser compatibility checks
- No side effects verification

#### Rejection Criteria

Fixes are rejected if they:

- Contain dangerous code patterns
- Modify vendor/node_modules files
- Have syntax errors
- Fail browser compatibility tests
- Remove existing functionality

---

### 4. Isolated Fix Testing

Fixes tested in sandbox before deployment.

#### Test Types

**Syntax Tests**:

- Node.js `--check` for JavaScript
- Python `compile()` for Python code
- Basic bracket/paren matching

**Execution Tests**:

- Run code in isolated Node.js process
- Monitor for errors and exceptions
- Verify no crashes

**Browser Tests** (if website URL provided):

- Inject fix into live page
- Check for console errors
- Verify page still loads

#### Special Handling

- Utility files skip Node.js validation (browser-only)
- TypeScript/JSX detected and handled appropriately
- HTML validation checks tag balance

---

### 5. Competitive Analysis

Analyzes competitor websites to find missing features.

#### Process

1. **Scrape Competitors**: Playwright captures screenshots
2. **Extract Features**: Gemini Vision analyzes images
3. **Compare**: Identify features your site lacks
4. **Prioritize**: Rank by frequency, impact, effort
5. **Recommend**: Present in natural language

#### Priority Scoring ((0-10)

Factors considered:

- **Frequency**: How many competitors have it
- **Business Impact**: Potential value to users
- **Implementation Effort**: Time/complexity to build
- **Category**: Type of feature

**High Priority** (7-10): Found in most competitors, high impact  
**Medium Priority** (4-6): Found in some competitors  
**Low Priority** (1-3): Found in few competitors

#### Feature Categories

- User Experience
- Performance
- Accessibility
- Security
- SEO
- Mobile Optimization
- Engagement
- Analytics

#### Example Output

```json
{
  "name": "Dark Mode",
  "category": "User Experience",
  "priority_score": 8.5,
  "found_in": ["competitor1.com", "competitor2.com"],
  "frequency": "67%",
  "estimated_effort": "1-2 days",
  "business_impact": "high"
}
```

---

### 6. Rollback Protection

Automatic monitoring and rollback if issues detected.

#### What It Monitors

- Site availability (HTTP status)
- Error rate increases
- Performance degradation
- Console error spikes

#### Rollback Triggers

- 5xx errors after deployment
- Accessibility score drops > 10 points
- Performance score drops > 15 points
- Critical bugs introduced

#### Process

1. Monitor site after each PR merge
2. Compare metrics to baseline
3. If degradation detected, create rollback PR
4. Notify team of automatic rollback

#### History Tracking

All changes tracked in `rollback_history.json`:

```json
{
  "id": 40,
  "timestamp": "2026-01-05T21:12:35",
  "type": "ai_pr",
  "pr_url": "https://github.com/user/repo/pull/123",
  "notes": "AI maintenance cycle - 3 fixes applied"
}
```

---

### 7. GitHub Integration

Automated pull request creation and management.

#### PR Creation

Each maintenance cycle creates a PR with:

- Branch: `ai-fix-{framework}-{timestamp}`
- Title: Descriptive summary
- Description: Detailed fix explanations
- Labels: Automated tagging

#### PR Description Format

```markdown
## 🤖 AI-Generated Fixes

**Fixes applied**: 3

### Fix 1: Accessibility improvement

- File: `index.html`
- Issue: Button missing aria-label
- Solution: Added aria-label attribute

### Fix 2: Performance optimization

...
```

#### Manual Review

All PRs require manual review before merging:

- Review code changes
- Run tests
- Verify fix quality
- Merge or request changes

---

### 8. Web UI Dashboard

Modern Next.js interface for monitoring and control.

#### Features

**Real-time Logs**:

- WebSocket streaming
- Color-coded log levels
- Auto-scroll option

**System Status**:

- Health indicators
- Environment check
- Dependency status

**Configuration**:

- Update settings
- Test connections
- View current config

**Bug Visualization**:

- List of detected issues
- Priority indicators
- Affected files

**Feature Recommendations**:

- Natural language summaries
- Priority cards
- Selection interface

#### Components

- `ConfigurationForm`: API connection setup
- `StatusMonitor`: System health display
- `LogsDisplay`: Real-time log streaming
- `IdentifiedBugs`: Bug list visualization
- `FeatureRecommendations`: Competitive analysis results

---

## Feature Comparison

| Feature              | Basic Mode | Enhanced Mode     |
| -------------------- | ---------- | ----------------- |
| Bug Detection        | ✅         | ✅ Enhanced       |
| AI Fix Generation    | ✅         | ✅ Improved Fixer |
| Validation           | ✅ Basic   | ✅ Multi-layer    |
| Testing              | ❌         | ✅ Sandbox        |
| Competitive Analysis | ❌         | ✅                |
| Rollback Protection  | ❌         | ✅                |
| Web UI               | ✅ Basic   | ✅ Full Dashboard |

## Upcoming Features

- **Automated Testing**: Generate test cases for fixes
- **Performance Budgets**: Set thresholds for metrics
- **Custom Rules**: Define custom validation rules
- **Slack Integration**: Notifications for PRs
- **Analytics Dashboard**: Historical metrics tracking
- **Multi-site Support**: Monitor multiple websites
- **A/B Testing**: Test fixes before full rollout

## Feature Flags

Enable/disable features via `.env`:

```bash
ENABLE_COMPETITIVE_ANALYSIS=true
USE_IMPROVED_FIXER=true
TEST_FIXES_BEFORE_APPLY=true
AUTO_RUN_COMPETITIVE_ANALYSIS=false
```

See [CONFIGURATION.md](./CONFIGURATION.md) for all options.
