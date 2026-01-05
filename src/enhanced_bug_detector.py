"""
Enhanced Bug Detector with comprehensive UI/UX, accessibility, and performance testing.
Uses multiple detection strategies for thorough bug identification.
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from playwright.async_api import async_playwright
import asyncio

async def detect_accessibility_issues(url):
    """
    Detect accessibility issues using Playwright and basic checks.
    Note: For production, consider using axe-core via @axe-core/playwright
    """
    bugs = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            
            # Check for missing alt text on images
            images_without_alt = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => !img.alt || img.alt.trim() === '')
                        .map(img => ({
                            src: img.src,
                            selector: img.tagName.toLowerCase()
                        }));
                }
            """)
            
            for img in images_without_alt:
                bugs.append({
                    "type": "accessibility",
                    "severity": "medium",
                    "description": "Image missing alt text",
                    "details": f"Image at {img['src']} is missing alt text, which affects screen readers",
                    "data": {
                        "type": "Missing Alt Text",
                        "element": img['selector'],
                        "url": img['src']
                    }
                })
            
            # Check for missing aria-labels on interactive elements
            buttons_without_labels = await page.evaluate("""
                () => {
                    const buttons = Array.from(document.querySelectorAll('button, [role="button"]'));
                    return buttons
                        .filter(btn => !btn.getAttribute('aria-label') && !btn.textContent.trim())
                        .map(btn => ({
                            tag: btn.tagName.toLowerCase(),
                            id: btn.id || 'no-id'
                        }));
                }
            """)
            
            for btn in buttons_without_labels:
                bugs.append({
                    "type": "accessibility",
                    "severity": "high",
                    "description": "Interactive element missing accessible label",
                    "details": f"{btn['tag']} element (id: {btn['id']}) has no accessible label",
                    "data": {
                        "type": "Missing Accessible Label",
                        "element": btn['tag']
                    }
                })
            
            # Check for poor color contrast (basic check)
            low_contrast_elements = await page.evaluate("""
                () => {
                    // Basic contrast check - in production, use proper contrast ratio calculation
                    const elements = Array.from(document.querySelectorAll('*'));
                    const issues = [];
                    
                    elements.slice(0, 50).forEach((el, idx) => {
                        const style = window.getComputedStyle(el);
                        const bg = style.backgroundColor;
                        const fg = style.color;
                        
                        // Very basic check - white text on white background
                        if (bg === 'rgb(255, 255, 255)' && fg === 'rgb(255, 255, 255)') {
                            issues.push({
                                tag: el.tagName.toLowerCase(),
                                id: el.id || `element-${idx}`
                            });
                        }
                    });
                    
                    return issues;
                }
            """)
            
            for el in low_contrast_elements:
                bugs.append({
                    "type": "accessibility",
                    "severity": "medium",
                    "description": "Potential color contrast issue",
                    "details": f"Element {el['tag']} (id: {el['id']}) may have poor color contrast",
                    "data": {
                        "type": "Color Contrast",
                        "element": el['tag']
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
                        .map(input => ({
                            type: input.type || input.tagName.toLowerCase(),
                            id: input.id || 'no-id'
                        }));
                }
            """)
            
            for inp in inputs_without_labels:
                bugs.append({
                    "type": "accessibility",
                    "severity": "high",
                    "description": "Form input missing label",
                    "details": f"Input element (type: {inp['type']}, id: {inp['id']}) is missing an associated label",
                    "data": {
                        "type": "Missing Form Label",
                        "element": inp['type']
                    }
                })
            
            await browser.close()
            
    except Exception as e:
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

async def detect_performance_issues(url):
    """
    Detect performance issues using Playwright performance metrics.
    """
    bugs = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate and measure performance
            await page.goto(url, wait_until='networkidle')
            
            # Get performance metrics
            metrics = await page.evaluate("""
                () => {
                    const perf = performance.getEntriesByType('navigation')[0];
                    const paint = performance.getEntriesByType('paint');
                    
                    return {
                        loadTime: perf.loadEventEnd - perf.fetchStart,
                        domContentLoaded: perf.domContentLoadedEventEnd - perf.fetchStart,
                        firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0,
                        resourceCount: performance.getEntriesByType('resource').length
                    };
                }
            """)
            
            # Check for slow page load
            if metrics['loadTime'] > 3000:  # 3 seconds
                bugs.append({
                    "type": "performance",
                    "severity": "medium",
                    "description": "Slow page load time",
                    "details": f"Page load time is {metrics['loadTime']:.0f}ms, which exceeds the recommended 3 seconds",
                    "data": {
                        "type": "Slow Page Load",
                        "loadTime": metrics['loadTime'],
                        "threshold": 3000
                    }
                })
            
            # Check for slow First Contentful Paint
            if metrics['firstContentfulPaint'] > 1500:  # 1.5 seconds
                bugs.append({
                    "type": "performance",
                    "severity": "medium",
                    "description": "Slow First Contentful Paint",
                    "details": f"FCP is {metrics['firstContentfulPaint']:.0f}ms, should be under 1.5s",
                    "data": {
                        "type": "Slow FCP",
                        "fcp": metrics['firstContentfulPaint'],
                        "threshold": 1500
                    }
                })
            
            # Check for too many resources
            if metrics['resourceCount'] > 100:
                bugs.append({
                    "type": "performance",
                    "severity": "low",
                    "description": "High number of resources",
                    "details": f"Page loads {metrics['resourceCount']} resources, consider optimizing",
                    "data": {
                        "type": "Too Many Resources",
                        "count": metrics['resourceCount']
                    }
                })
            
            # Check for large images
            large_images = await page.evaluate("""
                () => {
                    const images = Array.from(document.querySelectorAll('img'));
                    return images
                        .filter(img => {
                            return img.naturalWidth > 1920 || img.naturalHeight > 1080;
                        })
                        .map(img => ({
                            src: img.src,
                            width: img.naturalWidth,
                            height: img.naturalHeight
                        }));
                }
            """)
            
            for img in large_images:
                bugs.append({
                    "type": "performance",
                    "severity": "medium",
                    "description": "Large image file detected",
                    "details": f"Image {img['src']} is {img['width']}x{img['height']}, consider optimizing",
                    "data": {
                        "type": "Large Image",
                        "url": img['src'],
                        "dimensions": f"{img['width']}x{img['height']}"
                    }
                })
            
            await browser.close()
            
    except Exception as e:
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "Performance testing encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

async def detect_responsive_issues(url):
    """
    Detect responsive design issues by testing multiple viewport sizes.
    """
    bugs = []
    
    viewports = [
        {"width": 375, "height": 667, "name": "Mobile (iPhone)"},
        {"width": 768, "height": 1024, "name": "Tablet (iPad)"},
        {"width": 1920, "height": 1080, "name": "Desktop"}
    ]
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            
            for viewport in viewports:
                page = await browser.new_page(viewport={'width': viewport['width'], 'height': viewport['height']})
                await page.goto(url, wait_until='networkidle')
                
                # Check for horizontal scrolling (layout overflow)
                has_horizontal_scroll = await page.evaluate("""
                    () => {
                        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
                    }
                """)
                
                if has_horizontal_scroll:
                    bugs.append({
                        "type": "responsive",
                        "severity": "high",
                        "description": "Horizontal scrolling detected",
                        "details": f"Page has horizontal scroll at {viewport['name']} viewport ({viewport['width']}x{viewport['height']})",
                        "data": {
                            "type": "Horizontal Scroll",
                            "viewport": viewport['name'],
                            "dimensions": f"{viewport['width']}x{viewport['height']}"
                        }
                    })
                
                # Check for viewport meta tag
                has_viewport_meta = await page.evaluate("""
                    () => {
                        return !!document.querySelector('meta[name="viewport"]');
                    }
                """)
                
                if not has_viewport_meta and viewport['width'] == 375:
                    bugs.append({
                        "type": "responsive",
                        "severity": "high",
                        "description": "Missing viewport meta tag",
                        "details": "Page is missing viewport meta tag, which is essential for mobile responsiveness",
                        "data": {
                            "type": "Missing Viewport Meta",
                            "viewport": viewport['name']
                        }
                    })
                
                # Check for text that's too small on mobile
                if viewport['width'] == 375:
                    small_text = await page.evaluate("""
                        () => {
                            const elements = Array.from(document.querySelectorAll('p, span, div, h1, h2, h3, h4, h5, h6'));
                            return elements
                                .slice(0, 20)
                                .filter(el => {
                                    const style = window.getComputedStyle(el);
                                    const fontSize = parseFloat(style.fontSize);
                                    return fontSize < 14; // Less than 14px is too small
                                })
                                .length;
                        }
                    """)
                    
                    if small_text > 5:
                        bugs.append({
                            "type": "responsive",
                            "severity": "medium",
                            "description": "Text too small on mobile",
                            "details": f"Multiple elements have font size less than 14px on mobile viewport",
                            "data": {
                                "type": "Small Text on Mobile",
                                "viewport": viewport['name'],
                                "affected_elements": small_text
                            }
                        })
                
                await page.close()
            
            await browser.close()
            
    except Exception as e:
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "Responsive testing encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

async def detect_console_errors(url):
    """
    Detect JavaScript console errors.
    """
    bugs = []
    console_errors = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Listen to console errors
            page.on("console", lambda msg: console_errors.append({
                "type": msg.type,
                "text": msg.text
            }) if msg.type == "error" else None)
            
            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)  # Wait for any async errors
            
            # Listen to page errors
            page.on("pageerror", lambda error: console_errors.append({
                "type": "pageerror",
                "text": str(error)
            }))
            
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
            
            await browser.close()
            
    except Exception as e:
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "Console error detection encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

async def detect_static_code_issues(repo_path):
    """
    Detect static code issues like incomplete functions, TODOs, etc.
    """
    bugs = []
    if not repo_path or not os.path.exists(repo_path):
        return bugs

    try:
        # Walk through the repo
        for root, _, files in os.walk(repo_path):
            if 'node_modules' in root or '.git' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if not file.endswith(('.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css')):
                    continue
                    
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        # 1. Check for TODOs/FIXMEs
                        for i, line in enumerate(lines, 1):
                            if 'TODO' in line or 'FIXME' in line:
                                bugs.append({
                                    "type": "incomplete_code",
                                    "severity": "medium",
                                    "description": "Incomplete code detected (TODO/FIXME)",
                                    "details": f"Found '{line.strip()}' in {rel_path} at line {i}",
                                    "target_file": rel_path, # Helping the generator know where to fix
                                    "data": {
                                        "type": "TODO Comment",
                                        "file": rel_path,
                                        "line": i
                                    }
                                })
                        
                        # 2. Check for empty function blocks (simple heuristic)
                        # JS/TS: function ... {} or () => {}
                        if re.search(r'(function\s+\w+\s*\(.*?\)\s*\{\s*\}|=>\s*\{\s*\})', content):
                            bugs.append({
                                "type": "incomplete_code",
                                "severity": "high",
                                "description": "Empty function detected",
                                "details": f"Empty function body found in {rel_path}. This might be a placeholder.",
                                "target_file": rel_path,
                                "data": {
                                    "type": "Empty Function",
                                    "file": rel_path
                                }
                            })
                            
                        # Python: def ...:\n\s*pass
                        if file.endswith('.py') and re.search(r'def\s+\w+\s*\(.*?\):\s*\n\s*pass', content):
                             bugs.append({
                                "type": "incomplete_code",
                                "severity": "high",
                                "description": "Empty Python function detected",
                                "details": f"Empty python function (pass) found in {rel_path}.",
                                "target_file": rel_path,
                                "data": {
                                    "type": "Empty Function",
                                    "file": rel_path
                                }
                            })

                except Exception as e:
                    # Ignore read errors
                    pass
                    
    except Exception as e:
        print(f"[ERROR] Static analysis failed: {e}")

    return bugs

async def comprehensive_bug_detection(url, github_repo_path=None):
    """
    Run all bug detection strategies and return comprehensive results.
    """
    all_bugs = []
    
    print("[ENHANCED_BUG_DETECTOR] Starting comprehensive bug detection...")
    
    # Run all detection strategies in parallel
    results = await asyncio.gather(
        detect_accessibility_issues(url),
        detect_performance_issues(url),
        detect_responsive_issues(url),
        detect_console_errors(url),
        detect_static_code_issues(github_repo_path),
        return_exceptions=True
    )
    
    # Combine results
    for result in results:
        if isinstance(result, Exception):
            print(f"[ERROR] Bug detection error: {result}")
            all_bugs.append({
                "type": "test_framework_error",
                "severity": "medium",
                "description": "Bug detection encountered an error",
                "details": str(result),
                "data": {
                    "type": "Test Framework Error",
                    "description": str(result)
                }
            })
        else:
            all_bugs.extend(result)
    
    print(f"[ENHANCED_BUG_DETECTOR] Detected {len(all_bugs)} bugs")
    
    return all_bugs

