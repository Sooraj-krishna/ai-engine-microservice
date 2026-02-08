"""
Bug Severity Classifier

Classifies bugs into severity levels using AI-based analysis OR rule-based classification.
Determines which bugs require user approval vs. auto-approval.

Configuration:
- Set USE_AI_CLASSIFICATION=false in .env to use rule-based only (saves API tokens)
- Rule-based classification is quite accurate for most common bugs
"""

import os
from typing import Dict, List, Optional
from enum import Enum
from model_router import _query_gemini_api
import json


# Configuration: Set to False to save API tokens
USE_AI_CLASSIFICATION = os.getenv("USE_AI_CLASSIFICATION", "false").lower() == "true"


class BugSeverity(Enum):
    """Bug severity levels."""
    CRITICAL = "critical"  # Security, data loss, crashes - ALWAYS show user
    HIGH = "high"          # Broken features, major UX issues - Show user
    MEDIUM = "medium"      # Performance issues, minor bugs - Auto-approve with notification
    LOW = "low"            # Code cleanup, optimizations - Auto-approve silently


class BugClassifier:
    """Classifies bugs by severity and groups similar bugs together."""
    
    def __init__(self):
        self.classification_history = []
    
    def classify_bugs(self, bugs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Classify a list of bugs by severity.
        
        Args:
            bugs: List of bug dictionaries from analyzer
            
        Returns:
            Dictionary mapping severity to list of bugs:
            {
                "critical": [...],
                "high": [...],
                "medium": [...],
                "low": [...]
            }
        """
        if not bugs:
            return {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }
        
        print(f"[BUG_CLASSIFIER] Classifying {len(bugs)} bugs by severity...")
        
        classified = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for bug in bugs:
            try:
                severity = self._classify_single_bug(bug)
                classified[severity].append({
                    **bug,
                    "severity": severity,
                    "requires_approval": severity in ["critical", "high"]
                })
                print(f"[BUG_CLASSIFIER] Bug '{bug.get('type', 'unknown')}' classified as {severity.upper()}")
            except Exception as e:
                print(f"[BUG_CLASSIFIER] Classification failed for bug, defaulting to MEDIUM: {e}")
                # Default to medium severity with approval required on error
                classified["medium"].append({
                    **bug,
                    "severity": "medium",
                    "requires_approval": True
                })
        
        # Log summary
        total = sum(len(bugs) for bugs in classified.values())
        print(f"[BUG_CLASSIFIER] Classification complete:")
        print(f"[BUG_CLASSIFIER]   CRITICAL: {len(classified['critical'])} (user approval required)")
        print(f"[BUG_CLASSIFIER]   HIGH: {len(classified['high'])} (user approval required)")
        print(f"[BUG_CLASSIFIER]   MEDIUM: {len(classified['medium'])} (auto-approve with notification)")
        print(f"[BUG_CLASSIFIER]   LOW: {len(classified['low'])} (auto-approve silently)")
        
        return classified
    
    def _classify_single_bug(self, bug: Dict) -> str:
        """
        Classify a single bug using rule-based classification.
        Only uses AI if USE_AI_CLASSIFICATION=true and rule-based is uncertain.
        
        Args:
            bug: Bug dictionary with type, description, etc.
            
        Returns:
            Severity level: "critical", "high", "medium", or "low"
        """
        bug_type = bug.get("type", "unknown")
        description = bug.get("description", "")
        
        # Try enhanced rule-based classification first
        severity = self._rule_based_classification(bug_type, description)
        
        if severity:
            print(f"[CLASSIFIER] ✅ Rule-based: {severity.upper()}")
            return severity
        
        # If rule-based is uncertain, check if AI is enabled
        if USE_AI_CLASSIFICATION:
            print(f"[CLASSIFIER] Uncertain, using AI...")
            try:
                return self._ai_classification(bug)
            except Exception as e:
                print(f"[CLASSIFIER] AI failed: {e}, using fallback")
                return self._fallback_classification(bug_type)
        else:
            print(f"[CLASSIFIER] 💰 AI disabled (saving tokens), using fallback")
            return self._fallback_classification(bug_type)
    
    def _rule_based_classification(self, bug_type: str, description: str) -> Optional[str]:
        """
        Enhanced rule-based classification for high accuracy without AI.
        
        Returns:
            Severity level or None if uncertain
        """
        bug_type_lower = bug_type.lower()
        desc_lower = description.lower()
        combined = f"{bug_type_lower} {desc_lower}"
        
        # CRITICAL: Security, data loss, crashes, authentication
        critical_keywords = [
            # Security
            "security", "vulnerability", "injection", "xss", "csrf", "sql injection",
            "exposed", "credentials", "password", "authentication bypass", "unauthorized",
            "privilege escalation", "remote code execution", "rce",
            # Data & System
            "data loss", "data corruption", "database", "crash", "critical error",
            "system down", "server crash", "memory leak", "infinite loop",
            "deadlock", "race condition",
            # Access & Auth
            "cannot login", "auth failed", "session expired", "token invalid"
        ]
        
        for keyword in critical_keywords:
            if keyword in combined:
                print(f"[CLASSIFIER] CRITICAL keyword matched: '{keyword}'")
                return "critical"
        
        # HIGH: Broken core functionality, major errors
        high_keywords = [
            # Functionality
            "broken", "not working", "doesn't work", "failed", "fails",
            "error", "exception", "cannot access", "cannot load",
            # HTTP/API errors
            "404", "500", "502", "503", "timeout", "connection refused",
            # UI/UX critical
            "page not loading", "blank page", "white screen", "stuck",
            "frozen", "unresponsive", "not responding",
            # Build/Deploy
            "build failed", "deployment failed", "compilation error"
        ]
        
        for keyword in high_keywords:
            if keyword in combined:
                print(f"[CLASSIFIER] HIGH keyword matched: '{keyword}'")
                return "high"
        
        # LOW: Code quality, style, cleanup, minor improvements
        low_keywords = [
            # Code quality
            "code cleanup", "dead code", "unused", "duplicate code",
            "refactor", "optimize", "simplify",
            # Style & formatting
            "formatting", "indentation", "whitespace", "spacing",
            "typo", "comment", "documentation", "docstring",
            # Linting
            "lint", "eslint", "prettier", "style guide",
            # Minor improvements
            "console.log", "debug statement", "todo", "fixme"
        ]
        
        for keyword in low_keywords:
            if keyword in combined:
                print(f"[CLASSIFIER] LOW keyword matched: '{keyword}'")
                return "low"
        
        # MEDIUM: Performance, warnings, minor issues (default for unclear cases)
        medium_keywords = [
            "performance", "slow", "latency", "delay", "loading time",
            "warning", "deprecated", "outdated", "minor bug",
            "inconsistent", "incorrect", "missing", "improvement",
            "enhancement", "ui issue", "styling issue", "alignment"
        ]
        
        for keyword in medium_keywords:
            if keyword in combined:
                print(f"[CLASSIFIER] MEDIUM keyword matched: '{keyword}'")
                return "medium"
        
        # Pattern-based classification
        # Critical patterns
        if any(word in combined for word in ["can't", "cannot", "unable to"]) and \
           any(word in combined for word in ["login", "access", "auth", "sign in"]):
            print(f"[CLASSIFIER] CRITICAL pattern: authentication failure")
            return "critical"
        
        # High patterns  
        if "error" in combined and any(word in combined for word in ["page", "component", "feature"]):
            print(f"[CLASSIFIER] HIGH pattern: feature error")
            return "high"
        
        # If bug_type suggests severity
        if "critical" in bug_type_lower or "severe" in bug_type_lower:
            return "critical"
        if "major" in bug_type_lower or "important" in bug_type_lower:
            return "high"
        if "minor" in bug_type_lower or "trivial" in bug_type_lower:
            return "low"
        
        return None  # Uncertain, will default to medium in fallback
    
    def _ai_classification(self, bug: Dict) -> str:
        """
        Use AI to classify bug severity.
        
        Args:
            bug: Bug dictionary
            
        Returns:
            Severity level: "critical", "high", "medium", or "low"
        """
        prompt = f"""You are a bug severity classification system. Analyze the following bug and classify it into one severity level.

Bug Type: {bug.get('type', 'unknown')}
Description: {bug.get('description', '')}
Impact: {bug.get('impact', '')}
Affected Area: {bug.get('file', 'unknown')}

Severity Levels:
1. CRITICAL - Security vulnerabilities, data loss, crashes, authentication bypass, exposed credentials
2. HIGH - Broken core features, major UX issues, errors preventing user actions
3. MEDIUM - Performance issues, minor bugs, non-critical errors
4. LOW - Code cleanup, optimizations, style issues, unused code, formatting

Respond with ONLY a JSON object in this exact format (no markdown, no additional text):
{{
    "severity": "critical|high|medium|low",
    "confidence": 0.95,
    "reasoning": "brief explanation"
}}

Consider:
- User impact (how many users affected?)
- Business impact (does it prevent core functionality?)
- Security risk (any security implications?)
- Urgency (how soon must this be fixed?)
"""
        
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = _query_gemini_api(messages=messages, timeout=20)
            
            # Extract content
            content = response.get("content") or response.get("response", "")
            
            # Parse JSON response
            import re
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()
            
            result = json.loads(content)
            severity = result.get("severity", "medium").lower()
            
            # Validate severity
            if severity not in ["critical", "high", "medium", "low"]:
                print(f"[BUG_CLASSIFIER] Invalid severity '{severity}', defaulting to medium")
                return "medium"
            
            print(f"[BUG_CLASSIFIER] AI classified as {severity.upper()} (confidence: {result.get('confidence', 0)})")
            print(f"[BUG_CLASSIFIER] Reasoning: {result.get('reasoning', '')}")
            
            return severity
            
        except Exception as e:
            print(f"[BUG_CLASSIFIER] AI classification error: {e}")
            raise
    
    def _fallback_classification(self, bug_type: str) -> str:
        """
        Fallback classification when AI fails.
        
        Args:
            bug_type: Type of bug
            
        Returns:
            Conservative severity (defaults to medium)
        """
        bug_type_lower = bug_type.lower()
        
        if "security" in bug_type_lower or "critical" in bug_type_lower:
            return "critical"
        elif "performance" in bug_type_lower or "slow" in bug_type_lower:
            return "medium"
        elif "style" in bug_type_lower or "cleanup" in bug_type_lower:
            return "low"
        else:
            # Default to medium (safe choice - gets notification but auto-approved)
            return "medium"
    
    def group_similar_bugs(self, bugs: List[Dict]) -> List[List[Dict]]:
        """
        Group similar bugs together for batch processing.
        
        Args:
            bugs: List of classified bugs
            
        Returns:
            List of bug groups (each group is a list of similar bugs)
        """
        if not bugs:
            return []
        
        # Simple grouping by type for now
        groups_dict = {}
        for bug in bugs:
            bug_type = bug.get("type", "unknown")
            if bug_type not in groups_dict:
                groups_dict[bug_type] = []
            groups_dict[bug_type].append(bug)
        
        groups = list(groups_dict.values())
        
        print(f"[BUG_CLASSIFIER] Grouped {len(bugs)} bugs into {len(groups)} groups")
        for i, group in enumerate(groups, 1):
            print(f"[BUG_CLASSIFIER] Group {i}: {len(group)} bugs of type '{group[0].get('type', 'unknown')}'")
        
        return groups


# Global instance
bug_classifier = BugClassifier()
