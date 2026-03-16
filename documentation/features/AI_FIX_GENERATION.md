# AI-Powered Fix Generation

The core of the microservice is its ability to automatically generate code fixes for detected issues using Google's Gemini AI.

## How It Works

The system passes detected bugs matches them with the relevant source code, and constructs a context-aware prompt for the AI.

### Fix Types

#### 1. Bug Fixes

- **Target**: Existing files.
- **Action**: Modifies specific lines to resolve the issue (e.g., adding an `aria-label` or fixing a syntax error).
- **Safety**: Uses AST parsing to ensure only the intended function or component is modified.

#### 2. Utility Creation

- **Target**: New files (e.g., `utils/performance.ts`).
- **Action**: Creates helper functions for optimizations like debouncing, lazy loading, or memoization.
- **Philosophy**: Additive changes are safer than modifying complex existing logic.

## AI Models

We utilize the Gemini family of models:

- **gemini-1.5-flash**: The default workhorse. Fast and cost-effective for most fixes.
- **gemini-1.5-pro**: Used for complex logic or "Ultra Analysis" mode where deeper reasoning is required.

## Example

**Issue**: Accessibility violation on a button.

**Before**:

```html
<button>Submit</button>
```

**AI Fix**:

```html
<button aria-label="Submit form">Submit</button>
```
