"""
Build Validator

Validates generated code for common issues that cause build failures:
- Import path mismatches
- Component name inconsistencies
- Missing dependencies
- Syntax errors

Runs before PR submission to ensure code quality.
"""

import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class BuildValidator:
    """Validates generated code and identifies build-breaking issues."""
    
    # Common import patterns for TypeScript/JavaScript
    IMPORT_PATTERNS = [
        r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']',  # import X from 'path'
        r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']+)["\']',  # import { X } from 'path'
        r'import\s+\*\s+as\s+(\w+)\s+from\s+["\']([^"\']+)["\']',  # import * as X from 'path'
    ]
    
    # Path alias patterns (tsconfig.json paths)
    PATH_ALIASES = {
        '@/': 'src/',
        '@components/': 'src/components/',
        '@pages/': 'src/pages/',
        # NOTE: Do NOT add '~/': '' - it's not a standard alias and causes build errors
    }
    
    def validate_imports(self, generated_files: Dict[str, str], repo_path: str = None) -> Dict:
        """
        Validate that all imports in generated files are resolvable.
        
        Args:
            generated_files: Dict of {filepath: content}
            repo_path: Path to repository for checking existing files
            
        Returns:
            {
                'valid': bool,
                'issues': List[Dict],
                'warnings': List[Dict]
            }
        """
        issues = []
        warnings = []
        
        for filepath, content in generated_files.items():
            # Extract all imports from the file
            imports = self._extract_imports(content)
            
            for imp in imports:
                import_path = imp['path']
                imported_names = imp['names']
                line_number = imp['line']
                
                # Resolve the import path
                resolved_path = self._resolve_import_path(import_path, filepath, generated_files, repo_path)
                
                if not resolved_path:
                    issues.append({
                        'type': 'unresolved_import',
                        'file': filepath,
                        'line': line_number,
                        'import_path': import_path,
                        'message': f"Cannot resolve import '{import_path}'"
                    })
                    continue
                
                # Check if the imported names match the component name in the target file
                if resolved_path in generated_files:
                    target_content = generated_files[resolved_path]
                    component_issues = self._validate_component_names(
                        imported_names, target_content, resolved_path, filepath, line_number
                    )
                    issues.extend(component_issues)
        
        # Check for component name vs filename mismatches
        for filepath, content in generated_files.items():
            if filepath.endswith(('.tsx', '.jsx')):
                filename_issues = self._validate_filename_component_match(filepath, content)
                issues.extend(filename_issues)
        
        # Check for duplicate function/class names within files
        for filepath, content in generated_files.items():
            dup_issues = self._check_duplicate_identifiers(filepath, content)
            issues.extend(dup_issues)
        
        # Validate dependencies exist (basic check)
        for filepath, content in generated_files.items():
            if filepath.endswith(('.tsx', '.jsx', '.ts', '.js')):
                dep_issues = self._validate_dependencies(filepath, content, repo_path)
                issues.extend(dep_issues)
        
        # Check for orphaned components (created but never imported)
        orphan_issues = self._check_orphaned_components(generated_files)
        issues.extend(orphan_issues)
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def _extract_imports(self, content: str) -> List[Dict]:
        """Extract all import statements from file content."""
        imports = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Default import: import X from 'path'
            match = re.match(r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']', line)
            if match:
                imports.append({
                    'names': [match.group(1)],
                    'path': match.group(2),
                    'line': line_num,
                    'type': 'default'
                })
                continue
            
            # Named imports: import { X, Y } from 'path'
            match = re.match(r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']+)["\']', line)
            if match:
                names = [n.strip().split(' as ')[0].strip() for n in match.group(1).split(',')]
                imports.append({
                    'names': names,
                    'path': match.group(2),
                    'line': line_num,
                    'type': 'named'
                })
                continue
            
            # Namespace import: import * as X from 'path'
            match = re.match(r'import\s+\*\s+as\s+(\w+)\s+from\s+["\']([^"\']+)["\']', line)
            if match:
                imports.append({
                    'names': [match.group(1)],
                    'path': match.group(2),
                    'line': line_num,
                    'type': 'namespace'
                })
        
        return imports
    
    def _resolve_import_path(self, import_path: str, from_file: str, 
                            generated_files: Dict[str, str], repo_path: str = None) -> Optional[str]:
        """
        Resolve an import path to an actual file path.
        
        Args:
            import_path: The import path (e.g., '@/pages/ProfilePage')
            from_file: The file doing the importing
            generated_files: Dict of generated files
            repo_path: Path to repository
            
        Returns:
            Resolved file path or None if not found
        """
        # Handle relative imports
        if import_path.startswith('.'):
            from_dir = os.path.dirname(from_file)
            resolved = os.path.normpath(os.path.join(from_dir, import_path))
        else:
            # Handle path aliases
            resolved = import_path
            for alias, replacement in self.PATH_ALIASES.items():
                if import_path.startswith(alias):
                    resolved = import_path.replace(alias, replacement, 1)
                    break
        
        # Try common extensions
        extensions = ['', '.ts', '.tsx', '.js', '.jsx', '.json']
        for ext in extensions:
            test_path = resolved + ext
            
            # Check in generated files first
            if test_path in generated_files:
                return test_path
            
            # Normalize paths for comparison
            for gen_path in generated_files.keys():
                if gen_path.endswith(test_path) or test_path.endswith(gen_path):
                    return gen_path
        
        # If we have repo_path, check existing files
        if repo_path:
            for ext in extensions:
                full_path = os.path.join(repo_path, resolved + ext)
                if os.path.exists(full_path):
                    return resolved + ext
        
        return None
    
    def _validate_component_names(self, imported_names: List[str], target_content: str,
                                  target_file: str, from_file: str, line_number: int) -> List[Dict]:
        """Validate that imported component names actually exist in the target file."""
        issues = []
        
        # Extract component/function names from target file
        defined_exports = self._extract_exports(target_content)
        
        for name in imported_names:
            if name not in defined_exports:
                issues.append({
                    'type': 'component_name_mismatch',
                    'file': from_file,
                    'line': line_number,
                    'imported_name': name,
                    'target_file': target_file,
                    'available_exports': defined_exports,
                    'message': f"Component '{name}' is imported but not exported from '{target_file}'"
                })
        
        return issues
    
    def _extract_exports(self, content: str) -> List[str]:
        """Extract all exported names from file content."""
        exports = []
        
        # Default export: export default ComponentName
        match = re.search(r'export\s+default\s+(\w+)', content)
        if match:
            exports.append(match.group(1))
        
        # Default export (function/const): export default function X() or const X = () => export default X
        match = re.search(r'(?:function|const)\s+(\w+)', content)
        if match and 'export default' in content:
            exports.append(match.group(1))
        
        # Named exports: export { X, Y }
        matches = re.finditer(r'export\s+\{([^}]+)\}', content)
        for match in matches:
            names = [n.strip().split(' as ')[-1].strip() for n in match.group(1).split(',')]
            exports.extend(names)
        
        # Named exports (inline): export const X = ...
        matches = re.finditer(r'export\s+(?:const|function|class)\s+(\w+)', content)
        for match in matches:
            exports.append(match.group(1))
        
        return exports
    
    def _validate_filename_component_match(self, filepath: str, content: str) -> List[Dict]:
        """Validate that the main component name matches the filename."""
        issues = []
        
        # Get filename without extension
        filename = os.path.basename(filepath)
        component_name_from_file = os.path.splitext(filename)[0]
        
        # Extract the main component name from content
        # Look for: export default ComponentName or function ComponentName
        patterns = [
            r'export\s+default\s+function\s+(\w+)',
            r'function\s+(\w+)\s*\([^)]*\)\s*\{',  # First function definition
            r'const\s+(\w+)\s*[:=]\s*\([^)]*\)\s*=>', # Arrow function component
            r'export\s+default\s+(\w+)',
        ]
        
        component_name_from_content = None
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                component_name_from_content = match.group(1)
                break
        
        if component_name_from_content and component_name_from_content != component_name_from_file:
            issues.append({
                'type': 'filename_component_mismatch',
                'file': filepath,
                'filename_component': component_name_from_file,
                'actual_component': component_name_from_content,
                'message': f"Component '{component_name_from_content}' should match filename '{component_name_from_file}'"
            })
        
        return issues
    
    def generate_fixes(self, issues: List[Dict], generated_files: Dict[str, str]) -> Dict[str, str]:
        """
        Generate fixes for common validation issues.
        
        Args:
            issues: List of validation issues
            generated_files: Original generated files
            
        Returns:
            Dict of {filepath: fixed_content} for files that were fixed
        """
        fixed_files = {}
        
        for issue in issues:
            if issue['type'] == 'unresolved_import':
                # Try to fix import path
                fix = self._fix_import_path(issue, generated_files)
                if fix:
                    filepath, new_content = fix
                    fixed_files[filepath] = new_content
            
            elif issue['type'] == 'component_name_mismatch':
                # Fix component name to match import
                fix = self._fix_component_name(issue, generated_files)
                if fix:
                    filepath, new_content = fix
                    fixed_files[filepath] = new_content
            
            elif issue['type'] == 'filename_component_mismatch':
                # Fix component name to match filename
                fix = self._fix_filename_mismatch(issue, generated_files)
                if fix:
                    filepath, new_content = fix
                    fixed_files[filepath] = new_content
        
        return fixed_files
    
    def _fix_import_path(self, issue: Dict, generated_files: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """Fix an unresolved import by finding the correct path."""
        file_path = issue['file']
        wrong_path = issue['import_path']
        content = generated_files.get(file_path, '')
        
        if not content:
            return None
        
        # Try to find the correct path by looking for similar filenames
        target_basename = os.path.basename(wrong_path)
        
        for gen_file in generated_files.keys():
            if target_basename in gen_file or os.path.basename(gen_file).startswith(target_basename):
                # Found a match - update the import
                correct_path = self._calculate_relative_path(file_path, gen_file)
                new_content = content.replace(f'"{wrong_path}"', f'"{correct_path}"')
                new_content = new_content.replace(f"'{wrong_path}'", f"'{correct_path}'")
                
                print(f"[BUILD_VALIDATOR] Fixed import: '{wrong_path}' -> '{correct_path}'")
                return (file_path, new_content)
        
        return None
    
    def _fix_component_name(self, issue: Dict, generated_files: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """Fix component name mismatch."""
        target_file = issue['target_file']
        imported_name = issue['imported_name']
        content = generated_files.get(target_file, '')
        
        if not content:
            return None
        
        # Get the actual exported name
        exports = issue.get('available_exports', [])
        if not exports:
            return None
        
        actual_export = exports[0]
        
        # Rename the component in the file
        new_content = re.sub(
            rf'\bfunction\s+{re.escape(actual_export)}\b',
            f'function {imported_name}',
            content
        )
        new_content = re.sub(
            rf'\bconst\s+{re.escape(actual_export)}\b',
            f'const {imported_name}',
            new_content
        )
        new_content = re.sub(
            rf'\bexport\s+default\s+{re.escape(actual_export)}\b',
            f'export default {imported_name}',
            new_content
        )
        
        if new_content != content:
            print(f"[BUILD_VALIDATOR] Fixed component name: '{actual_export}' -> '{imported_name}'")
            return (target_file, new_content)
        
        return None
    
    def _fix_filename_mismatch(self, issue: Dict, generated_files: Dict[str, str]) -> Optional[Tuple[str, str]]:
        """Fix component name to match filename."""
        file_path = issue['file']
        expected_name = issue['filename_component']
        actual_name = issue['actual_component']
        content = generated_files.get(file_path, '')
        
        if not content:
            return None
        
        # CRITICAL: Check if expected_name already exists to avoid duplicates
        all_declarations = set()
        all_declarations.update(re.findall(r'\bfunction\s+(\w+)', content))
        all_declarations.update(re.findall(r'\bconst\s+(\w+)\s*=', content))
        
        if expected_name in all_declarations:
            print(f"[BUILD_VALIDATOR] ⚠️  {expected_name} already declared in {file_path}, skipping rename to avoid duplicates")
            return None
        
        # Safe to rename - expected_name doesn't exist yet
        # Rename component to match filename
        new_content = re.sub(
            rf'\bfunction\s+{re.escape(actual_name)}\b',
            f'function {expected_name}',
            content
        )
        new_content = re.sub(
            rf'\bconst\s+{re.escape(actual_name)}\b',
            f'const {expected_name}',
            new_content
        )
        new_content = re.sub(
            rf'\bexport\s+default\s+{re.escape(actual_name)}\b',
            f'export default {expected_name}',
            new_content
        )
        
        if new_content != content:
            print(f"[BUILD_VALIDATOR] Fixed component to match filename: '{actual_name}' -> '{expected_name}'")
            return (file_path, new_content)
        
        return None
    
    def _check_duplicate_identifiers(self, filepath: str, content: str) -> List[Dict]:
        """Check for duplicate function/class/const declarations."""
        issues = []
        
        # Extract all function, class, and const declarations
        patterns = [
            (r'function\s+(\w+)\s*\(', 'function'),
            (r'const\s+(\w+)\s*=', 'const'),
            (r'class\s+(\w+)', 'class'),
        ]
        
        identifiers = {}
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern, id_type in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    identifier = match.group(1)
                    
                    if identifier in identifiers:
                        issues.append({
                            'type': 'duplicate_identifier',
                            'file': filepath,
                            'line': line_num,
                            'identifier': identifier,
                            'identifier_type': id_type,
                            'first_declared_line': identifiers[identifier]['line'],
                            'message': f"Duplicate {id_type} '{identifier}' - already declared at line {identifiers[identifier]['line']}"
                        })
                    else:
                        identifiers[identifier] = {'line': line_num, 'type': id_type}
        
        return issues
    
    def _validate_dependencies(self, filepath: str, content: str, repo_path: str = None) -> List[Dict]:
        """Validate that imported dependencies exist in package.json."""
        issues = []
        
        # Extract npm package imports (not local files)
        npm_imports = []
        for line in content.split('\n'):
            # Match: import X from 'package-name'
            match = re.match(r'import\s+.*?from\s+["\']([^."][^"\']*)["\']', line)
            if match:
                pkg = match.group(1)
                # Filter out local imports (starting with ./ or @/)
                if not pkg.startswith(('./','../','@/','~/')):
                    npm_imports.append(pkg)
        
        if npm_imports and repo_path:
            # Try to read package.json
            package_json_path = os.path.join(repo_path, 'package.json')
            client_package_json = os.path.join(repo_path, 'client', 'package.json')
            
            dependencies = []
            for pkg_path in [package_json_path, client_package_json]:
                if os.path.exists(pkg_path):
                    try:
                        import json
                        with open(pkg_path, 'r') as f:
                            pkg_data = json.load(f)
                            dependencies.extend(pkg_data.get('dependencies', {}).keys())
                            dependencies.extend(pkg_data.get('devDependencies', {}).keys())
                    except Exception as e:
                        pass
            
            if dependencies:
                for npm_pkg in npm_imports:
                    # Check if the package exists in dependencies
                    pkg_name = npm_pkg.split('/')[0]  # Handle scoped packages
                    if pkg_name not in dependencies:
                        issues.append({
                            'type': 'missing_dependency',
                            'file': filepath,
                            'package': npm_pkg,
                            'message': f"Import '{npm_pkg}' not found in package.json dependencies"
                        })
        
        return issues
    
    def _check_orphaned_components(self, generated_files: Dict[str, str]) -> List[Dict]:
        """Check for components that are created but never imported."""
        issues = []
        
        # Find all React component files
        component_files = []
        for filepath in generated_files.keys():
            if filepath.endswith(('.tsx', '.jsx')):
                # Skip App files and index files
                basename = os.path.basename(filepath)
                if not basename.lower().startswith(('app.', 'index.', '_app.', '_document.')):
                    component_files.append(filepath)
        
        # Check if each component is imported somewhere
        for comp_file in component_files:
            component_name = os.path.splitext(os.path.basename(comp_file))[0]
            is_imported = False
            
            # Search for imports of this component in all files
            for filepath, content in generated_files.items():
                if filepath != comp_file:  # Don't check self-imports
                    # Check for various import patterns
                    import_patterns = [
                        rf'import.*{re.escape(component_name)}.*from',
                        rf'import.*\{{.*{re.escape(component_name)}.*\}}',
                    ]
                    
                    for pattern in import_patterns:
                        if re.search(pattern, content):
                            is_imported = True
                            break
                
                if is_imported:
                    break
            
            if not is_imported:
                issues.append({
                    'type': 'orphaned_component',
                    'file': comp_file,
                    'component_name': component_name,
                    'message': f"Component '{component_name}' is created but never imported in any file"
                })
        
        return issues
    
    def _calculate_relative_path(self, from_file: str, to_file: str) -> str:
        """Calculate relative import path between two files."""
        from_dir = os.path.dirname(from_file)
        to_path_no_ext = os.path.splitext(to_file)[0]
        
        # Try to use alias if possible
        for alias, replacement in self.PATH_ALIASES.items():
            if to_file.startswith(replacement):
                return alias + to_file[len(replacement):]
        
        # Fall back to relative path
        rel_path = os.path.relpath(to_path_no_ext, from_dir)
        if not rel_path.startswith('.'):
            rel_path = './' + rel_path
        
        return rel_path.replace(os.sep, '/')


# Global instance
build_validator = BuildValidator()
