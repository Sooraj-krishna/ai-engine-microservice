"""
ESLint Integration for Bug Detection
Runs ESLint on JavaScript/TypeScript files to find code quality issues and bugs.
"""

import asyncio
import subprocess
import json
import os
from pathlib import Path


async def run_eslint_analysis(repo_path):
    """
    Run ESLint on the repository and return detected bugs.
    
    Args:
        repo_path: Path to the repository (e.g., ./ai-engine-ui)
        
    Returns:
        list: Detected bugs in standardized format
    """
    bugs = []
    
    if not repo_path or not os.path.exists(repo_path):
        print(f"[ESLINT] Invalid repo path: {repo_path}")
        return bugs
    
    try:
        # Check if ESLint is available
        package_json = os.path.join(repo_path, 'package.json')
        if not os.path.exists(package_json):
            print("[ESLINT] No package.json found, skipping ESLint")
            return bugs
        
        # Check if node_modules exists
        node_modules = os.path.join(repo_path, 'node_modules')
        if not os.path.exists(node_modules):
            print("[ESLINT] No node_modules found, skipping ESLint")
            return bugs
            
        print(f"[ESLINT] Running ESLint analysis on {repo_path}...")
        
        # Run ESLint with JSON output
        # Focus on src directory if it exists
        src_path = os.path.join(repo_path, 'src')
        target_path = src_path if os.path.exists(src_path) else repo_path
        
        # ESLint command with specific rules for bug detection
        eslint_cmd = [
            "npx", "eslint",
            target_path,
            "--format", "json",
            "--no-error-on-unmatched-pattern",
            "--ext", ".js,.jsx,.ts,.tsx"
        ]
        
        result = subprocess.run(
            eslint_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # ESLint returns exit code 1 when it finds issues, which is expected
        if result.stdout:
            try:
                eslint_results = json.loads(result.stdout)
                bugs = parse_eslint_output(eslint_results, repo_path)
                print(f"[ESLINT] Found {len(bugs)} issues")
            except json.JSONDecodeError as e:
                print(f"[ESLINT] Failed to parse output: {e}")
        else:
            print("[ESLINT] No ESLint output received")
            
    except subprocess.TimeoutExpired:
        print("[ESLINT] ESLint timed out after 60 seconds")
    except FileNotFoundError:
        print("[ESLINT] ESLint not found. Install with: npm install --save-dev eslint")
    except Exception as e:
        print(f"[ESLINT] Error running ESLint: {e}")
    
    return bugs


def parse_eslint_output(eslint_results, repo_path):
    """
    Parse ESLint JSON output and convert to bug format.
    
    Args:
        eslint_results: ESLint JSON output
        repo_path: Repository path for relative file paths
        
    Returns:
        list: Bugs in standardized format
    """
    bugs = []
    
    # Filter rules that indicate actual bugs (not style issues)
    bug_rules = {
        'no-unused-vars': 'high',
        'no-undef': 'critical',
        'no-console': 'medium',
        'no-debugger': 'high',
        'import/no-unresolved': 'high',
        'react/prop-types': 'medium',
        'react/jsx-no-undef': 'high',
        'react/jsx-key': 'high',
        '@typescript-eslint/no-unused-vars': 'high',
        '@typescript-eslint/no-explicit-any': 'medium',
        'react-hooks/exhaustive-deps': 'medium',
        'react-hooks/rules-of-hooks': 'critical'
    }
    
    for file_result in eslint_results:
        file_path = file_result.get('filePath', '')
        messages = file_result.get('messages', [])
        
        # Make file path relative
        try:
            rel_path = os.path.relpath(file_path, repo_path)
        except:
            rel_path = file_path
        
        for msg in messages:
            rule_id = msg.get('ruleId', '')
            severity_level = msg.get('severity', 1)  # 1=warning, 2=error
            
            # Only include bugs, not style warnings
            if rule_id in bug_rules or severity_level == 2:
                severity = bug_rules.get(rule_id, 'medium' if severity_level == 1 else 'high')
                
                bugs.append({
                    'type': categorize_eslint_rule(rule_id),
                    'severity': severity,
                    'description': f"{rule_id}: {msg.get('message', 'ESLint issue')}",
                    'details': msg.get('message', ''),
                    'file': rel_path,
                    'line': msg.get('line', 0),
                    'column': msg.get('column', 0),
                    'code_snippet': msg.get('source', ''),
                    'rule': rule_id,
                    'target_file': rel_path,
                    'is_actual_bug': True,
                    'data': {
                        'type': 'ESLint Error',
                        'rule': rule_id,
                        'line': msg.get('line', 0),
                        'column': msg.get('column', 0)
                    }
                })
    
    return bugs


def categorize_eslint_rule(rule_id):
    """Categorize ESLint rule into bug type."""
    if 'unused' in rule_id or 'no-unused' in rule_id:
        return 'unused_code'
    elif 'undef' in rule_id or 'no-undef' in rule_id:
        return 'undefined_reference'
    elif 'console' in rule_id:
        return 'console_statement'
    elif 'debugger' in rule_id:
        return 'debug_statement'
    elif 'import' in rule_id or 'unresolved' in rule_id:
        return 'import_error'
    elif 'prop-types' in rule_id or 'jsx' in rule_id:
        return 'component_error'
    elif 'hooks' in rule_id:
        return 'react_hook_error'
    elif 'typescript' in rule_id:
        return 'type_error'
    else:
        return 'code_quality'


def filter_bug_patterns(bugs):
    """
    Filter bugs to focus on actual code issues.
    Removes style-only warnings.
    """
    # Rules to exclude (pure style, not bugs)
    exclude_rules = [
        'prettier',
        'semi',
        'quotes',
        'indent',
        'comma-dangle',
        'object-curly-spacing'
    ]
    
    filtered = []
    for bug in bugs:
        rule = bug.get('rule', '')
        if not any(exclude in rule for exclude in exclude_rules):
            filtered.append(bug)
    
    return filtered
