
import requests
from bs4 import BeautifulSoup
import os
import re

def detect_deployment_errors(url):
    """
    Detects deployment configuration errors by checking the website's status code.
    """
    errors = []
    try:
        response = requests.get(url, timeout=10)
        if response.status_code >= 400:
            errors.append({
                "type": "Deployment Configuration Error",
                "description": f"The application URL returned a {response.status_code} status code, which may indicate a deployment or routing problem.",
                "details": f"Status Code: {response.status_code}"
            })
    except requests.RequestException as e:
        errors.append({
            "type": "Deployment Configuration Error",
            "description": "Could not connect to the application URL, which may indicate a critical deployment failure.",
            "details": str(e)
        })
    return errors

def detect_broken_assets(url):
    """
    Detects broken static assets by checking for 404 errors on images, scripts, and stylesheets.
    """
    errors = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for tag in soup.find_all(['img', 'script', 'link']):
            asset_url = ''
            if tag.name == 'link' and tag.get('rel') == ['stylesheet']:
                asset_url = tag.get('href')
            elif tag.name in ['img', 'script']:
                asset_url = tag.get('src')

            if not asset_url:
                continue

            # Basic check for relative URLs
            if asset_url.startswith('/') and not asset_url.startswith('//'):
                asset_url = url.rstrip('/') + asset_url

            try:
                asset_response = requests.head(asset_url, timeout=5)
                if asset_response.status_code == 404:
                    errors.append({
                        "type": "Broken or Missing Static Assets",
                        "description": f"A static asset is missing, leading to broken images, styles, or functionality.",
                        "details": f"Asset URL: {asset_url} returned a 404 Not Found error."
                    })
            except requests.RequestException:
                # Could log this as a warning, but for now, we focus on 404s
                pass

    except requests.RequestException:
        # This error is already caught by detect_deployment_errors
        pass
    
    return errors

def detect_in_memory_storage(github_repo_path):
    """
    Scans the codebase for patterns indicating in-memory data storage.
    """
    errors = []
    # This is a simplified check. A real implementation would need more sophisticated static analysis.
    
    try:
        # Check for Python files
        for root, _, files in os.walk(github_repo_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Regex to find global lists/dicts being appended to, but not database interactions
                            if re.search(r"^\w+\s*=\s*\[\]|^\w+\s*=\s*\{\}", content, re.MULTILINE) and \
                               re.search(r"\.append\(|\.add\(", content):
                                if "database" not in content.lower() and "sql" not in content.lower():
                                    errors.append({
                                        "type": "Data Persistence and State Management Error",
                                        "description": "Potential use of in-memory storage detected. Data may be lost on server restarts.",
                                        "details": f"In-memory list or dict manipulation found in: {file_path}"
                                    })
                    except Exception as e:
                        print(f"[BUG_DETECTOR] Error reading or processing Python file {file_path}: {e}")

        # Check for JavaScript/TypeScript files
        for root, _, files in os.walk(github_repo_path):
            for file in files:
                if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Heuristic: look for array initialization and .push() in the same file
                            if re.search(r"=\s*\[\]", content) and re.search(r"\.push\(", content):
                                # Avoid frontend component files which use state management (useState)
                                if 'useState' in content or 'useReducer' in content:
                                    continue
                                
                                # Avoid files that look like database clients
                                if "database" not in content.lower() and "sql" not in content.lower() and "mongo" not in content.lower():
                                    errors.append({
                                        "type": "Data Persistence and State Management Error",
                                        "description": "Potential use of in-memory storage detected in JavaScript file. Data may be lost on server restarts.",
                                        "details": f"In-memory array manipulation found in: {file_path}"
                                    })
                    except Exception as e:
                        print(f"[BUG_DETECTOR] Error reading or processing JS/TS file {file_path}: {e}")
    except Exception as e:
        print(f"[BUG_DETECTOR] An unexpected error occurred during in-memory storage detection: {e}")
    return errors

def run_bug_detection(url, github_repo_path):
    """
    Runs all bug detection checks.
    """
    all_bugs = []
    all_bugs.extend(detect_deployment_errors(url))
    all_bugs.extend(detect_broken_assets(url))
    all_bugs.extend(detect_in_memory_storage(github_repo_path))
    return all_bugs
