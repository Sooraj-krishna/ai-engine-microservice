"""
Framework Validator - specialized rules for Next.js (App Router) and Vite.
Prevents common framework-specific build and runtime errors.
"""

import os
import re
from typing import Dict, List, Tuple, Optional

class FrameworkValidator:
    """Specialized validator for modern web frameworks."""

    def __init__(self):
        # Next.js App Router special files
        self.nextjs_app_router_files = [
            'page.tsx', 'page.jsx', 'page.js',
            'layout.tsx', 'layout.jsx', 'layout.js',
            'loading.tsx', 'loading.jsx', 'loading.js',
            'error.tsx', 'error.jsx', 'error.js',
            'not-found.tsx', 'not-found.jsx', 'not-found.js',
            'route.ts', 'route.js'
        ]

        # Hooks that require 'use client'
        self.react_client_hooks = [
            'useState', 'useEffect', 'useContext', 'useReducer',
            'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
            'useLayoutEffect', 'useInsertionEffect', 'useTransition',
            'useDeferredValue', 'useSyncExternalStore', 'useId',
            'useOptimistic', 'useFormStatus', 'useFormState'
        ]

    def validate_framework_rules(self, generated_files: Dict[str, str], repo_path: str = None) -> List[Dict]:
        """
        Validate framework-specific rules across all generated files.
        """
        issues = []
        
        for filepath, content in generated_files.items():
            # 1. Detect Framework Context
            is_nextjs = self._is_nextjs_project(repo_path, filepath)
            is_vite = self._is_vite_project(repo_path, filepath)

            # 2. Next.js App Router Rules
            if is_nextjs:
                issues.extend(self._validate_nextjs_rules(filepath, content))

            # 3. Vite Rules
            if is_vite:
                issues.extend(self._validate_vite_rules(filepath, content))

        return issues

    def _is_nextjs_project(self, repo_path: str, filepath: str) -> bool:
        """Heuristic to detect if it's a Next.js project."""
        if repo_path and (os.path.exists(os.path.join(repo_path, 'next.config.js')) or 
                         os.path.exists(os.path.join(repo_path, 'next.config.mjs'))):
            return True
        # Check path structure: app/ layout.tsx, etc.
        if 'app/' in filepath or 'pages/' in filepath:
            return True
        return False

    def _is_vite_project(self, repo_path: str, filepath: str) -> bool:
        """Heuristic to detect if it's a Vite project."""
        if repo_path and (os.path.exists(os.path.join(repo_path, 'vite.config.ts')) or 
                         os.path.exists(os.path.join(repo_path, 'vite.config.js'))):
            return True
        return False

    def _validate_nextjs_rules(self, filepath: str, content: str) -> List[Dict]:
        """Specific rules for Next.js App Router."""
        issues = []
        basename = os.path.basename(filepath)

        # A. 'use client' validation for App Router
        if 'app/' in filepath:
            has_client_hooks = any(re.search(rf'\b{re.escape(hook)}\b', content) for hook in self.react_client_hooks)
            has_use_client = re.search(r'["\']use client["\']', content)
            
            if has_client_hooks and not has_use_client:
                issues.append({
                    'type': 'missing_use_client',
                    'file': filepath,
                    'message': "React hooks found in server component. Needs 'use client' directive at the top.",
                    'severity': 'high'
                })

        # B. Default export validation for special files
        if basename in self.nextjs_app_router_files and not basename.startswith('route.'):
            if 'export default' not in content:
                issues.append({
                    'type': 'missing_default_export',
                    'file': filepath,
                    'message': f"Next.js special file '{basename}' must have a default export.",
                    'severity': 'critical'
                })

        # C. next/link vs <a> tags
        if '<a ' in content and 'Link ' not in content:
            # Simple heuristic: if it's a JSX file, recommend next/link
            if filepath.endswith(('.tsx', '.jsx')):
                issues.append({
                    'type': 'nextjs_link_recommendation',
                    'file': filepath,
                    'message': "Found <a> tag. Consider using 'next/link' for better performance and client-side navigation.",
                    'severity': 'low'
                })

        return issues

    def _validate_vite_rules(self, filepath: str, content: str) -> List[Dict]:
        """Specific rules for Vite."""
        issues = []

        # A. process.env vs import.meta.env
        if 'process.env' in content and filepath.endswith(('.ts', '.tsx', '.js', '.jsx')):
            issues.append({
                'type': 'vite_env_usage',
                'file': filepath,
                'message': "Vite uses 'import.meta.env' instead of 'process.env' for environment variables.",
                'severity': 'medium'
            })

        # B. File extensions for JSX
        if filepath.endswith(('.js', '.ts')) and ('<' in content and ('/>' in content or '</' in content)):
            issues.append({
                'type': 'vite_extension_mismatch',
                'file': filepath,
                'message': "Files containing JSX must use .jsx or .tsx extension in Vite.",
                'severity': 'high'
            })

        return issues

# Global instance
framework_validator = FrameworkValidator()
