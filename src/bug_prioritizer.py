"""
Bug Prioritizer - Smart bug prioritization based on impact and effort.
Helps users focus on high-value fixes first.
"""

from typing import Dict, List
import re


class BugPrioritizer:
    """Prioritizes bugs based on impact, effort, and user value."""
    
    def __init__(self):
        # Impact weights
        self.severity_weights = {
            "critical": 10,
            "high": 7,
            "medium": 4,
            "low": 2
        }
        
        # Effort estimates (in hours)
        self.effort_estimates = {
            "accessibility": 0.5,
            "performance": 2,
            "responsive": 1,
            "javascript_error": 3,
            "incomplete_code": 1
        }
    
    def prioritize_bugs(self, bugs: List[Dict]) -> List[Dict]:
        """
        Prioritize bugs by calculating priority score.
        
        Priority Score = (Impact × User Reach) / Effort
        
        Returns:
            Sorted list of bugs with priority scores and recommendations
        """
        if not bugs:
            return []
        
        print(f"[BUG_PRIORITIZER] Prioritizing {len(bugs)} bugs...")
        
        prioritized = []
        
        for bug in bugs:
            # Calculate impact
            impact = self._calculate_impact(bug)
            
            # Estimate effort
            effort = self._estimate_effort(bug)
            
            # Calculate user reach (how many users affected)
            user_reach = self._estimate_user_reach(bug)
            
            # Calculate priority score
            priority_score = (impact * user_reach) / max(effort, 0.1)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(bug, impact, effort, priority_score)
            
            prioritized.append({
                **bug,
                "priority_score": round(priority_score, 2),
                "impact": impact,
                "effort_hours": effort,
                "user_reach_percentage": user_reach,
                "recommendation": recommendation,
                "one_click_fix": effort < 1  # Can be fixed in < 1 hour
            })
        
        # Sort by priority score (highest first)
        prioritized.sort(key=lambda x: x["priority_score"], reverse=True)
        
        print(f"[BUG_PRIORITIZER] Top priority: {prioritized[0]['description']} (score: {prioritized[0]['priority_score']})")
        
        return prioritized
    
    def _calculate_impact(self, bug: Dict) -> float:
        """Calculate bug impact (0-10 scale)."""
        severity = bug.get("severity", "medium").lower()
        bug_type = bug.get("type", "").lower()
        
        # Base impact from severity
        impact = self.severity_weights.get(severity, 4)
        
        # Adjust based on bug type
        if "accessibility" in bug_type:
            impact *= 1.2  # Accessibility is important
        elif "performance" in bug_type:
            impact *= 1.3  # Performance affects all users
        elif "security" in bug_type:
            impact *= 1.5  # Security is critical
        
        return min(impact, 10)  # Cap at 10
    
    def _estimate_effort(self, bug: Dict) -> float:
        """Estimate effort in hours."""
        bug_type = bug.get("type", "").lower()
        
        # Get base estimate
        effort = self.effort_estimates.get(bug_type, 2)
        
        # Adjust based on description complexity
        description = bug.get("description", "").lower()
        if "missing" in description:
            effort *= 0.5  # Adding missing things is usually easier
        elif "refactor" in description or "rewrite" in description:
            effort *= 2  # Refactoring takes longer
        
        return effort
    
    def _estimate_user_reach(self, bug: Dict) -> float:
        """Estimate percentage of users affected (0-100)."""
        bug_type = bug.get("type", "").lower()
        
        # Default user reach by type
        user_reach_map = {
            "accessibility": 15,  # ~15% of users need accessibility features
            "performance": 100,   # All users affected by performance
            "responsive": 50,     # ~50% mobile users
            "javascript_error": 80,  # Most users hit JS errors
            "incomplete_code": 30   # Depends on feature usage
        }
        
        return user_reach_map.get(bug_type, 50)
    
    def _generate_recommendation(self, bug: Dict, impact: float, effort: float, priority: float) -> str:
        """Generate actionable recommendation."""
        if priority > 50:
            return f"🔴 Critical: Fix immediately! High impact ({impact:.1f}/10) affecting {self._estimate_user_reach(bug):.0f}% of users, only {effort:.1f}h effort"
        elif priority > 20:
            return f"🟡 Important: Fix soon. Medium-high impact ({impact:.1f}/10), {effort:.1f}h effort"
        elif priority > 10:
            return f"🟢 Nice to have: Fix when possible. Impact: {impact:.1f}/10, Effort: {effort:.1f}h"
        else:
            return f"⚪ Low priority: Consider deferring. Low impact ({impact:.1f}/10) or high effort ({effort:.1f}h)"
    
    def get_summary(self, prioritized_bugs: List[Dict]) -> Dict:
        """Get summary of prioritized bugs."""
        if not prioritized_bugs:
            return {}
        
        return {
            "total_bugs": len(prioritized_bugs),
            "critical_priority": len([b for b in prioritized_bugs if b["priority_score"] > 50]),
            "high_priority": len([b for b in prioritized_bugs if 20 < b["priority_score"] <= 50]),
            "medium_priority": len([b for b in prioritized_bugs if 10 < b["priority_score"] <= 20]),
            "low_priority": len([b for b in prioritized_bugs if b["priority_score"] <= 10]),
            "one_click_fixes": len([b for b in prioritized_bugs if b.get("one_click_fix", False)]),
            "top_bug": prioritized_bugs[0]["description"] if prioritized_bugs else None,
            "estimated_total_effort": sum(b["effort_hours"] for b in prioritized_bugs)
        }


# Global bug prioritizer instance
bug_prioritizer = BugPrioritizer()
