"""
Enhanced Code validation system to prevent destructive changes.
Validates all AI-generated code before applying to ensure safety.
Includes context-aware validation to reduce false positives.
"""

import os
import ast
import re
import json
from datetime import datetime

class CodeValidator:
    """Enhanced validator with context-aware dangerous pattern detection."""
    
    def __init__(self):
        # Context-aware dangerous patterns (more intelligent)
        self.dangerous_patterns = [
            # Only dangerous if removing from document/window/important elements
            r'document\.body\.innerHTML\s*=\s*["\'][\'"]\s*',  # Clearing entire body
            r'document\.documentElement\.remove\(',              # Removing html element
            r'window\..*\.remove\(',                            # Removing window properties
            
            # Database/server operations
            r'DROP\s+TABLE',         # Database drops
            r'DELETE\s+FROM.*WHERE\s+1\s*=\s*1',  # Mass delete operations
            r'rm\s+-rf',            # File deletion
            r'eval\(',              # Code execution
            r'Function\(',          # Dynamic function creation
            
            # Dangerous redirects/location changes
            r'window\.location\s*=.*["\']javascript:',  # JavaScript protocol redirects
            r'document\.location\s*=.*["\']javascript:', # JavaScript protocol redirects
            
            # Mass data clearing (but allow specific item removal)
            r'localStorage\.clear\(\)',     # Clearing entire localStorage
            r'sessionStorage\.clear\(\)',   # Clearing entire sessionStorage
            
            # Dangerous DOM modifications
            r'document\.write\(',           # Document.write
            r'document\.writeln\(',         # Document.writeln
            r'\.outerHTML\s*=\s*["\'][\'"]\s*',  # Clearing outerHTML
            
            # Process/system operations
            r'process\.exit\(',             # Process termination
            r'require\(["\']child_process["\']\)',  # Child process access
        ]
        
        # Safe patterns that should NOT be flagged (whitelist)
        self.safe_patterns = [
            r'\.remove\(\)\s*;\s*}\s*\)\s*;',          # Removing created elements (safe)
            r'parentElement\.remove\(\)',               # Removing parent (safe for tips/notifications)
            r'parentNode\.removeChild\(',               # Safe DOM removal
            r'tip\..*\.remove\(',                      # Removing tip elements (safe)
            r'element\..*\.remove\(',                  # Removing specific elements (safe)
            r'this\.parentElement\.parentElement\.remove\(',  # Removing notification elements
            r'if\s*\(\s*tip\.parentNode\s*\)\s*{\s*tip\.parentNode\.removeChild\(tip\)',  # Safe conditional removal
        ]
        
        # Required safety patterns
        self.required_safety_patterns = [
            r'AI-Generated',
            r'SAFE TO USE|SAFE:|Safe to use|SAFE TO USE:',
            r'export\s+default|module\.exports',
        ]
        
        # Safe file prefixes
        self.safe_file_prefixes = [
            'utils/ai-',
            'helpers/ai-',
            'tools/ai-',
            'scripts/ai-',
            'ai-generated/',
            'utilities/ai-',
        ]
        
        self.validation_log = []
    
    def validate_fix(self, fix):
        """Enhanced validation with context awareness."""
        path = fix.get("path", "")
        content = fix.get("content", "")
        description = fix.get("description", "")
        bug = fix.get("bug", {})
        
        warnings = []
        errors = []
        
        print(f"[VALIDATOR] Validating fix for: {path}")
        
        # Determine if this is a bug fix (modifying existing file) or utility file (new file)
        # Check multiple indicators that this is a bug fix
        has_bug_field = bool(bug) and isinstance(bug, dict) and len(bug) > 0
        description_mentions_bug = 'bug' in description.lower() or 'fix for' in description.lower() or 'fixing' in description.lower()
        is_bug_fix = has_bug_field or (description_mentions_bug and not any(path.startswith(prefix) for prefix in self.safe_file_prefixes))
        
        if is_bug_fix:
            print(f"[VALIDATOR] ✅ Detected bug fix - allowing modification to existing file: {path}")
            # For bug fixes: Allow modifications to existing files, but check for dangerous patterns
            # Skip the "safe file location" check for bug fixes
            # Still validate for dangerous patterns and syntax
            
            # Check if path is reasonable (not system files, not config files)
            if self.is_dangerous_file_path(path):
                errors.append(f"Dangerous file path for bug fix: {path}")
                print(f"[VALIDATOR] ⚠️ Bug fix targets dangerous file path: {path}")
        else:
            # For utility files: Strict validation - must be in safe location
            print(f"[VALIDATOR] Detected utility file - checking safe location: {path}")
            if not self.is_safe_new_file(path):
                errors.append(f"Unsafe file location: {path}")
                print(f"[VALIDATOR] ❌ Utility file not in safe location: {path}")
        
        # 2. Enhanced dangerous pattern checking with context awareness
        dangerous_matches = self.check_dangerous_patterns_with_context(content)
        errors.extend(dangerous_matches)
        
        # 3. Check for required safety markers (only for utility files)
        if not is_bug_fix:
            safety_markers_found = 0
            safety_markers_details = []
            
            for pattern in self.required_safety_patterns:
                if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                    safety_markers_found += 1
                    safety_markers_details.append(pattern)
            
            if safety_markers_found < 2:
                warnings.append(f"Only {safety_markers_found}/3 required safety markers found: {safety_markers_details}")
        
        # 4. Enhanced syntax validation
        if path.endswith(('.js', '.jsx')):
            js_errors = self.enhanced_javascript_validation(content)
            errors.extend(js_errors)
        elif path.endswith('.py'):
            py_errors = self.validate_python_syntax(content)
            errors.extend(py_errors)
        elif path.endswith(('.html', '.htm')):
            html_errors = self.validate_html_content(content)
            errors.extend(html_errors)
        
        # 5. Check content length
        if len(content) > 50000:
            warnings.append(f"Large file: {len(content)} characters")
        
        # 6. Check for proper error handling in JS code
        if path.endswith(('.js', '.jsx')):
            if 'try' not in content and 'catch' not in content and len(content) > 1000:
                warnings.append("Large JavaScript code lacks error handling")
        
        is_safe = len(errors) == 0
        self.log_validation(path, is_safe, warnings, errors)
        
        return is_safe, warnings, errors
    
    def check_dangerous_patterns_with_context(self, content):
        """Context-aware dangerous pattern detection."""
        errors = []
        
        for pattern in self.dangerous_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Check if this is actually safe based on context
                is_actually_safe = False
                safe_reason = ""
                
                for safe_pattern in self.safe_patterns:
                    if re.search(safe_pattern, content, re.IGNORECASE):
                        is_actually_safe = True
                        safe_reason = f"matches safe pattern: {safe_pattern}"
                        print(f"[VALIDATOR] Pattern '{pattern}' found but context is safe ({safe_reason})")
                        break
                
                # Additional context checks for common false positives
                if not is_actually_safe:
                    # Check if it's removing a created element (common in utilities)
                    if 'remove(' in pattern.lower() and 'appendChild' in content:
                        is_actually_safe = True
                        safe_reason = "element creation and removal pattern detected"
                        print(f"[VALIDATOR] Pattern '{pattern}' is safe: {safe_reason}")
                
                if not is_actually_safe:
                    errors.append(f"Dangerous pattern '{pattern}': {matches}")
        
        return errors
    
    def enhanced_javascript_validation(self, content):
        """Enhanced JavaScript validation with better string handling."""
        errors = []
        
        # Remove comments and strings for more accurate validation
        cleaned_content = self.remove_js_comments_and_strings(content)
        
        # Check for balanced braces, brackets, and parentheses in cleaned content
        open_braces = cleaned_content.count('{')
        close_braces = cleaned_content.count('}')
        if open_braces != close_braces:
            difference = abs(open_braces - close_braces)
            if difference > 2:  # Allow small discrepancies due to cleaning
                errors.append(f"Significant brace imbalance: {open_braces} opening vs {close_braces} closing")
        
        open_parens = cleaned_content.count('(')
        close_parens = cleaned_content.count(')')
        if open_parens != close_parens:
            difference = abs(open_parens - close_parens)
            if difference > 2:  # Allow small discrepancies
                errors.append(f"Significant parentheses imbalance: {open_parens} opening vs {close_parens} closing")
        
        open_brackets = cleaned_content.count('[')
        close_brackets = cleaned_content.count(']')
        if open_brackets != close_brackets:
            difference = abs(open_brackets - close_brackets)
            if difference > 1:  # Allow small discrepancies
                errors.append(f"Bracket imbalance: {open_brackets} opening vs {close_brackets} closing")
        
        # Check for common syntax errors in original content (not cleaned)
        # Look for unterminated template literals
        backtick_count = content.count('`')
        escaped_backticks = content.count('\\`')
        actual_backticks = backtick_count - escaped_backticks
        
        if actual_backticks % 2 != 0:
            errors.append("Potentially unterminated template literal")
        
        # Check for function syntax issues
        if re.search(r'function\s*\(\s*\)\s*{\s*$', content, re.MULTILINE):
            errors.append("Function appears to be missing closing brace")
        
        return errors
    
    def remove_js_comments_and_strings(self, content):
        """Remove comments and strings for more accurate syntax checking."""
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remove string literals (both single and double quoted)
        # This is a simplified approach - handles most cases
        content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
        content = re.sub(r"'(?:[^'\\]|\\.)*'", "''", content)
        content = re.sub(r'`(?:[^`\\]|\\.)*`', '``', content)
        
        return content
    
    def validate_python_syntax(self, content):
        """Python syntax validation using AST parsing."""
        errors = []
        
        try:
            # Try to parse the Python code
            ast.parse(content)
            print("[VALIDATOR] Python syntax validation passed")
        except SyntaxError as e:
            errors.append(f"Python syntax error at line {e.lineno}: {e.msg}")
        except Exception as e:
            errors.append(f"Python parsing error: {str(e)}")
        
        return errors
    
    def validate_html_content(self, content):
        """Basic HTML content validation."""
        errors = []
        
        # Check for balanced HTML tags (basic check)
        open_tags = re.findall(r'<(\w+)[^>]*>', content)
        close_tags = re.findall(r'</(\w+)>', content)
        
        # Self-closing tags that don't need closing tags
        self_closing_tags = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']
        
        for tag in set(open_tags):
            if tag.lower() not in self_closing_tags:
                open_count = open_tags.count(tag)
                close_count = close_tags.count(tag)
                if open_count != close_count:
                    errors.append(f"Unbalanced HTML tag '{tag}': {open_count} opening vs {close_count} closing")
        
        return errors
    
    def is_safe_new_file(self, path):
        """Check if the path represents a new, safe utility file."""
        # Must start with one of the safe prefixes
        is_safe_prefix = any(path.startswith(prefix) for prefix in self.safe_file_prefixes)
        
        # Must not contain path traversal attempts
        has_path_traversal = '..' in path or path.startswith('/')
        
        # Must not target system files
        system_paths = ['etc/', 'var/', 'usr/', 'root/', 'home/', 'system', 'windows', 'boot/', 'dev/', 'proc/']
        is_system_file = any(system in path.lower() for system in system_paths)
        
        # Must not target important config files
        important_files = ['package.json', 'package-lock.json', '.env', 'dockerfile', 'docker-compose', 'makefile']
        targets_important_file = any(important in path.lower() for important in important_files)
        
        return is_safe_prefix and not has_path_traversal and not is_system_file and not targets_important_file
    
    def is_dangerous_file_path(self, path):
        """Check if a file path is dangerous even for bug fixes."""
        # Must not contain path traversal attempts
        has_path_traversal = '..' in path or path.startswith('/')
        
        # Must not target system files
        system_paths = ['etc/', 'var/', 'usr/', 'root/', '/home/', 'system', 'windows', 'boot/', 'dev/', 'proc/']
        is_system_file = any(system in path.lower() for system in system_paths)
        
        # Must not target critical config files (even for bug fixes)
        critical_files = ['.env', 'dockerfile', 'docker-compose', 'makefile', 'package-lock.json']
        targets_critical_file = any(critical in path.lower() for critical in critical_files)
        
        # Allow package.json modifications (sometimes needed for bug fixes)
        # But warn about it
        
        return has_path_traversal or is_system_file or targets_critical_file
    
    def validate_all_fixes(self, fixes):
        """Validate all fixes and return only safe ones."""
        safe_fixes = []
        total_fixes = len(fixes)
        
        print(f"[VALIDATOR] Validating {total_fixes} fixes with enhanced context-aware validation...")
        
        for i, fix in enumerate(fixes, 1):
            print(f"[VALIDATOR] Validating fix {i}/{total_fixes}: {fix.get('path', 'unknown')}")
            
            is_safe, warnings, errors = self.validate_fix(fix)
            
            if is_safe:
                safe_fixes.append(fix)
                print(f"[SAFE] ✅ Approved fix {i}: {fix.get('path')}")
                
                if warnings:
                    for warning in warnings:
                        print(f"[WARNING] ⚠️ {warning}")
            else:
                print(f"[REJECTED] ❌ Fix {i} rejected: {fix.get('path')}")
                for error in errors:
                    print(f"[ERROR] 🚫 {error}")
                
                # Provide suggestions for common issues
                if any('string' in error.lower() for error in errors):
                    print(f"[SUGGESTION] 💡 String balance issues often resolve automatically - consider manual review")
                
                if any('dangerous pattern' in error.lower() and 'remove' in error.lower() for error in errors):
                    print(f"[SUGGESTION] 💡 Element removal detected - ensure it's for user-created elements only")
        
        approval_rate = (len(safe_fixes) / total_fixes * 100) if total_fixes > 0 else 0
        print(f"[VALIDATOR] Enhanced validation complete: {len(safe_fixes)}/{total_fixes} fixes approved ({approval_rate:.1f}%)")
        
        # If no fixes approved, provide debugging info
        if len(safe_fixes) == 0 and total_fixes > 0:
            print(f"[DEBUG] No fixes approved. Common issues and solutions:")
            print(f"[DEBUG] - String balance: Often false positives, consider reviewing manually")
            print(f"[DEBUG] - Dangerous patterns: Check if operations are on user-created elements")
            print(f"[DEBUG] - Safety markers: Ensure 'AI-Generated' and 'SAFE TO USE' are present")
        
        return safe_fixes
    
    def log_validation(self, path, is_safe, warnings, errors):
        """Log validation results for audit purposes."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "is_safe": is_safe,
            "warnings": warnings,
            "errors": errors
        }
        
        self.validation_log.append(log_entry)
        
        # Keep only last 100 validation logs
        if len(self.validation_log) > 100:
            self.validation_log = self.validation_log[-100:]
    
    def get_validation_report(self):
        """Get a summary report of recent validations."""
        total_validations = len(self.validation_log)
        safe_validations = sum(1 for entry in self.validation_log if entry["is_safe"])
        
        recent_errors = []
        for entry in self.validation_log[-10:]:
            if not entry["is_safe"]:
                recent_errors.extend(entry["errors"])
        
        return {
            "total_validations": total_validations,
            "safe_validations": safe_validations,
            "unsafe_validations": total_validations - safe_validations,
            "approval_rate": (safe_validations / total_validations * 100) if total_validations > 0 else 0,
            "rejection_rate": ((total_validations - safe_validations) / total_validations * 100) if total_validations > 0 else 0,
            "recent_validations": self.validation_log[-10:] if self.validation_log else [],
            "common_errors": list(set(recent_errors)),
            "last_validation": self.validation_log[-1]["timestamp"] if self.validation_log else None
        }
    
    def save_validation_log(self, filename="validation_log.json"):
        """Save validation log to file for audit purposes."""
        try:
            log_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "total_entries": len(self.validation_log),
                    "validator_version": "2.0.0-enhanced"
                },
                "summary": self.get_validation_report(),
                "detailed_logs": self.validation_log
            }
            
            with open(filename, 'w') as f:
                json.dump(log_data, f, indent=2)
            print(f"[VALIDATOR] Enhanced validation log saved to {filename}")
        except Exception as e:
            print(f"[ERROR] Failed to save validation log: {e}")
    
    def update_dangerous_patterns(self, new_patterns):
        """Allow updating dangerous patterns for customization."""
        if isinstance(new_patterns, list):
            self.dangerous_patterns.extend(new_patterns)
            print(f"[VALIDATOR] Added {len(new_patterns)} new dangerous patterns")
        else:
            print(f"[ERROR] new_patterns must be a list")
    
    def update_safe_patterns(self, new_safe_patterns):
        """Allow updating safe patterns for customization."""
        if isinstance(new_safe_patterns, list):
            self.safe_patterns.extend(new_safe_patterns)
            print(f"[VALIDATOR] Added {len(new_safe_patterns)} new safe patterns")
        else:
            print(f"[ERROR] new_safe_patterns must be a list")
    
    def get_validator_stats(self):
        """Get current validator configuration stats."""
        return {
            "dangerous_patterns_count": len(self.dangerous_patterns),
            "safe_patterns_count": len(self.safe_patterns),
            "required_safety_patterns_count": len(self.required_safety_patterns),
            "safe_file_prefixes_count": len(self.safe_file_prefixes),
            "total_validations_performed": len(self.validation_log),
            "version": "2.0.0-enhanced"
        }
