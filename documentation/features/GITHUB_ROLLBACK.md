# GitHub Integration & Rollback

The AI Engine acts as a virtual developer on your team, managing code changes via legitimate Git workflows.

## Pull Request Automation

Instead of committing directly to `main`, the AI follows best practices:

1.  **Branch Creation**: Creates a new branch (e.g., `ai-fix-nextjs-20240101`).
2.  **Commit**: Stages the generated and validated fixes.
3.  **Pull Request**: Opens a PR with a detailed description explaining **why** the change was made and **what** it does.

### PR Description Format

```markdown
## 🤖 AI-Generated Fixes

**Fixes applied**: 1

### Fix 1: Accessibility improvement

- **File**: `components/Button.tsx`
- **Issue**: Button missing aria-label
- **Solution**: Added aria-label attribute based on button text
```

## Rollback Protection

Ideally, bad code never passes validation. But if it does, the Rollback Manager is the safety net.

### Triggers

- **5xx Errors**: Spike in server errors after deployment.
- **Metric Degradation**: Accessibility score drops > 10 points or Performance drops > 15 points.
- **Critical Bugs**: Detection of new blocking bugs.

### Process

1.  **Monitoring**: The system monitors the live site immediately after a PR is merged.
2.  **Detection**: If a trigger condition is met within the monitoring window.
3.  **Action**: It automatically creates a "Revert" PR to undo the changes and notifies the team.
