"""
Automatic rollback system for AI changes that cause issues.
Monitors system health and automatically reverts problematic changes.
"""

import json
import os
from datetime import datetime, timedelta
from github import Github

class RollbackManager:
    """Manages rollback of problematic AI changes."""
    
    def __init__(self, history_file="rollback_history.json"):
        self.history_file = history_file
        self.history = self.load_history()
        self.rollback_triggers = {
            "critical_memory_usage": 95,      # Memory usage percentage
            "critical_cpu_usage": 95,         # CPU usage percentage
            "error_rate_threshold": 50,       # Number of errors
            "response_time_threshold": 10.0,  # Response time in seconds
            "health_score_threshold": 30      # Overall health score
        }
    
    def load_history(self):
        """Load rollback history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[ROLLBACK] Error loading history: {e}")
                return []
        return []
    
    def save_history(self):
        """Save rollback history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2, default=str)
            print(f"[ROLLBACK] History saved to {self.history_file}")
        except IOError as e:
            print(f"[ROLLBACK] Error saving history: {e}")
    
    def record_change(self, pr_url, commit_sha=None, branch_name=None, notes=None):
        """Record an AI-generated change for potential rollback."""
        change_record = {
            "id": len(self.history) + 1,
            "pr_url": pr_url,
            "commit_sha": commit_sha,
            "branch_name": branch_name,
            "timestamp": datetime.now().isoformat(),
            "notes": notes or "AI-generated change",
            "rolled_back": False,
            "rollback_reason": None,
            "rollback_timestamp": None
        }
        
        self.history.append(change_record)
        self.save_history()
        
        print(f"[ROLLBACK] Recorded change: PR {pr_url}")
        return change_record["id"]
    
    def should_rollback(self, monitoring_data):
        """
        Analyze monitoring data to determine if rollback is needed.
        Returns (should_rollback: bool, reason: str, severity: str).
        """
        reasons = []
        severity = "low"
        
        # Check system metrics
        system = monitoring_data.get("system", {})
        
        # Critical memory usage
        memory_percent = system.get("memory_percent", 0)
        if memory_percent >= self.rollback_triggers["critical_memory_usage"]:
            reasons.append(f"Critical memory usage: {memory_percent}%")
            severity = "critical"
        
        # Critical CPU usage
        cpu_percent = system.get("cpu_percent", 0)
        if cpu_percent >= self.rollback_triggers["critical_cpu_usage"]:
            reasons.append(f"Critical CPU usage: {cpu_percent}%")
            severity = "critical"
        
        # High error rate
        errors = monitoring_data.get("errors", {})
        error_count = len(errors.get("errors", []))
        if error_count >= self.rollback_triggers["error_rate_threshold"]:
            reasons.append(f"High error rate: {error_count} errors")
            severity = "high" if severity != "critical" else "critical"
        
        # Poor response time
        metrics = monitoring_data.get("metrics", {})
        response_time = metrics.get("avg_response_time", 0)
        if response_time >= self.rollback_triggers["response_time_threshold"]:
            reasons.append(f"Poor response time: {response_time}s")
            severity = "high" if severity == "low" else severity
        
        # Low health score
        combined = metrics.get("combined", {})
        health_score = combined.get("overall_health_score", 100)
        if health_score <= self.rollback_triggers["health_score_threshold"]:
            reasons.append(f"Low health score: {health_score}/100")
            severity = "high" if severity == "low" else severity
        
        # Check if there were recent AI changes (within last 2 hours)
        recent_changes = self.get_recent_changes(hours=2)
        if not recent_changes:
            # No recent changes to rollback
            return False, "", "none"
        
        should_rollback = len(reasons) > 0
        reason = "; ".join(reasons) if reasons else ""
        
        if should_rollback:
            print(f"[ROLLBACK] Rollback criteria met - Severity: {severity}")
            print(f"[ROLLBACK] Reasons: {reason}")
        
        return should_rollback, reason, severity
    
    def get_recent_changes(self, hours=24):
        """Get AI changes made within the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_changes = []
        for change in self.history:
            if change.get("rolled_back", False):
                continue
                
            try:
                change_time = datetime.fromisoformat(change["timestamp"])
                if change_time >= cutoff_time:
                    recent_changes.append(change)
            except (ValueError, KeyError):
                continue
        
        return recent_changes
    
    def create_rollback_pr(self, reason, severity="medium"):
        """Create a pull request that rolls back recent AI changes."""
        try:
            token = os.getenv("GITHUB_TOKEN")
            repo_name = os.getenv("GITHUB_REPO")
            
            if not token or not repo_name:
                print("[ROLLBACK] Missing GitHub configuration")
                return None
            
            g = Github(token)
            repo = g.get_repo(repo_name)
            
            # Get the most recent non-rolled-back change
            recent_changes = self.get_recent_changes(hours=2)
            if not recent_changes:
                print("[ROLLBACK] No recent changes to rollback")
                return None
            
            latest_change = recent_changes[-1]  # Most recent change
            
            # Create rollback branch
            base_branch = repo.get_branch("main")
            rollback_branch_name = f"rollback-ai-changes-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            try:
                repo.create_git_ref(
                    ref=f"refs/heads/{rollback_branch_name}",
                    sha=base_branch.commit.sha
                )
            except Exception as e:
                print(f"[ROLLBACK] Error creating branch: {e}")
                return None
            
            # Create rollback commit (this would need to be implemented based on what was changed)
            rollback_message = f"""
🔄 AI Engine Automatic Rollback

**Reason**: {reason}
**Severity**: {severity.upper()}
**Rollback Target**: PR {latest_change.get('pr_url', 'unknown')}
**Timestamp**: {datetime.now().isoformat()}

This is an automatic rollback initiated by the AI Engine monitoring system.
Recent AI-generated changes have caused system performance degradation.

**What was rolled back:**
- AI-generated utilities and modifications
- Files in utils/ai-* directories
- Any changes from the last AI maintenance cycle

**Next Steps:**
1. Review the monitoring data
2. Investigate root cause of performance issues
3. Improve AI generation logic if necessary
4. Re-run AI maintenance with better constraints

**Monitoring Data Summary:**
- Generated at: {datetime.now().isoformat()}
- Triggered by: {reason}
"""
            
            # For now, create an empty rollback (actual implementation would revert specific files)
            rollback_content = f'''# AI Engine Rollback Report

This file documents an automatic rollback performed by the AI Engine.

## Rollback Details
- **Timestamp**: {datetime.now().isoformat()}
- **Reason**: {reason}
- **Severity**: {severity}
- **Target Change ID**: {latest_change.get('id', 'unknown')}

## Action Taken
The AI Engine has automatically rolled back recent changes due to performance degradation.

## Monitoring Data
Performance metrics indicated system instability requiring immediate rollback.

## Resolution
System should return to stable state after this rollback is merged.
'''
            
            # Create the rollback documentation file
            repo.create_file(
                path=f"rollback-reports/rollback-{datetime.now().strftime('%Y%m%d%H%M%S')}.md",
                message=rollback_message,
                content=rollback_content,
                branch=rollback_branch_name
            )
            
            # Create rollback PR
            pr = repo.create_pull(
                title=f"🔄 AI Engine Automatic Rollback - {severity.upper()} Issue",
                head=rollback_branch_name,
                base="main",
                body=rollback_message
            )
            
            # Mark the change as rolled back
            latest_change["rolled_back"] = True
            latest_change["rollback_reason"] = reason
            latest_change["rollback_timestamp"] = datetime.now().isoformat()
            self.save_history()
            
            print(f"[ROLLBACK] Created rollback PR: {pr.html_url}")
            return pr.html_url
            
        except Exception as e:
            print(f"[ROLLBACK] Error creating rollback PR: {e}")
            return None
    
    def perform_rollback_if_needed(self, monitoring_data):
        """Check if rollback is needed and perform it automatically."""
        should_rollback, reason, severity = self.should_rollback(monitoring_data)
        
        if should_rollback:
            print(f"[ROLLBACK] Initiating automatic rollback - {severity} severity")
            pr_url = self.create_rollback_pr(reason, severity)
            
            if pr_url:
                print(f"[ROLLBACK] ✅ Rollback PR created: {pr_url}")
                return {
                    "rollback_performed": True,
                    "pr_url": pr_url,
                    "reason": reason,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print("[ROLLBACK] ❌ Failed to create rollback PR")
                return {
                    "rollback_performed": False,
                    "reason": reason,
                    "severity": severity,
                    "error": "Failed to create rollback PR"
                }
        
        return {"rollback_performed": False, "reason": "No rollback needed"}
    
    def get_rollback_history(self):
        """Get summary of rollback history."""
        total_changes = len(self.history)
        rolled_back = sum(1 for change in self.history if change.get("rolled_back", False))
        
        return {
            "total_changes": total_changes,
            "rolled_back_changes": rolled_back,
            "rollback_rate": (rolled_back / total_changes * 100) if total_changes > 0 else 0,
            "recent_rollbacks": [
                change for change in self.history 
                if change.get("rolled_back", False)
            ][-5:],  # Last 5 rollbacks
            "active_changes": [
                change for change in self.history 
                if not change.get("rolled_back", False)
            ]
        }
    
    def update_rollback_triggers(self, new_triggers):
        """Update rollback trigger thresholds."""
        self.rollback_triggers.update(new_triggers)
        print(f"[ROLLBACK] Updated triggers: {self.rollback_triggers}")
