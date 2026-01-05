"""
Enhanced analyzer that detects various types of issues from monitoring data.
Generates safe, actionable issues for the AI engine to address.
"""

from config_loader import load_rules
from utils import detect_framework, log_issue
from bug_detector import run_bug_detection
from e2e_tester import run_e2e_tests  # Keep for backward compatibility
from enhanced_bug_detector import comprehensive_bug_detection
from structured_e2e_tester import run_structured_e2e_tests
from lighthouse_tester import run_lighthouse_audit
from axe_accessibility_tester import run_axe_accessibility_audit
import asyncio

async def analyze_data(data, repo_files, url, repo_path):

    """

    Enhanced analysis function that handles Google Analytics, log files, and system data.

    Detects multiple types of issues while maintaining safety-first approach.

    

    Args:

        data (dict): Combined monitoring data from GA, logs, and system metrics

        repo_files (list): List of files in the repository

        url (str): The URL of the deployed application.

        repo_path (str): The local path to the cloned repository.

        

    Returns:

        list: Issues detected for the AI to fix (only safe, additive changes)

    """

    framework = detect_framework(repo_files)

    rules = load_rules(framework)

    issues = []

    

    print(f"[INFO] Analyzing data from sources: {data.get('data_sources', [])}")

    print(f"[INFO] Using CONSERVATIVE analysis mode to prevent breaking changes")

    

    # 1. Analyze Google Analytics data for UX issues

    analytics = data.get("analytics", {})

    if analytics and "error" not in analytics:

        ux_issues = analyze_google_analytics(analytics, rules, framework)

        issues.extend(ux_issues)

    

    # 2. Analyze server logs for performance and error issues

    metrics = data.get("metrics", {})

    if metrics:

        performance_issues = analyze_server_metrics(metrics, rules, framework)

        issues.extend(performance_issues)

    

    # 3. Analyze error patterns for error handling improvements

    errors = data.get("errors", {})

    if errors:

        error_issues = analyze_error_patterns(errors, rules, framework)

        issues.extend(error_issues)

    

    # 4. Analyze system performance for optimization opportunities

    system = data.get("system", {})

    if system:

        system_issues = analyze_system_performance(system, rules, framework)

        issues.extend(system_issues)

    

    # 5. Analyze combined metrics for comprehensive improvements

    combined = metrics.get("combined", {})

    if combined:

        combined_issues = analyze_combined_metrics(combined, rules, framework)

        issues.extend(combined_issues)

    

    # 6. Analyze repository structure for code quality issues

    repo_issues = analyze_repository_structure(repo_files, framework)

    issues.extend(repo_issues)

    

    # 7. Check for security-related issues

    security_issues = analyze_security_aspects(data, repo_files, framework)

    issues.extend(security_issues)



    # 8. Analyze for common application bugs

    if url and repo_path:

        print(f"[INFO] Running bug detection for URL: {url}")

        bugs = run_bug_detection(url, repo_path)

        if bugs:

            log_issue("Bug Detection", f"Found {len(bugs)} potential bugs.", "WARNING")

            for bug in bugs:

                issues.append({

                    "type": "bug_report",

                    "severity": "high",

                    "description": bug["description"],

                    "details": bug["details"],

                    "framework": framework,

                    "language": "n/a",

                    "target_file": "bug_report.md",

                    "data": bug,

                    "safe_mode": True

                })

    # 8.5. Enhanced comprehensive bug detection (NEW)
    if url and repo_path:
        print(f"[INFO] Running enhanced comprehensive bug detection for URL: {url}")
        try:
            enhanced_bugs = await comprehensive_bug_detection(url, repo_path)
            if enhanced_bugs:
                log_issue("Enhanced Bug Detection", f"Found {len(enhanced_bugs)} UI/UX bugs.", "WARNING")
                print(f"[ENHANCED_BUG_DETECTOR] ========================================")
                print(f"[ENHANCED_BUG_DETECTOR] Detected {len(enhanced_bugs)} bugs:")
                
                # Group bugs by type for better visibility
                bug_types = {}
                for bug in enhanced_bugs:
                    bug_type = bug.get("type", "ui_bug")
                    if bug_type not in bug_types:
                        bug_types[bug_type] = []
                    bug_types[bug_type].append(bug)
                
                # Log each bug type
                for bug_type, type_bugs in bug_types.items():
                    print(f"[ENHANCED_BUG_DETECTOR] - {bug_type}: {len(type_bugs)} bugs")
                    for i, bug in enumerate(type_bugs[:3], 1):  # Show first 3 of each type
                        print(f"[ENHANCED_BUG_DETECTOR]   {i}. {bug.get('description', 'No description')[:80]}")
                        print(f"[ENHANCED_BUG_DETECTOR]      Details: {bug.get('details', 'No details')[:100]}")
                
                print(f"[ENHANCED_BUG_DETECTOR] ========================================")
                
                for bug in enhanced_bugs:
                    issues.append({
                        "type": bug.get("type", "ui_bug"),
                        "severity": bug.get("severity", "medium"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": bug.get("target_file") or determine_target_file_for_bug(bug, repo_path),
                        "data": bug.get("data", {}),
                        "safe_mode": True
                    })
            else:
                print(f"[ENHANCED_BUG_DETECTOR] No UI/UX bugs detected")
        except Exception as e:
            print(f"[WARNING] Enhanced bug detection failed: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")

    # 8.6. Lighthouse performance audit (NEW)
    if url:
        print(f"[INFO] Running Lighthouse performance audit for URL: {url}")
        try:
            lighthouse_bugs = await run_lighthouse_audit(url)
            if lighthouse_bugs:
                log_issue("Lighthouse", f"Found {len(lighthouse_bugs)} performance issues.", "WARNING")
                for bug in lighthouse_bugs:
                    issues.append({
                        "type": bug.get("type", "performance"),
                        "severity": bug.get("severity", "medium"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": "utils/ai-performance-monitor.js",
                        "data": bug.get("data", {}),
                        "safe_mode": True
                    })
        except Exception as e:
            print(f"[WARNING] Lighthouse audit failed: {e}")

    # 8.7. Axe accessibility audit (NEW)
    if url:
        print(f"[INFO] Running Axe accessibility audit for URL: {url}")
        try:
            axe_bugs = await run_axe_accessibility_audit(url)
            if axe_bugs:
                log_issue("Axe Accessibility", f"Found {len(axe_bugs)} accessibility issues.", "WARNING")
                for bug in axe_bugs:
                    issues.append({
                        "type": bug.get("type", "accessibility"),
                        "severity": bug.get("severity", "medium"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": "utils/ai-accessibility-helper.js",
                        "data": bug.get("data", {}),
                        "safe_mode": True
                    })
        except Exception as e:
            print(f"[WARNING] Axe accessibility audit failed: {e}")

    # 9. Run structured E2E tests (NEW - replaces AI-generated tests)
    if url:
        print(f"[INFO] Running structured E2E tests for URL: {url}")
        try:
            structured_e2e_bugs = await run_structured_e2e_tests(url)
            if structured_e2e_bugs:
                log_issue("Structured E2E Test", f"Found {len(structured_e2e_bugs)} functional bugs.", "ERROR")
                for bug in structured_e2e_bugs:
                    issues.append({
                        "type": bug.get("type", "functional_bug"),
                        "severity": bug.get("severity", "high"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": "bug_report.md",
                        "data": bug.get("data", {}),
                        "safe_mode": True
                    })
        except Exception as e:
            print(f"[WARNING] Structured E2E tests failed: {e}")

    # 9.5. Run legacy AI-generated E2E tests (fallback, optional)
    if url:
        # Only run if structured tests found no issues (as a backup)
        try:
            legacy_e2e_bugs = await run_e2e_tests(url)
            if legacy_e2e_bugs:
                log_issue("Legacy E2E Test", f"Found {len(legacy_e2e_bugs)} additional bugs.", "ERROR")
                issues.extend(legacy_e2e_bugs)
        except Exception as e:
            print(f"[WARNING] Legacy E2E tests failed: {e}")



    print(f"[INFO] Analysis complete: {len(issues)} safe improvements suggested")

    

    # Return only issues marked as safe

    safe_issues = [issue for issue in issues if issue.get('safe_mode', False)]

    print(f"[INFO] Filtered to {len(safe_issues)} safe issues for implementation")

    

    return safe_issues

def analyze_google_analytics(analytics, rules, framework):
    """Analyze Google Analytics data for user experience issues."""
    issues = []
    
    # High bounce rate analysis
    bounce_rate = analytics.get("avg_bounce_rate", 0)
    if bounce_rate > rules.get("bounce_threshold", 0.55):
        log_issue("UX", f"High bounce rate: {bounce_rate:.2%}", "WARNING")
        issues.append({
            "type": "user_experience",
            "severity": "medium",
            "description": f"High bounce rate ({bounce_rate:.2%}) indicates users leaving quickly. Add engagement features.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-engagement-booster.js",
            "data": {"bounce_rate": bounce_rate},
            "safe_mode": True
        })
    
    # Low engagement analysis
    avg_session_duration = analytics.get("avg_session_duration", 0)
    if avg_session_duration < 30:  # Less than 30 seconds
        log_issue("UX", f"Low session duration: {avg_session_duration}s", "WARNING")
        issues.append({
            "type": "user_experience",
            "severity": "medium",
            "description": f"Low average session duration ({avg_session_duration}s). Create engagement utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-engagement-booster.js",
            "data": {"session_duration": avg_session_duration},
            "safe_mode": True
        })
    
    # Mobile vs Desktop analysis
    device_breakdown = analytics.get("device_breakdown", {})
    if device_breakdown:
        mobile_users = device_breakdown.get("MOBILE", 0)
        total_users = sum(device_breakdown.values())
        
        if total_users > 0:
            mobile_percentage = mobile_users / total_users
            if mobile_percentage > 0.6:  # More than 60% mobile users
                issues.append({
                    "type": "mobile_optimization",
                    "severity": "medium",
                    "description": f"High mobile traffic ({mobile_percentage:.1%}). Create mobile optimization utilities.",
                    "framework": framework,
                    "language": "javascript",
                    "target_file": "utils/ai-mobile-optimizer.js",
                    "data": {"mobile_percentage": mobile_percentage},
                    "safe_mode": True
                })
    
    # SEO analysis based on page views
    total_pageviews = analytics.get("total_pageviews", 0)
    if total_pageviews < 10:  # Very low traffic
        issues.append({
            "type": "seo_optimization",
            "severity": "low",
            "description": f"Low page views ({total_pageviews}). Create SEO optimization utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-seo-optimizer.js",
            "data": {"pageviews": total_pageviews},
            "safe_mode": True
        })
    
    return issues

def analyze_server_metrics(metrics, rules, framework):
    """Analyze server metrics for performance issues."""
    issues = []
    
    access_logs = metrics.get("access_logs", {})
    
    # Response time analysis
    avg_response_time = access_logs.get("avg_response_time", 0)
    if avg_response_time > rules.get("response_time_threshold", 3.0):
        log_issue("Performance", f"Slow response time: {avg_response_time:.2f}s", "WARNING")
        issues.append({
            "type": "performance",
            "severity": "high",
            "description": f"Average response time ({avg_response_time:.2f}s) exceeds threshold. Create performance utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-performance-monitor.js",
            "data": {"response_time": avg_response_time},
            "safe_mode": True
        })
    
    # Caching analysis
    if avg_response_time > 1.0:  # Slow enough to benefit from caching
        issues.append({
            "type": "caching",
            "severity": "medium",
            "description": f"Response time ({avg_response_time:.2f}s) could benefit from caching utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-cache-manager.js",
            "data": {"response_time": avg_response_time},
            "safe_mode": True
        })
    
    # Traffic analysis for analytics
    total_requests = access_logs.get("total_requests", 0)
    if total_requests > 100:  # Enough traffic to benefit from analytics
        issues.append({
            "type": "analytics",
            "severity": "low",
            "description": f"High traffic ({total_requests} requests). Create analytics tracking utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-analytics-helper.js",
            "data": {"requests": total_requests},
            "safe_mode": True
        })
    
    return issues

def analyze_error_patterns(errors, rules, framework):
    """Analyze error logs for error handling improvements."""
    issues = []
    
    server_errors = errors.get("server_errors", {})
    total_errors = server_errors.get("total_errors", 0)
    
    if total_errors > rules.get("error_threshold", 5):  # Raised threshold for safety
        log_issue("Error", f"High error count: {total_errors}", "ERROR")
        
        issues.append({
            "type": "error_handling",
            "severity": "high",
            "description": f"High error count ({total_errors}). Create error handling utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-error-handler.js",
            "data": {"error_count": total_errors},
            "safe_mode": True
        })
        
        # Security analysis if there are many errors
        if total_errors > 20:
            issues.append({
                "type": "security",
                "severity": "medium",
                "description": f"Many errors ({total_errors}) might indicate security issues. Create security utilities.",
                "framework": framework,
                "language": "javascript",
                "target_file": "utils/ai-security-helper.js",
                "data": {"error_count": total_errors},
                "safe_mode": True
            })
    
    return issues

def analyze_system_performance(system, rules, framework):
    """Analyze system-level performance metrics."""
    issues = []
    
    # Memory usage analysis (raised threshold for safety)
    memory_percent = system.get("memory_percent", 0)
    if memory_percent > 90:  # Only for critical memory usage
        log_issue("System", f"Critical memory usage: {memory_percent}%", "WARNING")
        issues.append({
            "type": "memory_optimization",
            "severity": "high",
            "description": f"Critical memory usage ({memory_percent}%). Create memory optimization utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-memory-optimizer.js",
            "data": {"memory_percent": memory_percent},
            "safe_mode": True
        })
    
    # CPU usage analysis
    cpu_percent = system.get("cpu_percent", 0)
    if cpu_percent > 85:  # High CPU usage
        log_issue("System", f"High CPU usage: {cpu_percent}%", "WARNING")
        issues.append({
            "type": "performance",
            "severity": "medium",
            "description": f"High CPU usage ({cpu_percent}%). Create performance monitoring utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-performance-monitor.js",
            "data": {"cpu_percent": cpu_percent},
            "safe_mode": True
        })
    
    # Disk usage analysis
    disk_percent = system.get("disk_percent", 0)
    if disk_percent > 85:  # High disk usage
        issues.append({
            "type": "storage_optimization",  # NEW ISSUE TYPE
            "severity": "medium",
            "description": f"High disk usage ({disk_percent}%). Create storage optimization utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-storage-optimizer.js",
            "data": {"disk_percent": disk_percent},
            "safe_mode": True
        })
    
    return issues

def analyze_combined_metrics(combined, rules, framework):
    """Analyze combined metrics for overall health assessment."""
    issues = []
    
    health_score = combined.get("overall_health_score", 100)
    performance_issues = combined.get("performance_issues", [])
    
    if health_score < 60:  # Poor health score
        log_issue("Overall Health", f"Low health score: {health_score}", "WARNING")
        
        issues.append({
            "type": "comprehensive_optimization",  # NEW ISSUE TYPE
            "severity": "high",
            "description": f"Overall health score is low ({health_score}/100). Create comprehensive optimization utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-comprehensive-optimizer.js",
            "data": {
                "health_score": health_score,
                "issues": performance_issues
            },
            "safe_mode": True
        })
    
    return issues

def analyze_repository_structure(repo_files, framework):
    """Analyze repository structure for code quality issues."""
    issues = []
    
    # Check for accessibility if HTML files exist
    html_files = [f for f in repo_files if f.endswith('.html') or f.endswith('.jsx') or f.endswith('.tsx')]
    if html_files:
        issues.append({
            "type": "accessibility",
            "severity": "low",
            "description": f"Found {len(html_files)} HTML/JSX files. Create accessibility helper utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-accessibility-helper.js",
            "data": {"html_files": len(html_files)},
            "safe_mode": True
        })
    
    # Check for documentation if README is missing
    has_readme = any('readme' in f.lower() for f in repo_files)
    if not has_readme:
        issues.append({
            "type": "documentation",  # NEW ISSUE TYPE
            "severity": "low",
            "description": "Missing README file. Create documentation helper utilities.",
            "framework": framework,
            "language": "markdown",
            "target_file": "utils/ai-documentation-helper.js",
            "data": {"has_readme": has_readme},
            "safe_mode": True
        })
    
    return issues

def analyze_security_aspects(data, repo_files, framework):
    """Analyze for basic security-related improvements."""
    issues = []
    
    # Check for package.json security
    has_package_json = any('package.json' in f for f in repo_files)
    if has_package_json:
        issues.append({
            "type": "dependency_security",  # NEW ISSUE TYPE
            "severity": "low",
            "description": "Found package.json. Create dependency security helper utilities.",
            "framework": framework,
            "language": "javascript",
            "target_file": "utils/ai-dependency-security.js",
            "data": {"has_package_json": has_package_json},
            "safe_mode": True
        })
    
    # General security utility for any web application
    issues.append({
        "type": "security",
        "severity": "low",
        "description": "Create general security validation utilities for web application.",
        "framework": framework,
        "language": "javascript",
        "target_file": "utils/ai-security-helper.js",
        "data": {"general_security": True},
        "safe_mode": True
    })
    
    return issues

def handle_unknown_issue_type(issue_type, data, framework):
    """
    Fallback function for completely unknown issue types.
    This creates a generic utility that can be extended.
    """
    return {
        "type": issue_type,  # Whatever the unknown type is
        "severity": "low",
        "description": f"Unknown issue type '{issue_type}' detected. Create generic helper utility.",
        "framework": framework,
        "language": "javascript",
        "target_file": f"utils/ai-{issue_type.replace('_', '-')}-helper.js",
        "data": data,
        "safe_mode": True
    }

def determine_target_file_for_bug(bug, repo_path):
    """
    Determine the appropriate target file for a bug fix based on bug type.
    """
    bug_type = bug.get("type", "")
    bug_data = bug.get("data", {})
    
    # If the bug data specifies a file, use it
    if bug_data.get("file"):
        return bug_data["file"]
    
    # Otherwise, determine based on type
    if bug_type in ["accessibility", "responsive", "performance"]:
        # These typically affect HTML/JSX files
        # Try to find the main entry point
        import os
        common_files = ["index.html", "src/index.html", "public/index.html", 
                       "app/page.tsx", "src/App.tsx", "src/App.jsx"]
        for file in common_files:
            full_path = os.path.join(repo_path, file) if repo_path else file
            if os.path.exists(full_path):
                return file
        return "index.html"  # Default fallback
    
    elif bug_type in ["javascript_error", "console_error"]:
        # JavaScript errors - target main JS file or create a fix utility
        return "utils/ai-error-fixes.js"
    
    else:
        # Unknown type - create a utility file
        return f"utils/ai-{bug_type.replace('_', '-')}-fix.js"

