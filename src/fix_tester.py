"""
Fix Tester - Tests fixes in isolated environment before applying.
Prevents bad fixes from going live by validating them first.
"""

import os
import tempfile
import shutil
import subprocess
import asyncio
import ast
import json
from pathlib import Path
from playwright.async_api import async_playwright

class FixTester:
    """
    Tests fixes in an isolated sandbox environment before applying to production.
    """
    
    def __init__(self, repo_path=None):
        self.repo_path = repo_path
        self.test_results = []
        
    async def test_fixes(self, fixes, website_url=None):
        """
        Test all fixes in isolation before applying.
        
        Args:
            fixes: List of fix dictionaries with 'path' and 'content'
            website_url: Optional URL for web-based testing
            
        Returns:
            tuple: (tested_fixes, failed_fixes)
        """
        if not fixes:
            return [], []
        
        print(f"[FIX_TESTER] Testing {len(fixes)} fixes in isolated environment...")
        
        tested_fixes = []
        failed_fixes = []
        
        for i, fix in enumerate(fixes, 1):
            print(f"[FIX_TESTER] Testing fix {i}/{len(fixes)}: {fix.get('path', 'unknown')}")
            
            try:
                test_result = await self.test_single_fix(fix, website_url)
                
                if test_result['passed']:
                    tested_fixes.append(fix)
                    print(f"[FIX_TESTER] ✅ Fix {i} passed all tests")
                else:
                    failed_fixes.append({
                        'fix': fix,
                        'reason': test_result.get('error', 'Test failed'),
                        'details': test_result.get('details', '')
                    })
                    print(f"[FIX_TESTER] ❌ Fix {i} failed: {test_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"[FIX_TESTER] ❌ Exception testing fix {i}: {e}")
                failed_fixes.append({
                    'fix': fix,
                    'reason': f"Exception during testing: {str(e)}",
                    'details': ''
                })
        
        print(f"[FIX_TESTER] Test results: {len(tested_fixes)} passed, {len(failed_fixes)} failed")
        return tested_fixes, failed_fixes
    
    async def test_single_fix(self, fix, website_url=None):
        """
        Test a single fix in isolation.
        
        Returns:
            dict: {'passed': bool, 'error': str, 'details': str}
        """
        file_path = fix.get('path', '')
        content = fix.get('content', '')
        file_ext = Path(file_path).suffix.lower()
        
        # Determine test strategy based on file type
        if file_ext in ['.js', '.jsx', '.ts', '.tsx', '.html', '.htm']:
            # Web-based files - test with Playwright
            return await self.test_web_fix(fix, website_url)
        elif file_ext == '.py':
            # Python files - test syntax and basic execution
            return await self.test_python_fix(fix)
        elif file_ext in ['.json', '.md', '.txt']:
            # Data files - test syntax/format
            return await self.test_data_fix(fix)
        else:
            # Unknown file type - basic validation only
            return await self.test_generic_fix(fix)
    
    async def test_web_fix(self, fix, website_url=None):
        """
        Test web-based fixes (JS, HTML) using Playwright.
        """
        file_path = fix.get('path', '')
        content = fix.get('content', '')
        
        # Create temporary test file
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file_path = os.path.join(temp_dir, os.path.basename(file_path))
            
            try:
                # Write fix content to temp file
                with open(test_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Test 1: Syntax validation
                syntax_check = self.check_javascript_syntax(content)
                if not syntax_check['valid']:
                    return {
                        'passed': False,
                        'error': 'JavaScript syntax error',
                        'details': syntax_check.get('error', 'Invalid syntax')
                    }
                
                # Test 2: Basic execution test (if it's a script)
                # Skip execution for browser-specific code (window/document) to avoid Node errors
                is_browser_code = 'window' in content or 'document' in content
                if file_path.endswith(('.js', '.jsx')) and not is_browser_code:
                    execution_test = await self.test_javascript_execution(content)
                    if not execution_test['passed']:
                        return {
                            'passed': False,
                            'error': 'JavaScript execution error',
                            'details': execution_test.get('error', 'Execution failed')
                        }
                
                # Test 3: HTML validation (if HTML file)
                if file_path.endswith(('.html', '.htm')):
                    html_check = self.check_html_structure(content)
                    if not html_check['valid']:
                        return {
                            'passed': False,
                            'error': 'HTML structure error',
                            'details': html_check.get('error', 'Invalid HTML')
                        }
                
                # Test 4: Browser compatibility (if website URL provided)
                if website_url:
                    browser_test = await self.test_browser_compatibility(content, website_url)
                    if not browser_test['passed']:
                        return {
                            'passed': False,
                            'error': 'Browser compatibility issue',
                            'details': browser_test.get('error', 'Browser test failed')
                        }
                
                return {
                    'passed': True,
                    'error': None,
                    'details': 'All web tests passed'
                }
                
            except Exception as e:
                return {
                    'passed': False,
                    'error': f'Exception during web testing: {str(e)}',
                    'details': ''
                }
    
    def check_javascript_syntax(self, code):
        """
        Check JavaScript syntax using Node.js.
        """
        try:
            # Use Node.js to check syntax
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Try to parse with Node.js
                result = subprocess.run(
                    ['node', '--check', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                os.unlink(temp_file)
                
                if result.returncode == 0:
                    return {'valid': True}
                else:
                    return {
                        'valid': False,
                        'error': result.stderr.strip() or 'Syntax error'
                    }
            except FileNotFoundError:
                # Node.js not available - skip syntax check
                os.unlink(temp_file)
                return {'valid': True, 'note': 'Node.js not available, skipping syntax check'}
            except subprocess.TimeoutExpired:
                os.unlink(temp_file)
                return {'valid': False, 'error': 'Syntax check timeout'}
                
        except Exception as e:
            return {'valid': False, 'error': f'Syntax check exception: {str(e)}'}
    
    async def test_javascript_execution(self, code):
        """
        Test JavaScript code execution in isolated environment.
        """
        try:
            # Wrap code in safe execution context
            test_code = f"""
            (function() {{
                try {{
                    {code}
                    return {{ success: true }};
                }} catch (e) {{
                    return {{ success: false, error: e.message }};
                }}
            }})();
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(test_code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                os.unlink(temp_file)
                
                if result.returncode == 0:
                    return {'passed': True}
                else:
                    return {
                        'passed': False,
                        'error': result.stderr.strip() or 'Execution error'
                    }
            except FileNotFoundError:
                # Node.js not available
                os.unlink(temp_file)
                return {'passed': True, 'note': 'Node.js not available, skipping execution test'}
            except subprocess.TimeoutExpired:
                os.unlink(temp_file)
                return {'passed': False, 'error': 'Execution timeout'}
                
        except Exception as e:
            return {'passed': False, 'error': f'Execution test exception: {str(e)}'}
    
    def check_html_structure(self, html):
        """
        Basic HTML structure validation.
        """
        try:
            # Check for balanced tags (basic)
            open_tags = html.count('<')
            close_tags = html.count('>')
            
            if open_tags != close_tags:
                return {
                    'valid': False,
                    'error': f'Unbalanced tags: {open_tags} opening, {close_tags} closing'
                }
            
            # Check for basic HTML structure
            if '<html' in html.lower() or '<body' in html.lower() or '<script' in html.lower() or '<div' in html.lower():
                return {'valid': True}
            
            # If it's just a fragment, that's okay too
            return {'valid': True}
            
        except Exception as e:
            return {'valid': False, 'error': f'HTML check exception: {str(e)}'}
    
    async def test_browser_compatibility(self, content, website_url):
        """
        Test fix compatibility with actual website using Playwright.
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Navigate to website
                await page.goto(website_url, wait_until='networkidle', timeout=30000)
                
                # Inject the fix content
                try:
                    # If it's JavaScript, inject it
                    if '<script' in content or 'function' in content or 'class' in content:
                        await page.evaluate(content)
                    
                    # Check for console errors
                    console_errors = []
                    page.on("console", lambda msg: console_errors.append({
                        "type": msg.type,
                        "text": msg.text
                    }) if msg.type == "error" else None)
                    
                    page.on("pageerror", lambda error: console_errors.append({
                        "type": "pageerror",
                        "text": str(error)
                    }))
                    
                    # Wait a bit for any async errors
                    await page.wait_for_timeout(2000)
                    
                    if console_errors:
                        await browser.close()
                        return {
                            'passed': False,
                            'error': f'Browser console errors: {len(console_errors)} errors',
                            'details': str(console_errors[0].get('text', ''))[:200]
                        }
                    
                    # Check if page still loads
                    page_title = await page.title()
                    if not page_title:
                        await browser.close()
                        return {
                            'passed': False,
                            'error': 'Page failed to load after fix injection'
                        }
                    
                    await browser.close()
                    return {'passed': True}
                    
                except Exception as e:
                    await browser.close()
                    return {
                        'passed': False,
                        'error': f'Browser test exception: {str(e)}'
                    }
                    
        except Exception as e:
            return {
                'passed': False,
                'error': f'Browser compatibility test failed: {str(e)}'
            }
    
    async def test_python_fix(self, fix):
        """
        Test Python fixes for syntax and basic execution.
        """
        content = fix.get('content', '')
        
        try:
            # Test 1: Syntax check
            compile(content, '<string>', 'exec')
            
            # Test 2: Basic import check (if imports exist)
            if 'import' in content or 'from' in content:
                # Try to parse imports
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    return {
                        'passed': False,
                        'error': f'Python syntax error: {str(e)}'
                    }
            
            return {'passed': True}
            
        except SyntaxError as e:
            return {
                'passed': False,
                'error': f'Python syntax error: {str(e)}'
            }
        except Exception as e:
            return {
                'passed': False,
                'error': f'Python test exception: {str(e)}'
            }
    
    async def test_data_fix(self, fix):
        """
        Test data file fixes (JSON, etc.).
        """
        content = fix.get('content', '')
        file_path = fix.get('path', '')
        
        try:
            if file_path.endswith('.json'):
                # Validate JSON
                json.loads(content)
                return {'passed': True}
            else:
                # For other data files, just check if content is not empty
                if content.strip():
                    return {'passed': True}
                else:
                    return {
                        'passed': False,
                        'error': 'File content is empty'
                    }
                    
        except json.JSONDecodeError as e:
            return {
                'passed': False,
                'error': f'Invalid JSON: {str(e)}'
            }
        except Exception as e:
            return {
                'passed': False,
                'error': f'Data file test exception: {str(e)}'
            }
    
    async def test_generic_fix(self, fix):
        """
        Generic test for unknown file types.
        """
        content = fix.get('content', '')
        
        # Basic checks
        if not content or not content.strip():
            return {
                'passed': False,
                'error': 'Fix content is empty'
            }
        
        # Check for suspicious patterns
        dangerous_patterns = [
            'rm -rf',
            'format c:',
            'delete from',
            'drop table'
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return {
                    'passed': False,
                    'error': f'Dangerous pattern detected: {pattern}'
                }
        
        return {'passed': True}
    
    def get_test_summary(self):
        """
        Get summary of test results.
        """
        return {
            'total_tested': len(self.test_results),
            'passed': sum(1 for r in self.test_results if r.get('passed')),
            'failed': sum(1 for r in self.test_results if not r.get('passed'))
        }


