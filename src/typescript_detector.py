"""
TypeScript Type Checker for Bug Detection
Runs TypeScript compiler to find type errors without emitting files.
"""

import asyncio
import subprocess
import json
import os
import re


async def run_tsc_type_check(repo_path):
    """
    Run TypeScript compiler type checking.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        list: Detected type errors in standardized format
    """
    bugs = []
    
    if not repo_path or not os.path.exists(repo_path):
        print(f"[TSC] Invalid repo path: {repo_path}")
        return bugs
    
    try:
        # Check if tsconfig.json exists
        tsconfig = os.path.join(repo_path, 'tsconfig.json')
        if not os.path.exists(tsconfig):
            print("[TSC] No tsconfig.json found, skipping TypeScript check")
            return bugs
        
        print(f"[TSC] Running TypeScript type checking on {repo_path}...")
        
        # Run TypeScript compiler with --noEmit (just check, don't build)
        tsc_cmd = [
            "npx", "tsc",
            "--noEmit",
            "--pretty", "false"  # Disable colors for easier parsing
        ]
        
        result = subprocess.run(
            tsc_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=90
        )
        
        # TypeScript returns exit code 2 when there are type errors
        if result.stdout or result.stderr:
            output = result.stdout + result.stderr
            bugs = parse_tsc_errors(output, repo_path)
            print(f"[TSC] Found {len(bugs)} type errors")
        else:
            print("[TSC] No type errors found")
            
    except subprocess.TimeoutExpired:
        print("[TSC] TypeScript check timed out after 90 seconds")
    except FileNotFoundError:
        print("[TSC] TypeScript not found. Install with: npm install --save-dev typescript")
    except Exception as e:
        print(f"[TSC] Error running TypeScript check: {e}")
    
    return bugs


def parse_tsc_errors(output, repo_path):
    """
    Parse TypeScript compiler error output.
    
    Format: filename(line,col): error TSxxxx: message
    Example: src/App.tsx(42,15): error TS2304: Cannot find name 'navigate'.
    
    Args:
        output: TSC error output
        repo_path: Repository path
        
    Returns:
        list: Type errors in standardized format
    """
    bugs = []
    
    # Regex to parse TypeScript errors
    # Pattern: filename(line,column): error TScode: message
    error_pattern = re.compile(
        r'^(.+?)\((\d+),(\d+)\):\s+error\s+(TS\d+):\s+(.+)$',
        re.MULTILINE
    )
    
    for match in error_pattern.finditer(output):
        file_path = match.group(1).strip()
        line = int(match.group(2))
        column = int(match.group(3))
        error_code = match.group(4)
        message = match.group(5).strip()
        
        # Make path relative
        try:
            rel_path = os.path.relpath(file_path, repo_path)
        except:
            rel_path = file_path
        
        # Categorize the error
        bug_type, severity = categorize_ts_error(error_code, message)
        
        bugs.append({
            'type': bug_type,
            'severity': severity,
            'description': f"{error_code}: {message}",
            'details': message,
            'file': rel_path,
            'line': line,
            'column': column,
            'error_code': error_code,
            'target_file': rel_path,
            'is_actual_bug': True,
            'data': {
                'type': 'TypeScript Error',
                'error_code': error_code,
                'line': line,
                'column': column
            }
        })
    
    return bugs


def categorize_ts_error(error_code, message):
    """
    Categorize TypeScript error and assign severity.
    
    Common error codes:
    - TS2304: Cannot find name
    - TS2307: Cannot find module
    - TS2322: Type X is not assignable to type Y
    - TS2339: Property does not exist on type
    - TS2345: Argument of type X is not assignable to parameter of type Y
    - TS2551: Property does not exist (did you mean?)
    - TS7006: Implicitly has 'any' type
    """
    message_lower = message.lower()
    
    # Critical errors (undefined references, missing imports)
    if error_code in ['TS2304', 'TS2307']:
        return 'undefined_reference', 'critical'
    
    # High severity (type mismatches, missing properties)
    elif error_code in ['TS2322', 'TS2339', 'TS2345', 'TS2551']:
        return 'type_error', 'high'
    
    # Medium severity (implicit any, missing types)
    elif error_code in ['TS7006', 'TS7031']:
        return 'missing_type', 'medium'
    
    # Property access errors
    elif 'property' in message_lower and 'does not exist' in message_lower:
        return 'property_error', 'high'
    
    # Import/module errors
    elif 'module' in message_lower or 'import' in message_lower:
        return 'import_error', 'critical'
    
    # Default
    else:
        return 'type_error', 'medium'


def suggest_fix_for_error(error_code, message):
    """
    Suggest a fix based on the error code and message.
    """
    suggestions = {
        'TS2304': "Check if the variable/function is imported or defined. Make sure imports are correct.",
        'TS2307': "Verify the module path is correct. Check if the file exists and the import statement is accurate.",
        'TS2322': "Type mismatch. Ensure the assigned value matches the expected type.",
        'TS2339': "Property does not exist. Check if you're accessing the correct property name.",
        'TS2345': "Argument type mismatch. Verify the function parameters and their types.",
        'TS7006': "Add explicit type annotation to remove implicit 'any' type."
    }
    
    return suggestions.get(error_code, "Review TypeScript documentation for this error code.")
