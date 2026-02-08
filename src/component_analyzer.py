"""
React/Next.js Component Analyzer
Analyzes React components for common bugs and issues.
"""

import os
import re
import asyncio
from pathlib import Path


async def analyze_react_components(repo_path):
    """
    Analyze React/Next.js components for common bugs.
    
    Args:
        repo_path: Path to the repository source directory
        
    Returns:
        list: Detected component bugs
    """
    bugs = []
    
    if not repo_path or not os.path.exists(repo_path):
        print(f"[COMPONENT] Invalid path: {repo_path}")
        return bugs
    
    print(f"[COMPONENT] Analyzing React components in {repo_path}...")
    
    # Find all React component files
    component_files = []
    for root, dirs, files in os.walk(repo_path):
        # Skip node_modules and build directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'build', 'dist', '.next']]
        
        for file in files:
            if file.endswith(('.jsx', '.tsx')):
                component_files.append(os.path.join(root, file))
    
    print(f"[COMPONENT] Found {len(component_files)} component files")
    
    # Analyze each component
    for file_path in component_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                rel_path = os.path.relpath(file_path, repo_path)
                
                # Run various checks
                bugs.extend(check_broken_event_handlers(content, rel_path))
                bugs.extend(check_missing_keys(content, rel_path))
                bugs.extend(check_unused_state(content, rel_path))
                bugs.extend(check_unsafe_lifecycle(content, rel_path))
                
        except Exception as e:
            print(f"[COMPONENT] Error analyzing {file_path}: {e}")
    
    print(f"[COMPONENT] Found {len(bugs)} component issues")
    return bugs


def check_broken_event_handlers(content, file_path):
    """
    Check for event handlers that might be broken.
    E.g., onClick={handleClick} but handleClick is not defined
    """
    bugs = []
    lines = content.split('\n')
    
    # Find all event handler references
    # Pattern: onClick={someFunction} or onClick={() => someFunction()}
    handler_pattern = re.compile(r'on[A-Z]\w+\s*=\s*\{([^}]+)\}')
    
    for i, line in enumerate(lines, 1):
        matches = handler_pattern.findall(line)
        for match in matches:
            # Extract function name
            func_match = re.search(r'(\w+)', match)
            if func_match:
                func_name = func_match.group(1)
                
                # Check if it's a common valid pattern
                if func_name in ['e', 'event', 'props', 'this', 'true', 'false', 'null']:
                    continue
                
                # Check if function is defined in file
                func_def_pattern = re.compile(rf'\b(const|let|var|function)\s+{func_name}\b')
                if not func_def_pattern.search(content):
                    bugs.append({
                        'type': 'component_error',
                        'severity': 'high',
                        'description': f"Event handler '{func_name}' is not defined",
                        'details': f"Event handler referenced in line {i} but not found in component",
                        'file': file_path,
                        'line': i,
                        'target_file': file_path,
                        'is_actual_bug': True,
                        'data': {
                            'type': 'Undefined Event Handler',
                            'handler_name': func_name,
                            'line': i
                        }
                    })
    
    return bugs


def check_missing_keys(content, file_path):
    """
    Check for missing key props in list rendering.
    """
    bugs = []
    lines = content.split('\n')
    
    # Pattern: .map(() => <Component without key prop
    # This is a simplified check
    map_pattern = re.compile(r'\.map\s*\([^)]*\)\s*=>\s*<(\w+)')
    
    for i, line in enumerate(lines, 1):
        if '.map(' in line and '=>' in line and '<' in line:
            # Check if 'key=' appears in next few lines
            context = '\n'.join(lines[i-1:min(i+3, len(lines))])
            if 'key=' not in context and 'key =' not in context:
                bugs.append({
                    'type': 'component_error',
                    'severity': 'medium',
                    'description': "Missing 'key' prop in list rendering",
                    'details': f"Map function at line {i} likely missing key prop",
                    'file': file_path,
                    'line': i,
                    'target_file': file_path,
                    'is_actual_bug': True,
                    'data': {
                        'type': 'Missing Key Prop',
                        'line': i
                    }
                })
    
    return bugs


def check_unused_state(content, file_path):
    """
    Check for useState declarations that are never used.
    """
    bugs = []
    lines = content.split('\n')
    
    # Find all useState declarations
    # Pattern: const [state, setState] = useState(...)
    state_pattern = re.compile(r'const\s+\[(\w+),\s*\w+\]\s*=\s*useState')
    
    for i, line in enumerate(lines, 1):
        matches = state_pattern.findall(line)
        for state_name in matches:
            # Check if state is used anywhere else in the file
            # Simple check: appears more than once
            if content.count(state_name) <= 1:
                bugs.append({
                    'type': 'unused_code',
                    'severity': 'low',
                    'description': f"Unused state variable '{state_name}'",
                    'details': f"State declared at line {i} but never used",
                    'file': file_path,
                    'line': i,
                    'target_file': file_path,
                    'is_actual_bug': True,
                    'data': {
                        'type': 'Unused State',
                        'state_name': state_name,
                        'line': i
                    }
                })
    
    return bugs


def check_unsafe_lifecycle(content, file_path):
    """
    Check for unsafe React lifecycle methods.
    """
    bugs = []
    lines = content.split('\n')
    
    unsafe_methods = [
        'componentWillMount',
        'componentWillReceiveProps',
        'componentWillUpdate'
    ]
    
    for i, line in enumerate(lines, 1):
        for method in unsafe_methods:
            if method in line:
                bugs.append({
                    'type': 'deprecated_api',
                    'severity': 'medium',
                    'description': f"Unsafe lifecycle method '{method}' detected",
                    'details': f"Use {method.replace('UNSAFE_', '')} is deprecated. Use alternatives like getDerivedStateFromProps or useEffect",
                    'file': file_path,
                    'line': i,
                    'target_file': file_path,
                    'is_actual_bug': True,
                    'data': {
                        'type': 'Unsafe Lifecycle Method',
                        'method': method,
                        'line': i
                    }
                })
    
    return bugs
