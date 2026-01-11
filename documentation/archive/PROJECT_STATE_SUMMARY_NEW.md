# Project State Summary (Updated for Dynamic Model Routing & Incremental Fixes)

## 🎯 What This Project Does
An AI-powered maintenance system that detects issues, generates incremental fixes, and ships them safely with automated validation and GitHub PRs. Now uses dynamic OpenRouter model selection and section-by-section fixing to stay within context limits and avoid rate-limit stalls.

---

## 📊 Current State

### ✅ Working End-to-End
- FastAPI backend (port 8000) + Next.js frontend (port 3000).
- Real-time logs, status dashboard, config UI.
- GitHub PR creation with rollback protection and audit trail.

### 🔍 Detection
- UI/UX: broken assets, layout issues.
- Accessibility: Axe-core when available; fallbacks included.
- Performance: Lighthouse when available; metrics fallbacks.
- Responsive and console-error checks.

### 🛠️ Fixing (Now Incremental & Context-Aware)
- Standard and Improved Fixer paths.
- Incremental, section-by-section fixes (keeps context small).
- Dynamic OpenRouter model routing with free-first priority, context filtering, and fallbacks/retries.
- Validates fixes before applying; skips dangerous changes.
- Structured outputs per section: file, section, fix snippet, status, reason, model used.

### 🔒 Safety
- Validation before apply.
- Rollback history and protection.
- Audit trail of actions and logs.

---

## 🚀 What’s New vs Previous Summary (@PROJECT_STATE_SUMMARY.md)
- **Dynamic model selection**: OpenRouter models are auto-discovered, filtered by context, prioritized free-first, and retried on rate limits/provider errors.
- **Incremental fixes**: `applyIncrementalFixes` and `processIssue` handle one section at a time with validation and logging.
- **Auto issue processing**: `autoProcessIssue` can scan the repo by path filters, build sections, and run incremental fixes with custom validation hooks.
- **User-friendly log report**: Summaries of log severity for non-technical users in the UI.

---

## 📈 Key Components
- `src/model_router.py` (Python) and `ai-engine-ui/src/lib/modelRouter.ts`: model discovery, context-based selection, free-only/fallback logic.
- `ai-engine-ui/src/lib/incrementalFixer.ts`: section-level fixing, retries, validation, structured results.
- `ai-engine-ui/src/lib/issueFixer.ts`: per-issue orchestration over provided sections/files.
- `ai-engine-ui/src/lib/autoIssueFixer.ts`: automated file discovery (by path patterns), section building, and end-to-end fixing.
- `ai-engine-ui/src/app/api/ask/route.ts`: server API for routed model calls.
- UI: LogReport for simplified, severity-tagged log summaries.

---

## 🧪 Validation & Testing
- Fixes validated before apply; unsafe fixes skipped.
- Structured E2E, accessibility (Axe), and performance (Lighthouse) when available; fallbacks otherwise.
- Section results include status/reason to keep a clear audit trail.

---

## 🎯 Suggested Next Steps
- Wire `autoProcessIssue` into the backend flow to automate issue→files→fix pipeline.
- Add visual regression testing for UI changes.
- Track fix success rates (fix pattern learning) to improve model prompts/choices.
- Add multi-model support toggle in the UI for paid/large-context options when needed.

---

## One-Sentence Update
The system now fixes issues incrementally with dynamic, free-first OpenRouter model selection, keeping context small, retrying on provider limits, and logging structured per-section results for safer, more reliable maintenance.***

