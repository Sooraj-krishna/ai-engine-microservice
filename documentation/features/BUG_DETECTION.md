# Automated Bug Detection

The AI Engine Microservice includes a comprehensive multi-layered bug detection system designed to catch performance, accessibility, and runtime issues automatically.

## What It Detects

### 🚀 Performance Issues

Leveraging Google Lighthouse, we monitor Core Web Vitals:

- **First Contentful Paint (FCP)**: Alert if > 1.8s
- **Large Contentful Paint (LCP)**: Alert if > 2.5s
- **Cumulative Layout Shift (CLS)**: Alert if > 0.1
- **First Input Delay (FID)**: Alert if > 100ms

### ♿ Accessibility Violations

Using `axe-core`, we scan for WCAG compliance:

- Missing ARIA labels
- Color contrast issues
- Keyboard navigation problems
- Screen reader incompatibility

### 🐛 JavaScript Errors

Real-time monitoring of the browser console:

- Console errors
- Unhandled promise rejections
- Runtime exceptions
- Network failures (4xx/5xx responses)

### 📱 Responsive Design

Checks for mobile-friendliness:

- Mobile viewport configuration
- Touch target sizing
- Text readability on small screens

## How It Works

1. **Browser Launch**: Playwright launches a headless Chromium instance.
2. **Audit Execution**:
   - **Lighthouse**: Runs a full performance audit.
   - **Axe-core**: Injects and analyzes the DOM for accessibility.
3. **Log Monitoring**: Captures all console and network logs during the session.
4. **Aggregation**: Results are parsed, prioritized by severity, and prepared for the AI Fixer.

## Usage

**Trigger Manual Scan**:

```bash
curl -X POST http://localhost:8000/run
```

**View Results**:

```bash
curl http://localhost:8000/status
```
