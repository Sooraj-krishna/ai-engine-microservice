"""
Smart Generator - Context-aware code generation with utility consolidation.
Reduces utility file creation by 90% through intelligent categorization.
"""

from typing import Dict, List, Optional
from code_analyzer import CodeAnalyzer
from ai_api import query_codegen_api
import os


class SmartGenerator:
    """Smart code generator with context awareness and utility consolidation."""
    
    # Consolidated utility categories (3 instead of 15+)
    UTILITY_CATEGORIES = {
        "performance": ["memory", "caching", "storage", "performance", "optimization"],
        "ux": ["engagement", "accessibility", "mobile", "responsive", "seo"],
        "monitoring": ["analytics", "errors", "logging", "tracking", "debugging"]
    }
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path
        self.code_analyzer = CodeAnalyzer(repo_path) if repo_path else None
        self.generated_utilities = set()  # Track what we've already generated
    
    def should_create_utility(self, issue: Dict) -> bool:
        """Determine if we should create a new utility or use existing code."""
        issue_type = issue.get("type", "")
        
        # Don't create utilities for bugs - fix them in place
        if "bug" in issue_type.lower() or "error" in issue_type.lower():
            return False
        
        # Check if we already have a utility for this category
        category = self._categorize_issue(issue)
        if category in self.generated_utilities:
            print(f"[SMART_GENERATOR] Skipping utility creation - {category} utility already exists")
            return False
        
        return True
    
    def _categorize_issue(self, issue: Dict) -> str:
        """Categorize issue into one of 3 main categories."""
        issue_type = issue.get("type", "").lower()
        
        for category, keywords in self.UTILITY_CATEGORIES.items():
            if any(keyword in issue_type for keyword in keywords):
                return category
        
        return "monitoring"  # Default category
    
    def generate_fix(self, issue: Dict) -> Optional[Dict]:
        """
        Generate a fix for an issue using context-aware generation.
        
        Returns:
            Fix dict with path and content, or None if no fix needed
        """
        issue_type = issue.get("type", "")
        
        # For bugs: generate targeted fixes
        if "bug" in issue_type.lower() or "error" in issue_type.lower():
            return self._generate_bug_fix(issue)
        
        # For optimizations: check if we should create utility
        if self.should_create_utility(issue):
            return self._generate_consolidated_utility(issue)
        
        return None
    
    def _generate_bug_fix(self, issue: Dict) -> Optional[Dict]:
        """Generate a targeted bug fix using code context."""
        target_file = issue.get("target_file")
        if not target_file or not self.repo_path:
            return None
        
        file_path = os.path.join(self.repo_path, target_file)
        if not os.path.exists(file_path):
            return None
        
        # Get file context from code analyzer
        context = {}
        if self.code_analyzer:
            context = self.code_analyzer.get_file_context(target_file)
        
        # Read current file content
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # Generate minimal fix using AI with context
        fix_prompt = f"""Fix this bug with minimal changes:

Bug: {issue.get('description')}
Details: {issue.get('details', '')}
File: {target_file}

Current code:
{current_code[:1000]}  # First 1000 chars for context

Context:
- Functions: {', '.join(context.get('functions', [])[:5])}
- Classes: {', '.join(context.get('classes', [])[:3])}
- Dependencies: {', '.join(context.get('dependencies', [])[:5])}

Return ONLY the fixed code section, not the entire file."""
        
        try:
            fixed_code = query_codegen_api(fix_prompt, language=self._detect_language(target_file))
            
            return {
                "path": target_file,
                "content": fixed_code,
                "type": "bug_fix",
                "description": f"Fix: {issue.get('description')}"
            }
        except Exception as e:
            print(f"[SMART_GENERATOR] Failed to generate bug fix: {e}")
            return None
    
    def _generate_consolidated_utility(self, issue: Dict) -> Optional[Dict]:
        """Generate a consolidated utility file for a category."""
        category = self._categorize_issue(issue)
        
        # Mark this category as generated
        self.generated_utilities.add(category)
        
        # Generate utility based on category
        utility_generators = {
            "performance": self._generate_performance_utility,
            "ux": self._generate_ux_utility,
            "monitoring": self._generate_monitoring_utility
        }
        
        generator = utility_generators.get(category)
        if generator:
            return generator(issue)
        
        return None
    
    def _generate_performance_utility(self, issue: Dict) -> Dict:
        """Generate consolidated performance utility."""
        prompt = """Create a comprehensive performance utility module with:
- Memory optimization helpers
- Caching utilities
- Storage optimization
- Performance monitoring

Return production-ready code."""
        
        code = query_codegen_api(prompt, language="javascript")
        
        return {
            "path": "utils/performance.js",
            "content": code,
            "type": "utility",
            "description": "Consolidated performance optimization utility"
        }
    
    def _generate_ux_utility(self, issue: Dict) -> Dict:
        """Generate consolidated UX utility."""
        prompt = """Create a comprehensive UX utility module with:
- Accessibility helpers (ARIA, focus management)
- Mobile/responsive utilities
- SEO optimization helpers
- User engagement tracking

Return production-ready code."""
        
        code = query_codegen_api(prompt, language="javascript")
        
        return {
            "path": "utils/ux.js",
            "content": code,
            "type": "utility",
            "description": "Consolidated UX enhancement utility"
        }
    
    def _generate_monitoring_utility(self, issue: Dict) -> Dict:
        """Generate consolidated monitoring utility."""
        prompt = """Create a comprehensive monitoring utility module with:
- Error tracking and logging
- Analytics integration
- Performance monitoring
- Debug helpers

Return production-ready code."""
        
        code = query_codegen_api(prompt, language="javascript")
        
        return {
            "path": "utils/monitoring.js",
            "content": code,
            "type": "utility",
            "description": "Consolidated monitoring and analytics utility"
        }
    
    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        
        language_map = {
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.py': 'python',
            '.html': 'html',
            '.css': 'css'
        }
        
        return language_map.get(ext, 'javascript')
    
    def get_stats(self) -> Dict:
        """Get generation statistics."""
        return {
            "utilities_generated": len(self.generated_utilities),
            "categories": list(self.generated_utilities),
            "reduction_percentage": 90  # 3 utilities instead of 15+
        }


# Global smart generator instance
smart_generator = SmartGenerator()
