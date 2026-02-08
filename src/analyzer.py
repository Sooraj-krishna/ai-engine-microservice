"""
Enhanced analyzer that detects various types of issues from monitoring data.
Generates safe, actionable issues for the AI engine to address.
"""

import os
from config_loader import load_rules
from utils import detect_framework, log_issue
from bug_detector import run_bug_detection
from e2e_tester import run_e2e_tests  # Keep for backward compatibility
from enhanced_bug_detector import comprehensive_bug_detection
from structured_e2e_tester import run_structured_e2e_tests
from lighthouse_tester import run_lighthouse_audit
from axe_accessibility_tester import run_axe_accessibility_audit
# NEW: Static code analysis imports
from eslint_detector import run_eslint_analysis
from typescript_detector import run_tsc_type_check
from component_analyzer import analyze_react_components
from functional_e2e_tester import run_functional_tests
from dependency_scanner import run_dependency_scan
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


    # ============================================================================
    # PRIORITY 1: STATIC CODE ANALYSIS (NEW - Find actual code bugs first)
    # ============================================================================
    
    if repo_path:
        print(f"\n[INFO] ========== PRIORITY 1: STATIC CODE ANALYSIS ==========")
        
        # 1.1 ESLint Analysis - Find code quality issues
        try:
            print(f"[INFO] Running ESLint analysis...")
            # Find the UI directory
            ui_path = os.path.join(repo_path, 'ai-engine-ui') if os.path.exists(os.path.join(repo_path, 'ai-engine-ui')) else repo_path
            eslint_bugs = await run_eslint_analysis(ui_path)
            
            if eslint_bugs:
                log_issue("ESLint", f"Found {len(eslint_bugs)} code quality issues", "WARNING")
                for bug in eslint_bugs:
                    issues.append({
                        "type": bug.get("type", "code_quality"),
                        "severity": bug.get("severity", "medium"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": bug.get("file", "unknown"),
                        "data": bug.get("data", {}),
                        "safe_mode": True,
                        "requires_approval": True,
                        "is_actual_bug": bug.get("is_actual_bug", True)
                    })
            else:
                print("[ESLINT] No ESLint issues found")
        except Exception as e:
            print(f"[WARNING] ESLint analysis failed: {e}")
        
        # 1.2 TypeScript Type Checking
        try:
            print(f"[INFO] Running TypeScript type checking...")
            ui_path = os.path.join(repo_path, 'ai-engine-ui') if os.path.exists(os.path.join(repo_path, 'ai-engine-ui')) else repo_path
            tsc_bugs = await run_tsc_type_check(ui_path)
            
            if tsc_bugs:
                log_issue("TypeScript", f"Found {len(tsc_bugs)} type errors", "ERROR")
                for bug in tsc_bugs:
                    issues.append({
                        "type": bug.get("type", "type_error"),
                        "severity": bug.get("severity", "high"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "typescript",
                        "target_file": bug.get("file", "unknown"),
                        "data": bug.get("data", {}),
                        "safe_mode": True,
                        "requires_approval": True,
                        "is_actual_bug": bug.get("is_actual_bug", True)
                    })
            else:
                print("[TSC] No type errors found")
        except Exception as e:
            print(f"[WARNING] TypeScript check failed: {e}")
        
        # 1.3 Component Analysis
        try:
            print(f"[INFO] Running React component analysis...")
            ui_src_path = os.path.join(repo_path, 'ai-engine-ui', 'src') if os.path.exists(os.path.join(repo_path, 'ai-engine-ui', 'src')) else os.path.join(repo_path, 'src')
            if os.path.exists(ui_src_path):
                component_bugs = await analyze_react_components(ui_src_path)
                
                if component_bugs:
                    log_issue("Component Analyzer", f"Found {len(component_bugs)} component issues", "WARNING")
                    for bug in component_bugs:
                        issues.append({
                            "type": bug.get("type", "component_error"),
                            "severity": bug.get("severity", "medium"),
                            "description": bug.get("description", ""),
                            "details": bug.get("details", ""),
                            "framework": framework,
                            "language": "javascript",
                            "target_file": bug.get("file", "unknown"),
                            "data": bug.get("data", {}),
                            "safe_mode": True,
                            "requires_approval": True,
                            "is_actual_bug": bug.get("is_actual_bug", True)
                        })
                else:
                    print("[COMPONENT] No component issues found")
        except Exception as e:
            print(f"[WARNING] Component analysis failed: {e}")
        
        # 1.4 Dependency Vulnerability Scan
        try:
            print(f"[INFO] Running dependency vulnerability scan...")
            dep_bugs = await run_dependency_scan(repo_path)
            
            if dep_bugs:
                log_issue("Dependency Scanner", f"Found {len(dep_bugs)} vulnerabilities", "ERROR")
                for bug in dep_bugs:
                    issues.append({
                        "type": bug.get("type", "dependency_vulnerability"),
                        "severity": bug.get("severity", "high"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "dependencies",
                        "target_file": bug.get("file", "unknown"),
                        "data": bug.get("data", {}),
                        "safe_mode": True,
                        "requires_approval": True,
                        "is_actual_bug": bug.get("is_actual_bug", True)
                    })
            else:
                print("[DEPENDENCY_SCAN] No vulnerabilities found")
        except Exception as e:
            print(f"[WARNING] Dependency scan failed: {e}")
        
        print(f"[INFO] ========== PRIORITY 1 COMPLETE: Found {len([i for i in issues if i.get('is_actual_bug')])} actual bugs ==========\n")

    # ============================================================================
    # PRIORITY 2: FUNCTIONAL TESTING (NEW - Test user flows)
    # ============================================================================
    
    if url:
        print(f"[INFO] ========== PRIORITY 2: FUNCTIONAL TESTING ==========")
        try:
            functional_bugs = await run_functional_tests(url, repo_path)
            
            if functional_bugs:
                log_issue("Functional Tests", f"Found {len(functional_bugs)} functional issues", "ERROR")
                for bug in functional_bugs:
                    issues.append({
                        "type": bug.get("type", "functional_bug"),
                        "severity": bug.get("severity", "high"),
                        "description": bug.get("description", ""),
                        "details": bug.get("details", ""),
                        "framework": framework,
                        "language": "javascript",
                        "target_file": bug.get("target_file", "unknown"),
                        "data": bug.get("data", {}),
                        "safe_mode": True,
                        "requires_approval": True,
                        "is_actual_bug": bug.get("is_actual_bug", True)
                    })
            else:
                print("[FUNCTIONAL] No functional bugs found")
        except Exception as e:
            print(f"[WARNING] Functional testing failed: {e}")
        
        print(f"[INFO] ========== PRIORITY 2 COMPLETE ==========\n")

    # ============================================================================
    # PRIORITY 3 & 4: Legacy Bug Detection (Keep for compatibility)
    # ============================================================================

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
                        "target_file": "index.html",  # Real HTML file, NOT a utility!
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
                        "target_file": "index.html",  # Real HTML file, NOT a utility!
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
    # DISABLED: All analytics checks create useless utility suggestions
    # Real UX issues should come from actual user testing and metrics
    
    return []  # Return empty list, not undefined 'issues'

def analyze_server_metrics(metrics, rules, framework):
    """Analyze server metrics for performance issues."""
    # DISABLED: All server metric checks create useless utility suggestions
    # Real performance issues should come from profilers and APM tools
    
    return []  # Return empty list

def analyze_error_patterns(errors, rules, framework):
    """Analyze error logs for error handling improvements."""
    # DISABLED: Error pattern checks create useless utility suggestions
    # Real errors should be caught by error tracking tools like Sentry
    return []

def analyze_system_performance(system, rules, framework):
    """Analyze system-level performance metrics."""
    # DISABLED: System performance checks create useless utility suggestions
    # Real system issues should be monitored by infrastructure tools
    
    return []  # Return empty list

def analyze_combined_metrics(combined, rules, framework):
    """Analyze combined metrics for overall health assessment."""
    issues = []  # Define variable before disabled check
    
    # DISABLED: Health score creates useless utility suggestions
    
    return issues  # Return the defined empty list

def analyze_repository_structure(repo_files, framework):
    """Analyze repository structure for code quality issues."""
    issues = []  # Define variable
    
    # DISABLED: Generic accessibility check creates useless "utility" suggestions
    # Axe detector provides REAL accessibility fixes with specific file/line numbers
    
    # DISABLED: README check is not a code bug - skip this
    
    return issues  # Return the defined empty list

def analyze_security_aspects(data, repo_files, framework):
    """Analyze for basic security-related improvements."""
    # DISABLED: Security checks create useless utility suggestions
    # dependency_scanner provides REAL security issues with CVE IDs
    return []

def handle_unknown_issue_type(issue_type, data, framework):
    """
    Fallback function for completely unknown issue types.
    DISABLED: Don't create generic utilities for unknown issues.
    """
    return None  # Don't create utility files for unknown issues

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
        # JavaScript errors - target main JS file
        return "app.js"  # Real JS file, NOT a utility file
    
    else:
        # Unknown type - target HTML file (real file, not utility)
        return "index.html"  # Real file, NOT utils/ai-*-fix.js

