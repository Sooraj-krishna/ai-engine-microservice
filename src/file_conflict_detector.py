"""
File Conflict Detector

Detects and prevents:
- Duplicate function/class/const identifiers
- File overwrites (entire file replacements)
- Files created in wrong locations
- Naming convention violations

Author: AI Engine
Created: 2026-01-19
"""

import os
import re
from typing import Dict, List, Optional, Set
from pathlib import Path
import ast


class FileConflictDetector:
    """Detects file conflicts and naming issues"""
    
    def __init__(self):
        print("[CONFLICT_DETECTOR] Initialized")
    
    async def detect_conflicts(
        self,
        generated_files: Dict[str, str],
        repo_path: str
    ) -> Dict:
        """
        Detect conflicts in generated files.
        
        Args:
            generated_files: Dict of {filepath: content}
            repo_path: Path to repository
            
        Returns:
            {
                'conflicts': List[Dict],
                'warnings': List[str]
            }
        """
        conflicts = []
        warnings = []
        
        print(f"[CONFLICT_DETECTOR] Checking {len(generated_files)} files for conflicts")
        
        # 1. Check for duplicate identifiers within generated files
        duplicate_conflicts = self._check_duplicate_identifiers(generated_files)
        conflicts.extend(duplicate_conflicts)
        
        # 2. Check for file overwrites
        overwrite_conflicts = await self._check_overwrites(generated_files, repo_path)
        conflicts.extend(overwrite_conflicts)
        
        # 3. Check file locations and paths
        location_conflicts = self._check_file_locations(generated_files, repo_path)
        conflicts.extend(location_conflicts)
        
        # 4. Check naming conventions
        naming_conflicts = self._check_naming_conventions(generated_files)
        conflicts.extend(naming_conflicts)
        
        # 5. Check for path traversal attempts
        traversal_conflicts = self._check_path_traversal(generated_files)
        conflicts.extend(traversal_conflicts)
        
        print(f"[CONFLICT_DETECTOR] Found {len(conflicts)} conflicts, {len(warnings)} warnings")
        
        return {
            'conflicts': conflicts,
            'warnings': warnings
        }
    
    def _check_duplicate_identifiers(self, generated_files: Dict[str, str]) -> List[Dict]:
        """Check for duplicate function/class/const names across generated files"""
        conflicts = []
        
        # Track identifiers: {name: [list of files]}
        js_identifiers: Dict[str, List[str]] = {}
        py_identifiers: Dict[str, List[str]] = {}
        
        for filepath, content in generated_files.items():
            ext = Path(filepath).suffix
            
            if ext in ['.js', '.jsx', '.ts', '.tsx']:
                # Extract JavaScript/TypeScript identifiers
                identifiers = self._extract_js_identifiers(content)
                for identifier in identifiers:
                    if identifier not in js_identifiers:
                        js_identifiers[identifier] = []
                    js_identifiers[identifier].append(filepath)
            
            elif ext == '.py':
                # Extract Python identifiers
                identifiers = self._extract_py_identifiers(content)
                for identifier in identifiers:
                    if identifier not in py_identifiers:
                        py_identifiers[identifier] = []
                    py_identifiers[identifier].append(filepath)
        
        # Find duplicates
        for identifier, files in js_identifiers.items():
            if len(files) > 1:
                conflicts.append({
                    'type': 'duplicate_identifier',
                    'file': ', '.join(files),
                    'message': f"Duplicate identifier '{identifier}' in multiple files",
                    'resolution': f"Rename '{identifier}' in one of the files or use unique names"
                })
        
        for identifier, files in py_identifiers.items():
            if len(files) > 1:
                conflicts.append({
                    'type': 'duplicate_identifier',
                    'file': ', '.join(files),
                    'message': f"Duplicate identifier '{identifier}' in multiple Python files",
                    'resolution': f"Rename '{identifier}' in one of the files"
                })
        
        return conflicts
    
    def _extract_js_identifiers(self, content: str) -> Set[str]:
        """Extract function, class, and const names from JavaScript/TypeScript"""
        identifiers = set()
        
        # Function declarations
        func_pattern = r'\b(function|const|let|var)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*[=\(]'
        for match in re.finditer(func_pattern, content):
            identifiers.add(match.group(2))
        
        # Class declarations
        class_pattern = r'\bclass\s+([a-zA-Z_$][a-zA-Z0-9_$]*)'
        for match in re.finditer(class_pattern, content):
            identifiers.add(match.group(1))
        
        # Export default function
        export_pattern = r'export\s+default\s+(?:function\s+)?([a-zA-Z_$][a-zA-Z0-9_$]*)'
        for match in re.finditer(export_pattern, content):
            identifiers.add(match.group(1))
        
        return identifiers
    
    def _extract_py_identifiers(self, content: str) -> Set[str]:
        """Extract function and class names from Python"""
        identifiers = set()
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    identifiers.add(node.name)
        except:
            # If AST parsing fails, use regex
            func_pattern = r'\bdef\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            class_pattern = r'\bclass\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[\(:]'
            
            for match in re.finditer(func_pattern, content):
                identifiers.add(match.group(1))
            for match in re.finditer(class_pattern, content):
                identifiers.add(match.group(1))
        
        return identifiers
    
    async def _check_overwrites(self, generated_files: Dict[str, str], repo_path: str) -> List[Dict]:
        """Check if generated files would overwrite existing files completely"""
        conflicts = []
        
        for filepath, content in generated_files.items():
            full_path = os.path.join(repo_path, filepath)
            
            if os.path.exists(full_path):
                # File exists - check if this is a complete overwrite
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                    
                    # Check if the new content is completely different
                    # (More than 80% different)
                    similarity = self._calculate_similarity(existing_content, content)
                    
                    if similarity < 0.2:  # Less than 20% similar
                        conflicts.append({
                            'type': 'file_overwrite',
                            'file': filepath,
                            'message': f"Generated code would completely overwrite existing file",
                            'resolution': 'Review the changes carefully or create a new file with a different name'
                        })
                except Exception as e:
                    print(f"[CONFLICT_DETECTOR] Error reading {filepath}: {e}")
        
        return conflicts
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0.0 to 1.0)"""
        # Simple word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _check_file_locations(self, generated_files: Dict[str, str], repo_path: str) -> List[Dict]:
        """Check if files are being created in appropriate locations"""
        conflicts = []
        
        # Dangerous locations
        dangerous_paths = [
            'node_modules/',
            '.git/',
            'venv/',
            'env/',
            '__pycache__/',
            'build/',
            'dist/',
        ]
        
        # System paths
        system_paths = [
            '/etc/',
            '/var/',
            '/usr/',
            '/root/',
            '/system/',
            'C:\\Windows\\',
        ]
        
        for filepath in generated_files.keys():
            # Check for dangerous paths
            for dangerous in dangerous_paths:
                if dangerous in filepath:
                    conflicts.append({
                        'type': 'dangerous_location',
                        'file': filepath,
                        'message': f"File created in dangerous location: {dangerous}",
                        'resolution': 'Move file to appropriate source directory'
                    })
            
            # Check for system paths
            for system_path in system_paths:
                if filepath.startswith(system_path):
                    conflicts.append({
                        'type': 'system_path',
                        'file': filepath,
                        'message': f"File targets system path: {system_path}",
                        'resolution': 'Use relative paths within project directory'
                    })
        
        return conflicts
    
    def _check_naming_conventions(self, generated_files: Dict[str, str]) -> List[Dict]:
        """Check if component names match file names"""
        conflicts = []
        
        for filepath, content in generated_files.items():
            ext = Path(filepath).suffix
            filename = Path(filepath).stem
            
            if ext in ['.jsx', '.tsx']:
                # Extract main component name
                component_match = re.search(
                    r'(?:export\s+default\s+)?(?:function|class|const)\s+([A-Z][a-zA-Z0-9]*)',
                    content
                )
                
                if component_match:
                    component_name = component_match.group(1)
                    
                    # Check if filename matches component name
                    if filename != component_name:
                        conflicts.append({
                            'type': 'naming_mismatch',
                            'file': filepath,
                            'message': f"Component name '{component_name}' doesn't match filename '{filename}'",
                            'resolution': f"Rename file to '{component_name}{ext}' or rename component to '{filename}'"
                        })
        
        return conflicts
    
    def _check_path_traversal(self, generated_files: Dict[str, str]) -> List[Dict]:
        """Check for path traversal attempts"""
        conflicts = []
        
        for filepath in generated_files.keys():
            if '..' in filepath:
                conflicts.append({
                    'type': 'path_traversal',
                    'file': filepath,
                    'message': 'Path contains ".." (path traversal attempt)',
                    'resolution': 'Use relative paths without parent directory references'
                })
            
            if filepath.startswith('/'):
                conflicts.append({
                    'type': 'absolute_path',
                    'file': filepath,
                    'message': 'Path is absolute (should be relative)',
                    'resolution': 'Use relative paths from project root'
                })
        
        return conflicts


# Global instance
file_conflict_detector = FileConflictDetector()
