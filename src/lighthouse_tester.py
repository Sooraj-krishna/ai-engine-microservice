"""
Lighthouse integration for performance and best practices testing.
Uses Playwright to run Lighthouse audits.
"""

import asyncio
import json
from playwright.async_api import async_playwright
import subprocess
import os

async def run_lighthouse_audit(url):
    """
    Run Lighthouse audit using Playwright and return performance issues.
    """
    bugs = []
    
    try:
        # Check if lighthouse is available
        try:
            result = subprocess.run(['npx', '--version'], capture_output=True, timeout=5)
            has_npx = result.returncode == 0
        except:
            has_npx = False
        
        if not has_npx:
            print("[LIGHTHOUSE] npx not available, using Playwright performance API instead")
            return await run_playwright_performance_audit(url)
        
        # Use lighthouse via npx
        print(f"[LIGHTHOUSE] Running Lighthouse audit for {url}")
        
        # Run lighthouse in headless mode
        result = subprocess.run(
            [
                'npx', 'lighthouse', url,
                '--output=json',
                '--output-path=/tmp/lighthouse-report.json',
                '--chrome-flags="--headless --no-sandbox"',
                '--quiet'
            ],
            capture_output=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode != 0:
            print(f"[LIGHTHOUSE] Lighthouse failed, falling back to Playwright: {result.stderr.decode()}")
            return await run_playwright_performance_audit(url)
        
        # Read lighthouse report
        try:
            with open('/tmp/lighthouse-report.json', 'r') as f:
                report = json.load(f)
        except FileNotFoundError:
            print("[LIGHTHOUSE] Report file not found, using Playwright fallback")
            return await run_playwright_performance_audit(url)
        
        # Extract scores and issues
        categories = report.get('categories', {})
        
        # Performance score
        performance_score = categories.get('performance', {}).get('score', 0) * 100
        if performance_score < 50:
            bugs.append({
                "type": "performance",
                "severity": "high",
                "description": f"Low Lighthouse performance score: {performance_score:.0f}/100",
                "details": f"Performance score is below 50. Consider optimizing images, reducing JavaScript execution time, and eliminating render-blocking resources.",
                "data": {
                    "type": "Low Performance Score",
                    "score": performance_score,
                    "threshold": 50
                }
            })
        elif performance_score < 75:
            bugs.append({
                "type": "performance",
                "severity": "medium",
                "description": f"Moderate Lighthouse performance score: {performance_score:.0f}/100",
                "details": f"Performance score is below 75. Some optimizations recommended.",
                "data": {
                    "type": "Moderate Performance Score",
                    "score": performance_score,
                    "threshold": 75
                }
            })
        
        # Accessibility score
        accessibility_score = categories.get('accessibility', {}).get('score', 0) * 100
        if accessibility_score < 90:
            bugs.append({
                "type": "accessibility",
                "severity": "medium",
                "description": f"Lighthouse accessibility score: {accessibility_score:.0f}/100",
                "details": f"Accessibility score is below 90. Check for missing alt text, ARIA labels, and proper semantic HTML.",
                "data": {
                    "type": "Accessibility Issues",
                    "score": accessibility_score,
                    "threshold": 90
                }
            })
        
        # Best practices score
        best_practices_score = categories.get('best-practices', {}).get('score', 0) * 100
        if best_practices_score < 90:
            bugs.append({
                "type": "best_practices",
                "severity": "low",
                "description": f"Lighthouse best practices score: {best_practices_score:.0f}/100",
                "details": f"Best practices score is below 90. Review security headers, console errors, and modern web standards.",
                "data": {
                    "type": "Best Practices Issues",
                    "score": best_practices_score,
                    "threshold": 90
                }
            })
        
        # Extract specific audit failures
        audits = report.get('audits', {})
        for audit_id, audit in audits.items():
            if audit.get('score') is not None and audit['score'] < 0.9:
                if audit.get('id') in ['first-contentful-paint', 'largest-contentful-paint', 'total-blocking-time']:
                    bugs.append({
                        "type": "performance",
                        "severity": "medium",
                        "description": f"Performance issue: {audit.get('title', audit_id)}",
                        "details": audit.get('description', ''),
                        "data": {
                            "type": audit.get('title', audit_id),
                            "score": audit.get('score', 0),
                            "details": audit.get('details', {})
                        }
                    })
        
        print(f"[LIGHTHOUSE] Found {len(bugs)} issues from Lighthouse audit")
        
    except Exception as e:
        print(f"[LIGHTHOUSE] Error running Lighthouse: {e}")
        # Fallback to Playwright
        return await run_playwright_performance_audit(url)
    
    return bugs

async def run_playwright_performance_audit(url):
    """
    Fallback performance audit using Playwright's performance API.
    """
    bugs = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate and measure
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
                        resourceCount: performance.getEntriesByType('resource').length,
                        totalSize: performance.getEntriesByType('resource').reduce((sum, r) => sum + (r.transferSize || 0), 0)
                    };
                }
            """)
            
            # Check Core Web Vitals
            if metrics['loadTime'] > 3000:
                bugs.append({
                    "type": "performance",
                    "severity": "high",
                    "description": f"Slow page load: {metrics['loadTime']:.0f}ms",
                    "details": f"Page load time exceeds 3 seconds. Consider optimizing resources and reducing JavaScript execution.",
                    "data": {
                        "type": "Slow Page Load",
                        "loadTime": metrics['loadTime'],
                        "threshold": 3000
                    }
                })
            
            if metrics['firstContentfulPaint'] > 1500:
                bugs.append({
                    "type": "performance",
                    "severity": "medium",
                    "description": f"Slow First Contentful Paint: {metrics['firstContentfulPaint']:.0f}ms",
                    "details": f"FCP should be under 1.5 seconds for good user experience.",
                    "data": {
                        "type": "Slow FCP",
                        "fcp": metrics['firstContentfulPaint'],
                        "threshold": 1500
                    }
                })
            
            # Check resource count
            if metrics['resourceCount'] > 100:
                bugs.append({
                    "type": "performance",
                    "severity": "low",
                    "description": f"High number of resources: {metrics['resourceCount']}",
                    "details": f"Consider bundling and minifying resources to reduce HTTP requests.",
                    "data": {
                        "type": "Too Many Resources",
                        "count": metrics['resourceCount']
                    }
                })
            
            await browser.close()
            
    except Exception as e:
        print(f"[LIGHTHOUSE] Error in Playwright performance audit: {e}")
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "Performance audit encountered an error",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": str(e)
            }
        })
    
    return bugs

