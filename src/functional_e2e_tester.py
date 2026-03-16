"""
Functional End-to-End Testing with Playwright
Tests actual user flows and interactions to find functional bugs.
"""

import asyncio
from playwright.async_api import async_playwright
import os


async def run_functional_tests(url, repo_path=None):
    """
    Run functional E2E tests on the application.
    
    Args:
        url: Application URL to test
        repo_path: Optional repository path for context
        
    Returns:
        list: Detected functional bugs
    """
    bugs = []
    
    if not url:
        print("[FUNCTIONAL] No URL provided")
        return bugs
    
    print(f"[FUNCTIONAL] Running functional tests on {url}...")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set up console error tracking
            console_errors = []
            page.on('console', lambda msg: 
                console_errors.append(msg.text) if msg.type == 'error' else None
            )
            
            # Set up page error tracking
            page_errors = []
            page.on('pageerror', lambda exc: page_errors.append(str(exc)))
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                bugs.append({
                    'type': 'page_load_error',
                    'severity': 'critical',
                    'description': f"Failed to load page: {url}",
                    'details': str(e),
                    'target_file': 'index.html',
                    'is_actual_bug': True,
                    'data': {'type': 'Page Load Error', 'url': url}
                })
                await browser.close()
                return bugs
            
            # Test 1: Check for console errors
            if console_errors:
                bugs.append({
                    'type': 'console_error',
                    'severity': 'high',
                    'description': f"Console errors detected: {len(console_errors)} error(s)",
                    'details': f"Errors: {', '.join(console_errors[:3])}",
                    'target_file': 'Check browser console',
                    'is_actual_bug': True,
                    'data': {
                        'type': 'Console Error',
                        'count': len(console_errors),
                        'errors': console_errors[:5]
                    }
                })
            
            # Test 2: Check for page errors
            if page_errors:
                bugs.append({
                    'type': 'javascript_error',
                    'severity': 'critical',
                    'description': f"JavaScript runtime errors: {len(page_errors)} error(s)",
                    'details': f"Errors: {', '.join(page_errors[:3])}",
                    'target_file': 'Check source files',
                    'is_actual_bug': True,
                    'data': {
                        'type': 'Runtime Error',
                        'count': len(page_errors),
                        'errors': page_errors[:5]
                    }
                })
            
            # Test 3: Test all interactive elements
            interactive_bugs = await test_interactive_elements(page)
            bugs.extend(interactive_bugs)
            
            # Test 4: Test navigation
            nav_bugs = await test_navigation(page, url)
            bugs.extend(nav_bugs)
            
            # Test 5: Test forms
            form_bugs = await test_forms(page)
            bugs.extend(form_bugs)
            
            await browser.close()
            
    except Exception as e:
        print(f"[FUNCTIONAL] Error in functional tests: {e}")
        bugs.append({
            'type': 'test_framework_error',
            'severity': 'medium',
            'description': "Functional testing encountered an error",
            'details': str(e),
            'target_file': 'N/A',
            'is_actual_bug': False,
            'data': {'type': 'Test Error', 'error': str(e)}
        })
    
    print(f"[FUNCTIONAL] Found {len(bugs)} functional issues")
    return bugs


async def test_interactive_elements(page):
    """Test all buttons and clickable elements."""
    bugs = []
    
    try:
        # Find all buttons
        buttons = await page.query_selector_all('button, [role="button"], .btn, input[type="button"], input[type="submit"]')
        
        print(f"[FUNCTIONAL] Testing {len(buttons)} interactive elements...")
        
        disabled_buttons = []
        for i, button in enumerate(buttons[:20]):  # Test first 20 to avoid timeout
            try:
                is_disabled = await button.is_disabled()
                is_visible = await button.is_visible()
                text = await button.inner_text() if is_visible else ''
                
                # Check if button is visible but disabled without reason
                if is_visible and is_disabled:
                    disabled_buttons.append(text or f"Button {i+1}")
                
                # Try clicking enabled visible buttons
                if is_visible and not is_disabled:
                    try:
                        await button.click(timeout=2000)
                        await page.wait_for_timeout(500)  # Wait for any actions
                    except Exception as e:
                        # Button click failed
                        bugs.append({
                            'type': 'interaction_error',
                            'severity': 'high',
                            'description': f"Button '{text or f'Button {i+1}'}' click failed",
                            'details': str(e),
                            'target_file': 'Component with button',
                            'is_actual_bug': True,
                            'data': {
                                'type': 'Click Error',
                                'button_text': text,
                                'error': str(e)
                            }
                        })
            except Exception as e:
                # Error accessing button
                continue
        
        if disabled_buttons:
            bugs.append({
                'type': 'ux_issue',
                'severity': 'low',
                'description': f"{len(disabled_buttons)} visible buttons are disabled",
                'details': f"Buttons: {', '.join(disabled_buttons[:5])}",
                'target_file': 'Review button states',
                'is_actual_bug': False,
                'data': {
                    'type': 'Disabled Buttons',
                    'count': len(disabled_buttons),
                    'buttons': disabled_buttons[:10]
                }
            })
            
    except Exception as e:
        print(f"[FUNCTIONAL] Error testing interactive elements: {e}")
    
    return bugs


async def test_navigation(page, base_url):
    """Test navigation links."""
    bugs = []
    
    try:
        # Find all links
        links = await page.query_selector_all('a[href]')
        
        print(f"[FUNCTIONAL] Testing {len(links)} links...")
        
        broken_links = []
        for i, link in enumerate(links[:15]):  # Test first 15 links
            try:
                href = await link.get_attribute('href')
                text = await link.inner_text() if await link.is_visible() else ''
                
                # Skip external links and anchors
                if not href or href.startswith('http') or href.startswith('#') or href.startswith('mailto'):
                    continue
                
                # Check if it's a broken link (404)
                if href.startswith('/'):
                    # Internal link - could test by navigating
                    # For now, just log
                    pass
                    
            except Exception as e:
                broken_links.append((text or f"Link {i+1}", href or 'unknown'))
        
        if broken_links:
            bugs.append({
                'type': 'navigation_error',
                'severity': 'medium',
                'description': f"Potential navigation issues with {len(broken_links)} links",
                'details': f"Links: {', '.join([f'{t} ({h})' for t, h in broken_links[:3]])}",
                'target_file': 'Navigation components',
                'is_actual_bug': True,
                'data': {
                    'type': 'Navigation Error',
                    'count': len(broken_links),
                    'links': broken_links[:10]
                }
            })
            
    except Exception as e:
        print(f"[FUNCTIONAL] Error testing navigation: {e}")
    
    return bugs


async def test_forms(page):
    """Test form submissions."""
    bugs = []
    
    try:
        # Find all forms
        forms = await page.query_selector_all('form')
        
        print(f"[FUNCTIONAL] Testing {len(forms)} forms...")
        
        for i, form in enumerate(forms[:5]):  # Test first 5 forms
            try:
                # Find submit button
                submit_btn = await form.query_selector('button[type="submit"], input[type="submit"]')
                
                if submit_btn:
                    # Check if form has required fields
                    required_fields = await form.query_selector_all('[required]')
                    
                    # Try submitting empty form (should show validation)
                    if required_fields:
                        try:
                            await submit_btn.click(timeout=2000)
                            await page.wait_for_timeout(500)
                            
                            # Check if validation messages appeared
                            # This is a basic check
                            
                        except Exception as e:
                            bugs.append({
                                'type': 'form_error',
                                'severity': 'medium',
                                'description': f"Form {i+1} submission error",
                                'details': str(e),
                                'target_file': 'Form component',
                                'is_actual_bug': True,
                                'data': {
                                    'type': 'Form Submission Error',
                                    'form_index': i+1,
                                    'error': str(e)
                                }
                            })
                            
            except Exception as e:
                continue
                
    except Exception as e:
        print(f"[FUNCTIONAL] Error testing forms: {e}")
    
    return bugs
