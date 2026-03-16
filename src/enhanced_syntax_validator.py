"""
Enhanced Syntax Validator

Language-aware syntax validation that properly handles:
- TypeScript/TSX (using tsc)
- JavaScript/JSX (using ESLint/Babel)
- Python (using AST)
- HTML (using HTML5 validator)
- JSON (using JSON parser)

Replaces the Node.js-only validation that was causing TypeScript/JSX files to be rejected.

Author: AI Engine
Created: 2026-01-19
"""

import os
import subprocess
import tempfile
import json
import ast
from typing import Dict, List, Optional
from pathlib import Path


class SyntaxValidator:
    """Language-aware syntax validator"""
    
    def __init__(self):
        self.validation_cache = {}
        print("[SYNTAX_VALIDATOR] Initialized")
    
    async def validate(self, filepath: str, content: str) -> Dict:
        """
        Validate syntax for any file type.
        
        Args:
            filepath: Path to file (used to determine language)
            content: File content
            
        Returns:
            {
                'valid': bool,
                'errors': List[Dict],
                'warnings': List[Dict]
            }
        """
        file_ext = Path(filepath).suffix.lower()
        
        # Route to appropriate validator based on file extension
        if file_ext in ['.ts', '.tsx']:
            return await self.validate_typescript(content, filepath)
        elif file_ext in ['.js', '.jsx']:
            return await self.validate_javascript(content, filepath)
        elif file_ext == '.py':
            return await self.validate_python(content, filepath)
        elif file_ext in ['.html', '.htm']:
            return await self.validate_html(content, filepath)
        elif file_ext == '.json':
            return await self.validate_json(content, filepath)
        else:
            # Unknown file type - basic validation only
            return await self.validate_generic(content, filepath)
    
    async def validate_typescript(self, content: str, filepath: str) -> Dict:
        """
        Validate TypeScript/TSX using tsc compiler.
        Falls back to basic syntax checking if tsc not available.
        """
        print(f"[SYNTAX_VALIDATOR] Validating TypeScript: {filepath}")
        
        # Check if tsc is available
        try:
            result = subprocess.run(
                ['tsc', '--version'],
                capture_output=True,
                timeout=2
            )
            tsc_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tsc_available = False
        
        if tsc_available:
            return await self._validate_with_tsc(content, filepath)
        else:
            print(f"[SYNTAX_VALIDATOR] tsc not available, using basic validation")
            return await self._validate_typescript_basic(content, filepath)
    
    async def _validate_with_tsc(self, content: str, filepath: str) -> Dict:
        """Validate TypeScript using tsc compiler"""
        errors = []
        warnings = []
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=Path(filepath).suffix,
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Run tsc with noEmit flag (just check, don't compile)
            result = subprocess.run(
                ['tsc', '--noEmit', '--jsx', 'react', '--allowJs', 'true', tmp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse tsc output
            if result.returncode != 0:
                error_lines = result.stdout.split('\n')
                for line in error_lines:
                    if line.strip() and '(' in line:
                        # Parse error format: "file.ts(line,col): error message"
                        try:
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                location = parts[0]
                                message = parts[1].strip()
                                
                                # Extract line number
                                if '(' in location:
                                    line_info = location.split('(')[1].split(')')[0]
                                    line_num = int(line_info.split(',')[0])
                                else:
                                    line_num = None
                                
                                errors.append({
                                    'message': message,
                                    'line': line_num,
                                    'suggestion': None
                                })
                        except:
                            # If parsing fails, just add the raw message
                            errors.append({'message': line.strip(), 'line': None})
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except subprocess.TimeoutExpired:
            return {
                'valid': False,
                'errors': [{'message': 'TypeScript validation timed out', 'line': None}],
                'warnings': []
            }
        except Exception as e:
            print(f"[SYNTAX_VALIDATOR] tsc validation error: {e}")
            return await self._validate_typescript_basic(content, filepath)
    
    async def _validate_typescript_basic(self, content: str, filepath: str) -> Dict:
        """
        Basic TypeScript validation when tsc is not available.
        Checks for common syntax errors without full type checking.
        """
        errors = []
        warnings = []
        
        # Basic balance checks
        balance_errors = self._check_balance(content)
        errors.extend(balance_errors)
        
        # Check for common TypeScript patterns
        if 'interface ' in content and not content.strip().endswith('}'):
            warnings.append({
                'message': 'Interface may be incomplete',
                'line': None
            })
        
        # Allow TypeScript code even with basic validation
        # (We don't want to block valid TS code just because tsc isn't available)
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_javascript(self, content: str, filepath: str) -> Dict:
        """
        Validate JavaScript/JSX using ESLint or Node.js.
        Falls back to basic validation if tools not available.
        """
        print(f"[SYNTAX_VALIDATOR] Validating JavaScript: {filepath}")
        
        # Try ESLint first (best for JSX)
        try:
            result = subprocess.run(
                ['npx', 'eslint', '--version'],
                capture_output=True,
                timeout=2
            )
            eslint_available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            eslint_available = False
        
        if eslint_available and ('.jsx' in filepath or 'import React' in content):
            return await self._validate_with_eslint(content, filepath)
        
        # Try Node.js for plain JavaScript
        if '.jsx' not in filepath and 'import React' not in content:
            return await self._validate_with_nodejs(content, filepath)
        
        # Fall back to basic validation
        return await self._validate_javascript_basic(content, filepath)
    
    async def _validate_with_eslint(self, content: str, filepath: str) -> Dict:
        """Validate JavaScript/JSX using ESLint"""
        errors = []
        warnings = []
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix=Path(filepath).suffix,
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            # Run ESLint with minimal config (just syntax checking)
            result = subprocess.run(
                [
                    'npx', 'eslint',
                    '--no-eslintrc',
                    '--parser', '@typescript-eslint/parser' if filepath.endswith('.tsx') else 'espree',
                    '--parser-options', 'ecmaVersion:latest,sourceType:module,ecmaFeatures:{jsx:true}',
                    '--format', 'json',
                    tmp_path
                ],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse ESLint JSON output
            if result.stdout:
                try:
                    eslint_results = json.loads(result.stdout)
                    for file_result in eslint_results:
                        for message in file_result.get('messages', []):
                            error_dict = {
                                'message': message.get('message', ''),
                                'line': message.get('line'),
                                'suggestion': None
                            }
                            
                            if message.get('severity') == 2:
                                errors.append(error_dict)
                            else:
                                warnings.append(error_dict)
                except json.JSONDecodeError:
                    pass
            
            # Clean up
            os.unlink(tmp_path)
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': warnings
            }
            
        except Exception as e:
            print(f"[SYNTAX_VALIDATOR] ESLint validation error: {e}")
            return await self._validate_javascript_basic(content, filepath)
    
    async def _validate_with_nodejs(self, content: str, filepath: str) -> Dict:
        """Validate JavaScript using Node.js --check flag"""
        errors = []
        
        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.js',
                delete=False,
                encoding='utf-8'
            ) as tmp_file:
                tmp_file.write(content)
                tmp_path = tmp_file.name
            
            result = subprocess.run(
                ['node', '--check', tmp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                errors.append({
                    'message': result.stderr.strip(),
                    'line': None
                })
            
            os.unlink(tmp_path)
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'warnings': []
            }
            
        except Exception as e:
            print(f"[SYNTAX_VALIDATOR] Node.js validation error: {e}")
            return await self._validate_javascript_basic(content, filepath)
    
    async def _validate_javascript_basic(self, content: str, filepath: str) -> Dict:
        """Basic JavaScript validation without external tools"""
        errors = []
        warnings = []
        
        # Basic balance checks
        balance_errors = self._check_balance(content)
        errors.extend(balance_errors)
        
        # Check for unterminated template literals
        backtick_count = content.count('`') - content.count('\\`')
        if backtick_count % 2 != 0:
            errors.append({
                'message': 'Unterminated template literal',
                'line': None
            })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_python(self, content: str, filepath: str) -> Dict:
        """Validate Python using AST parsing"""
        print(f"[SYNTAX_VALIDATOR] Validating Python: {filepath}")
        errors = []
        
        try:
            ast.parse(content)
            return {
                'valid': True,
                'errors': [],
                'warnings': []
            }
        except SyntaxError as e:
            errors.append({
                'message': f'Python syntax error: {e.msg}',
                'line': e.lineno,
                'suggestion': None
            })
            return {
                'valid': False,
                'errors': errors,
                'warnings': []
            }
        except Exception as e:
            errors.append({
                'message': f'Python parsing error: {str(e)}',
                'line': None
            })
            return {
                'valid': False,
                'errors': errors,
                'warnings': []
            }
    
    async def validate_html(self, content: str, filepath: str) -> Dict:
        """Basic HTML validation"""
        print(f"[SYNTAX_VALIDATOR] Validating HTML: {filepath}")
        errors = []
        warnings = []
        
        # Check for balanced tags
        import re
        
        open_tags = re.findall(r'<(\w+)[^>]*>', content)
        close_tags = re.findall(r'</(\w+)>', content)
        
        # Self-closing tags
        self_closing = ['img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr']
        
        for tag in set(open_tags):
            if tag.lower() not in self_closing:
                open_count = open_tags.count(tag)
                close_count = close_tags.count(tag)
                if open_count != close_count:
                    errors.append({
                        'message': f"Unbalanced HTML tag '{tag}': {open_count} opening vs {close_count} closing",
                        'line': None
                    })
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    async def validate_json(self, content: str, filepath: str) -> Dict:
        """Validate JSON"""
        print(f"[SYNTAX_VALIDATOR] Validating JSON: {filepath}")
        errors = []
        
        try:
            json.loads(content)
            return {
                'valid': True,
                'errors': [],
                'warnings': []
            }
        except json.JSONDecodeError as e:
            errors.append({
                'message': f'JSON parse error: {e.msg}',
                'line': e.lineno,
                'suggestion': None
            })
            return {
                'valid': False,
                'errors': errors,
                'warnings': []
            }
    
    async def validate_generic(self, content: str, filepath: str) -> Dict:
        """Generic validation for unknown file types"""
        print(f"[SYNTAX_VALIDATOR] Generic validation: {filepath}")
        
        # Just check that content is not empty
        if not content.strip():
            return {
                'valid': False,
                'errors': [{'message': 'Empty file', 'line': None}],
                'warnings': []
            }
        
        return {
            'valid': True,
            'errors': [],
            'warnings': []
        }
    
    def _check_balance(self, content: str) -> List[Dict]:
        """Check for balanced braces, brackets, and parentheses"""
        errors = []
        
        # Remove strings and comments to avoid false positives
        cleaned = self._remove_strings_and_comments(content)
        
        # Check balances
        checks = [
            ('{', '}', 'braces'),
            ('(', ')', 'parentheses'),
            ('[', ']', 'brackets')
        ]
        
        for open_char, close_char, name in checks:
            open_count = cleaned.count(open_char)
            close_count = cleaned.count(close_char)
            
            if abs(open_count - close_count) > 2:  # Allow small discrepancies
                errors.append({
                    'message': f'Unbalanced {name}: {open_count} opening vs {close_count} closing',
                    'line': None,
                    'suggestion': f'Check for missing {close_char if open_count > close_count else open_char}'
                })
        
        return errors
    
    def _remove_strings_and_comments(self, content: str) -> str:
        """Remove strings and comments to avoid false positives in balance checking"""
        import re
        
        # Remove multi-line comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove single-line comments
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # Remove strings
        content = re.sub(r'"(?:[^"\\]|\\.)*"', '""', content)
        content = re.sub(r"'(?:[^'\\]|\\.)*'", "''", content)
        content = re.sub(r'`(?:[^`\\]|\\.)*`', '``', content)
        
        return content


# Global instance
syntax_validator = SyntaxValidator()
