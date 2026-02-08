"""
Auto-Approval Manager

Determines whether bug fixes require user approval based on severity and safety checks.
Manages configurable thresholds and maintains audit trail.
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path


class AutoApprovalManager:
    """Manages auto-approval logic for bug fixes."""
    
    def __init__(self, config_dir: str = "data/auto_approval"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.audit_file = self.config_dir / "audit.json"
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load auto-approval configuration."""
        default_config = {
            "auto_approve_severities": ["medium", "low"],  # Auto-approve medium and low
            "require_approval_severities": ["critical", "high"],  # Always require approval
            "silent_severities": ["low"],  # Don't notify user
            "notification_severities": ["medium"],  # Notify but auto-approve
            "enabled": True,  # Global enable/disable
            "max_auto_approvals_per_day": 50,  # Safety limit
            "emergency_pause": False  # Emergency pause flag
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    return {**default_config, **loaded}
            except Exception as e:
                print(f"[AUTO_APPROVAL] Error loading config: {e}, using defaults")
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict):
        """Save configuration to disk."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"[AUTO_APPROVAL] Error saving config: {e}")
    
    def should_auto_approve(self, bug_item: Dict) -> Dict:
        """
        Determine if a bug fix should be auto-approved.
        
        Args:
            bug_item: Bug item from queue
            
        Returns:
            {
                "auto_approve": bool,
                "silent": bool,  # Should execute silently without user notification
                "reason": str
            }
        """
        severity = bug_item.get("severity", "medium")
        bug_id = bug_item.get("id", "unknown")
        
        # Check if auto-approval is globally disabled
        if not self.config.get("enabled", True):
            return {
                "auto_approve": False,
                "silent": False,
                "reason": "Auto-approval globally disabled"
            }
        
        # Check emergency pause
        if self.config.get("emergency_pause", False):
            return {
                "auto_approve": False,
                "silent": False,
                "reason": "Emergency pause activated"
            }
        
        # Check daily limit
        if not self._check_daily_limit():
            return {
                "auto_approve": False,
                "silent": False,
                "reason": "Daily auto-approval limit reached"
            }
        
        # Check severity-based rules
        if severity in self.config.get("require_approval_severities", ["critical", "high"]):
            return {
                "auto_approve": False,
                "silent": False,
                "reason": f"{severity.upper()} severity always requires user approval"
            }
        
        if severity in self.config.get("auto_approve_severities", ["medium", "low"]):
            silent = severity in self.config.get("silent_severities", ["low"])
            
            # Record the approval decision
            self._record_decision(bug_id, severity, True, silent)
            
            return {
                "auto_approve": True,
                "silent": silent,
                "reason": f"{severity.upper()} severity auto-approved (silent={silent})"
            }
        
        # Default to requiring approval for unknown severities
        return {
            "auto_approve": False,
            "silent": False,
            "reason": f"Unknown severity '{severity}', requiring approval"
        }
    
    def _check_daily_limit(self) -> bool:
        """Check if daily auto-approval limit has been reached."""
        max_per_day = self.config.get("max_auto_approvals_per_day", 50)
        
        # Count today's auto-approvals
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not self.audit_file.exists():
            return True
        
        try:
            with open(self.audit_file, 'r') as f:
                audit = json.load(f)
                
            today_approvals = [
                a for a in audit 
                if a.get("date") == today and a.get("auto_approved", False)
            ]
            
            count = len(today_approvals)
            
            if count >= max_per_day:
                print(f"[AUTO_APPROVAL] Daily limit reached: {count}/{max_per_day}")
                return False
            
            return True
            
        except Exception as e:
            print(f"[AUTO_APPROVAL] Error checking daily limit: {e}")
            return True  # Allow on error (safe default)
    
    def _record_decision(self, bug_id: str, severity: str, auto_approved: bool, silent: bool):
        """Record approval decision to audit trail."""
        decision = {
            "bug_id": bug_id,
            "severity": severity,
            "auto_approved": auto_approved,
            "silent": silent,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        try:
            audit = []
            if self.audit_file.exists():
                with open(self.audit_file, 'r') as f:
                    audit = json.load(f)
            
            audit.append(decision)
            
            # Keep last 10000 decisions
            if len(audit) > 10000:
                audit = audit[-10000:]
            
            with open(self.audit_file, 'w') as f:
                json.dump(audit, f, indent=2)
                
        except Exception as e:
            print(f"[AUTO_APPROVAL] Error recording decision: {e}")
    
    def update_config(self, updates: Dict) -> Dict:
        """
        Update configuration.
        
        Args:
            updates: Dictionary of configuration updates
            
        Returns:
            Updated configuration
        """
        self.config.update(updates)
        self._save_config(self.config)
        
        print(f"[AUTO_APPROVAL] Configuration updated: {updates}")
        
        return self.config
    
    def get_config(self) -> Dict:
        """Get current configuration."""
        return self.config.copy()
    
    def get_daily_stats(self) -> Dict:
        """
        Get statistics for today's auto-approvals.
        
        Returns:
            Statistics dictionary
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        if not self.audit_file.exists():
            return {
                "date": today,
                "total": 0,
                "auto_approved": 0,
                "silent": 0,
                "requires_approval": 0
            }
        
        try:
            with open(self.audit_file, 'r') as f:
                audit = json.load(f)
            
            today_decisions = [a for a in audit if a.get("date") == today]
            
            return {
                "date": today,
                "total": len(today_decisions),
                "auto_approved": len([a for a in today_decisions if a.get("auto_approved")]),
                "silent": len([a for a in today_decisions if a.get("silent")]),
                "requires_approval": len([a for a in today_decisions if not a.get("auto_approved")])
            }
            
        except Exception as e:
            print(f"[AUTO_APPROVAL] Error getting stats: {e}")
            return {"date": today, "total": 0, "error": str(e)}
    
    def emergency_pause(self):
        """Activate emergency pause - disables all auto-approvals."""
        self.config["emergency_pause"] = True
        self._save_config(self.config)
        print("[AUTO_APPROVAL] ⚠️ EMERGENCY PAUSE ACTIVATED - All auto-approvals disabled")
    
    def resume(self):
        """Resume auto-approvals after emergency pause."""
        self.config["emergency_pause"] = False
        self._save_config(self.config)
        print("[AUTO_APPROVAL] ✅ Auto-approvals resumed")


# Global instance
auto_approval_manager = AutoApprovalManager()
