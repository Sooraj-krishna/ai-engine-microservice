"""
Security Validator

Comprehensive security checks for generated code:
- XSS vulnerabilities
- Injection attacks
- Exposed secrets
- Unsafe patterns
- Dependency vulnerabilities

Author: AI Engine
Created: 2026-01-19
"""

import re
import os
from typing import Dict, List, Optional
import json


class SecurityValidator:
    """Validates code for security vulnerabilities"""
    
    def __init__(self):
        # XSS patterns
        self.xss_patterns = [
            (r'\.innerHTML\s*=\s*(?!["\']\s*$)', 'Unsafe innerHTML assignment (XSS risk)', True),
            (r'document\.write\s*\(', 'document.write() is dangerous (XSS risk)', True),
            (r'eval\s*\(', 'eval() is dangerous (code injection risk)', True),
            (r'Function\s*\(', 'Function constructor is dangerous (code injection risk)', True),
            (r'setTimeout\s*\(\s*["\']', 'setTimeout with string argument (code injection risk)', False),
            (r'setInterval\s*\(\s*["\']', 'setInterval with string argument (code injection risk)', False),
        ]
        
        # SQL Injection patterns
        self.sql_injection_patterns = [
            (r'SELECT.*FROM.*WHERE.*\+.*', 'Possible SQL injection vulnerability', True),
            (r'DELETE\s+FROM.*WHERE\s+1\s*=\s*1', 'Dangerous SQL DELETE', True),
            (r'DROP\s+TABLE', 'DROP TABLE detected', True),
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            (r'exec\s*\(', 'exec() call detected (command injection risk)', True),
            (r'system\s*\(', 'system() call detected (command injection risk)', True),
            (r'subprocess\..*shell\s*=\s*True', 'subprocess with shell=True (command injection risk)', True),
        ]
        
        # Secret patterns (API keys, tokens, credentials)
        self.secret_patterns = [
            (r'api[_-]?key\s*[:=]\s*["\'][^"\']{20,}["\']', 'Possible API key in code', True),
            (r'secret[_-]?key\s*[:=]\s*["\'][^"\']{20,}["\']', 'Possible secret key in code', True),
            (r'password\s*[:=]\s*["\'][^"\']+["\']', 'Hardcoded password detected', True),
            (r'token\s*[:=]\s*["\'][^"\']{20,}["\']', 'Possible auth token in code', True),
            (r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', 'Bearer token in code', True),
        ]
        
        # CORS/CSP patterns
        self.cors_patterns = [
            (r'Access-Control-Allow-Origin:\s*\*', 'Wildcard CORS allows requests from any origin', False),
            (r'credentials:\s*["\']include["\']', 'Credentials include with CORS may be risky', False),
        ]
        
        # Unsafe file operations
        self.file_operation_patterns = [
            (r'fs\.unlink\s*\((?!.*\.on\s*\()', 'Unprotected file deletion', False),
            (r'rm\s+-rf', 'Dangerous file deletion command', True),
            (r'__import__\s*\(', '__import__() can be exploited', False),
        ]
        
        print("[SECURITY_VALIDATOR] Initialized")
    
    async def validate(self, filepath: str, content: str) -> Dict:
        """
        Validate code for security vulnerabilities.
        
        Args:
            filepath: Path to file
            content: File content
            
        Returns:
            {
                'vulnerabilities': List[Dict],
                'warnings': List[str],
                'score': int  # Security score 0-100
            }
        """
        vulnerabilities = []
        warnings = []
        
        # Skip certain file types
        if filepath.endswith(('.json', '.md', '.txt', '.css')):
            return {
                'vulnerabilities': [],
                'warnings': [],
                'score': 100
            }
        
        # Check for XSS vulnerabilities
        for pattern, message, critical in self.xss_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'xss',
                    'message': message,
                    'line': line_num,
                    'critical': critical,
                    'pattern': pattern,
                    'fix': self._suggest_xss_fix(pattern)
                })
        
        # Check for SQL injection
        for pattern, message, critical in self.sql_injection_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'sql_injection',
                    'message': message,
                    'line': line_num,
                    'critical': critical,
                    'fix': 'Use parameterized queries or prepared statements'
                })
        
        # Check for command injection
        for pattern, message, critical in self.command_injection_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'command_injection',
                    'message': message,
                    'line': line_num,
                    'critical': critical,
                    'fix': 'Use safer alternatives or sanitize input'
                })
        
        # Check for exposed secrets
        for pattern, message, critical in self.secret_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'secret_exposure',
                    'message': message,
                    'line': line_num,
                    'critical': critical,
                    'fix': 'Move secrets to environment variables or secure vault'
                })
        
        # Check CORS issues
        for pattern, message, critical in self.cors_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                if critical:
                    vulnerabilities.append({
                        'type': 'cors',
                        'message': message,
                        'line': line_num,
                        'critical': critical,
                        'fix': 'Specify exact allowed origins'
                    })
                else:
                    warnings.append(f"Line {line_num}: {message}")
        
        # Check unsafe file operations
        for pattern, message, critical in self.file_operation_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                vulnerabilities.append({
                    'type': 'unsafe_operation',
                    'message': message,
                    'line': line_num,
                    'critical': critical,
                    'fix': 'Add proper validation and error handling'
                })
        
        # Calculate security score
        critical_count = sum(1 for v in vulnerabilities if v.get('critical', False))
        non_critical_count = len(vulnerabilities) - critical_count
        
        score = 100
        score -= critical_count * 25  # -25 points per critical vulnerability
        score -= non_critical_count * 10  # -10 points per non-critical vulnerability
        score = max(0, score)
        
        return {
            'vulnerabilities': vulnerabilities,
            'warnings': warnings,
            'score': score
        }
    
    def _suggest_xss_fix(self, pattern: str) -> str:
        """Suggest fix for XSS vulnerability"""
        if 'innerHTML' in pattern:
            return 'Use textContent instead of innerHTML, or sanitize HTML with DOMPurify'
        elif 'document.write' in pattern:
            return 'Use modern DOM methods like createElement and appendChild'
        elif 'eval' in pattern:
            return 'Avoid eval(); use JSON.parse() for JSON or refactor code'
        elif 'Function' in pattern:
            return 'Avoid Function constructor; use regular function declarations'
        else:
            return 'Sanitize all user input before use'
    
    async def check_dependencies(self, package_json_path: str = None, requirements_txt_path: str = None) -> Dict:
        """
        Check dependencies for known vulnerabilities.
        
        This is a placeholder - in production, you'd integrate with:
        - npm audit for JavaScript
        - safety or pip-audit for Python
        """
        warnings = []
        
        # Check package.json if provided
        if package_json_path and os.path.exists(package_json_path):
            warnings.append("Dependency scanning not implemented - consider running 'npm audit'")
        
        # Check requirements.txt if provided
        if requirements_txt_path and os.path.exists(requirements_txt_path):
            warnings.append("Dependency scanning not implemented - consider running 'safety check'")
        
        return {
            'vulnerabilities': [],
            'warnings': warnings,
            'score': 100
        }


# Global instance
security_validator = SecurityValidator()
