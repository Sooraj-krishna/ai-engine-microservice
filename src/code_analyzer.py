"""
Code Analyzer - Parses AST and builds dependency graphs for better code understanding.
Helps generate more accurate fixes by understanding code structure.
"""

import os
import ast
import json
from pathlib import Path
from collections import defaultdict
import re

class CodeAnalyzer:
    """
    Analyzes code structure using AST parsing and dependency analysis.
    """
    
    def __init__(self, repo_path=None):
        self.repo_path = repo_path
        self.dependency_graph = defaultdict(set)
        self.file_structure = {}
        self.imports_map = {}
        self.functions_map = {}
        self.classes_map = {}
        
    def analyze_repository(self):
        """
        Analyze the entire repository structure.
        """
        if not self.repo_path or not os.path.exists(self.repo_path):
            return {}
        
        print(f"[CODE_ANALYZER] Analyzing repository structure: {self.repo_path}")
        
        # Analyze all code files
        for root, dirs, files in os.walk(self.repo_path):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__', '.next', 'dist', 'build']]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Analyze based on file type
                if file.endswith('.py'):
                    self.analyze_python_file(file_path, rel_path)
                elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                    self.analyze_javascript_file(file_path, rel_path)
                elif file.endswith(('.html', '.htm')):
                    self.analyze_html_file(file_path, rel_path)
        
        # Build dependency graph
        self.build_dependency_graph()
        
        return {
            'dependency_graph': dict(self.dependency_graph),
            'file_structure': self.file_structure,
            'imports_map': self.imports_map,
            'functions_map': self.functions_map,
            'classes_map': self.classes_map
        }
    
    def analyze_python_file(self, file_path, rel_path):
        """
        Analyze Python file using AST.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # Skip files with syntax errors
                return
            
            file_info = {
                'type': 'python',
                'imports': [],
                'functions': [],
                'classes': [],
                'dependencies': []
            }
            
            # Walk AST
            for node in ast.walk(tree):
                # Extract imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info['imports'].append(alias.name)
                        self.imports_map[rel_path] = self.imports_map.get(rel_path, []) + [alias.name]
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        file_info['imports'].append(node.module)
                        self.imports_map[rel_path] = self.imports_map.get(rel_path, []) + [node.module]
                
                # Extract functions
                elif isinstance(node, ast.FunctionDef):
                    file_info['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                    self.functions_map[f"{rel_path}::{node.name}"] = {
                        'file': rel_path,
                        'line': node.lineno,
                        'type': 'function'
                    }
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    file_info['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': methods
                    })
                    self.classes_map[f"{rel_path}::{node.name}"] = {
                        'file': rel_path,
                        'line': node.lineno,
                        'methods': methods
                    }
            
            self.file_structure[rel_path] = file_info
            
        except Exception as e:
            print(f"[CODE_ANALYZER] Error analyzing Python file {rel_path}: {e}")
    
    def analyze_javascript_file(self, file_path, rel_path):
        """
        Analyze JavaScript/TypeScript file using regex patterns.
        (Full AST parsing would require esprima or similar, using patterns for now)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'type': 'javascript',
                'imports': [],
                'functions': [],
                'classes': [],
                'exports': []
            }
            
            # Extract imports (ES6 and CommonJS)
            import_patterns = [
                r"import\s+.*?\s+from\s+['\"]([^'\"]+)['\"]",  # ES6 imports
                r"require\(['\"]([^'\"]+)['\"]\)",  # CommonJS requires
            ]
            
            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                file_info['imports'].extend(matches)
                self.imports_map[rel_path] = self.imports_map.get(rel_path, []) + matches
            
            # Extract function declarations
            function_patterns = [
                r"function\s+(\w+)\s*\(",  # function name()
                r"const\s+(\w+)\s*=\s*\([^)]*\)\s*=>",  # const name = () =>
                r"(\w+)\s*:\s*function\s*\(",  # name: function()
                r"(\w+)\s*:\s*\([^)]*\)\s*=>",  # name: () =>
            ]
            
            for pattern in function_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if match not in [f['name'] for f in file_info['functions']]:
                        file_info['functions'].append({'name': match})
                        self.functions_map[f"{rel_path}::{match}"] = {
                            'file': rel_path,
                            'type': 'function'
                        }
            
            # Extract class declarations
            class_pattern = r"class\s+(\w+)"
            class_matches = re.findall(class_pattern, content)
            for class_name in class_matches:
                # Extract methods
                method_pattern = rf"{class_name}\s*{{[^}}]*?(\w+)\s*\([^)]*\)\s*{{"
                methods = re.findall(method_pattern, content, re.DOTALL)
                
                file_info['classes'].append({
                    'name': class_name,
                    'methods': methods[:10]  # Limit to first 10 methods
                })
                self.classes_map[f"{rel_path}::{class_name}"] = {
                    'file': rel_path,
                    'methods': methods[:10]
                }
            
            # Extract exports
            export_patterns = [
                r"export\s+(?:default\s+)?(?:function|class|const|let)\s+(\w+)",
                r"module\.exports\s*=\s*(\w+)",
            ]
            for pattern in export_patterns:
                exports = re.findall(pattern, content)
                file_info['exports'].extend(exports)
            
            self.file_structure[rel_path] = file_info
            
        except Exception as e:
            print(f"[CODE_ANALYZER] Error analyzing JS file {rel_path}: {e}")
    
    def analyze_html_file(self, file_path, rel_path):
        """
        Analyze HTML file structure.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_info = {
                'type': 'html',
                'scripts': [],
                'stylesheets': [],
                'ids': [],
                'classes': []
            }
            
            # Extract script sources
            script_pattern = r'<script[^>]*src=["\']([^"\']+)["\']'
            scripts = re.findall(script_pattern, content, re.IGNORECASE)
            file_info['scripts'].extend(scripts)
            
            # Extract stylesheet links
            link_pattern = r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']stylesheet["\']'
            stylesheets = re.findall(link_pattern, content, re.IGNORECASE)
            file_info['stylesheets'].extend(stylesheets)
            
            # Extract IDs
            id_pattern = r'id=["\']([^"\']+)["\']'
            ids = re.findall(id_pattern, content, re.IGNORECASE)
            file_info['ids'] = list(set(ids))[:20]  # Limit to 20 unique IDs
            
            # Extract classes
            class_pattern = r'class=["\']([^"\']+)["\']'
            classes = re.findall(class_pattern, content, re.IGNORECASE)
            file_info['classes'] = list(set(classes))[:20]  # Limit to 20 unique classes
            
            self.file_structure[rel_path] = file_info
            
        except Exception as e:
            print(f"[CODE_ANALYZER] Error analyzing HTML file {rel_path}: {e}")
    
    def build_dependency_graph(self):
        """
        Build dependency graph from imports and file relationships.
        """
        # Build graph based on imports
        for file_path, imports in self.imports_map.items():
            for imp in imports:
                # Try to find the file that provides this import
                provider = self.find_provider(imp)
                if provider:
                    self.dependency_graph[file_path].add(provider)
        
        # Build graph based on HTML script/stylesheet references
        for file_path, file_info in self.file_structure.items():
            if file_info.get('type') == 'html':
                # Link to referenced scripts
                for script in file_info.get('scripts', []):
                    script_file = self.find_file_by_name(script)
                    if script_file:
                        self.dependency_graph[file_path].add(script_file)
                
                # Link to referenced stylesheets
                for stylesheet in file_info.get('stylesheets', []):
                    css_file = self.find_file_by_name(stylesheet)
                    if css_file:
                        self.dependency_graph[file_path].add(css_file)
    
    def find_provider(self, import_name):
        """
        Find the file that provides a given import.
        """
        if not self.repo_path:
            return None
        
        # Try different strategies
        # 1. Direct file match
        possible_paths = [
            f"{import_name.replace('.', '/')}.py",
            f"{import_name.replace('.', '/')}/__init__.py",
            f"{import_name}.js",
            f"{import_name}.jsx",
            f"{import_name}.ts",
            f"{import_name}.tsx",
        ]
        
        for path in possible_paths:
            full_path = os.path.join(self.repo_path, path)
            if os.path.exists(full_path):
                return os.path.relpath(full_path, self.repo_path)
        
        # 2. Search in file structure
        for file_path, file_info in self.file_structure.items():
            # Check exports
            if import_name in file_info.get('exports', []):
                return file_path
            
            # Check if file name matches
            file_name = os.path.basename(file_path)
            if file_name.startswith(import_name.split('.')[-1]):
                return file_path
        
        return None
    
    def find_file_by_name(self, name):
        """
        Find file by name (for script/stylesheet references).
        """
        if not self.repo_path:
            return None
        
        # Remove query strings and fragments
        clean_name = name.split('?')[0].split('#')[0]
        
        # Try to find the file
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file == clean_name or file.endswith(clean_name):
                    return os.path.relpath(os.path.join(root, file), self.repo_path)
        
        return None
    
    def get_related_files(self, file_path, max_depth=2):
        """
        Get files related to a given file through dependencies.
        """
        related = set()
        visited = set()
        
        def traverse(current_file, depth):
            if depth > max_depth or current_file in visited:
                return
            
            visited.add(current_file)
            
            # Get direct dependencies
            deps = self.dependency_graph.get(current_file, set())
            for dep in deps:
                related.add(dep)
                if depth < max_depth:
                    traverse(dep, depth + 1)
            
            # Get files that depend on this file
            for other_file, deps in self.dependency_graph.items():
                if current_file in deps:
                    related.add(other_file)
                    if depth < max_depth:
                        traverse(other_file, depth + 1)
        
        traverse(file_path, 0)
        return list(related)
    
    def get_file_context(self, file_path):
        """
        Get comprehensive context for a file including structure and dependencies.
        """
        file_info = self.file_structure.get(file_path, {})
        related_files = self.get_related_files(file_path)
        
        context = {
            'file': file_path,
            'type': file_info.get('type', 'unknown'),
            'imports': file_info.get('imports', []),
            'functions': file_info.get('functions', []),
            'classes': file_info.get('classes', []),
            'dependencies': list(self.dependency_graph.get(file_path, set())),
            'dependents': [
                f for f, deps in self.dependency_graph.items()
                if file_path in deps
            ],
            'related_files': related_files[:10]  # Limit to 10 related files
        }
        
        return context
    
    def get_codebase_summary(self):
        """
        Get summary of the entire codebase structure.
        """
        return {
            'total_files': len(self.file_structure),
            'python_files': sum(1 for f in self.file_structure.values() if f.get('type') == 'python'),
            'javascript_files': sum(1 for f in self.file_structure.values() if f.get('type') == 'javascript'),
            'html_files': sum(1 for f in self.file_structure.values() if f.get('type') == 'html'),
            'total_functions': len(self.functions_map),
            'total_classes': len(self.classes_map),
            'dependency_edges': sum(len(deps) for deps in self.dependency_graph.values())
        }

