"""
Bug Consolidator - Groups similar bugs to reduce duplication

This module consolidates bugs detected during maintenance cycles by grouping
similar issues together. For example, 10 "button-name" accessibility violations
across different pages become 1 consolidated bug.

Benefits:
- Reduces API token usage (fewer bugs to process)
- Generates better fixes (AI sees all affected locations together)
- Reduces maintenance cycle time
"""

from typing import List, Dict, Any
from collections import defaultdict
import json


class BugConsolidator:
    """Consolidates similar bugs into grouped bugs."""
    
    def __init__(self):
        self.consolidation_rules = {
            # Accessibility bugs are highly consolidatable
            "accessibility": {
                "group_by": ["rule_id", "severity"],
                "merge_threshold": 2,  # Merge if 2+ similar bugs
            },
            # Performance bugs can be grouped by type
            "performance": {
                "group_by": ["type", "severity"],
                "merge_threshold": 2,
            },
            # Responsive issues by breakpoint
            "responsive": {
                "group_by": ["type", "severity"],
                "merge_threshold": 2,
            },
            # Default rule for other bug types
            "default": {
                "group_by": ["type", "severity"],
                "merge_threshold": 3,  # Higher threshold for unknown types
            }
        }
    
    def consolidate(self, bugs: List[Dict]) -> List[Dict]:
        """
        Consolidate similar bugs into grouped bugs.
        
        Args:
            bugs: List of bug dictionaries
            
        Returns:
            List of consolidated bug dictionaries
        """
        if not bugs:
            return []
        
        print(f"\n[BUG_CONSOLIDATOR] ========================================")
        print(f"[BUG_CONSOLIDATOR] INPUT: {len(bugs)} bugs")
        
        # Log breakdown by type BEFORE consolidation
        type_counts_before = defaultdict(int)
        for bug in bugs:
            bug_type = bug.get("type", "unknown")
            type_counts_before[bug_type] += 1
        
        print(f"[BUG_CONSOLIDATOR] Type breakdown BEFORE:")
        for bug_type, count in sorted(type_counts_before.items(), key=lambda x: x[1], reverse=True):
            print(f"[BUG_CONSOLIDATOR]   - {bug_type}: {count}")
        
        # Group bugs by type first
        bugs_by_type = defaultdict(list)
        for bug in bugs:
            bug_type = bug.get("type", "unknown")
            bugs_by_type[bug_type].append(bug)
        
        consolidated = []
        total_merged = 0
        
        # Process each type group
        for bug_type, type_bugs in bugs_by_type.items():
            print(f"\n[BUG_CONSOLIDATOR] Processing {len(type_bugs)} {bug_type} bugs...")
            
            # Get consolidation rules for this type
            rules = self.consolidation_rules.get(bug_type, self.consolidation_rules["default"])
            print(f"[BUG_CONSOLIDATOR]   Rules: group_by={rules['group_by']}, threshold={rules['merge_threshold']}")
            
            # Group by consolidation criteria
            groups = self._group_bugs(type_bugs, rules["group_by"])
            print(f"[BUG_CONSOLIDATOR]   Found {len(groups)} unique groups")
            
            # Merge groups that meet threshold
            type_merged = 0
            for group_key, group_bugs in groups.items():
                if len(group_bugs) >= rules["merge_threshold"]:
                    # Consolidate this group
                    consolidated_bug = self._merge_bugs(group_bugs)
                    consolidated.append(consolidated_bug)
                    type_merged += len(group_bugs) - 1  # Count merged bugs
                    print(f"[BUG_CONSOLIDATOR]   ✓ Merged {len(group_bugs)} bugs into 1: {group_key[:60]}...")
                else:
                    # Keep individual bugs
                    consolidated.extend(group_bugs)
            
            total_merged += type_merged
            print(f"[BUG_CONSOLIDATOR]   {bug_type}: {len(type_bugs)} → {len(type_bugs) - type_merged} ({type_merged} merged)")
        
        # Log breakdown by type AFTER consolidation
        type_counts_after = defaultdict(int)
        for bug in consolidated:
            bug_type = bug.get("type", "unknown")
            type_counts_after[bug_type] += 1
        
        print(f"\n[BUG_CONSOLIDATOR] Type breakdown AFTER:")
        for bug_type, count in sorted(type_counts_after.items(), key=lambda x: x[1], reverse=True):
            before_count = type_counts_before[bug_type]
            reduction = before_count - count
            print(f"[BUG_CONSOLIDATOR]   - {bug_type}: {before_count} → {count} ({reduction} merged)")
        
        reduction_percent = int((len(bugs) - len(consolidated)) / len(bugs) * 100) if bugs else 0
        print(f"\n[BUG_CONSOLIDATOR] ✅ TOTAL: {len(bugs)} → {len(consolidated)} bugs ({len(bugs) - len(consolidated)} reduction, {reduction_percent}%)")
        print(f"[BUG_CONSOLIDATOR] ========================================\n")
        return consolidated
    
    def _group_bugs(self, bugs: List[Dict], group_by: List[str]) -> Dict[str, List[Dict]]:
        """
        Group bugs by specified criteria.
        
        Args:
            bugs: List of bugs to group
            group_by: List of fields to group by (e.g., ["rule_id", "severity"])
            
        Returns:
            Dictionary mapping group keys to bug lists
        """
        groups = defaultdict(list)
        
        for bug in bugs:
            # Build group key from specified fields
            key_parts = []
            
            for field in group_by:
                if field == "rule_id":
                    # Extract rule_id from data
                    value = bug.get("data", {}).get("rule_id", bug.get("type", "unknown"))
                else:
                    value = bug.get(field, "unknown")
                
                key_parts.append(str(value))
            
            group_key = "_".join(key_parts)
            groups[group_key].append(bug)
        
        return groups
    
    def _merge_bugs(self, bugs: List[Dict]) -> Dict:
        """
        Merge multiple similar bugs into one consolidated bug.
        
        Args:
            bugs: List of bugs to merge
            
        Returns:
            Consolidated bug dictionary
        """
        if not bugs:
            return None
        
        # Use first bug as template
        base_bug = bugs[0].copy()
        
        # Collect all affected files
        affected_files = []
        total_instances = 0
        
        for bug in bugs:
            # Extract file
            target_file = bug.get("target_file", "unknown")
            if target_file not in affected_files:
                affected_files.append(target_file)
            
            # Sum instances
            instances = bug.get("data", {}).get("nodes_affected", 1)
            total_instances += instances
        
        # Update base bug with consolidated info
        base_bug["affected_files"] = affected_files
        base_bug["consolidated"] = True
        base_bug["original_count"] = len(bugs)
        
        # Update description
        rule_id = base_bug.get("data", {}).get("rule_id", base_bug.get("type", "unknown"))
        base_bug["description"] = f"{base_bug.get('description', '')} (found in {len(affected_files)} file(s))"
        
        # Update data
        if "data" in base_bug:
            base_bug["data"]["nodes_affected"] = total_instances
            base_bug["data"]["files_affected"] = len(affected_files)
        
        # Choose highest severity
        severities = ["critical", "high", "medium", "low"]
        highest_severity = "low"
        for bug in bugs:
            sev = bug.get("severity", "low")
            if severities.index(sev) < severities.index(highest_severity):
                highest_severity = sev
        
        base_bug["severity"] = highest_severity
        
        return base_bug


# Singleton instance
bug_consolidator = BugConsolidator()
