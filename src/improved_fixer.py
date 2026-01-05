"""
Improved Bug Fixer with code diff generation and incremental fixing.
Uses chunking and better context management for accurate fixes.
"""

import difflib
import os
from ai_api import query_codegen_api
from validator import CodeValidator
import re

# Optional: Use code analyzer for better understanding
try:
    from code_analyzer import CodeAnalyzer
    CODE_ANALYZER_AVAILABLE = True
except ImportError:
    CODE_ANALYZER_AVAILABLE = False
    print("[IMPROVED_FIXER] Code analyzer not available, using basic context")

def generate_code_diff(original_code, fixed_code):
    """
    Generate a unified diff between original and fixed code.
    """
    original_lines = original_code.splitlines(keepends=True)
    fixed_lines = fixed_code.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        fixed_lines,
        fromfile='original',
        tofile='fixed',
        lineterm=''
    )
    
    return ''.join(diff)

def get_file_chunk(file_path, start_line, end_line):
    """
    Get a specific chunk of a file for focused fixing.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            chunk_lines = lines[start_line:end_line]
            return {
                'code': ''.join(chunk_lines),
                'start_line': start_line,
                'end_line': end_line,
                'context_before': ''.join(lines[max(0, start_line-5):start_line]),
                'context_after': ''.join(lines[end_line:min(len(lines), end_line+5)])
            }
    except Exception as e:
        print(f"[ERROR] Failed to read file chunk: {e}")
        return None

def find_relevant_code_section(bug, file_path):
    """
    Find the relevant code section for a bug.
    Uses heuristics to locate the problematic code.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
        
        # Try to find relevant section based on bug details
        bug_details = bug.get('details', '').lower()
        bug_type = bug.get('type', '')
        
        # Search for relevant patterns
        relevant_lines = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Match based on bug type
            if bug_type == 'accessibility' and ('img' in line_lower or 'button' in line_lower or 'input' in line_lower):
                relevant_lines.append(i)
            elif bug_type == 'performance' and ('script' in line_lower or 'link' in line_lower or 'img' in line_lower):
                relevant_lines.append(i)
            elif bug_type == 'responsive' and ('meta' in line_lower or 'viewport' in line_lower):
                relevant_lines.append(i)
            elif bug_type == 'javascript_error':
                # Try to find the error location
                if any(keyword in line_lower for keyword in bug_details.split()[:3]):
                    relevant_lines.append(i)
        
        if relevant_lines:
            # Get chunk around first relevant line
            first_line = relevant_lines[0]
            return get_file_chunk(file_path, max(0, first_line-10), min(len(lines), first_line+20))
        
        # Default: return first 50 lines
        return get_file_chunk(file_path, 0, 50)
        
    except Exception as e:
        print(f"[ERROR] Failed to find relevant code section: {e}")
        return None

def generate_minimal_fix(bug, code_chunk, file_path, code_context=None):
    """
    Generate a minimal fix for a bug using AI, with limited context and code understanding.
    """
    bug_type = bug.get('type', 'unknown')
    bug_description = bug.get('description', '')
    bug_details = bug.get('details', '')
    
    # Build context information
    context_info = ""
    if code_context:
        context_info = f"""
CODEBASE CONTEXT:
- File type: {code_context.get('type', 'unknown')}
- Imports: {', '.join(code_context.get('imports', [])[:5])}
- Functions in file: {', '.join([f['name'] for f in code_context.get('functions', [])[:5]])}
- Related files: {', '.join(code_context.get('related_files', [])[:3])}
- Dependencies: {', '.join(code_context.get('dependencies', [])[:3])}
"""
    
    # Create focused prompt with context
    prompt = f"""
You are fixing a {bug_type} bug in a web application.

BUG DESCRIPTION: {bug_description}
BUG DETAILS: {bug_details}
{context_info}
CURRENT CODE (only the relevant section):
```html
{code_chunk['code'][:1500]}  # Limit to 1500 chars
```

REQUIREMENTS:
1. Generate ONLY the minimal fix needed
2. Don't change unrelated code
3. Follow best practices for {bug_type} fixes
4. Consider the codebase context when making changes
5. Return ONLY the fixed code section, not the entire file
6. Keep the same code structure and formatting
7. Ensure compatibility with related files and dependencies

FIXED CODE:
"""
    
    try:
        # Generate fix using AI
        fixed_code = query_codegen_api(prompt, language="html")
        
        # Clean up the response
        fixed_code = clean_ai_response(fixed_code)
        
        return {
            'original': code_chunk['code'],
            'fixed': fixed_code,
            'diff': generate_code_diff(code_chunk['code'], fixed_code),
            'file_path': file_path,
            'start_line': code_chunk['start_line'],
            'end_line': code_chunk['end_line']
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to generate fix: {e}")
        return None

def clean_ai_response(response):
    """
    Clean AI response to extract just the code.
    """
    # Remove markdown code blocks
    if '```' in response:
        lines = response.split('\n')
        # Find code block
        start_idx = None
        end_idx = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if start_idx is None:
                    start_idx = i + 1
                else:
                    end_idx = i
                    break
        
        if start_idx is not None:
            if end_idx is not None:
                response = '\n'.join(lines[start_idx:end_idx])
            else:
                response = '\n'.join(lines[start_idx:])
    
    return response.strip()

def apply_fix_to_file(file_path, fix):
    """
    Apply a fix to a file by replacing the relevant section.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Replace the section
        start = fix['start_line']
        end = fix['end_line']
        
        # Split fixed code into lines
        fixed_lines = fix['fixed'].splitlines(keepends=True)
        if not fixed_lines[-1].endswith('\n') and fixed_lines:
            fixed_lines[-1] += '\n'
        
        # Replace
        new_lines = lines[:start] + fixed_lines + lines[end:]
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to apply fix: {e}")
        return False

def incremental_fix_bugs(bugs, repo_path):
    """
    Fix bugs incrementally, one at a time, with validation.
    Uses code analysis for better understanding.
    """
    validator = CodeValidator()
    fixes = []
    failed_fixes = []
    
    print(f"[IMPROVED_FIXER] Starting incremental fix process for {len(bugs)} bugs...")
    
    # Analyze codebase structure for better context
    code_analyzer = None
    if CODE_ANALYZER_AVAILABLE and repo_path and os.path.exists(repo_path):
        try:
            print(f"[IMPROVED_FIXER] Analyzing codebase structure for better context...")
            code_analyzer = CodeAnalyzer(repo_path=repo_path)
            codebase_info = code_analyzer.analyze_repository()
            print(f"[IMPROVED_FIXER] Codebase analysis complete: {codebase_info.get('total_files', 0)} files analyzed")
        except Exception as e:
            print(f"[WARNING] Code analysis failed: {e}, continuing without it")
            code_analyzer = None
    
    # Sort bugs by severity (high first)
    severity_order = {'high': 0, 'medium': 1, 'low': 2}
    sorted_bugs = sorted(bugs, key=lambda b: severity_order.get(b.get('severity', 'low'), 2))
    
    for i, bug in enumerate(sorted_bugs, 1):
        print(f"[IMPROVED_FIXER] Processing bug {i}/{len(sorted_bugs)}: {bug.get('type', 'unknown')}")
        
        # Determine file to fix
        file_path = determine_file_to_fix(bug, repo_path)
        
        if not file_path:
            print(f"[SKIP] Could not determine file for bug: {bug.get('type')}")
            failed_fixes.append({
                'bug': bug,
                'reason': 'Could not determine file'
            })
            continue
        
        # Get relevant code section
        code_chunk = find_relevant_code_section(bug, file_path)
        
        if not code_chunk:
            print(f"[SKIP] Could not find relevant code section")
            failed_fixes.append({
                'bug': bug,
                'reason': 'Could not find relevant code section'
            })
            continue
        
        # Get code context if analyzer available
        code_context = None
        if code_analyzer:
            try:
                rel_path = os.path.relpath(file_path, repo_path) if repo_path else file_path
                code_context = code_analyzer.get_file_context(rel_path)
                print(f"[IMPROVED_FIXER] Got context for {rel_path}: {len(code_context.get('related_files', []))} related files")
            except Exception as e:
                print(f"[WARNING] Failed to get code context: {e}")
        
        # Generate fix with context
        fix = generate_minimal_fix(bug, code_chunk, file_path, code_context=code_context)
        
        if not fix:
            print(f"[SKIP] Failed to generate fix")
            failed_fixes.append({
                'bug': bug,
                'reason': 'Failed to generate fix'
            })
            continue
        
        # Validate fix
        if validator.validate_fix(fix['fixed']):
            rel_path = os.path.relpath(file_path, repo_path) if repo_path else file_path
            fixes.append({
                'path': rel_path,
                'content': fix['fixed'],
                'diff': fix['diff'],
                'description': f"Fix for {bug.get('type')}: {bug.get('description', '')}",
                'bug': bug
            })
            print(f"[IMPROVED_FIXER] ✅ Generated and validated fix for {bug.get('type')}")
            print(f"[IMPROVED_FIXER]    Target file: {rel_path}")
            print(f"[IMPROVED_FIXER]    Fix description: {bug.get('description', '')[:100]}")
            if fix['diff']:
                diff_lines = fix['diff'].split('\n')[:10]  # Show first 10 lines of diff
                print(f"[IMPROVED_FIXER]    Diff preview:")
                for line in diff_lines:
                    if line.startswith('+'):
                        print(f"[IMPROVED_FIXER]      {line[:80]}")
        else:
            print(f"[IMPROVED_FIXER] ❌ Fix failed validation")
            print(f"[IMPROVED_FIXER]    Bug: {bug.get('type')} - {bug.get('description', '')[:80]}")
            failed_fixes.append({
                'bug': bug,
                'reason': 'Failed validation',
                'fix': fix
            })
    
    print(f"[IMPROVED_FIXER] ========================================")
    print(f"[IMPROVED_FIXER] SUMMARY:")
    print(f"[IMPROVED_FIXER] - Total bugs processed: {len(sorted_bugs)}")
    print(f"[IMPROVED_FIXER] - Fixes generated: {len(fixes)}")
    print(f"[IMPROVED_FIXER] - Failed fixes: {len(failed_fixes)}")
    if failed_fixes:
        print(f"[IMPROVED_FIXER] Failed fix reasons:")
        failure_reasons = {}
        for failed in failed_fixes:
            reason = failed['reason']
            failure_reasons[reason] = failure_reasons.get(reason, 0) + 1
        for reason, count in failure_reasons.items():
            print(f"[IMPROVED_FIXER]   - {reason}: {count}")
    print(f"[IMPROVED_FIXER] ========================================")
    
    return fixes, failed_fixes

def determine_file_to_fix(bug, repo_path):
    """
    Determine which file needs to be fixed based on bug type and details.
    """
    bug_type = bug.get('type', '')
    bug_data = bug.get('data', {})
    
    # Common file patterns
    if bug_type in ['accessibility', 'responsive', 'performance']:
        # Usually HTML files
        html_files = find_files_by_extension(repo_path, ['.html', '.jsx', '.tsx', '.vue'])
        if html_files:
            return html_files[0]  # Return first HTML file found
    
    elif bug_type == 'javascript_error':
        # JavaScript files
        js_files = find_files_by_extension(repo_path, ['.js', '.jsx', '.ts', '.tsx'])
        if js_files:
            return js_files[0]
    
    # Default: look for index.html or main entry point
    common_files = ['index.html', 'app.html', 'main.html', 'src/index.html']
    for common_file in common_files:
        file_path = os.path.join(repo_path, common_file)
        if os.path.exists(file_path):
            return file_path
    
    return None

def find_files_by_extension(repo_path, extensions):
    """
    Find files with given extensions in the repository.
    """
    files = []
    
    for root, dirs, filenames in os.walk(repo_path):
        # Skip node_modules and other common directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.next']]
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files

