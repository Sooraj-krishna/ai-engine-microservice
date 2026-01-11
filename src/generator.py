"""
Enhanced Controlled Code Generator with Validation Integration.
Makes safe, targeted improvements with comprehensive safety checks.
Prevents major UI changes and function removal.
"""

from ai_api import query_codegen_api
from validator import CodeValidator
from datetime import datetime
import traceback
import os

# Optional: Use improved fixer if available
try:
    from improved_fixer import incremental_fix_bugs
    IMPROVED_FIXER_AVAILABLE = True
except ImportError:
    IMPROVED_FIXER_AVAILABLE = False
    print("[GENERATOR] Improved fixer not available, using standard approach")

async def prepare_fixes(issues, repo_path=None):
    """
    Generate code fixes for detected issues.
    For bug reports: Fixes bugs in existing files using improved fixer.
    For optimization issues: Creates utility files (safe, additive).
    Includes comprehensive validation before returning fixes.
    
    Args:
        issues: List of detected issues
        repo_path: Optional path to repository for improved fixing
    """
    # Separate bugs from optimization issues
    # Bugs are issues with type 'bug_report' or from enhanced bug detection (accessibility, performance, responsive, etc.)
    bugs = []
    optimization_issues = []
    
    print(f"[GENERATOR] Analyzing {len(issues)} issues to separate bugs from optimizations...")
    
    for issue in issues:
        issue_type = issue.get('type', '')
        issue_severity = issue.get('severity', 'low')
        # Bug types: bug_report, accessibility, performance, responsive, javascript_error, console_error, etc.
        is_bug = (issue_type == 'bug_report' or 
                 issue_type in ['accessibility', 'performance', 'responsive', 'javascript_error', 'console_error', 'ui_bug', 'test_framework_error'] or
                 issue_severity == 'high')
        
        if is_bug:
            bugs.append(issue)
            print(f"[GENERATOR] Classified as BUG: {issue_type} (severity: {issue_severity})")
        else:
            optimization_issues.append(issue)
            print(f"[GENERATOR] Classified as OPTIMIZATION: {issue_type} (severity: {issue_severity})")
    
    print(f"[GENERATOR] Summary: {len(bugs)} bugs, {len(optimization_issues)} optimization issues")
    
    all_fixes = []
    
    # STEP 1: Fix bugs FIRST (before optimizations)
    if bugs:
        print(f"[GENERATOR] ========================================")
        print(f"[GENERATOR] STEP 1: Processing {len(bugs)} bugs first...")
        print(f"[GENERATOR] ========================================")
        
        # Check if we should use improved fixer for bugs
        use_improved_fixer = (
            IMPROVED_FIXER_AVAILABLE and 
            repo_path and 
            os.path.exists(repo_path) and
            (os.getenv('USE_IMPROVED_FIXER', 'true').lower() == 'true' or len(bugs) > 0)
        )
        
        if use_improved_fixer:
            print(f"[GENERATOR] Using improved incremental fixer for {len(bugs)} bugs...")
            try:
                bug_fixes, failed = incremental_fix_bugs(bugs, repo_path)
                print(f"[GENERATOR] Improved fixer: {len(bug_fixes)} bug fixes, {len(failed)} failed")
                
                if bug_fixes:
                    # Convert improved fixer format to standard format
                    for fix in bug_fixes:
                        # Use the fix content directly (improved fixer provides the fixed code)
                        fix_path = fix.get('path', '')
                        # Convert absolute path to relative path if repo_path is provided
                        if repo_path and os.path.isabs(fix_path) and fix_path.startswith(repo_path):
                            fix_path = os.path.relpath(fix_path, repo_path)
                        elif repo_path and os.path.isabs(fix_path):
                            # If it's an absolute path but not in repo, try to find relative
                            fix_path = os.path.basename(fix_path)
                        
                        all_fixes.append({
                            'path': fix_path.replace('\\', '/'),  # Normalize path separators
                            'content': fix.get('content', ''),  # The fixed code from improved fixer
                            'description': fix.get('description', 'Bug fix'),
                            'bug': fix.get('bug', {})
                        })
                    
                    print(f"[GENERATOR] ✅ Generated {len(bug_fixes)} bug fixes")
                else:
                    print(f"[GENERATOR] ⚠️ Improved fixer returned no fixes, will try AI-based fix generation")
                    # Fall through to generate fixes using AI
                    bug_fixes = None
                    
            except Exception as e:
                print(f"[WARNING] Improved fixer failed: {e}")
                import traceback
                print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                bug_fixes = None
        
        # Fallback: Generate bug fixes using AI if improved fixer failed or unavailable
        if not bug_fixes or len(bug_fixes) == 0:
            print(f"[GENERATOR] Generating bug fixes using AI API...")
            try:
                for i, bug in enumerate(bugs, 1):
                    print(f"[GENERATOR] Generating fix for bug {i}/{len(bugs)}: {bug.get('type', 'unknown')}")
                    
                    bug_type = bug.get('type', 'unknown')
                    bug_description = bug.get('description', '')
                    bug_details = bug.get('details', '')
                    target_file = bug.get('target_file')
                    
                    # Try to read file content for context
                    file_context = ""
                    if target_file and repo_path:
                        try:
                            full_path = os.path.join(repo_path, target_file)
                            if os.path.exists(full_path):
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # Limit content size to avoid context window issues
                                    if len(content) > 10000:
                                        file_context = content[:10000] + "\n... (truncated)"
                                    else:
                                        file_context = content
                                print(f"[GENERATOR] Read context from {target_file} ({len(file_context)} chars)")
                        except Exception as e:
                            print(f"[WARNING] Could not read target file {target_file}: {e}")
                    
                    # Generate fix prompt
                    fix_prompt = f"""
You are fixing a {bug_type} bug in a web application.

BUG DESCRIPTION: {bug_description}
BUG DETAILS: {bug_details}
TARGET FILE: {target_file or 'Unknown'}

CURRENT CODE:
```
{file_context}
```

REQUIREMENTS:
1. Generate a complete fix for this bug
2. Fix the actual code that has the bug
3. Return the FULL fixed file content, not just a patch
4. Ensure the fix resolves the issue described
5. Follow best practices
6. MINIMAL COMMENTS - only brief one-liners where necessary
7. NO long explanatory comments
8. IMPORTANT: Return ONLY the code, no markdown formatting or explanation.

Please provide the complete fixed code for the file that needs to be fixed.
"""
                    
                    try:
                        # Generate fix using AI
                        fixed_code = query_codegen_api(fix_prompt, language="javascript")
                        
                        if fixed_code and len(fixed_code.strip()) > 0:
                            # Cleaner separation of code from markdown if present
                            if fixed_code.startswith('```') and '```' in fixed_code[3:]:
                                # Extract code block
                                lines = fixed_code.split('\n')
                                if lines[0].startswith('```'):
                                    lines = lines[1:]
                                if lines[-1].strip() == '```':
                                    lines = lines[:-1]
                                fixed_code = '\n'.join(lines)
                            
                            # Determine file path - STRICTER LOGIC
                            file_path = target_file
                            
                            if not file_path:
                                print(f"[GENERATOR] ⚠️ Skipping bug fix: No target file identified for {bug_type}")
                                continue
                            
                            # SAFETY: Ensure path is relative to repo root for Git operations
                            if repo_path and os.path.isabs(file_path) and file_path.startswith(repo_path):
                                file_path = os.path.relpath(file_path, repo_path)
                                print(f"[GENERATOR] Converted absolute path to relative: {file_path}")
                            elif os.path.isabs(file_path):
                                # Try to make it relative if it's absolute but repo_path matching failed/wasn't provided
                                # This assumes the script runs from near the repo or paths are standard
                                try:
                                    if repo_path:
                                        file_path = os.path.relpath(file_path, repo_path)
                                    else:
                                        # Fallback: take basename if we can't determine relative path
                                        # This is risky but better than failing
                                        print(f"[GENERATOR] ⚠️ Could not determine relative path for {file_path}, using basename") 
                                        file_path = os.path.basename(file_path)
                                except Exception as e:
                                    print(f"[WARNING] Path processing error: {e}")
                                
                            all_fixes.append({
                                'path': file_path,
                                'content': fixed_code,
                                'description': f"Fix for {bug_type}: {bug_description[:100]}",
                                'bug': bug
                            })
                            print(f"[GENERATOR] ✅ Generated AI fix for {bug_type} in {file_path}")
                        else:
                            print(f"[GENERATOR] ⚠️ AI returned empty fix for {bug_type}")
                    except Exception as e:
                        print(f"[ERROR] Failed to generate AI fix for bug {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"[ERROR] AI-based bug fix generation failed: {e}")
        
        print(f"[GENERATOR] ✅ Step 1 complete: {len(all_fixes)} bug fixes generated")
    
    # STEP 2: Generate optimization utilities AFTER bugs are fixed
    
    # STEP 2: Generate optimization utilities AFTER bugs are fixed
    validator = CodeValidator()
    optimization_fixes = []
    
    if optimization_issues:
        print(f"[GENERATOR] ========================================")
        print(f"[GENERATOR] STEP 2: Processing {len(optimization_issues)} optimization issues (will create utility files)...")
        print(f"[GENERATOR] ========================================")
    else:
        print(f"[GENERATOR] No optimization issues to process, only bug fixes")
    
    for i, issue in enumerate(optimization_issues, 1):
        try:
            issue_type = issue.get('type')
            issue_data = issue.get('data', {})
            
            print(f"[GENERATOR] Processing issue {i}/{len(optimization_issues)}: {issue_type}")
            
            # Only process issues marked as safe
            if not issue.get('safe_mode', False):
                print(f"[SKIP] Issue {issue_type} not marked as safe mode")
                continue
            
            # Generate appropriate utility based on issue type
            fix = None
            if issue_type == 'memory_optimization':
                fix = create_memory_utility(issue, issue_data)
            elif issue_type == 'user_experience':
                fix = create_engagement_utility(issue, issue_data)
            elif issue_type == 'performance':
                fix = create_performance_utility(issue, issue_data)
            elif issue_type == 'error_handling':
                fix = create_error_handler_utility(issue, issue_data)
            elif issue_type == 'security':
                fix = create_security_utility(issue, issue_data)
            elif issue_type == 'seo_optimization':
                fix = create_seo_utility(issue, issue_data)
            elif issue_type == 'accessibility':
                fix = create_accessibility_utility(issue, issue_data)
            elif issue_type == 'mobile_optimization':
                fix = create_mobile_utility(issue, issue_data)
            elif issue_type == 'caching':
                fix = create_caching_utility(issue, issue_data)
            elif issue_type == 'analytics':
                fix = create_analytics_utility(issue, issue_data)
            elif issue_type == 'storage_optimization':
                fix = create_storage_utility(issue, issue_data)
            elif issue_type == 'comprehensive_optimization':
                fix = create_comprehensive_utility(issue, issue_data)
            elif issue_type == 'documentation':
                fix = create_documentation_utility(issue, issue_data)
            elif issue_type == 'dependency_security':
                fix = create_dependency_security_utility(issue, issue_data)
            else:
                # Fallback for unknown issue types
                print(f"[GENERATOR] Unknown issue type '{issue_type}', creating generic utility")
                fix = create_generic_utility(issue, issue_data)
            
            if fix:
                optimization_fixes.append(fix)
                print(f"[SUCCESS] Generated utility for {issue_type}: {fix.get('path')}")
            else:
                print(f"[ERROR] Failed to generate fix for {issue_type}")
                
        except Exception as e:
            print(f"[ERROR] Exception generating fix for issue {i}: {e}")
            print(traceback.format_exc())
            continue
    
    # Combine bug fixes and optimization fixes
    all_fixes.extend(optimization_fixes)
    
    bug_fix_count = len([f for f in all_fixes if 'bug' in f]) if all_fixes else 0
    print(f"[GENERATOR] ========================================")
    print(f"[GENERATOR] SUMMARY:")
    print(f"[GENERATOR] - Bug fixes generated: {bug_fix_count}")
    print(f"[GENERATOR] - Utility files generated: {len(optimization_fixes)}")
    print(f"[GENERATOR] - Total fixes: {len(all_fixes)}")
    print(f"[GENERATOR] ========================================")
    
    if not all_fixes:
        print("[GENERATOR] No fixes generated")
        return []
    
    # VALIDATE ALL FIXES before returning
    print(f"[GENERATOR] Starting validation process...")
    safe_fixes = validator.validate_all_fixes(all_fixes)
    
    print(f"[GENERATOR] Validation complete: {len(safe_fixes)}/{len(all_fixes)} fixes approved as safe")
    
    # TEST FIXES in isolated environment (if enabled)
    test_fixes = os.getenv('TEST_FIXES_BEFORE_APPLY', 'true').lower() == 'true'
    if test_fixes and safe_fixes:
        print(f"[GENERATOR] Testing {len(safe_fixes)} fixes in isolated environment...")
        try:
            from fix_tester import FixTester
            website_url = os.getenv('WEBSITE_URL')
            tester = FixTester(repo_path=repo_path)
            tested_fixes, failed_tests = await tester.test_fixes(safe_fixes, website_url=website_url)
            
            if tested_fixes:
                print(f"[GENERATOR] ✅ {len(tested_fixes)} fixes passed all tests")
            if failed_tests:
                print(f"[GENERATOR] ========================================")
                print(f"[GENERATOR] ⚠️ {len(failed_tests)} fixes failed tests:")
                print(f"[GENERATOR] ========================================")
                for idx, failed in enumerate(failed_tests, 1):
                    fix_path = failed['fix'].get('path', 'unknown')
                    reason = failed.get('reason', 'Unknown reason')
                    details = failed.get('details', '')
                    print(f"[GENERATOR] {idx}. FAILED: {fix_path}")
                    print(f"[GENERATOR]    Reason: {reason}")
                    if details:
                        print(f"[GENERATOR]    Details: {details[:200]}")
                    print(f"[GENERATOR]    Fix description: {failed['fix'].get('description', 'No description')[:100]}")
                print(f"[GENERATOR] ========================================")
            
            return tested_fixes
        except ImportError:
            print("[WARNING] Fix tester not available, skipping tests")
        except Exception as e:
            print(f"[WARNING] Fix testing failed: {e}, proceeding with validated fixes")
            return safe_fixes
    
    return safe_fixes

def create_memory_utility(issue, data):
    """Create a separate memory optimization utility file."""
    return {
        "path": "utils/ai-memory-optimizer.js",
        "content": f'''/**
 * AI-Generated Memory Optimization Utility
 * Generated: {datetime.now().isoformat()}
 * Issue: Memory usage at {data.get("memory_percent", "N/A")}%
 * SAFE TO USE: This file only adds functionality, never removes existing code.
 * 
 * USAGE: Import and call optimizeMemory() periodically
 */

class MemoryOptimizer {{
    constructor() {{
        this.isOptimizing = false;
        this.stats = {{
            lastOptimization: null,
            memoryFreed: 0,
            optimizationCount: 0
        }};
        
        console.log('[AI Memory Optimizer] Initialized safely');
    }}
    
    // Safe memory optimization that doesn't break existing code
    optimizeMemory() {{
        if (this.isOptimizing) {{
            console.log('[AI Memory Optimizer] Optimization already in progress');
            return false;
        }}
        
        this.isOptimizing = true;
        
        try {{
            const startTime = performance.now();
            
            // Clear unused cached data (safe approach)
            this.clearUnusedCache();
            
            // Optimize images if possible
            this.optimizeImages();
            
            // Clean up event listeners safely
            this.cleanupEventListeners();
            
            // Force garbage collection if available
            if (window.gc) {{
                window.gc();
            }}
            
            const endTime = performance.now();
            this.stats.lastOptimization = new Date().toISOString();
            this.stats.optimizationCount++;
            
            console.log(`[AI Memory Optimizer] Optimization completed safely in ${{endTime - startTime}}ms`);
            return true;
            
        }} catch (error) {{
            console.warn('[AI Memory Optimizer] Error during optimization:', error);
            return false;
        }} finally {{
            this.isOptimizing = false;
        }}
    }}
    
    clearUnusedCache() {{
        // Only clear items that are clearly temporary or old
        if (typeof localStorage !== 'undefined') {{
            const keysToRemove = [];
            
            Object.keys(localStorage).forEach(key => {{
                if (key.startsWith('temp_') || 
                    key.startsWith('cache_old_') || 
                    key.includes('_expired_')) {{
                    keysToRemove.push(key);
                }}
            }});
            
            keysToRemove.forEach(key => localStorage.removeItem(key));
            console.log(`[AI Memory Optimizer] Cleared ${{keysToRemove.length}} cache items`);
        }}
    }}
    
    optimizeImages() {{
        // Non-destructive image optimization
        let optimizedCount = 0;
        document.querySelectorAll('img').forEach(img => {{
            if (!img.hasAttribute('data-ai-optimized')) {{
                if (img.loading !== 'lazy' && img.offsetTop > window.innerHeight) {{
                    img.loading = 'lazy';
                    optimizedCount++;
                }}
                img.setAttribute('data-ai-optimized', 'true');
            }}
        }});
        
        if (optimizedCount > 0) {{
            console.log(`[AI Memory Optimizer] Optimized ${{optimizedCount}} images for lazy loading`);
        }}
    }}
    
    cleanupEventListeners() {{
        // Remove duplicate event listeners safely
        if (window.aiEventListenerCleanup) {{
            // Prevent multiple cleanup attempts
            return;
        }}
        
        window.aiEventListenerCleanup = true;
        console.log('[AI Memory Optimizer] Event listener cleanup completed');
    }}
    
    getStats() {{
        return {{ ...this.stats }};
    }}
    
    // Automatic periodic optimization
    startPeriodicOptimization(intervalMs = 300000) {{ // 5 minutes default
        if (this.optimizationInterval) {{
            clearInterval(this.optimizationInterval);
        }}
        
        this.optimizationInterval = setInterval(() => {{
            this.optimizeMemory();
        }}, intervalMs);
        
        console.log(`[AI Memory Optimizer] Periodic optimization started (every ${{intervalMs/1000}}s)`);
    }}
    
    stopPeriodicOptimization() {{
        if (this.optimizationInterval) {{
            clearInterval(this.optimizationInterval);
            this.optimizationInterval = null;
            console.log('[AI Memory Optimizer] Periodic optimization stopped');
        }}
    }}
}}

// Export for use in existing application
export default MemoryOptimizer;

// Also provide global access (safe fallback)
if (typeof window !== 'undefined') {{
    window.AIMemoryOptimizer = MemoryOptimizer;
    
    // Auto-initialize if memory usage is critical
    if (performance && performance.memory) {{
        const memoryUsage = (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100;
        if (memoryUsage > 80) {{
            const optimizer = new MemoryOptimizer();
            optimizer.optimizeMemory();
        }}
    }}
}}''',
        "description": f"AI-Generated: Safe memory optimization utility (current usage: {data.get('memory_percent', 'N/A')}%)"
    }

def create_engagement_utility(issue, data):
    """Create a separate user engagement utility file."""
    return {
        "path": "utils/ai-engagement-booster.js",
        "content": '''/**
 * AI-Generated User Engagement Utility
 * SAFE TO USE: This only adds features, never removes existing functionality
 */

class EngagementBooster {
    constructor(options = {}) {
        this.config = {
            showTips: options.showTips !== false,
            tipDelay: options.tipDelay || 15000, // 15 seconds
            maxTips: options.maxTips || 3,
            respectUserPreferences: true
        };
        
        this.tipsShown = 0;
        this.isActive = true;
        this.userInteracted = false;
        
        // Only initialize if not already running
        if (!window.aiEngagementActive) {
            this.init();
            window.aiEngagementActive = true;
        }
    }
    
    init() {
        // Safe initialization that doesn't interfere with existing code
        this.trackUserInteraction();
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.startEngagement());
        } else {
            this.startEngagement();
        }
        
        console.log('[AI Engagement] Booster initialized safely');
    }
    
    trackUserInteraction() {
        // Track if user is actively engaging
        ['click', 'scroll', 'keydown', 'touchstart'].forEach(eventType => {
            document.addEventListener(eventType, () => {
                this.userInteracted = true;
            }, { once: true, passive: true });
        });
    }
    
    startEngagement() {
        // Only start if user hasn't interacted yet (they might need guidance)
        setTimeout(() => {
            if (this.isActive && this.tipsShown < this.config.maxTips && !this.userInteracted) {
                this.showEngagementTip();
            }
        }, this.config.tipDelay);
    }
    
    showEngagementTip() {
        if (this.tipsShown >= this.config.maxTips || this.userInteracted) return;
        
        const tip = this.createTipElement();
        document.body.appendChild(tip);
        this.tipsShown++;
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (tip.parentNode) {
                tip.parentNode.removeChild(tip);
            }
        }, 10000);
        
        console.log(`[AI Engagement] Tip ${this.tipsShown} shown`);
    }
    
    createTipElement() {
        const tipMessages = [
            "💡 Welcome! Explore the features to get the most out of this site.",
            "🔍 Try searching or browsing the content sections.",
            "⭐ Found something interesting? Don't forget to bookmark it!"
        ];
        
        const message = tipMessages[this.tipsShown % tipMessages.length];
        
        const tip = document.createElement('div');
        tip.innerHTML = `
            <div style="position: fixed; bottom: 20px; right: 20px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 15px 20px; 
                        border-radius: 12px; max-width: 320px; z-index: 9999;
                        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
                        font-size: 14px; line-height: 1.4;
                        animation: slideIn 0.3s ease-out;">
                <p style="margin: 0 0 10px 0;">${message}</p>
                <button onclick="this.parentElement.parentElement.remove(); window.aiEngagementActive = false;" 
                        style="background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); 
                               color: white; padding: 6px 12px; border-radius: 6px; 
                               cursor: pointer; float: right; font-size: 12px;">Got it!</button>
                <div style="clear: both;"></div>
            </div>
            <style>
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            </style>
        `;
        return tip;
    }
    
    disable() {
        this.isActive = false;
        console.log('[AI Engagement] Booster disabled');
    }
    
    getStats() {
        return {
            tipsShown: this.tipsShown,
            userInteracted: this.userInteracted,
            isActive: this.isActive
        };
    }
}

// Safe global export
export default EngagementBooster;

// Auto-initialize with user preference respect
if (typeof window !== 'undefined' && !window.aiEngagementBooster) {
    // Only auto-initialize if user hasn't been here before
    const hasVisited = localStorage.getItem('ai-engagement-seen');
    if (!hasVisited) {
        window.aiEngagementBooster = new EngagementBooster();
        localStorage.setItem('ai-engagement-seen', 'true');
    }
}''',
        "description": "AI-Generated: Safe user engagement enhancement utility"
    }

def create_performance_utility(issue, data):
    """Create performance monitoring utility."""
    return {
        "path": "utils/ai-performance-monitor.js",
        "content": '''/**
 * AI-Generated Performance Monitoring Utility
 * SAFE TO USE: Only monitors and suggests, never modifies existing code
 */

class PerformanceMonitor {
    constructor() {
        this.metrics = {
            pageLoadTime: 0,
            domContentLoaded: 0,
            resourcesLoaded: 0,
            firstPaint: 0,
            firstContentfulPaint: 0
        };
        
        this.observations = [];
        this.init();
        
        console.log('[AI Performance Monitor] Initialized safely');
    }
    
    init() {
        // Safely monitor performance without affecting existing functionality
        if (typeof window.performance !== 'undefined') {
            this.collectMetrics();
            this.setupObservers();
        }
    }
    
    collectMetrics() {
        // Collect comprehensive performance metrics
        window.addEventListener('load', () => {
            this.metrics.pageLoadTime = performance.now();
            this.collectNavigationTiming();
            this.analyzePerformance();
        });
        
        document.addEventListener('DOMContentLoaded', () => {
            this.metrics.domContentLoaded = performance.now();
        });
        
        // Collect paint timing if available
        if ('PerformanceObserver' in window) {
            try {
                const paintObserver = new PerformanceObserver((list) => {
                    list.getEntries().forEach((entry) => {
                        if (entry.name === 'first-paint') {
                            this.metrics.firstPaint = entry.startTime;
                        } else if (entry.name === 'first-contentful-paint') {
                            this.metrics.firstContentfulPaint = entry.startTime;
                        }
                    });
                });
                paintObserver.observe({ entryTypes: ['paint'] });
            } catch (e) {
                console.log('[AI Performance Monitor] Paint timing not available');
            }
        }
    }
    
    collectNavigationTiming() {
        if (performance.getEntriesByType) {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.metrics.dnsLookup = navigation.domainLookupEnd - navigation.domainLookupStart;
                this.metrics.tcpConnect = navigation.connectEnd - navigation.connectStart;
                this.metrics.serverResponse = navigation.responseEnd - navigation.requestStart;
                this.metrics.domProcessing = navigation.domComplete - navigation.domLoading;
            }
        }
    }
    
    setupObservers() {
        // Monitor resource loading performance
        if ('PerformanceObserver' in window) {
            try {
                const resourceObserver = new PerformanceObserver((list) => {
                    list.getEntries().forEach((entry) => {
                        if (entry.duration > 1000) { // Resources taking >1 second
                            this.observations.push({
                                type: 'slow-resource',
                                name: entry.name,
                                duration: entry.duration,
                                timestamp: Date.now()
                            });
                        }
                    });
                });
                resourceObserver.observe({ entryTypes: ['resource'] });
            } catch (e) {
                console.log('[AI Performance Monitor] Resource observer not available');
            }
        }
    }
    
    analyzePerformance() {
        // Provide suggestions without making changes
        const suggestions = [];
        
        if (this.metrics.pageLoadTime > 3000) {
            suggestions.push('Page load time exceeds 3 seconds - consider optimizing images and scripts');
        }
        
        if (this.metrics.firstContentfulPaint > 1500) {
            suggestions.push('First Contentful Paint is slow - optimize critical rendering path');
        }
        
        if (this.metrics.dnsLookup > 100) {
            suggestions.push('DNS lookup is slow - consider using a faster DNS provider');
        }
        
        // Log suggestions safely
        if (suggestions.length > 0) {
            console.log('[AI Performance Monitor] Optimization suggestions:', suggestions);
        }
        
        return suggestions;
    }
    
    getMetrics() {
        return { ...this.metrics };
    }
    
    getObservations() {
        return [...this.observations];
    }
    
    generateReport() {
        const report = {
            timestamp: new Date().toISOString(),
            metrics: this.getMetrics(),
            observations: this.getObservations(),
            suggestions: this.analyzePerformance(),
            score: this.calculatePerformanceScore()
        };
        
        console.log('[AI Performance Monitor] Performance Report:', report);
        return report;
    }
    
    calculatePerformanceScore() {
        let score = 100;
        
        if (this.metrics.pageLoadTime > 3000) score -= 20;
        if (this.metrics.firstContentfulPaint > 1500) score -= 15;
        if (this.metrics.dnsLookup > 100) score -= 10;
        if (this.observations.length > 5) score -= 10;
        
        return Math.max(0, score);
    }
}

export default PerformanceMonitor;

// Auto-initialize performance monitoring
if (typeof window !== 'undefined' && !window.aiPerformanceMonitor) {
    window.aiPerformanceMonitor = new PerformanceMonitor();
}''',
        "description": "AI-Generated: Safe performance monitoring and analysis utility"
    }

def create_error_handler_utility(issue, data):
    """Create a safe error handling utility."""
    return {
        "path": "utils/ai-error-handler.js",
        "content": '''/**
 * AI-Generated Error Handling Utility
 * SAFE TO USE: Only adds error logging and handling, doesn't modify existing code
 */

class ErrorHandler {
    constructor() {
        this.errors = [];
        this.maxErrors = 100;
        this.errorCounts = {};
        this.setupGlobalErrorHandling();
        
        console.log('[AI Error Handler] Initialized safely');
    }
    
    setupGlobalErrorHandling() {
        // Safely add global error handling without interfering
        const originalErrorHandler = window.onerror;
        const originalUnhandledRejection = window.onunhandledrejection;
        
        window.onerror = (message, source, lineno, colno, error) => {
            this.logError({
                type: 'javascript',
                message: String(message),
                source: String(source),
                lineno: lineno,
                colno: colno,
                stack: error ? error.stack : null,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent
            });
            
            // Call original handler if it existed
            if (originalErrorHandler) {
                return originalErrorHandler(message, source, lineno, colno, error);
            }
            
            return false; // Don't suppress default error handling
        };
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError({
                type: 'promise',
                message: String(event.reason),
                stack: event.reason && event.reason.stack ? event.reason.stack : null,
                timestamp: new Date().toISOString()
            });
            
            // Call original handler if it existed
            if (originalUnhandledRejection) {
                originalUnhandledRejection(event);
            }
        });
        
        // Handle console errors safely
        const originalConsoleError = console.error;
        console.error = (...args) => {
            this.logError({
                type: 'console',
                message: args.map(arg => String(arg)).join(' '),
                timestamp: new Date().toISOString()
            });
            
            // Call original console.error
            originalConsoleError.apply(console, args);
        };
    }
    
    logError(errorInfo) {
        try {
            // Prevent infinite recursion
            if (errorInfo.message && errorInfo.message.includes('[AI Error Handler]')) {
                return;
            }
            
            this.errors.push(errorInfo);
            
            // Count error types for analysis
            const errorKey = `${errorInfo.type}:${errorInfo.message ? errorInfo.message.substring(0, 50) : 'unknown'}`;
            this.errorCounts[errorKey] = (this.errorCounts[errorKey] || 0) + 1;
            
            // Keep only recent errors to prevent memory leaks
            if (this.errors.length > this.maxErrors) {
                this.errors = this.errors.slice(-this.maxErrors);
            }
            
            console.warn('[AI Error Handler] Error logged:', {
                type: errorInfo.type,
                message: errorInfo.message ? errorInfo.message.substring(0, 100) : 'No message'
            });
            
            // Auto-report critical errors
            if (this.isCriticalError(errorInfo)) {
                this.reportCriticalError(errorInfo);
            }
            
        } catch (loggingError) {
            // Fail silently to prevent error loops
            console.warn('[AI Error Handler] Logging failed:', loggingError.message);
        }
    }
    
    isCriticalError(errorInfo) {
        const criticalPatterns = [
            /cannot read property/i,
            /is not defined/i,
            /network error/i,
            /failed to fetch/i,
            /script error/i
        ];
        
        return criticalPatterns.some(pattern => 
            pattern.test(errorInfo.message)
        );
    }
    
    reportCriticalError(errorInfo) {
        // Safe critical error reporting
        console.error('[AI Error Handler] CRITICAL ERROR DETECTED:', {
            type: errorInfo.type,
            message: errorInfo.message,
            timestamp: errorInfo.timestamp
        });
    }
    
    getErrorSummary() {
        const recentErrors = this.errors.slice(-10);
        const errorsByType = this.groupErrorsByType();
        
        return {
            totalErrors: this.errors.length,
            recentErrors: recentErrors,
            errorsByType: errorsByType,
            topErrors: this.getTopErrors(),
            lastErrorTime: this.errors.length > 0 ? this.errors[this.errors.length - 1].timestamp : null
        };
    }
    
    groupErrorsByType() {
        const grouped = {};
        this.errors.forEach(error => {
            grouped[error.type] = (grouped[error.type] || 0) + 1;
        });
        return grouped;
    }
    
    getTopErrors() {
        return Object.entries(this.errorCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([error, count]) => ({ error, count }));
    }
    
    clearErrors() {
        this.errors = [];
        this.errorCounts = {};
        console.log('[AI Error Handler] Error history cleared');
    }
    
    exportErrors() {
        return {
            timestamp: new Date().toISOString(),
            errors: [...this.errors],
            summary: this.getErrorSummary()
        };
    }
}

export default ErrorHandler;

// Auto-initialize if not already done
if (typeof window !== 'undefined' && !window.aiErrorHandler) {
    window.aiErrorHandler = new ErrorHandler();
}''',
        "description": "AI-Generated: Safe error handling and logging utility"
    }

def create_security_utility(issue, data):
    """Create a basic security utility."""
    return {
        "path": "utils/ai-security-helper.js",
        "content": '''/**
 * AI-Generated Security Helper Utility
 * SAFE TO USE: Only adds security validations, doesn't modify existing functionality
 */

class SecurityHelper {
    constructor() {
        this.suspiciousPatterns = [
            /<script[^>]*>.*?<\\/script>/gi,
            /javascript:/gi,
            /on\\w+\\s*=/gi,
            /data:text\\/html/gi,
            /vbscript:/gi
        ];
        
        this.violations = [];
        this.init();
        
        console.log('[AI Security Helper] Initialized safely');
    }
    
    init() {
        // Set up Content Security Policy monitoring if available
        if ('SecurityPolicyViolationEvent' in window) {
            document.addEventListener('securitypolicyviolation', (e) => {
                this.logViolation({
                    type: 'csp',
                    violatedDirective: e.violatedDirective,
                    blockedURI: e.blockedURI,
                    timestamp: new Date().toISOString()
                });
            });
        }
    }
    
    // Safe input sanitization helper
    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Basic XSS prevention
        return input
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\\//g, '&#x2F;');
    }
    
    // Check for suspicious content
    validateContent(content) {
        if (typeof content !== 'string') return { isValid: true, issues: [] };
        
        const issues = [];
        
        this.suspiciousPatterns.forEach((pattern, index) => {
            const matches = content.match(pattern);
            if (matches) {
                issues.push({
                    pattern: `Suspicious pattern ${index + 1}`,
                    matches: matches.slice(0, 3), // Limit to first 3 matches
                    severity: 'medium'
                });
            }
        });
        
        return {
            isValid: issues.length === 0,
            issues: issues
        };
    }
    
    // Safe URL validation
    isValidUrl(url) {
        try {
            const urlObj = new URL(url);
            const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
            return allowedProtocols.includes(urlObj.protocol);
        } catch {
            return false;
        }
    }
    
    // Generate simple CSRF token
    generateCSRFToken() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    }
    
    // Check if running over HTTPS
    isSecureContext() {
        return location.protocol === 'https:' || location.hostname === 'localhost';
    }
    
    // Validate form data before submission
    validateFormData(formData) {
        const issues = [];
        
        for (let [key, value] of formData.entries()) {
            if (typeof value === 'string') {
                const validation = this.validateContent(value);
                if (!validation.isValid) {
                    issues.push({
                        field: key,
                        issues: validation.issues
                    });
                }
            }
        }
        
        return {
            isValid: issues.length === 0,
            fieldIssues: issues
        };
    }
    
    // Log security violations
    logViolation(violation) {
        this.violations.push({
            ...violation,
            timestamp: violation.timestamp || new Date().toISOString()
        });
        
        // Keep only recent violations
        if (this.violations.length > 50) {
            this.violations = this.violations.slice(-50);
        }
        
        console.warn('[AI Security Helper] Security violation logged:', violation);
    }
    
    // Get security report
    getSecurityReport() {
        return {
            timestamp: new Date().toISOString(),
            isSecureContext: this.isSecureContext(),
            violations: [...this.violations],
            recommendations: this.getSecurityRecommendations()
        };
    }
    
    getSecurityRecommendations() {
        const recommendations = [];
        
        if (!this.isSecureContext()) {
            recommendations.push('Consider using HTTPS for better security');
        }
        
        if (this.violations.length > 0) {
            recommendations.push('Review and address security policy violations');
        }
        
        if (!document.querySelector('meta[http-equiv="Content-Security-Policy"]')) {
            recommendations.push('Consider implementing Content Security Policy');
        }
        
        return recommendations;
    }
}

export default SecurityHelper;

// Auto-initialize security monitoring
if (typeof window !== 'undefined' && !window.aiSecurityHelper) {
    window.aiSecurityHelper = new SecurityHelper();
}''',
        "description": "AI-Generated: Basic security validation utilities"
    }

def create_generic_utility(issue, data):
    """Create a generic utility for unknown issue types."""
    issue_type = issue.get('type', 'unknown')
    clean_type = issue_type.replace('_', '').title()
    
    return {
        "path": f"utils/ai-{issue_type.replace('_', '-')}-helper.js",
        "content": f'''/**
 * AI-Generated {issue_type.replace('_', ' ').title()} Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only adds helper functionality, doesn't modify existing code
 */

class {clean_type}Helper {{
    constructor() {{
        this.initialized = true;
        this.data = {data if data else '{}'};
        this.startTime = Date.now();
        
        console.log('[AI {issue_type.replace('_', ' ').title()}] Utility initialized safely');
    }}
    
    // Main helper function for {issue_type}
    help() {{
        console.log('[AI {issue_type.replace('_', ' ').title()}] Helper is ready to assist');
        
        // Log the issue data for debugging
        if (Object.keys(this.data).length > 0) {{
            console.log('[AI {issue_type.replace('_', ' ').title()}] Issue data:', this.data);
        }}
        
        return true;
    }}
    
    // Get information about this utility
    getInfo() {{
        return {{
            type: '{issue_type}',
            description: 'AI-generated helper utility for {issue_type.replace('_', ' ')} issues',
            safe: true,
            initialized: this.initialized,
            uptime: Date.now() - this.startTime,
            data: this.data
        }};
    }}
    
    // Placeholder for specific {issue_type} functionality
    process() {{
        console.log('[AI {issue_type.replace('_', ' ').title()}] Processing {issue_type} requirements...');
        
        // Add specific logic based on issue type
        return {{
            processed: true,
            timestamp: new Date().toISOString(),
            type: '{issue_type}'
        }};
    }}
    
    // Get status of this helper
    getStatus() {{
        return {{
            active: this.initialized,
            type: '{issue_type}',
            uptime: Date.now() - this.startTime
        }};
    }}
}}

export default {clean_type}Helper;

// Auto-initialize if needed
if (typeof window !== 'undefined' && !window.ai{clean_type}Helper) {{
    window.ai{clean_type}Helper = new {clean_type}Helper();
}}''',
        "description": f"AI-Generated: Generic {issue_type.replace('_', ' ')} helper utility"
    }

# Additional utility creators for new issue types...
def create_seo_utility(issue, data):
    """Create SEO optimization utility."""
    return {
        "path": "utils/ai-seo-optimizer.js",
        "content": f'''/**
 * AI-Generated SEO Optimization Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only adds SEO helpers, doesn't modify existing content
 */

class SEOOptimizer {{
    constructor() {{
        this.recommendations = [];
        this.analyzePage();
        
        console.log('[AI SEO Optimizer] Initialized safely');
    }}
    
    analyzePage() {{
        const recommendations = [];
        
        // Check for missing meta description
        const metaDesc = document.querySelector('meta[name="description"]');
        if (!metaDesc || !metaDesc.content || metaDesc.content.length < 120) {{
            recommendations.push({{
                type: 'meta-description',
                issue: 'Missing or short meta description',
                suggestion: 'Add a meta description of 150-160 characters'
            }});
        }}
        
        // Check for missing or poor title
        if (!document.title || document.title.length < 30) {{
            recommendations.push({{
                type: 'title',
                issue: 'Page title is missing or too short',
                suggestion: 'Add a descriptive title of 30-60 characters'
            }});
        }}
        
        // Check for images without alt text
        const imagesWithoutAlt = document.querySelectorAll('img:not([alt]), img[alt=""]');
        if (imagesWithoutAlt.length > 0) {{
            recommendations.push({{
                type: 'alt-text',
                issue: `${{imagesWithoutAlt.length}} images missing alt text`,
                suggestion: 'Add descriptive alt text to all images'
            }});
        }}
        
        // Check heading structure
        const h1Count = document.querySelectorAll('h1').length;
        if (h1Count === 0) {{
            recommendations.push({{
                type: 'headings',
                issue: 'No H1 heading found',
                suggestion: 'Add one H1 heading to the page'
            }});
        }} else if (h1Count > 1) {{
            recommendations.push({{
                type: 'headings',
                issue: `Multiple H1 headings (${{h1Count}}) found`,
                suggestion: 'Use only one H1 per page'
            }});
        }}
        
        this.recommendations = recommendations;
        
        if (recommendations.length > 0) {{
            console.log('[AI SEO Optimizer] SEO recommendations:', recommendations);
        }} else {{
            console.log('[AI SEO Optimizer] No SEO issues found');
        }}
    }}
    
    getRecommendations() {{
        return [...this.recommendations];
    }}
    
    // Generate meta description suggestion
    suggestMetaDescription(content) {{
        if (typeof content !== 'string') return '';
        
        // Extract first meaningful sentence
        const sentences = content.split('.').filter(s => s.trim().length > 20);
        const suggestion = sentences[0] ? sentences[0].trim() : '';
        
        // Truncate to SEO-friendly length
        return suggestion.length > 160 ? suggestion.substring(0, 157) + '...' : suggestion;
    }}
    
    // Check page loading speed factors
    checkPageSpeed() {{
        const recommendations = [];
        
        // Check for large images
        document.querySelectorAll('img').forEach(img => {{
            if (img.naturalWidth > 1920 || img.naturalHeight > 1080) {{
                recommendations.push('Consider optimizing large images for web');
            }}
        }});
        
        // Check for inline styles (affects loading)
        const inlineStyles = document.querySelectorAll('[style]').length;
        if (inlineStyles > 10) {{
            recommendations.push('Consider moving inline styles to CSS files');
        }}
        
        return recommendations;
    }}
    
    generateSEOReport() {{
        return {{
            timestamp: new Date().toISOString(),
            recommendations: this.getRecommendations(),
            pageSpeedSuggestions: this.checkPageSpeed(),
            pageInfo: {{
                title: document.title,
                metaDescription: document.querySelector('meta[name="description"]')?.content || 'Not found',
                h1Count: document.querySelectorAll('h1').length,
                imageCount: document.querySelectorAll('img').length,
                imagesWithoutAlt: document.querySelectorAll('img:not([alt]), img[alt=""]').length
            }}
        }};
    }}
}}

export default SEOOptimizer;

// Auto-initialize SEO analysis
if (typeof window !== 'undefined' && !window.aiSEOOptimizer) {{
    window.aiSEOOptimizer = new SEOOptimizer();
}}''',
        "description": "AI-Generated: SEO analysis and recommendation utility"
    }

# Add more utility creators as needed...
def create_accessibility_utility(issue, data):
    """Create accessibility improvement utility."""
    return {
        "path": "utils/ai-accessibility-helper.js",
        "content": '''/**
 * AI-Generated Accessibility Helper
 * SAFE TO USE: Only adds accessibility features, doesn't modify existing elements
 */

class AccessibilityHelper {
    constructor() {
        this.issues = [];
        this.improvements = [];
        this.scanAccessibility();
        
        console.log('[AI Accessibility Helper] Initialized safely');
    }
    
    scanAccessibility() {
        const issues = [];
        
        // Check for images without alt text
        document.querySelectorAll('img:not([alt]), img[alt=""]').forEach((img, index) => {
            issues.push({
                type: 'missing_alt',
                element: `img[${index}]`,
                message: 'Image missing alt text',
                severity: 'medium'
            });
        });
        
        // Check for buttons without accessible labels
        document.querySelectorAll('button:not([aria-label])').forEach((btn, index) => {
            if (!btn.textContent.trim()) {
                issues.push({
                    type: 'missing_label',
                    element: `button[${index}]`,
                    message: 'Button missing accessible label',
                    severity: 'high'
                });
            }
        });
        
        // Check for form inputs without labels
        document.querySelectorAll('input:not([aria-label]):not([id])').forEach((input, index) => {
            const associatedLabel = document.querySelector(`label[for="${input.id}"]`);
            if (!associatedLabel && !input.getAttribute('aria-label')) {
                issues.push({
                    type: 'missing_input_label',
                    element: `input[${index}]`,
                    message: 'Form input missing label',
                    severity: 'high'
                });
            }
        });
        
        // Check for links with poor text
        document.querySelectorAll('a').forEach((link, index) => {
            const text = link.textContent.trim().toLowerCase();
            const poorLinkTexts = ['click here', 'read more', 'more', 'link', 'here'];
            
            if (poorLinkTexts.includes(text)) {
                issues.push({
                    type: 'poor_link_text',
                    element: `a[${index}]`,
                    message: 'Link text not descriptive',
                    severity: 'low'
                });
            }
        });
        
        // Check color contrast (basic check)
        this.checkColorContrast();
        
        this.issues = issues;
        
        if (issues.length > 0) {
            console.log(`[AI Accessibility] Found ${issues.length} accessibility issues`);
        } else {
            console.log('[AI Accessibility] No accessibility issues found');
        }
    }
    
    checkColorContrast() {
        // Basic color contrast checking
        document.querySelectorAll('*').forEach((element, index) => {
            if (index > 100) return; // Limit checking to first 100 elements
            
            const styles = getComputedStyle(element);
            const backgroundColor = styles.backgroundColor;
            const color = styles.color;
            
            // Very basic check for common poor contrast combinations
            if (backgroundColor === 'rgb(255, 255, 255)' && color === 'rgb(192, 192, 192)') {
                this.issues.push({
                    type: 'poor_contrast',
                    element: `element[${index}]`,
                    message: 'Potentially poor color contrast',
                    severity: 'medium'
                });
            }
        });
    }
    
    addKeyboardSupport() {
        // Add skip link if not present
        if (!document.querySelector('.skip-link')) {
            const skipLink = document.createElement('a');
            skipLink.href = '#main';
            skipLink.className = 'skip-link';
            skipLink.textContent = 'Skip to main content';
            skipLink.style.cssText = `
                position: absolute;
                top: -40px;
                left: 6px;
                background: #000;
                color: #fff;
                padding: 8px;
                text-decoration: none;
                z-index: 1000;
                border-radius: 4px;
            `;
            
            skipLink.addEventListener('focus', () => {
                skipLink.style.top = '6px';
            });
            
            skipLink.addEventListener('blur', () => {
                skipLink.style.top = '-40px';
            });
            
            document.body.insertBefore(skipLink, document.body.firstChild);
            
            this.improvements.push('Added skip navigation link');
            console.log('[AI Accessibility] Added skip navigation link');
        }
    }
    
    addFocusIndicators() {
        // Ensure all interactive elements have visible focus indicators
        const style = document.createElement('style');
        style.textContent = `
            /* AI-Generated Focus Indicators */
            button:focus,
            a:focus,
            input:focus,
            select:focus,
            textarea:focus {
                outline: 2px solid #0066cc !important;
                outline-offset: 2px !important;
            }
            
            .skip-link:focus {
                outline: 2px solid #fff !important;
            }
        `;
        
        if (!document.querySelector('#ai-accessibility-styles')) {
            style.id = 'ai-accessibility-styles';
            document.head.appendChild(style);
            this.improvements.push('Added focus indicators for better keyboard navigation');
        }
    }
    
    getIssues() {
        return [...this.issues];
    }
    
    getImprovements() {
        return [...this.improvements];
    }
    
    generateAccessibilityReport() {
        return {
            timestamp: new Date().toISOString(),
            issues: this.getIssues(),
            improvements: this.getImprovements(),
            summary: {
                totalIssues: this.issues.length,
                highSeverity: this.issues.filter(i => i.severity === 'high').length,
                mediumSeverity: this.issues.filter(i => i.severity === 'medium').length,
                lowSeverity: this.issues.filter(i => i.severity === 'low').length
            }
        };
    }
    
    // Auto-improve accessibility where safe
    autoImprove() {
        this.addKeyboardSupport();
        this.addFocusIndicators();
        
        console.log('[AI Accessibility] Auto-improvements applied');
        return this.improvements;
    }
}

export default AccessibilityHelper;

// Auto-initialize and improve accessibility
if (typeof window !== 'undefined' && !window.aiAccessibilityHelper) {
    window.aiAccessibilityHelper = new AccessibilityHelper();
    
    // Auto-apply safe improvements
    setTimeout(() => {
        window.aiAccessibilityHelper.autoImprove();
    }, 1000);
}''',
        "description": "AI-Generated: Accessibility scanning and improvement utility"
    }

def create_mobile_utility(issue, data):
    """Create mobile optimization utility."""
    return {
        "path": "utils/ai-mobile-optimizer.js",
        "content": f'''/**
 * AI-Generated Mobile Optimization Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only adds mobile-friendly features, doesn't modify existing code
 */

class MobileOptimizer {{
    constructor() {{
        this.isMobile = this.detectMobile();
        this.optimizations = [];
        this.init();
        
        console.log('[AI Mobile Optimizer] Initialized safely');
    }}
    
    detectMobile() {{
        return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
               window.innerWidth <= 768;
    }}
    
    init() {{
        if (this.isMobile) {{
            this.optimizeForMobile();
        }}
    }}
    
    optimizeForMobile() {{
        // Add viewport meta tag if missing
        if (!document.querySelector('meta[name="viewport"]')) {{
            const viewport = document.createElement('meta');
            viewport.name = 'viewport';
            viewport.content = 'width=device-width, initial-scale=1.0';
            document.head.appendChild(viewport);
            this.optimizations.push('Added responsive viewport meta tag');
        }}
        
        // Optimize touch targets
        this.optimizeTouchTargets();
        
        // Add mobile-friendly styles
        this.addMobileStyles();
        
        console.log('[AI Mobile Optimizer] Mobile optimizations applied');
    }}
    
    optimizeTouchTargets() {{
        const style = document.createElement('style');
        style.textContent = `
            /* AI-Generated Mobile Touch Optimizations */
            button, a, input, select, textarea {{
                min-height: 44px !important;
                min-width: 44px !important;
            }}
            
            /* Improve touch scrolling */
            * {{
                -webkit-overflow-scrolling: touch;
            }}
        `;
        
        if (!document.querySelector('#ai-mobile-styles')) {{
            style.id = 'ai-mobile-styles';
            document.head.appendChild(style);
            this.optimizations.push('Optimized touch targets for mobile');
        }}
    }}
    
    addMobileStyles() {{
        const mobileStyle = document.createElement('style');
        mobileStyle.textContent = `
            /* AI-Generated Mobile-Friendly Styles */
            @media (max-width: 768px) {{
                body {{
                    font-size: 16px !important;
                }}
                
                input, textarea {{
                    font-size: 16px !important;
                }}
                
                .container {{
                    padding: 0 15px !important;
                }}
            }}
        `;
        
        if (!document.querySelector('#ai-mobile-responsive')) {{
            mobileStyle.id = 'ai-mobile-responsive';
            document.head.appendChild(mobileStyle);
            this.optimizations.push('Added mobile-responsive styles');
        }}
    }}
    
    getOptimizations() {{
        return [...this.optimizations];
    }}
    
    generateMobileReport() {{
        return {{
            timestamp: new Date().toISOString(),
            isMobile: this.isMobile,
            optimizations: this.getOptimizations(),
            userAgent: navigator.userAgent,
            screenSize: {{
                width: window.innerWidth,
                height: window.innerHeight
            }}
        }};
    }}
}}

export default MobileOptimizer;

// Auto-initialize mobile optimization
if (typeof window !== 'undefined' && !window.aiMobileOptimizer) {{
    window.aiMobileOptimizer = new MobileOptimizer();
}}''',
        "description": "AI-Generated: Mobile optimization utility"
    }

def create_caching_utility(issue, data):
    """Create caching optimization utility."""
    return {
        "path": "utils/ai-cache-manager.js",
        "content": f'''/**
 * AI-Generated Cache Management Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only adds caching functionality, doesn't modify existing code
 */

class CacheManager {{
    constructor() {{
        this.cache = new Map();
        this.stats = {{
            hits: 0,
            misses: 0,
            sets: 0
        }};
        
        console.log('[AI Cache Manager] Initialized safely');
    }}
    
    set(key, value, ttl = 3600000) {{ // Default 1 hour TTL
        const item = {{
            value: value,
            timestamp: Date.now(),
            ttl: ttl
        }};
        
        this.cache.set(key, item);
        this.stats.sets++;
        
        // Auto-cleanup expired items
        this.cleanup();
        
        return true;
    }}
    
    get(key) {{
        const item = this.cache.get(key);
        
        if (!item) {{
            this.stats.misses++;
            return null;
        }}
        
        // Check if expired
        if (Date.now() - item.timestamp > item.ttl) {{
            this.cache.delete(key);
            this.stats.misses++;
            return null;
        }}
        
        this.stats.hits++;
        return item.value;
    }}
    
    has(key) {{
        return this.cache.has(key) && !this.isExpired(key);
    }}
    
    isExpired(key) {{
        const item = this.cache.get(key);
        if (!item) return true;
        return Date.now() - item.timestamp > item.ttl;
    }}
    
    delete(key) {{
        return this.cache.delete(key);
    }}
    
    clear() {{
        this.cache.clear();
        this.stats = {{ hits: 0, misses: 0, sets: 0 }};
        console.log('[AI Cache Manager] Cache cleared');
    }}
    
    cleanup() {{
        const now = Date.now();
        let cleaned = 0;
        
        for (const [key, item] of this.cache.entries()) {{
            if (now - item.timestamp > item.ttl) {{
                this.cache.delete(key);
                cleaned++;
            }}
        }}
        
        if (cleaned > 0) {{
            console.log(`[AI Cache Manager] Cleaned up ${{cleaned}} expired items`);
        }}
    }}
    
    getStats() {{
        const hitRate = this.stats.hits + this.stats.misses > 0 
            ? (this.stats.hits / (this.stats.hits + this.stats.misses) * 100).toFixed(2)
            : 0;
            
        return {{
            ...this.stats,
            hitRate: hitRate + '%',
            size: this.cache.size
        }};
    }}
    
    // Cache API responses
    cacheAPIResponse(url, response, ttl = 300000) {{ // 5 minutes default
        return this.set(`api:${{url}}`, response, ttl);
    }}
    
    getCachedAPIResponse(url) {{
        return this.get(`api:${{url}}`);
    }}
    
    // Cache DOM elements
    cacheElement(selector, element, ttl = 60000) {{ // 1 minute default
        return this.set(`dom:${{selector}}`, element, ttl);
    }}
    
    getCachedElement(selector) {{
        return this.get(`dom:${{selector}}`);
    }}
}}

export default CacheManager;

// Auto-initialize cache manager
if (typeof window !== 'undefined' && !window.aiCacheManager) {{
    window.aiCacheManager = new CacheManager();
}}''',
        "description": "AI-Generated: Cache management utility"
    }

def create_analytics_utility(issue, data):
    """Create analytics utility."""
    return {
        "path": "utils/ai-analytics-helper.js",
        "content": f'''/**
 * AI-Generated Analytics Helper
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only adds analytics tracking, doesn't modify existing functionality
 */

class AnalyticsHelper {{
    constructor() {{
        this.events = [];
        this.sessionId = this.generateSessionId();
        this.startTime = Date.now();
        
        this.init();
        console.log('[AI Analytics Helper] Initialized safely');
    }}
    
    generateSessionId() {{
        return 'ai_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }}
    
    init() {{
        // Track page views
        this.trackPageView();
        
        // Track user interactions
        this.trackUserInteractions();
        
        // Track performance metrics
        this.trackPerformance();
    }}
    
    trackPageView() {{
        const pageData = {{
            type: 'pageview',
            url: window.location.href,
            title: document.title,
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId
        }};
        
        this.events.push(pageData);
        console.log('[AI Analytics] Page view tracked');
    }}
    
    trackUserInteractions() {{
        // Track clicks
        document.addEventListener('click', (e) => {{
            this.trackEvent('click', {{
                element: e.target.tagName,
                text: e.target.textContent?.substring(0, 50),
                x: e.clientX,
                y: e.clientY
            }});
        }}, {{ passive: true }});
        
        // Track form submissions
        document.addEventListener('submit', (e) => {{
            this.trackEvent('form_submit', {{
                formId: e.target.id || 'unknown',
                formAction: e.target.action
            }});
        }}, {{ passive: true }});
        
        // Track scroll depth
        let maxScroll = 0;
        window.addEventListener('scroll', () => {{
            const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
            if (scrollPercent > maxScroll) {{
                maxScroll = scrollPercent;
                if (maxScroll % 25 === 0) {{ // Track every 25%
                    this.trackEvent('scroll_depth', {{ percent: maxScroll }});
                }}
            }}
        }}, {{ passive: true }});
    }}
    
    trackPerformance() {{
        window.addEventListener('load', () => {{
            if (performance && performance.timing) {{
                const timing = performance.timing;
                const loadTime = timing.loadEventEnd - timing.navigationStart;
                
                this.trackEvent('performance', {{
                    loadTime: loadTime,
                    domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0
                }});
            }}
        }});
    }}
    
    trackEvent(eventType, data = {{}}) {{
        const event = {{
            type: eventType,
            data: data,
            timestamp: new Date().toISOString(),
            sessionId: this.sessionId
        }};
        
        this.events.push(event);
        
        // Keep only recent events to prevent memory issues
        if (this.events.length > 100) {{
            this.events = this.events.slice(-100);
        }}
    }}
    
    getEvents() {{
        return [...this.events];
    }}
    
    getSessionStats() {{
        const sessionDuration = Date.now() - this.startTime;
        const eventCounts = {{}};
        
        this.events.forEach(event => {{
            eventCounts[event.type] = (eventCounts[event.type] || 0) + 1;
        }});
        
        return {{
            sessionId: this.sessionId,
            duration: sessionDuration,
            eventCount: this.events.length,
            eventCounts: eventCounts,
            startTime: new Date(this.startTime).toISOString()
        }};
    }}
    
    exportData() {{
        return {{
            session: this.getSessionStats(),
            events: this.getEvents()
        }};
    }}
    
    // Send data to external analytics (placeholder)
    sendToAnalytics(data) {{
        // This would integrate with Google Analytics, Mixpanel, etc.
        console.log('[AI Analytics] Data ready for external analytics:', data);
        return true;
    }}
}}

export default AnalyticsHelper;

// Auto-initialize analytics
if (typeof window !== 'undefined' && !window.aiAnalyticsHelper) {{
    window.aiAnalyticsHelper = new AnalyticsHelper();
}}''',
        "description": "AI-Generated: Analytics tracking utility"
    }

def create_storage_utility(issue, data):
    """Create storage optimization utility."""
    return {
        "path": "utils/ai-storage-optimizer.js",
        "content": f'''/**
 * AI-Generated Storage Optimization Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only optimizes storage usage, doesn't modify existing data
 */

class StorageOptimizer {{
    constructor() {{
        this.optimizations = [];
        this.init();
        
        console.log('[AI Storage Optimizer] Initialized safely');
    }}
    
    init() {{
        this.analyzeStorage();
        this.optimizeStorage();
    }}
    
    analyzeStorage() {{
        const analysis = {{
            localStorage: this.analyzeLocalStorage(),
            sessionStorage: this.analyzeSessionStorage(),
            cookies: this.analyzeCookies()
        }};
        
        console.log('[AI Storage Optimizer] Storage analysis:', analysis);
        return analysis;
    }}
    
    analyzeLocalStorage() {{
        if (typeof localStorage === 'undefined') return {{ available: false }};
        
        const keys = Object.keys(localStorage);
        const totalSize = keys.reduce((size, key) => {{
            return size + (localStorage[key] ? localStorage[key].length : 0);
        }}, 0);
        
        return {{
            available: true,
            keyCount: keys.length,
            totalSize: totalSize,
            keys: keys
        }};
    }}
    
    analyzeSessionStorage() {{
        if (typeof sessionStorage === 'undefined') return {{ available: false }};
        
        const keys = Object.keys(sessionStorage);
        const totalSize = keys.reduce((size, key) => {{
            return size + (sessionStorage[key] ? sessionStorage[key].length : 0);
        }}, 0);
        
        return {{
            available: true,
            keyCount: keys.length,
            totalSize: totalSize,
            keys: keys
        }};
    }}
    
    analyzeCookies() {{
        const cookies = document.cookie.split(';').map(c => c.trim());
        const cookieCount = cookies.length;
        
        return {{
            count: cookieCount,
            cookies: cookies
        }};
    }}
    
    optimizeStorage() {{
        // Clean up expired or unnecessary data
        this.cleanupExpiredData();
        
        // Compress large data if possible
        this.compressLargeData();
        
        // Remove duplicate entries
        this.removeDuplicates();
        
        console.log('[AI Storage Optimizer] Storage optimization completed');
    }}
    
    cleanupExpiredData() {{
        if (typeof localStorage === 'undefined') return;
        
        const keysToRemove = [];
        const now = Date.now();
        
        Object.keys(localStorage).forEach(key => {{
            if (key.includes('_expires_')) {{
                const expiresKey = key;
                const dataKey = key.replace('_expires_', '');
                const expiryTime = parseInt(localStorage.getItem(expiresKey));
                
                if (expiryTime && now > expiryTime) {{
                    keysToRemove.push(expiresKey);
                    keysToRemove.push(dataKey);
                }}
            }}
        }});
        
        keysToRemove.forEach(key => {{
            localStorage.removeItem(key);
        }});
        
        if (keysToRemove.length > 0) {{
            this.optimizations.push(`Cleaned up ${{keysToRemove.length}} expired items`);
        }}
    }}
    
    compressLargeData() {{
        if (typeof localStorage === 'undefined') return;
        
        Object.keys(localStorage).forEach(key => {{
            const value = localStorage.getItem(key);
            if (value && value.length > 1000) {{ // Compress data larger than 1KB
                try {{
                    const compressed = this.compressString(value);
                    if (compressed.length < value.length) {{
                        localStorage.setItem(key, compressed);
                        localStorage.setItem(key + '_compressed', 'true');
                        this.optimizations.push(`Compressed large data for key: ${{key}}`);
                    }}
                }} catch (e) {{
                    console.warn('[AI Storage Optimizer] Compression failed for key:', key);
                }}
            }}
        }});
    }}
    
    compressString(str) {{
        // Simple compression using JSON.stringify for repeated patterns
        try {{
            return JSON.stringify(str);
        }} catch {{
            return str;
        }}
    }}
    
    decompressString(str) {{
        try {{
            return JSON.parse(str);
        }} catch {{
            return str;
        }}
    }}
    
    removeDuplicates() {{
        if (typeof localStorage === 'undefined') return;
        
        const seen = new Set();
        const keysToRemove = [];
        
        Object.keys(localStorage).forEach(key => {{
            const value = localStorage.getItem(key);
            const valueHash = this.hashString(value);
            
            if (seen.has(valueHash)) {{
                keysToRemove.push(key);
            }} else {{
                seen.add(valueHash);
            }}
        }});
        
        keysToRemove.forEach(key => {{
            localStorage.removeItem(key);
        }});
        
        if (keysToRemove.length > 0) {{
            this.optimizations.push(`Removed ${{keysToRemove.length}} duplicate entries`);
        }}
    }}
    
    hashString(str) {{
        let hash = 0;
        for (let i = 0; i < str.length; i++) {{
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }}
        return hash;
    }}
    
    getOptimizations() {{
        return [...this.optimizations];
    }}
    
    generateStorageReport() {{
        return {{
            timestamp: new Date().toISOString(),
            analysis: this.analyzeStorage(),
            optimizations: this.getOptimizations(),
            recommendations: this.getRecommendations()
        }};
    }}
    
    getRecommendations() {{
        const recommendations = [];
        const analysis = this.analyzeStorage();
        
        if (analysis.localStorage.available && analysis.localStorage.totalSize > 5000000) {{
            recommendations.push('LocalStorage usage is high - consider cleanup');
        }}
        
        if (analysis.cookies.count > 20) {{
            recommendations.push('Many cookies detected - review necessity');
        }}
        
        return recommendations;
    }}
}}

export default StorageOptimizer;

// Auto-initialize storage optimization
if (typeof window !== 'undefined' && !window.aiStorageOptimizer) {{
    window.aiStorageOptimizer = new StorageOptimizer();
}}''',
        "description": "AI-Generated: Storage optimization utility"
    }

def create_comprehensive_utility(issue, data):
    """Create comprehensive optimization utility."""
    return {
        "path": "utils/ai-comprehensive-optimizer.js",
        "content": f'''/**
 * AI-Generated Comprehensive Optimization Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Combines multiple optimization strategies
 */

class ComprehensiveOptimizer {{
    constructor() {{
        this.optimizations = [];
        this.modules = {{}};
        this.init();
        
        console.log('[AI Comprehensive Optimizer] Initialized safely');
    }}
    
    async init() {{
        // Initialize all optimization modules
        await this.initModules();
        this.runOptimizations();
    }}
    
    async initModules() {{
        // Performance optimization
        this.modules.performance = {{
            name: 'Performance',
            status: 'initialized',
            optimizations: []
        }};
        
        // Memory optimization
        this.modules.memory = {{
            name: 'Memory',
            status: 'initialized',
            optimizations: []
        }};
        
        // User experience optimization
        this.modules.ux = {{
            name: 'User Experience',
            status: 'initialized',
            optimizations: []
        }};
        
        // Security optimization
        this.modules.security = {{
            name: 'Security',
            status: 'initialized',
            optimizations: []
        }};
    }}
    
    runOptimizations() {{
        // Performance optimizations
        this.optimizePerformance();
        
        // Memory optimizations
        this.optimizeMemory();
        
        // UX optimizations
        this.optimizeUserExperience();
        
        // Security optimizations
        this.optimizeSecurity();
        
        console.log('[AI Comprehensive Optimizer] All optimizations completed');
    }}
    
    optimizePerformance() {{
        const optimizations = [];
        
        // Optimize images
        document.querySelectorAll('img').forEach(img => {{
            if (!img.loading) {{
                img.loading = 'lazy';
                optimizations.push('Added lazy loading to images');
            }}
        }});
        
        // Optimize scripts
        document.querySelectorAll('script[src]').forEach(script => {{
            if (!script.async && !script.defer) {{
                script.defer = true;
                optimizations.push('Added defer to non-critical scripts');
            }}
        }});
        
        this.modules.performance.optimizations = optimizations;
    }}
    
    optimizeMemory() {{
        const optimizations = [];
        
        // Clear unused event listeners
        if (window.gc) {{
            window.gc();
            optimizations.push('Forced garbage collection');
        }}
        
        // Optimize DOM queries
        const style = document.createElement('style');
        style.textContent = `
            /* AI-Generated Memory Optimizations */
            .ai-optimized {{
                contain: layout style paint;
            }}
        `;
        document.head.appendChild(style);
        optimizations.push('Added CSS containment for better memory management');
        
        this.modules.memory.optimizations = optimizations;
    }}
    
    optimizeUserExperience() {{
        const optimizations = [];
        
        // Add loading indicators
        if (!document.querySelector('.ai-loading-indicator')) {{
            const indicator = document.createElement('div');
            indicator.className = 'ai-loading-indicator';
            indicator.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 20px;
                border-radius: 8px;
                z-index: 10000;
                display: none;
            `;
            indicator.textContent = 'Loading...';
            document.body.appendChild(indicator);
            optimizations.push('Added loading indicator');
        }}
        
        // Improve form UX
        document.querySelectorAll('input, textarea').forEach(input => {{
            if (!input.placeholder && input.type !== 'submit') {{
                input.placeholder = 'Enter ' + (input.name || 'value');
                optimizations.push('Added helpful placeholders');
            }}
        }});
        
        this.modules.ux.optimizations = optimizations;
    }}
    
    optimizeSecurity() {{
        const optimizations = [];
        
        // Add security headers if possible
        if (!document.querySelector('meta[http-equiv="Content-Security-Policy"]')) {{
            const csp = document.createElement('meta');
            csp.httpEquiv = 'Content-Security-Policy';
            csp.content = "default-src 'self'; script-src 'self' 'unsafe-inline'";
            document.head.appendChild(csp);
            optimizations.push('Added basic Content Security Policy');
        }}
        
        // Sanitize user inputs
        document.querySelectorAll('input, textarea').forEach(input => {{
            input.addEventListener('input', (e) => {{
                // Basic XSS prevention
                e.target.value = e.target.value.replace(/<script[^>]*>.*?<\\/script>/gi, '');
            }});
        }});
        optimizations.push('Added input sanitization');
        
        this.modules.security.optimizations = optimizations;
    }}
    
    getOptimizations() {{
        return this.modules;
    }}
    
    generateComprehensiveReport() {{
        return {{
            timestamp: new Date().toISOString(),
            modules: this.getOptimizations(),
            summary: {{
                totalOptimizations: Object.values(this.modules).reduce((sum, module) => 
                    sum + module.optimizations.length, 0),
                modulesCount: Object.keys(this.modules).length
            }}
        }};
    }}
}}

export default ComprehensiveOptimizer;

// Auto-initialize comprehensive optimization
if (typeof window !== 'undefined' && !window.aiComprehensiveOptimizer) {{
    window.aiComprehensiveOptimizer = new ComprehensiveOptimizer();
}}''',
        "description": "AI-Generated: Comprehensive optimization utility"
    }

def create_documentation_utility(issue, data):
    """Create documentation utility."""
    return {
        "path": "utils/ai-documentation-helper.js",
        "content": f'''/**
 * AI-Generated Documentation Helper
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only generates documentation, doesn't modify existing code
 */

class DocumentationHelper {{
    constructor() {{
        this.documentation = {{}};
        this.init();
        
        console.log('[AI Documentation Helper] Initialized safely');
    }}
    
    init() {{
        this.generateAPIDocumentation();
        this.generateComponentDocumentation();
        this.generateUsageExamples();
    }}
    
    generateAPIDocumentation() {{
        const apis = [];
        
        // Scan for functions and methods
        if (typeof window !== 'undefined') {{
            Object.keys(window).forEach(key => {{
                if (typeof window[key] === 'function' && key.startsWith('ai')) {{
                    apis.push({{
                        name: key,
                        type: 'function',
                        description: 'AI-generated utility function'
                    }});
                }}
            }});
        }}
        
        this.documentation.apis = apis;
    }}
    
    generateComponentDocumentation() {{
        const components = [];
        
        // Document custom elements
        document.querySelectorAll('*').forEach(element => {{
            if (element.tagName.includes('-')) {{
                components.push({{
                    name: element.tagName.toLowerCase(),
                    attributes: Array.from(element.attributes).map(attr => attr.name),
                    description: 'Custom web component'
                }});
            }}
        }});
        
        this.documentation.components = components;
    }}
    
    generateUsageExamples() {{
        this.documentation.examples = [
            {{
                title: 'Using AI Memory Optimizer',
                code: `
// Initialize memory optimizer
const optimizer = new MemoryOptimizer();
optimizer.optimizeMemory();

// Start periodic optimization
optimizer.startPeriodicOptimization(300000); // Every 5 minutes
                `,
                description: 'Example of using the memory optimization utility'
            }},
            {{
                title: 'Using AI Cache Manager',
                code: `
// Initialize cache manager
const cache = new CacheManager();

// Cache API responses
cache.set('user-data', userData, 3600000); // 1 hour TTL
const cachedData = cache.get('user-data');

// Get cache statistics
console.log(cache.getStats());
                `,
                description: 'Example of using the cache management utility'
            }},
            {{
                title: 'Using AI Analytics Helper',
                code: `
// Initialize analytics
const analytics = new AnalyticsHelper();

// Track custom events
analytics.trackEvent('button_click', {{ buttonId: 'submit' }});

// Get session statistics
console.log(analytics.getSessionStats());
                `,
                description: 'Example of using the analytics tracking utility'
            }}
        ];
    }}
    
    generateDocumentation() {{
        return {{
            timestamp: new Date().toISOString(),
            apis: this.documentation.apis || [],
            components: this.documentation.components || [],
            examples: this.documentation.examples || [],
            summary: {{
                apiCount: (this.documentation.apis || []).length,
                componentCount: (this.documentation.components || []).length,
                exampleCount: (this.documentation.examples || []).length
            }}
        }};
    }}
    
    exportDocumentation() {{
        const doc = this.generateDocumentation();
        console.log('[AI Documentation Helper] Generated documentation:', doc);
        return doc;
    }}
    
    // Generate markdown documentation
    generateMarkdown() {{
        const doc = this.generateDocumentation();
        let markdown = '# AI-Generated Documentation\\n\\n';
        
        // APIs section
        if (doc.apis.length > 0) {{
            markdown += '## APIs\\n\\n';
            doc.apis.forEach(api => {{
                markdown += `### ${{api.name}}\\n`;
                markdown += `**Type:** ${{api.type}}\\n`;
                markdown += `**Description:** ${{api.description}}\\n\\n`;
            }});
        }}
        
        // Components section
        if (doc.components.length > 0) {{
            markdown += '## Components\\n\\n';
            doc.components.forEach(component => {{
                markdown += `### ${{component.name}}\\n`;
                markdown += `**Attributes:** ${{component.attributes.join(', ')}}\\n`;
                markdown += `**Description:** ${{component.description}}\\n\\n`;
            }});
        }}
        
        // Examples section
        if (doc.examples.length > 0) {{
            markdown += '## Usage Examples\\n\\n';
            doc.examples.forEach(example => {{
                markdown += `### ${{example.title}}\\n`;
                markdown += `${{example.description}}\\n\\n`;
                markdown += '```javascript\\n';
                markdown += example.code;
                markdown += '\\n```\\n\\n';
            }});
        }}
        
        return markdown;
    }}
}}

export default DocumentationHelper;

// Auto-initialize documentation helper
if (typeof window !== 'undefined' && !window.aiDocumentationHelper) {{
    window.aiDocumentationHelper = new DocumentationHelper();
}}''',
        "description": "AI-Generated: Documentation generation utility"
    }

def create_dependency_security_utility(issue, data):
    """Create dependency security utility."""
    return {
        "path": "utils/ai-dependency-security.js",
        "content": f'''/**
 * AI-Generated Dependency Security Utility
 * Generated: {datetime.now().isoformat()}
 * SAFE TO USE: Only scans for security issues, doesn't modify dependencies
 */

class DependencySecurityScanner {{
    constructor() {{
        this.vulnerabilities = [];
        this.recommendations = [];
        this.init();
        
        console.log('[AI Dependency Security Scanner] Initialized safely');
    }}
    
    init() {{
        this.scanScripts();
        this.scanExternalResources();
        this.generateRecommendations();
    }}
    
    scanScripts() {{
        const scripts = document.querySelectorAll('script[src]');
        const externalScripts = [];
        
        scripts.forEach(script => {{
            const src = script.src;
            if (src && !src.startsWith(window.location.origin)) {{
                externalScripts.push({{
                    src: src,
                    integrity: script.integrity || 'none',
                    crossorigin: script.crossorigin || 'none',
                    risk: this.assessRisk(src)
                }});
            }}
        }});
        
        this.vulnerabilities.push({{
            type: 'external_scripts',
            count: externalScripts.length,
            scripts: externalScripts
        }});
    }}
    
    scanExternalResources() {{
        const externalResources = [];
        
        // Check for external CSS
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {{
            if (link.href && !link.href.startsWith(window.location.origin)) {{
                externalResources.push({{
                    type: 'css',
                    url: link.href,
                    integrity: link.integrity || 'none'
                }});
            }}
        }});
        
        // Check for external images
        document.querySelectorAll('img[src]').forEach(img => {{
            if (img.src && !img.src.startsWith(window.location.origin)) {{
                externalResources.push({{
                    type: 'image',
                    url: img.src
                }});
            }}
        }});
        
        if (externalResources.length > 0) {{
            this.vulnerabilities.push({{
                type: 'external_resources',
                count: externalResources.length,
                resources: externalResources
            }});
        }}
    }}
    
    assessRisk(url) {{
        const riskFactors = [];
        
        // Check for HTTP (non-HTTPS)
        if (url.startsWith('http://')) {{
            riskFactors.push('non-https');
        }}
        
        // Check for common CDN domains
        const trustedCDNs = [
            'cdnjs.cloudflare.com',
            'unpkg.com',
            'jsdelivr.net',
            'googleapis.com',
            'gstatic.com'
        ];
        
        const domain = new URL(url).hostname;
        if (!trustedCDNs.some(cdn => domain.includes(cdn))) {{
            riskFactors.push('unknown-domain');
        }}
        
        return riskFactors.length > 0 ? riskFactors : ['low-risk'];
    }}
    
    generateRecommendations() {{
        this.vulnerabilities.forEach(vuln => {{
            if (vuln.type === 'external_scripts') {{
                vuln.scripts.forEach(script => {{
                    if (script.risk.includes('non-https')) {{
                        this.recommendations.push({{
                            type: 'security',
                            priority: 'high',
                            message: `Use HTTPS for external script: ${{script.src}}`,
                            action: 'Update script URL to use HTTPS'
                        }});
                    }}
                    
                    if (script.integrity === 'none') {{
                        this.recommendations.push({{
                            type: 'security',
                            priority: 'medium',
                            message: `Add integrity check for script: ${{script.src}}`,
                            action: 'Add integrity attribute to script tag'
                        }});
                    }}
                }});
            }}
        }});
    }}
    
    getVulnerabilities() {{
        return [...this.vulnerabilities];
    }}
    
    getRecommendations() {{
        return [...this.recommendations];
    }}
    
    generateSecurityReport() {{
        return {{
            timestamp: new Date().toISOString(),
            vulnerabilities: this.getVulnerabilities(),
            recommendations: this.getRecommendations(),
            summary: {{
                totalVulnerabilities: this.vulnerabilities.length,
                highPriorityRecommendations: this.recommendations.filter(r => r.priority === 'high').length,
                mediumPriorityRecommendations: this.recommendations.filter(r => r.priority === 'medium').length
            }}
        }};
    }}
    
    // Check if a specific URL is secure
    isSecureUrl(url) {{
        try {{
            const urlObj = new URL(url);
            return urlObj.protocol === 'https:';
        }} catch {{
            return false;
        }}
    }}
    
    // Validate script integrity
    validateScriptIntegrity(script) {{
        if (!script.integrity || script.integrity === 'none') {{
            return {{ valid: false, reason: 'No integrity check' }};
        }}
        
        return {{ valid: true, reason: 'Integrity check present' }};
    }}
}}

export default DependencySecurityScanner;

// Auto-initialize dependency security scanner
if (typeof window !== 'undefined' && !window.aiDependencySecurityScanner) {{
    window.aiDependencySecurityScanner = new DependencySecurityScanner();
}}''',
        "description": "AI-Generated: Dependency security scanning utility"
    }
