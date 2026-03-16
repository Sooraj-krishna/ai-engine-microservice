"""
Routing Validator

Automatically detects when new pages are created without proper routing
and generates App.tsx fixes to ensure all pages are accessible.

This prevents "orphaned" pages that are created but not wired into the app.
"""

import os
import re
from typing import Dict, List, Optional


class RoutingValidator:
    """Validates routing and auto-generates fixes for missing routes."""
    
    # Patterns to detect page files
    PAGE_PATTERNS = [
        r'/pages/.*\.(tsx|jsx|ts|js)$',
        r'/components/.*Page\.(tsx|jsx|ts|js)$',
        r'-page\.(tsx|jsx|ts|js)$',
        r'Page\.(tsx|jsx|ts|js)$'
    ]
    
    # Possible app file locations (in priority order)
    APP_FILE_PATHS = [
        'client/src/App.tsx',
        'src/App.tsx',
        'client/src/app.tsx',
        'src/app.tsx',
        'app/layout.tsx',  # Next.js App Router
        'pages/_app.tsx',   # Next.js Pages Router
        'App.tsx',
        'app.tsx'
    ]
    
    def validate_routing(self, generated_files: Dict[str, str], 
                        repo_path: str, tech_stack: Dict) -> Dict:
        """
        Validate that all new pages have proper routing.
        
        Args:
            generated_files: Dict of {filepath: content} that were generated
            repo_path: Path to repository
            tech_stack: Tech stack info from code analyzer
            
        Returns:
            {
                'needs_fix': bool,
                'issues': List[str],
                'fixes': List[{'path': str, 'content': str}],
                'new_pages': List[str]
            }
        """
        result = {
            'needs_fix': False,
            'issues': [],
            'fixes': [],
            'new_pages': []
        }
        
        # Detect new pages
        new_pages = self._detect_new_pages(generated_files)
        result['new_pages'] = new_pages
        
        if not new_pages:
            print("[ROUTING_VALIDATOR] No new pages detected")
            return result
        
        print(f"[ROUTING_VALIDATOR] Detected {len(new_pages)} new pages: {new_pages}")
        
        # Check if Next.js App Router (auto-routing)
        framework = tech_stack.get('framework', '').lower()
        if 'next' in framework and any('app/' in p for p in new_pages):
            print("[ROUTING_VALIDATOR] Next.js App Router detected - routes auto-generated")
            return result
        
        # Find App file
        app_file_path = self._find_app_file(repo_path, generated_files)
        
        if not app_file_path:
            result['issues'].append("Could not find App.tsx or main routing file")
            print("[ROUTING_VALIDATOR] WARNING: No App file found, cannot auto-fix")
            return result
        
        print(f"[ROUTING_VALIDATOR] Found app file: {app_file_path}")
        
        # Check if App.tsx was modified
        app_modified = app_file_path in generated_files
        
        if app_modified:
            # Check if all new pages are imported and routed
            app_content = generated_files[app_file_path]
            missing_routes = self._check_routes(new_pages, app_content)
            
            if missing_routes:
                result['needs_fix'] = True
                result['issues'].append(f"App.tsx modified but missing routes: {missing_routes}")
        else:
            # App.tsx not modified - need to add routing
            result['needs_fix'] = True
            result['issues'].append("New pages created but App.tsx not updated")
            
            # Generate routing fix
            routing_fix = self._generate_routing_fix(
                new_pages, 
                app_file_path, 
                repo_path,
                tech_stack
            )
            
            if routing_fix:
                result['fixes'].append({
                    'path': app_file_path,
                    'content': routing_fix
                })
                print(f"[ROUTING_VALIDATOR] Generated routing fix for {app_file_path}")
        
        return result
    
    def _detect_new_pages(self, generated_files: Dict[str, str]) -> List[str]:
        """Detect which generated files are pages."""
        new_pages = []
        
        for filepath in generated_files.keys():
            # Check if file matches page patterns
            for pattern in self.PAGE_PATTERNS:
                if re.search(pattern, filepath):
                    new_pages.append(filepath)
                    break
        
        return new_pages
    
    def _find_app_file(self, repo_path: str, generated_files: Dict[str, str]) -> Optional[str]:
        """Find the main App file."""
        # First check generated files
        for path in self.APP_FILE_PATHS:
            if path in generated_files:
                return path
        
        # Then check repo
        for path in self.APP_FILE_PATHS:
            full_path = os.path.join(repo_path, path)
            if os.path.exists(full_path):
                return path
        
        return None
    
    def _check_routes(self, new_pages: List[str], app_content: str) -> List[str]:
        """Check if new pages are imported and routed in app content."""
        missing = []
        
        for page_path in new_pages:
            # Extract component name from path
            component_name = self._extract_component_name(page_path)
            
            # Check if imported
            import_pattern = f"import.*{component_name}.*from"
            if not re.search(import_pattern, app_content):
                missing.append(page_path)
                continue
            
            # Check if used in JSX (either <Component /> or element=)
            usage_pattern = f"(<{component_name}|element={{<{component_name})"
            if not re.search(usage_pattern, app_content):
                missing.append(page_path)
        
        return missing
    
    def _extract_component_name(self, filepath: str) -> str:
        """Extract component name from file path."""
        # Get filename without extension
        filename = os.path.basename(filepath)
        name = os.path.splitext(filename)[0]
        return name
    
    def _generate_routing_fix(self, new_pages: List[str], app_file_path: str,
                              repo_path: str, tech_stack: Dict) -> Optional[str]:
        """Generate App.tsx content with routes added."""
        
        # Read existing App.tsx
        existing_content = ""
        full_app_path = os.path.join(repo_path, app_file_path)
        
        try:
            with open(full_app_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except Exception as e:
            print(f"[ROUTING_VALIDATOR] Could not read {app_file_path}: {e}")
            return None
        
        # Generate imports
        imports = []
        routes = []
        
        for page_path in new_pages:
            component_name = self._extract_component_name(page_path)
            
            # Calculate relative import path from app file
            import_path = self._calculate_import_path(app_file_path, page_path)
            
            # Generate import statement
            imports.append(f"import {component_name} from '{import_path}';")
            
            # Generate route
            route_path = self._generate_route_path(page_path)
            routes.append(f'  <Route path="{route_path}" element={{<{component_name} />}} />')
        
        # Insert imports after existing imports
        import_section = "\n".join(imports)
        
        # Find where to insert imports (after last import)
        last_import_match = list(re.finditer(r'^import .+;', existing_content, re.MULTILINE))
        
        if last_import_match:
            insert_pos = last_import_match[-1].end()
            new_content = (
                existing_content[:insert_pos] +
                "\n" + import_section +
                existing_content[insert_pos:]
            )
        else:
            # No imports found, add at top after any comments
            new_content = import_section + "\n\n" + existing_content
        
        # Insert routes (look for <Routes> or return statement)
        routes_section = "\n".join(routes)
        
        # Try to find <Routes> block
        routes_match = re.search(r'(<Routes>)(.*?)(</Routes>)', new_content, re.DOTALL)
        
        if routes_match:
            # Insert before </Routes>
            insert_pos = routes_match.end(2)
            new_content = (
                new_content[:insert_pos] +
                "\n" + routes_section + "\n      " +
                new_content[insert_pos:]
            )
        else:
            # Add comment indicating manual routing needed
            new_content += f"\n\n// TODO: Add these routes to your routing configuration:\n// {routes_section}\n"
        
        return new_content
    
    def _calculate_import_path(self, from_path: str, to_path: str) -> str:
        """Calculate relative import path."""
        # Simple implementation - can be enhanced
        from_dir = os.path.dirname(from_path)
        
        # Remove file extension from to_path
        to_path_no_ext = os.path.splitext(to_path)[0]
        
        # If both in same directory, just use filename
        if os.path.dirname(to_path) == from_dir:
            return './' + os.path.basename(to_path_no_ext)
        
        # Calculate relative path
        # For simplicity, assume common patterns
        if 'pages' in to_path:
            return to_path_no_ext.replace('client/src/', './').replace('src/', './')
        
        return to_path_no_ext
    
    def _generate_route_path(self, page_path: str) -> str:
        """Generate URL path from file path."""
        # Extract meaningful path from file path
        # e.g., pages/ProductsPage.tsx -> /products
        
        filename = self._extract_component_name(page_path)
        
        # Remove "Page" suffix
        route_name = filename.replace('Page', '').replace('page', '')
        
        # Convert to lowercase and add slash
        return f"/{route_name.lower()}"


# Global instance
routing_validator = RoutingValidator()
