"""
File Integrity Checker

Validates file completeness and syntax before declaring changes "already implemented".
Prevents chatbot from exiting early when files exist but are broken/truncated.
"""

import os
import re
from typing import Tuple, Dict, Optional


class FileIntegrityChecker:
    """Checks if files are complete and syntactically valid."""
    
    def __init__(self):
        # Minimum expected file sizes (lines) for common files
        self.min_sizes = {
            'index.css': 200,  # Tailwind CSS files are typically large
            'globals.css': 100,
            'App.tsx': 50,
            'App.jsx': 50,
        }
    
    def check_file(self, filename: str, content: str, file_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check if a file is complete and valid.
        
        Args:
            filename: Name of the file
            content: File content to check
            file_path: Optional full path for additional context
            
        Returns:
            (is_valid, message) tuple
        """
        if not content or not content.strip():
            return False, "File is empty"
        
        # Check based on file type
        if filename.endswith('.css'):
            return self._check_css(filename, content)
        elif filename.endswith(('.ts', '.tsx', '.js', '.jsx')):
            return self._check_javascript(filename, content)
        elif filename.endswith('.html'):
            return self._check_html(content)
        elif filename.endswith('.json'):
            return self._check_json(content)
        
        # Unknown file type - assume valid
        return True, "OK"
    
    def _check_css(self, filename: str, content: str) -> Tuple[bool, str]:
        """Check CSS file integrity."""
        lines = content.split('\n')
        line_count = len(lines)
        
        # Check for unclosed blocks
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            return False, f"CSS has unclosed blocks: {open_braces} {{ vs {close_braces} }}"
        
        # Check if file seems truncated
        basename = os.path.basename(filename)
        if basename in self.min_sizes:
            expected_min = self.min_sizes[basename]
            if line_count < expected_min:
                return False, f"File only has {line_count} lines (expected {expected_min}+), likely truncated"
        
        # Check for incomplete rules at end
        if content.rstrip().endswith('{'):
            return False, "CSS ends with unclosed rule"
        
        # Check for common truncation patterns
        last_lines = lines[-5:] if len(lines) > 5 else lines
        for line in last_lines:
            if '...' in line or line.strip() == '':
                continue
            # If last non-empty line doesn't end properly, might be truncated
            stripped = line.strip()
            if stripped and not stripped.endswith(('}', ';', '*/')) and not stripped.startswith('/*'):
                # Could be truncated mid-property
                pass  # This is too aggressive, skip for now
        
        return True, "CSS file appears complete"
    
    def _check_javascript(self, filename: str, content: str) -> Tuple[bool, str]:
        """Check JavaScript/TypeScript file integrity."""
        lines = content.split('\n')
        line_count = len(lines)
        
        # Check for basic brace balance
        opens = content.count('{') + content.count('(') + content.count('[')
        closes = content.count('}') + content.count(')') + content.count(']')
        
        if abs(opens - closes) > 2:  # Allow small differences for template literals
            return False, f"Unbalanced braces/brackets: {opens} open vs {closes} close"
        
        # Check if file seems abnormally small
        basename = os.path.basename(filename)
        if basename in self.min_sizes:
            expected_min = self.min_sizes[basename]
            if line_count < expected_min:
                return False, f"File only has {line_count} lines (expected {expected_min}+)"
        
        # Check for incomplete syntax at end
        content_stripped = content.rstrip()
        if content_stripped.endswith(('function', 'const', 'let', 'var', 'class', 'import')):
            return False, "File ends with incomplete statement"
        
        return True, "JavaScript/TypeScript file appears complete"
    
    def _check_html(self, content: str) -> Tuple[bool, str]:
        """Check HTML file integrity."""
        # Simple tag balance check
        opening_tags = len(re.findall(r'<(\w+)[^>]*>', content))
        closing_tags = len(re.findall(r'</(\w+)>', content))
        
        # Allow some difference for self-closing tags
        if abs(opening_tags - closing_tags) > 10:
            return False, f"Unbalanced HTML tags: {opening_tags} open vs {closing_tags} close"
        
        return True, "HTML file appears complete"
    
    def _check_json(self, content: str) -> Tuple[bool, str]:
        """Check JSON file integrity."""
        import json
        try:
            json.loads(content)
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
    
    def check_file_size_change(
        self, 
        original_size: int, 
        new_size: int, 
        threshold: float = 0.5
    ) -> Tuple[bool, str]:
        """
        Check if file size change is suspiciously large.
        
        Args:
            original_size: Original file size in lines
            new_size: New file size in lines
            threshold: Max allowed reduction (0.5 = 50% reduction triggers warning)
            
        Returns:
            (is_acceptable, message) tuple
        """
        if original_size == 0:
            return True, "New file"
        
        reduction_pct = (original_size - new_size) / original_size
        
        if reduction_pct > threshold:
            return False, f"File reduced by {reduction_pct*100:.0f}% ({original_size} → {new_size} lines). Likely truncation."
        
        return True, "File size change acceptable"


# Global instance
file_integrity_checker = FileIntegrityChecker()
