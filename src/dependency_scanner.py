"""
Dependency Vulnerability Scanner
Runs npm audit and pip-audit to find security issues in dependencies
"""

import subprocess
import json
import os
from typing import List, Dict


async def run_dependency_scan(repo_path: str) -> List[Dict]:
    """
    Run dependency vulnerability scans on the repository.
    
    Args:
        repo_path: Path to repository
        
    Returns:
        List of vulnerability bugs
    """
    bugs = []
    
    if not repo_path or not os.path.exists(repo_path):
        print("[DEPENDENCY_SCAN] No valid repo path provided")
        return bugs
    
    print(f"\n[DEPENDENCY_SCAN] ========================================")
    print(f"[DEPENDENCY_SCAN] Scanning dependencies in {repo_path}")
    
    # Scan npm dependencies
    npm_bugs = await scan_npm_dependencies(repo_path)
    bugs.extend(npm_bugs)
    
    # Scan pip dependencies
    pip_bugs = await scan_pip_dependencies(repo_path)
    bugs.extend(pip_bugs)
    
    print(f"[DEPENDENCY_SCAN] ✅ Found {len(bugs)} dependency vulnerabilities")
    print(f"[DEPENDENCY_SCAN] ========================================\n")
    
    return bugs


async def scan_npm_dependencies(repo_path: str) -> List[Dict]:
    """Scan npm dependencies for vulnerabilities."""
    bugs = []
    
    # Check for package.json in main repo or ui directory
    ui_path = os.path.join(repo_path, 'ai-engine-ui')
    npm_paths = []
    
    if os.path.exists(os.path.join(repo_path, 'package.json')):
        npm_paths.append(repo_path)
    if os.path.exists(os.path.join(ui_path, 'package.json')):
        npm_paths.append(ui_path)
    
    if not npm_paths:
        print("[DEPENDENCY_SCAN] No package.json found, skipping npm audit")
        return bugs
    
    for npm_path in npm_paths:
        print(f"[DEPENDENCY_SCAN] Running npm audit in {os.path.basename(npm_path)}...")
        
        try:
            # Run npm audit with JSON output
            result = subprocess.run(
                ['npm', 'audit', '--json'],
                cwd=npm_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # npm audit returns non-zero if vulnerabilities found (expected)
            if result.stdout:
                audit_data = json.loads(result.stdout)
                
                # Parse vulnerabilities
                vulnerabilities = audit_data.get('vulnerabilities', {})
                
                if vulnerabilities:
                    print(f"[DEPENDENCY_SCAN]   Found {len(vulnerabilities)} npm vulnerabilities")
                    
                    for pkg_name, vuln_data in list(vulnerabilities.items())[:20]:  # Limit to 20
                        severity = vuln_data.get('severity', 'medium')
                        via = vuln_data.get('via', [])
                        
                        # Extract CVE info
                        cve_ids = []
                        descriptions = []
                        for v in via:
                            if isinstance(v, dict):
                                if v.get('source'):
                                    cve_ids.append(v.get('source'))
                                if v.get('title'):
                                    descriptions.append(v.get('title'))
                        
                        description = descriptions[0] if descriptions else f"Vulnerability in {pkg_name}"
                        cve = ', '.join(cve_ids[:3]) if cve_ids else 'No CVE'
                        
                        bugs.append({
                            'type': 'dependency_vulnerability',
                            'severity': map_npm_severity(severity),
                            'description': f"npm: {description}",
                            'details': f"Package: {pkg_name}\nSeverity: {severity}\nCVE: {cve}",
                            'file': 'package.json',
                            'target_file': os.path.join(os.path.basename(npm_path), 'package.json'),
                            'is_actual_bug': True,
                            'data': {
                                'type': 'npm vulnerability',
                                'package': pkg_name,
                                'severity': severity,
                                'cve': cve,
                                'scanner': 'npm audit'
                            }
                        })
                else:
                    print(f"[DEPENDENCY_SCAN]   ✅ No npm vulnerabilities found")
                    
        except subprocess.TimeoutExpired:
            print(f"[DEPENDENCY_SCAN]   ⚠️  npm audit timed out")
        except Exception as e:
            print(f"[DEPENDENCY_SCAN]   ⚠️  npm audit failed: {e}")
    
    return bugs


async def scan_pip_dependencies(repo_path: str) -> List[Dict]:
    """Scan Python dependencies for vulnerabilities."""
    bugs = []
    
    # Check for requirements.txt or pyproject.toml
    requirements_paths = [
        os.path.join(repo_path, 'requirements.txt'),
        os.path.join(repo_path, 'src', 'requirements.txt'),
        os.path.join(repo_path, 'pyproject.toml'),
    ]
    
    requirements_file = None
    for path in requirements_paths:
        if os.path.exists(path):
            requirements_file = path
            break
    
    if not requirements_file:
        print("[DEPENDENCY_SCAN] No requirements.txt found, skipping pip-audit")
        return bugs
    
    print(f"[DEPENDENCY_SCAN] Running pip-audit on {os.path.basename(requirements_file)}...")
    
    try:
        # Check if pip-audit is installed
        check_result = subprocess.run(
            ['pip-audit', '--version'],
            capture_output=True,
            timeout=5
        )
        
        if check_result.returncode != 0:
            print("[DEPENDENCY_SCAN]   ⚠️  pip-audit not installed, skipping")
            return bugs
        
        # Run pip-audit with JSON output
        result = subprocess.run(
            ['pip-audit', '--format', 'json', '-r', requirements_file],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.stdout:
            try:
                audit_data = json.loads(result.stdout)
                vulnerabilities = audit_data.get('dependencies', [])
                
                if vulnerabilities:
                    print(f"[DEPENDENCY_SCAN]   Found {len(vulnerabilities)} pip vulnerabilities")
                    
                    for vuln in vulnerabilities[:20]:  # Limit to 20
                        pkg_name = vuln.get('name', 'unknown')
                        pkg_version = vuln.get('version', 'unknown')
                        vulns_list = vuln.get('vulns', [])
                        
                        for v in vulns_list[:3]:  # Max 3 CVEs per package
                            cve_id = v.get('id', 'No CVE')
                            description = v.get('description', f'Vulnerability in {pkg_name}')
                            fix_versions = v.get('fix_versions', [])
                            
                            bugs.append({
                                'type': 'dependency_vulnerability',
                                'severity': 'high',  # pip-audit doesn't provide severity
                                'description': f"pip: {description[:100]}",
                                'details': f"Package: {pkg_name} {pkg_version}\nCVE: {cve_id}\nFix: {', '.join(fix_versions) if fix_versions else 'No fix available'}",
                                'file': os.path.basename(requirements_file),
                                'target_file': os.path.relpath(requirements_file, repo_path),
                                'is_actual_bug': True,
                                'data': {
                                    'type': 'pip vulnerability',
                                    'package': pkg_name,
                                    'version': pkg_version,
                                    'cve': cve_id,
                                    'fix_versions': fix_versions,
                                    'scanner': 'pip-audit'
                                }
                            })
                else:
                    print(f"[DEPENDENCY_SCAN]   ✅ No pip vulnerabilities found")
            except json.JSONDecodeError:
                print(f"[DEPENDENCY_SCAN]   ⚠️  Could not parse pip-audit output")
                
    except FileNotFoundError:
        print("[DEPENDENCY_SCAN]   ⚠️  pip-audit command not found")
    except subprocess.TimeoutExpired:
        print(f"[DEPENDENCY_SCAN]   ⚠️  pip-audit timed out")
    except Exception as e:
        print(f"[DEPENDENCY_SCAN]   ⚠️  pip-audit failed: {e}")
    
    return bugs


def map_npm_severity(npm_severity: str) -> str:
    """Map npm severity to our severity levels."""
    severity_map = {
        'critical': 'critical',
        'high': 'high',
        'moderate': 'medium',
        'low': 'low',
        'info': 'low'
    }
    return severity_map.get(npm_severity.lower(), 'medium')
