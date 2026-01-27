"""
Codebase Constraint Builder

Centralizes the logic for building code generation constraints.
Both plan generation and code generation use this to ensure consistency.

This module prevents the AI from hallucinating non-existent imports by
providing explicit lists of available files, import aliases, and UI components.
"""

import os
import json
import re
from typing import Dict, List, Optional
from pathlib import Path


class CodebaseConstraintBuilder:
    """Builds constraints for AI code generation based on actual codebase structure."""
    
    def __init__(self, repo_path: str):
        """
        Initialize constraint builder.
        
        Args:
            repo_path: Path to the repository root
        """
        self.repo_path = repo_path
        self._cache = {}
    
    def build_complete_constraints(self, tech_stack: Dict = None, files_being_created: List[str] = None) -> str:
        """
        Build complete constraints string for AI prompts.
        
        Args:
            tech_stack: Tech stack information from CodeAnalyzer
            files_being_created: List of file paths being created in this PR (optional)
            
        Returns:
            Complete constraints string to include in prompts
        """
        constraints = []
        
        # 1. Existing files constraints (includes files being created)
        existing_files = self.build_existing_files_constraints(files_being_created=files_being_created)
        if existing_files:
            constraints.append(existing_files)
        
        # 2. Import alias constraints
        import_aliases = self.build_import_alias_constraints()
        if import_aliases:
            constraints.append(import_aliases)
        
        # 3. UI library constraints
        ui_constraints = self.build_ui_library_constraints()
        if ui_constraints:
            constraints.append(ui_constraints)
        
        # 4. Framework constraints
        if tech_stack:
            framework_constraints = self.build_framework_constraints(tech_stack)
            if framework_constraints:
                constraints.append(framework_constraints)
        
        return "\n\n".join(constraints)
    
    def build_existing_files_constraints(self, files_being_created: List[str] = None) -> str:
        """
        Build constraints listing all existing import able files.
        
        Args:
            files_being_created: List of file paths being created in this PR (optional)
        
        Returns:
            Formatted string with existing files organized by directory
        """
        if 'existing_files' in self._cache and not files_being_created:
            return self._cache['existing_files']
        
        try:
            # Discover all code files
            code_extensions = {'.tsx', '.ts', '.jsx', '.js', '.py'}
            files_by_dir = {}
            
            # Walk the repository
            skip_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build', 
                        'venv', '.venv', 'vendor', 'coverage', '.idea', '.vscode'}
            
            for root, dirs, files in os.walk(self.repo_path):
                # Filter out directories to skip
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                rel_root = os.path.relpath(root, self.repo_path)
                if rel_root == '.':
                    rel_root = ''
                
                for file in files:
                    ext = os.path.splitext(file)[1]
                    if ext in code_extensions:
                        # Determine category
                        rel_path = os.path.join(rel_root, file) if rel_root else file
                        
                        # Categorize by directory type
                        if 'page' in rel_path.lower():
                            category = 'Pages'
                        elif 'component' in rel_path.lower():
                            category = 'Components'
                        elif 'app' in file.lower() or 'main' in file.lower():
                            category = 'App Files'
                        elif 'route' in rel_path.lower():
                            category = 'Routes'
                        else:
                            category = 'Other Files'
                        
                        if category not in files_by_dir:
                            files_by_dir[category] = []
                        files_by_dir[category].append(rel_path)
            
            # NEW: Add files being created in this PR
            if files_being_created:
                for filepath in files_being_created:
                    # Categorize similarly
                    if 'page' in filepath.lower():
                        category = 'Pages (Being Created)'
                    elif 'component' in filepath.lower():
                        category = 'Components (Being Created)'
                    elif 'app' in filepath.lower() or 'main' in filepath.lower():
                        category = 'App Files (Being Created)'
                    elif 'route' in filepath.lower():
                        category = 'Routes (Being Created)'
                    else:
                        category = 'Other Files (Being Created)'
                    
                    if category not in files_by_dir:
                        files_by_dir[category] = []
                    files_by_dir[category].append(filepath)
            
            # Build constraint string
            constraint_parts = ["===== EXISTING FILES REFERENCE ====="]
            constraint_parts.append("The following files exist in the codebase OR are being created in this PR.")
            constraint_parts.append("ONLY import from these files. DO NOT create imports for non-existent files.")
            constraint_parts.append("")
            
            # Sort categories for consistent output
            priority_order = ['App Files', 'Pages', 'Components', 'Routes', 'Other Files',
                            'Pages (Being Created)', 'Components (Being Created)', 
                            'App Files (Being Created)', 'Routes (Being Created)', 'Other Files (Being Created)']
            for category in priority_order:
                if category in files_by_dir:
                    constraint_parts.append(f"{category}:")
                    for filepath in sorted(files_by_dir[category])[:50]:  # Limit to 50 per category
                        constraint_parts.append(f"  - {filepath}")
                    constraint_parts.append("")
            
            constraint_parts.append("CRITICAL RULES:")
            constraint_parts.append("1. If a file is NOT in this list, it does NOT exist")
            constraint_parts.append("2. Files marked '(Being Created)' will be available for import - they are being generated in this same PR")
            constraint_parts.append("3. DO NOT create imports like './pages/AboutPage' unless AboutPage is listed above")
            constraint_parts.append("4. When in doubt, verify the file is in this list before importing it")
            constraint_parts.append("==========================================")
            
            result = "\n".join(constraint_parts)
            # Don't cache if files_being_created was provided
            if not files_being_created:
                self._cache['existing_files'] = result
            return result
            
        except Exception as e:
            print(f"[CONSTRAINT_BUILDER] Error building existing files constraints: {e}")
            return ""
    
    def build_import_alias_constraints(self) -> str:
        """
        Build constraints for import path aliases from tsconfig.json/jsconfig.json.
        
        Returns:
            Formatted string with import alias rules
        """
        if 'import_aliases' in self._cache:
            return self._cache['import_aliases']
        
        try:
            # Check for tsconfig.json or jsconfig.json
            config_paths = [
                os.path.join(self.repo_path, "tsconfig.json"),
                os.path.join(self.repo_path, "jsconfig.json"),
                os.path.join(self.repo_path, "client", "tsconfig.json"),
                os.path.join(self.repo_path, "client", "jsconfig.json"),
            ]
            
            config_path = None
            for path in config_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if not config_path:
                return ""
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse JSON, handling comments
            content_clean = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
            content_clean = re.sub(r',(\s*[}\]])', r'\1', content_clean)
            
            try:
                config = json.loads(content_clean)
            except json.JSONDecodeError:
                # Try to extract just the paths section
                paths_match = re.search(r'"paths"\s*:\s*{([^}]+)}', content, re.DOTALL)
                if not paths_match:
                    return ""
                
                paths_json = '{' + paths_match.group(0) + '}'
                paths_json = re.sub(r'//.*?$', '', paths_json, flags=re.MULTILINE)
                paths_json = re.sub(r'/\*.*?\*/', '', paths_json, flags=re.DOTALL)
                paths_json = re.sub(r',(\s*})', r'\1', paths_json)
                
                minimal_config = json.loads(paths_json)
                config = {"compilerOptions": minimal_config}
            
            # Extract paths
            paths = config.get("compilerOptions", {}).get("paths", {})
            
            if not paths:
                return ""
            
            # Build constraint string
            constraint_parts = ["===== CRITICAL: IMPORT PATH REQUIREMENTS ====="]
            constraint_parts.append("This project uses import path aliases configured in tsconfig.json:")
            constraint_parts.append("")
            constraint_parts.append("CONFIGURED ALIASES:")
            
            for alias_pattern, path_list in paths.items():
                if path_list:
                    clean_alias = alias_pattern.replace("/*", "")
                    base_path = path_list[0].replace("/*", "")
                    constraint_parts.append(f"  {clean_alias}/ → for imports from {base_path}")
            
            constraint_parts.append("")
            constraint_parts.append("MANDATORY IMPORT RULES:")
            constraint_parts.append("1. ALWAYS use the configured aliases for cross-directory imports")
            constraint_parts.append("2. NEVER use relative paths like './pages/' or '../components/' for cross-directory imports")
            constraint_parts.append("3. ALWAYS include file extension (.tsx, .jsx, .ts, .js) in ALL imports")
            constraint_parts.append("4. Relative imports (./) are ONLY for files in the SAME directory")
            constraint_parts.append("")
            constraint_parts.append("CORRECT EXAMPLES:")
            constraint_parts.append("  ✓ import ProfilePage from '@/pages/ProfilePage.tsx'")
            constraint_parts.append("  ✓ import { Button } from '@/components/ui/button.tsx'")
            constraint_parts.append("")
            constraint_parts.append("WRONG EXAMPLES (WILL CAUSE BUILD FAILURE):")
            constraint_parts.append("  ✗ import ProfilePage from './pages/ProfilePage.tsx'  (use @/pages/)")
            constraint_parts.append("  ✗ import ProfilePage from './pages/ProfilePage'  (missing extension)")
            constraint_parts.append("  ✗ import { Button } from '../components/ui/button.tsx'  (use @/components/)")
            constraint_parts.append("")
            constraint_parts.append("IF YOU USE WRONG IMPORT PATHS, ROLLUP/VITE WILL FAIL TO RESOLVE THEM.")
            constraint_parts.append("=============================================")
            
            result = "\n".join(constraint_parts)
            self._cache['import_aliases'] = result
            return result
            
        except Exception as e:
            print(f"[CONSTRAINT_BUILDER] Error building import alias constraints: {e}")
            return ""
    
    def build_ui_library_constraints(self) -> str:
        """
        Build constraints for available UI components.
        
        Returns:
            Formatted string with UI component import rules
        """
        if 'ui_library' in self._cache:
            return self._cache['ui_library']
        
        try:
            # Look for package.json
            package_json_paths = [
                os.path.join(self.repo_path, "package.json"),
                os.path.join(self.repo_path, "client", "package.json"),
            ]
            
            package_json_path = None
            for path in package_json_paths:
                if os.path.exists(path):
                    package_json_path = path
                    break
            
            if not package_json_path:
                return ""
            
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # Detect UI library
            ui_library = None
            shadcn_indicators = ["@radix-ui/react-slot", "class-variance-authority", "tailwind-merge"]
            
            if any(dep in all_deps for dep in shadcn_indicators):
                ui_library = "shadcn/ui"
            elif "@mui/material" in all_deps:
                ui_library = "material-ui"
            elif "antd" in all_deps:
                ui_library = "ant-design"
            elif "@chakra-ui/react" in all_deps:
                ui_library = "chakra-ui"
            
            if not ui_library:
                return ""
            
            # Find UI components directory
            ui_component_paths = [
                os.path.join(self.repo_path, "client", "src", "components", "ui"),
                os.path.join(self.repo_path, "src", "components", "ui"),
            ]
            
            available_components = []
            for ui_dir in ui_component_paths:
                if os.path.exists(ui_dir) and os.path.isdir(ui_dir):
                    for filename in os.listdir(ui_dir):
                        if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                            component_name = os.path.splitext(filename)[0]
                            available_components.append(component_name)
                    break
            
            # Build constraint string
            constraint_parts = ["===== CRITICAL: UI LIBRARY REQUIREMENTS ====="]
            constraint_parts.append(f"UI Framework: {ui_library}")
            constraint_parts.append("")
            
            if available_components:
                constraint_parts.append("AVAILABLE UI COMPONENTS:")
                for comp in sorted(available_components):
                    constraint_parts.append(f"  - {comp}")
                constraint_parts.append("")
            
            constraint_parts.append("MANDATORY IMPORT RULES:")
            constraint_parts.append("1. DO NOT use Material-UI (@mui/material) unless it's in package.json")
            constraint_parts.append("2. DO NOT use Ant Design (antd) unless it's in package.json")
            constraint_parts.append("3. USE ONLY the component imports from the components listed above")
            constraint_parts.append("4. For icons, use lucide-react: import { IconName } from 'lucide-react'")
            constraint_parts.append("5. ALWAYS include .tsx extension in component imports")
            constraint_parts.append("")
            constraint_parts.append("CORRECT EXAMPLES:")
            if available_components:
                constraint_parts.append(f"  ✓ import {{ Button }} from '@/components/ui/{available_components[0]}.tsx'")
            constraint_parts.append("  ✓ import { Activity, CheckCircle } from 'lucide-react'")
            constraint_parts.append("")
            constraint_parts.append("WRONG EXAMPLES (WILL CAUSE BUILD FAILURE):")
            constraint_parts.append("  ✗ import { Button } from '@mui/material'  (NOT installed)")
            constraint_parts.append("  ✗ import { Button } from 'antd'  (NOT installed)")
            constraint_parts.append("  ✗ import { toast } from '@/components/ui/use-toast'  (NOT available)")
            constraint_parts.append("")
            constraint_parts.append("IF YOU USE COMPONENTS NOT IN THE LIST, THE BUILD WILL FAIL.")
            constraint_parts.append("=============================================")
            
            result = "\n".join(constraint_parts)
            self._cache['ui_library'] = result
            return result
            
        except Exception as e:
            print(f"[CONSTRAINT_BUILDER] Error building UI library constraints: {e}")
            return ""
    
    def build_framework_constraints(self, tech_stack: Dict) -> str:
        """
        Build framework-specific constraints.
        
        Args:
            tech_stack: Tech stack information
            
        Returns:
            Formatted string with framework rules
        """
        framework = tech_stack.get('framework', 'unknown')
        language = tech_stack.get('language', 'javascript')
        
        constraint_parts = ["===== FRAMEWORK-SPECIFIC REQUIREMENTS ====="]
        constraint_parts.append(f"Framework: {framework}")
        constraint_parts.append(f"Language: {language}")
        constraint_parts.append("")
        
        # Framework-specific rules
        if framework == 'react' or framework == 'nextjs':
            ext = '.tsx' if language == 'typescript' else '.jsx'
            constraint_parts.append("REACT COMPONENT RULES:")
            constraint_parts.append(f"1. Component files MUST use {ext} extension")
            constraint_parts.append("2. Component name MUST match filename exactly")
            constraint_parts.append("3. Use default export for components")
            constraint_parts.append("4. Example: ProfilePage.tsx → export default function ProfilePage()")
        
        constraint_parts.append("=============================================")
        
        return "\n".join(constraint_parts)
    
    def get_existing_files_list(self) -> List[str]:
        """
        Get list of all existing code files.
        
        Returns:
            List of relative file paths
        """
        code_extensions = {'.tsx', '.ts', '.jsx', '.js', '.py'}
        files = []
        
        skip_dirs = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build', 
                    'venv', '.venv', 'vendor', 'coverage'}
        
        for root, dirs, filenames in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            rel_root = os.path.relpath(root, self.repo_path)
            if rel_root == '.':
                rel_root = ''
            
            for file in filenames:
                ext = os.path.splitext(file)[1]
                if ext in code_extensions:
                    rel_path = os.path.join(rel_root, file) if rel_root else file
                    files.append(rel_path)
        
        return files
    
    def clear_cache(self):
        """Clear the internal cache."""
        self._cache = {}


# Convenience functions for backward compatibility
def build_existing_files_constraints(repo_path: str) -> str:
    """Build existing files constraints."""
    builder = CodebaseConstraintBuilder(repo_path)
    return builder.build_existing_files_constraints()


def build_import_alias_constraints(repo_path: str) -> str:
    """Build import alias constraints."""
    builder = CodebaseConstraintBuilder(repo_path)
    return builder.build_import_alias_constraints()


def build_ui_library_constraints(repo_path: str) -> str:
    """Build UI library constraints."""
    builder = CodebaseConstraintBuilder(repo_path)
    return builder.build_ui_library_constraints()


def build_complete_constraints(repo_path: str, tech_stack: Dict = None) -> str:
    """Build complete constraints."""
    builder = CodebaseConstraintBuilder(repo_path)
    return builder.build_complete_constraints(tech_stack)
