"""
Axe-core integration for comprehensive accessibility testing.
Uses Playwright with axe-core for detailed accessibility audits.
"""

import asyncio
from playwright.async_api import async_playwright
import subprocess
import os

async def run_axe_accessibility_audit(url):
    """
    Run axe-core accessibility audit using Playwright.
    Falls back to basic checks if axe-core is not available.
    """
    bugs = []
    
    try:
        # Check if @axe-core/playwright is available
        try:
            result = subprocess.run(['npm', 'list', '@axe-core/playwright'], capture_output=True, timeout=5)
            has_axe = result.returncode == 0
        except:
            has_axe = False
        
        if not has_axe:
            print("[AXE] @axe-core/playwright not installed, using basic accessibility checks")
            return await run_basic_accessibility_checks(url)
        
        # Use axe-core via Playwright
        print(f"[AXE] Running axe-core accessibility audit for {url}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            
            # Inject and run axe-core
            await page.add_script_tag(url='https://unpkg.com/axe-core@latest/axe.min.js')
            
            # Run axe
            results = await page.evaluate("""
                async () => {
                    return await axe.run();
                }
            """)
            
            # Process results
            violations = results.get('violations', [])
            
            for violation in violations:
                # Group by rule ID
                rule_id = violation.get('id', 'unknown')
                impact = violation.get('impact', 'moderate')
                description = violation.get('description', '')
                nodes = violation.get('nodes', [])
                
                severity_map = {
                    'critical': 'high',
                    'serious': 'high',
                    'moderate': 'medium',
                    'minor': 'low'
                }
                
                bugs.append({
                    "type": "accessibility",
                    "severity": severity_map.get(impact, 'medium'),
                    "description": f"Axe violation: {rule_id}",
                    "details": f"{description}. Found in {len(nodes)} element(s).",
                    "data": {
                        "type": "Axe Violation",
                        "rule_id": rule_id,
                        "impact": impact,
                        "description": description,
                        "nodes_affected": len(nodes),
                        "help_url": violation.get('helpUrl', '')
                    }
                })
            
            await browser.close()
            
            print(f"[AXE] Found {len(bugs)} accessibility violations")
            
    except Exception as e:
        print(f"[AXE] Error running axe-core: {e}")
        # Fallback to basic checks
        return await run_basic_accessibility_checks(url)
    
    return bugs

async def run_basic_accessibility_checks(url):
    """
    Basic accessibility checks using Playwright (fallback when axe-core is not available).
    """
    bugs = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            
            # Check for missing alt text
            images_without_alt = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => !img.alt || img.alt.trim() === '')
                        .length;
                }
            """)
            
            if images_without_alt > 0:
                bugs.append({
                    "type": "accessibility",
                    "severity": "medium",
                    "description": f"{images_without_alt} image(s) missing alt text",
                    "details": "Images without alt text are not accessible to screen readers.",
                    "data": {
                        "type": "Missing Alt Text",
                        "count": images_without_alt
                    }
                })
            
            # Check for missing form labels
            inputs_without_labels = await page.evaluate("""
                () => {
                    const inputs = Array.from(document.querySelectorAll('input, textarea, select'));
                    return inputs
                        .filter(input => {
                            const id = input.id;
                            if (!id) return true;
                            const label = document.querySelector(`label[for="${id}"]`);
                            return !label && !input.getAttribute('aria-label');
                        })
                        .length;
                }
            """)
            
            if inputs_without_labels > 0:
                bugs.append({
                    "type": "accessibility",
                    "severity": "high",
                    "description": f"{inputs_without_labels} form input(s) missing labels",
                    "details": "Form inputs without labels are not accessible to screen readers.",
                    "data": {
                        "type": "Missing Form Labels",
                        "count": inputs_without_labels
                    }
                })
            
            # Check for missing ARIA labels on interactive elements
            buttons_without_labels = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
                    return buttons
                        .filter(btn => !btn.getAttribute('aria-label') && !btn.textContent.trim())
                        .length;
                }
            """)
            
            if buttons_without_labels > 0:
                bugs.append({
                    "type": "accessibility",
                    "severity": "high",
                    "description": f"{buttons_without_labels} button(s) missing accessible labels",
                    "details": "Interactive elements without accessible labels are not usable by screen readers.",
                    "data": {
                        "type": "Missing Button Labels",
                        "count": buttons_without_labels
                    }
                })
            
            # Check for missing heading structure
            h1_count = await page.evaluate("() => document.querySelectorAll('h1').length")
            if h1_count == 0:
                bugs.append({
                    "type": "accessibility",
                    "severity": "medium",
                    "description": "Page missing H1 heading",
                    "details": "Pages should have at least one H1 heading for proper document structure.",
                    "data": {
                        "type": "Missing H1",
                        "count": 0
                    }
                })
            
            await browser.close()
            
    except Exception as e:
        print(f"[AXE] Error in basic accessibility checks: {e}")
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "Accessibility testing encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

