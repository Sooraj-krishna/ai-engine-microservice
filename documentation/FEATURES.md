# System Features

The AI Engine Microservice is a comprehensive platform composed of several intelligent subsystems. Below is the detailed documentation for each core feature.

## 📚 Feature Documentation

| Feature                                                            | Description                                                                |
| :----------------------------------------------------------------- | :------------------------------------------------------------------------- |
| **[Automated Bug Detection](./features/BUG_DETECTION.md)**         | Multi-layered detection of performance, accessibility, and runtime issues. |
| **[AI Fix Generation](./features/AI_FIX_GENERATION.md)**           | Context-aware code repair and utility generation using Google Gemini.      |
| **[Code Validation & Safety](./features/VALIDATION.md)**           | Safety checks, syntax validation, and sandboxed execution testing.         |
| **[Competitive Analysis](./features/COMPETITIVE_ANALYSIS.md)**     | AI-driven analysis of competitor websites to identify feature gaps.        |
| **[Redis & Queue Management](./features/REDIS_QUEUE.md)**          | Background task processing, state management, and smart caching.           |
| **[GitHub Integration & Rollback](./features/GITHUB_ROLLBACK.md)** | Automated PR workflow and safety nets for reverting bad changes.           |
| **[Web UI Dashboard](./features/DASHBOARD.md)**                    | Real-time monitoring, log streaming, and system control.                   |

## Feature Flags

You can enable or disable specific features via your `.env` file:

```bash
ENABLE_COMPETITIVE_ANALYSIS=true
USE_IMPROVED_FIXER=true
TEST_FIXES_BEFORE_APPLY=true
```
