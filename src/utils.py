def detect_framework(repo_files):
    """
    Infer main web framework by scanning filenames and directory patterns.
    Returns: 'react', 'nextjs', 'django', 'node', 'python', etc.
    """
    files = [f.lower() for f in repo_files]
    if any('manage.py' in f for f in files) or any(f.endswith('.py') for f in files):
        return 'django' if 'manage.py' in files else 'python'
    if any('package.json' in f for f in files):
        if any(x in f for f in files for x in ['.tsx', '/pages/']):
            return 'nextjs'
        if any(x in f for f in files for x in ['.jsx', '/components/', '.js']):
            return 'react'
        return 'node'
    return 'unknown'

def log_issue(issue, details, level="INFO"):
    print(f"[{level}] - {issue}: {details}")
