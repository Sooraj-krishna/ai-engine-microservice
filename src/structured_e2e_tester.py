"""
Structured E2E testing using Playwright's built-in capabilities.
Uses rule-based test patterns instead of AI generation for more reliable testing.
"""

import asyncio
from playwright.async_api import async_playwright, expect

async def run_structured_e2e_tests(url):
    """
    Run structured E2E tests using Playwright's built-in test patterns.
    More reliable than AI-generated tests.
    """
    bugs = []
    
    print(f"[STRUCTURED_E2E] Running structured E2E tests for {url}")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Test 1: Page loads successfully
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                print("[STRUCTURED_E2E] ✓ Page loaded successfully")
            except Exception as e:
                bugs.append({
                    "type": "functional_bug",
                    "severity": "high",
                    "description": "Page failed to load",
                    "details": f"The page at {url} failed to load: {str(e)}",
                    "data": {
                        "type": "Page Load Failure",
                        "error": str(e)
                    }
                })
                await browser.close()
                return bugs
            
            # Test 2: Check for console errors
            console_errors = []
            page.on("console", lambda msg: console_errors.append({
                "type": msg.type,
                "text": msg.text
            }) if msg.type == "error" else None)
            
            page.on("pageerror", lambda error: console_errors.append({
                "type": "pageerror",
                "text": str(error)
            }))
            
            # Wait a bit for async errors
            await page.wait_for_timeout(2000)
            
            if console_errors:
                for error in console_errors:
                    bugs.append({
                        "type": "javascript_error",
                        "severity": "high",
                        "description": "JavaScript console error detected",
                        "details": f"Console error: {error['text']}",
                        "data": {
                            "type": "Console Error",
                            "error": error['text']
                        }
                    })
            
            # Test 3: Check for broken images
            broken_images = await page.evaluate("""
                async () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    const broken = [];
                    
                    for (const img of images) {
                        if (img.complete && img.naturalHeight === 0 && img.src) {
                            broken.push(img.src);
                        }
                    }
                    
                    return broken;
                }
            """)
            
            if broken_images:
                bugs.append({
                    "type": "ui_bug",
                    "severity": "medium",
                    "description": f"{len(broken_images)} broken image(s) detected",
                    "details": f"Images failed to load: {', '.join(broken_images[:3])}",
                    "data": {
                        "type": "Broken Images",
                        "count": len(broken_images),
                        "urls": broken_images[:5]  # Limit to first 5
                    }
                })
            
            # Test 4: Check for broken links (internal)
            broken_links = []
            links = await page.evaluate("""
                () => {
                    return Array.from(document.querySelectorAll('a[href]'))
                        .map(a => a.href)
                        .filter(href => href.startsWith(window.location.origin))
                        .slice(0, 10);  // Check first 10 internal links
                }
            """)
            
            for link in links[:5]:  # Limit to 5 for performance
                try:
                    response = await page.request.get(link)
                    if response.status >= 400:
                        broken_links.append(link)
                except:
                    broken_links.append(link)
            
            if broken_links:
                bugs.append({
                    "type": "ui_bug",
                    "severity": "medium",
                    "description": f"{len(broken_links)} broken link(s) detected",
                    "details": f"Links returned error status: {', '.join(broken_links[:3])}",
                    "data": {
                        "type": "Broken Links",
                        "count": len(broken_links),
                        "urls": broken_links
                    }
                })
            
            # Test 5: Check for interactive elements (buttons, forms)
            interactive_elements = await page.evaluate("""
                () => {
                    const buttons = document.querySelectorAll('button, [role="button"], input[type="submit"]');
                    const forms = document.querySelectorAll('form');
                    
                    return {
                        buttons: buttons.length,
                        forms: forms.length,
                        disabled_buttons: Array.from(buttons).filter(b => b.disabled).length
                    };
                }
            """)
            
            # Test 6: Check if main content is visible
            try:
                # Look for common main content selectors
                main_selectors = ['main', '[role="main"]', '.main', '#main', '.content', '#content']
                main_visible = False
                
                for selector in main_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            if is_visible:
                                main_visible = True
                                break
                    except:
                        continue
                
                if not main_visible and interactive_elements['buttons'] == 0:
                    bugs.append({
                        "type": "ui_bug",
                        "severity": "medium",
                        "description": "Main content may not be visible or page may be empty",
                        "details": "Could not find visible main content area or interactive elements.",
                        "data": {
                            "type": "Content Visibility",
                            "interactive_elements": interactive_elements
                        }
                    })
            except Exception as e:
                print(f"[STRUCTURED_E2E] Error checking content visibility: {e}")
            
            # Test 7: Check for form submission (if forms exist)
            if interactive_elements['forms'] > 0:
                forms = await page.query_selector_all('form')
                for form in forms[:2]:  # Test first 2 forms
                    try:
                        # Check if form has required fields
                        required_fields = await form.query_selector_all('input[required], select[required], textarea[required]')
                        if required_fields:
                            # Try to submit empty form (should show validation)
                            submit_button = await form.query_selector('button[type="submit"], input[type="submit"]')
                            if submit_button:
                                # Don't actually submit, just check if form is properly structured
                                pass
                    except Exception as e:
                        print(f"[STRUCTURED_E2E] Error checking form: {e}")
            
            await browser.close()
            
            print(f"[STRUCTURED_E2E] Completed tests, found {len(bugs)} issues")
            
    except Exception as e:
        print(f"[STRUCTURED_E2E] Error during E2E testing: {e}")
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "E2E testing framework encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

