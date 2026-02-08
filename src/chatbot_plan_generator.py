"""
Chatbot Plan Generator

Generates implementation plans for user approval using Gemini AI.
Creates detailed, actionable plans with effort estimates and previews.
"""

import os
from typing import Dict, List, Optional
from model_router import _query_gemini_api
import json


class PlanGenerator:
    """Generates implementation plans for various user requests."""
    
    def generate_plan(self, intent: str, user_message: str, entities: Dict,
                     conversation_history: List[Dict] = None,
                     tech_stack_context: Dict = None) -> Dict:
        """
        Generate an implementation plan based on user intent.
        
        Args:
            intent: Detected intent category
            user_message: Original user message
            entities: Extracted entities from intent detection
            conversation_history: Previous conversation for context
            tech_stack_context: Tech stack and project structure info
            
        Returns:
            {
                "plan_id": str,
                "intent": str,
                "summary": str,
                "steps": List[Dict],
                "estimated_effort": str,
                "complexity": str,
                "affected_files": List[str],
                "preview": Dict (code/visual preview if applicable),
                "risks": List[str],
                "rollback_strategy": str
            }
        """
        # Load repository context for accurate file paths
        if not tech_stack_context:
            # Fallback: load minimal context
            codebase_context = self._load_codebase_context(intent, user_message)
        else:
            # Use provided tech stack context
            codebase_context = self._load_codebase_context(intent, user_message) if intent in ["ui_change", "bug_fix"] else {}
        
        # CRITICAL: Extract what user specifically asked for
        key_entities = self._extract_key_entities(user_message, intent)
        
        prompt = self._build_plan_prompt(intent, user_message, entities, conversation_history, codebase_context, tech_stack_context, key_entities)

        
        try:
            messages = [{"role": "user", "content": prompt}]
            gemini_response = _query_gemini_api(messages=messages, timeout=60)
            
            if "error" in gemini_response:
                print(f"[PLAN_GENERATOR] Error from Gemini: {gemini_response['error']}")
                return self._create_error_plan(user_message, intent)

            response_text = gemini_response.get("content") or gemini_response.get("response", "")
            plan = self._parse_plan_response(response_text, intent, user_message)
            
            print(f"[PLAN_GENERATOR] Generated plan with {len(plan.get('steps', []))} steps")
            return plan
            
        except Exception as e:
            print(f"[PLAN_GENERATOR] Exception: {e}")
            return self._create_error_plan(user_message, intent)
    
    def _load_codebase_context(self, intent: str, user_message: str = "") -> Dict:
        """Load relevant codebase files for context."""
        try:
            # Only load files for UI changes and bug fixes to save tokens
            if intent not in ["ui_change", "bug_fix"]:
                return {}
            
            from github_handler import clone_or_pull_repo
            import os
            
            # Check if GITHUB_REPO is configured
            github_repo = os.getenv("GITHUB_REPO")
            if not github_repo:
                print("[PLAN_GEN] GITHUB_REPO not configured, skipping file context loading")
                return {}
            
            repo_path = clone_or_pull_repo()
            if not repo_path:
                print("[PLAN_GEN] Could not access repository")
                return {}
            
            context = {
                "files": {},
                "tech_stack": {},
                "project_structure": {"directories": {}}
            }
            
            # Load key UI files for context
            ui_files_to_check = [
                "client/src/index.css",
                "client/src/globals.css",
                "styles/globals.css",
               "src/index.css",
                "app/globals.css"
            ]
            
            for file_path in ui_files_to_check:
                full_path = os.path.join(repo_path, file_path)
                if os.path.exists(full_path):
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Limit size to avoid token overflow
                            if len(content) < 5000:
                                context["files"][file_path] = content
                                print(f"[PLAN_GEN] Loaded {file_path} for context")
                    except Exception as e:
                        print(f"[PLAN_GEN] Could not read {file_path}: {e}")
            
            return context
        except Exception as e:
            print(f"[PLAN_GEN] Error loading codebase context: {e}")
            return {}
    
    def _get_file_extension(self, framework: str, language: str) -> str:
        """Get correct file extension based on tech stack."""
        mapping = {
            ("react", "typescript"): ".tsx",
            ("react", "javascript"): ".jsx",
            ("vue", "typescript"): ".vue",
            ("vue", "javascript"): ".vue",
            ("angular", "typescript"): ".ts",
            ("nextjs", "typescript"): ".tsx",
            ("nextjs", "javascript"): ".jsx",
        }
        return mapping.get((framework.lower(), language.lower()), ".js")
    
    def _detect_ui_dependencies(self, repo_path: str) -> Dict:
        """
        Detect UI library from package.json.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dict with UI library name and dependencies
        """
        import os
        import json
        
        try:
            # Look for package.json in common locations
            package_json_paths = [
                os.path.join(repo_path, "package.json"),
                os.path.join(repo_path, "ai-engine-ui", "package.json"),
                os.path.join(repo_path, "client", "package.json"),
                os.path.join(repo_path, "frontend", "package.json"),
            ]
            
            package_json_path = None
            for path in package_json_paths:
                if os.path.exists(path):
                    package_json_path = path
                    break
            
            if not package_json_path:
                print("[PLAN_GEN] No package.json found")
                return {"name": "unknown", "dependencies": []}
            
            with open(package_json_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            deps = package_data.get("dependencies", {})
            dev_deps = package_data.get("devDependencies", {})
            all_deps = {**deps, **dev_deps}
            
            # Detect UI library based on dependencies
            ui_library = {"name": "unknown", "dependencies": []}
            
            # Check for shadcn/ui indicators
            shadcn_indicators = ["@radix-ui/react-slot", "class-variance-authority", "tailwind-merge"]
            if any(dep in all_deps for dep in shadcn_indicators):
                ui_library["name"] = "shadcn/ui"
                ui_library["dependencies"] = [dep for dep in shadcn_indicators if dep in all_deps]
                print(f"[PLAN_GEN] Detected UI library: shadcn/ui")
            
            # Check for Material-UI
            elif "@mui/material" in all_deps:
                ui_library["name"] = "material-ui"
                ui_library["dependencies"] = ["@mui/material"]
                print(f"[PLAN_GEN] Detected UI library: Material-UI")
            
            # Check for Ant Design
            elif "antd" in all_deps:
                ui_library["name"] = "ant-design"
                ui_library["dependencies"] = ["antd"]
                print(f"[PLAN_GEN] Detected UI library: Ant Design")
            
            # Check for Chakra UI
            elif "@chakra-ui/react" in all_deps:
                ui_library["name"] = "chakra-ui"
                ui_library["dependencies"] = ["@chakra-ui/react"]
                print(f"[PLAN_GEN] Detected UI library: Chakra UI")
            
            return ui_library
            
        except Exception as e:
            print(f"[PLAN_GEN] Error detecting UI dependencies: {e}")
            return {"name": "unknown", "dependencies": []}
    
    def _extract_ui_component_examples(self, repo_path: str) -> Dict[str, str]:
        """
        Extract UI component import patterns from existing codebase.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dict mapping component names to import statements
        """
        import os
        import re
        
        component_examples = {}
        
        try:
            # Look for UI component directories
            ui_component_paths = [
                os.path.join(repo_path, "ai-engine-ui", "src", "components", "ui"),
                os.path.join(repo_path, "client", "src", "components", "ui"),
                os.path.join(repo_path, "src", "components", "ui"),
            ]
            
            ui_dir = None
            for path in ui_component_paths:
                if os.path.exists(path) and os.path.isdir(path):
                    ui_dir = path
                    break
            
            if not ui_dir:
                print("[PLAN_GEN] No UI components directory found")
                return {}
            
            # Read UI component files
            for filename in os.listdir(ui_dir):
                if filename.endswith(('.tsx', '.ts', '.jsx', '.js')):
                    component_name = filename.replace('.tsx', '').replace('.ts', '').replace('.jsx', '').replace('.js', '')
                    component_name_capitalized = component_name.capitalize()
                    
                    # Generate import statement based on file location
                    # Assuming standard shadcn/ui pattern
                    import_stmt = f"import {{ {component_name_capitalized} }} from '@/components/ui/{component_name}'"
                    component_examples[component_name_capitalized] = import_stmt
            
            # Also extract icon imports from existing components
            example_files = [
                os.path.join(repo_path, "ai-engine-ui", "src", "components", "StatusMonitor.tsx"),
                os.path.join(repo_path, "ai-engine-ui", "src", "app", "page.tsx"),
            ]
            
            for file_path in example_files:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # Extract lucide-react icon imports
                            icon_import_match = re.search(r"import\s+{([^}]+)}\s+from\s+['\"]lucide-react['\"]", content)
                            if icon_import_match and "Icons" not in component_examples:
                                icons = [icon.strip() for icon in icon_import_match.group(1).split(',')]
                                component_examples["Icons"] = f"import {{ {', '.join(icons[:5])} }} from 'lucide-react'"
                            
                            # Extract cn utility import
                            cn_import_match = re.search(r"import\s+{[^}]*cn[^}]*}\s+from\s+['\"]@/lib/utils['\"]", content)
                            if cn_import_match and "Utilities" not in component_examples:
                                component_examples["Utilities"] = "import { cn } from '@/lib/utils'"
                            
                            break  # Only need one example
                    except Exception as e:
                        print(f"[PLAN_GEN] Could not read {file_path}: {e}")
            
            print(f"[PLAN_GEN] Extracted {len(component_examples)} component examples")
            return component_examples
            
        except Exception as e:
            print(f"[PLAN_GEN] Error extracting component examples: {e}")
            return {}
    
    def _detect_import_aliases(self, repo_path: str) -> Dict[str, str]:
        """
        Detect import path aliases from tsconfig.json or jsconfig.json.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Dict mapping alias to base path, e.g. {"@": "src/", "~": "./"}
        """
        import os
        import json
        import re
        
        aliases = {}
        
        try:
            # Check for tsconfig.json or jsconfig.json
            config_paths = [
                os.path.join(repo_path, "tsconfig.json"),
                os.path.join(repo_path, "jsconfig.json"),
                os.path.join(repo_path, "client", "tsconfig.json"),
                os.path.join(repo_path, "client", "jsconfig.json"),
            ]
            
            config_path = None
            for path in config_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if not config_path:
                print("[PLAN_GEN] No tsconfig.json/jsconfig.json found")
                return {}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse JSON, handling comments
            try:
                # First try: strip comments manually
                # Remove single-line comments
                content_clean = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
                # Remove multi-line comments
                content_clean = re.sub(r'/\*.*?\*/', '', content_clean, flags=re.DOTALL)
                # Remove trailing commas before closing braces/brackets
                content_clean = re.sub(r',(\s*[}\]])', r'\1', content_clean)
                
                config = json.loads(content_clean)
            except json.JSONDecodeError:
                # Second try: use a more liberal approach - extract just the paths section
                print("[PLAN_GEN] Failed to parse full tsconfig, trying to extract paths section")
                
                # Look for "paths" section in the content
                paths_match = re.search(r'"paths"\s*:\s*{([^}]+)}', content, re.DOTALL)
                if paths_match:
                    # Build a minimal valid JSON with just paths
                    paths_json = '{' + paths_match.group(0) + '}'
                    # Clean it
                    paths_json = re.sub(r'//.*?$', '', paths_json, flags=re.MULTILINE)
                    paths_json = re.sub(r'/\*.*?\*/', '', paths_json, flags=re.DOTALL)
                    paths_json = re.sub(r',(\s*})', r'\1', paths_json)
                    
                    try:
                        minimal_config = json.loads(paths_json)
                        config = {"compilerOptions": minimal_config}
                    except:
                        print("[PLAN_GEN] Could not parse tsconfig paths, skipping alias detection")
                        return {}
                else:
                    print("[PLAN_GEN] No paths section found in tsconfig")
                    return {}
            
            # Extract paths from compilerOptions
            paths = config.get("compilerOptions", {}).get("paths", {})
            base_url = config.get("compilerOptions", {}).get("baseUrl", "./")
            
            for alias_pattern, path_list in paths.items():
                if path_list:
                    # Convert "@/*" to "@", "~/*" to "~"
                    clean_alias = alias_pattern.replace("/*", "")
                    # Get the base path, removing /* if present
                    base_path = path_list[0].replace("/*", "")
                    aliases[clean_alias] = base_path
            
            if aliases:
                print(f"[PLAN_GEN] Detected import aliases: {aliases}")
            else:
                print("[PLAN_GEN] No import aliases found, will use relative imports")
            
            return aliases
            
        except Exception as e:
            print(f"[PLAN_GEN] Error detecting import aliases: {e}")
            return {}
    
    def _extract_key_entities(self, user_message: str, intent: str) -> Dict:
        """
        Extract specific nouns and actions from user request.
        This ensures AI generates files matching what user actually asked for.
        
        Args:
            user_message: User's request
            intent: Detected intent
            
        Returns:
            Dict with extracted pages, components, actions
        """
        import re
        
        message_lower = user_message.lower()
        
        extracted = {
            "pages": [],
            "components": [],
            "actions": [],
            "routes": []
        }
        
        # Extract page names
        page_patterns = [
            r'(profile|login|signup|dashboard|settings|contact|about|home)\s+page',
            r'page\s+for\s+(\w+)',
            r'create\s+(?:a\s+)?(\w+)\s+page',
        ]
        
        for pattern in page_patterns:
            matches = re.findall(pattern, message_lower)
            extracted["pages"].extend(matches)
        
        # Extract component names
        component_patterns = [
            r'(header|footer|navbar|sidebar|menu)',
            r'(\w+)\s+(button|icon|modal|form|card)',
            r'add\s+(?:a\s+)?(\w+)\s+(?:icon|button)',
        ]
        
        for pattern in component_patterns:
            matches = re.findall(pattern, message_lower)
            if isinstance(matches[0] if matches else None, tuple):
                extracted["components"].extend([m[0] for m in matches])
            else:
                extracted["components"].extend(matches)
        
        # Extract actions
        action_patterns = [
            r'(create|add|update|modify|delete|remove)',
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, message_lower)
            extracted["actions"].extend(matches)
        
        # Deduplicate
        extracted["pages"] = list(set(extracted["pages"]))
        extracted["components"] = list(set(extracted["components"]))
        extracted["actions"] = list(set(extracted["actions"]))
        
        return extracted
    
    def _build_plan_prompt(self, intent: str, user_message: str, entities: Dict,
                          conversation_history: List[Dict] = None, codebase_context: Dict = None,
                          tech_stack_context: Dict = None, key_entities: Dict = None) -> str:
        """Build prompt for plan generation with tech stack awareness."""
        
        if codebase_context is None:
            codebase_context = {}
        if tech_stack_context is None:
            tech_stack_context = {}
        if key_entities is None:
            key_entities = {}
        
        context = ""
        if conversation_history and len(conversation_history) > 0:
            context = "\n\nConversation context:\n"
            for msg in conversation_history[-3:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role.upper()}: {content}\n"
        
        # Build entity-specific guidance
        entity_info = ""
        if key_entities and (key_entities.get("pages") or key_entities.get("components")):
            pages = key_entities.get("pages", [])
            components = key_entities.get("components", [])
            
            entity_info = f"""
===== USER SPECIFICALLY REQUESTED =====
Pages to create: {', '.join(pages) if pages else 'Not specified'}
Components to modify/create: {', '.join(components) if components else 'Not specified'}

CRITICAL NAMING RULES:
1. Use these EXACT names for files
2. For "{pages[0] if pages else 'example'}" page → Create {pages[0].capitalize() if pages else 'Example'}Page.tsx
3. DO NOT invent different names (e.g., don't create ContactPage when user said ProfilePage)

Examples:
  - User says "profile page" → ProfilePage.tsx with route /profile
  - User says "settings page" → SettingsPage.tsx with route /settings
  - User says "contact page" → ContactPage.tsx with route /contact

DO NOT CREATE FILES THE USER DIDN'T ASK FOR!
========================================
"""
        
        # Build tech stack section
        tech_info = ""
        if tech_stack_context:
            tech_stack = tech_stack_context.get("tech_stack", {})
            structure = tech_stack_context.get("project_structure", {})
            
            framework = tech_stack.get("framework", "unknown")
            language = tech_stack.get("language", "javascript")
            
            # Determine correct file extension
            file_ext = self._get_file_extension(framework, language)
            
            # Get discovered directories
            top_dirs = structure.get("top_code_directories", [])
            
            # Build examples of correct paths
            component_dir = next((d for d in top_dirs if 'component' in d.lower()), 'client/src/components')
            page_dir = next((d for d in top_dirs if 'page' in d.lower()), 'client/src/pages')
            
            tech_info = f"""
===== CRITICAL: PROJECT STRUCTURE =====
Framework: {framework}
Language: {language}
File Extension: {file_ext}

DISCOVERED DIRECTORIES (USE THESE EXACT PATHS):
{chr(10).join(f"  - {d}" for d in top_dirs[:5]) if top_dirs else "  - src/"}

MANDATORY FILE PATH RULES:
1. File extension MUST be {file_ext} (NOT .js, NOT .jsx if TypeScript)
2. Use ONLY the directories listed above
3. DO NOT use generic paths like "src/components/" or "src/pages/"
4. For components: Use {component_dir}/
5. For pages: Use {page_dir}/

CORRECT PATH EXAMPLES:
  ✓ {component_dir}/Header.tsx
  ✓ {page_dir}/ProfilePage.tsx
  ✓ client/src/App.tsx

WRONG PATHS (DO NOT USE):
  ✗ src/components/Header.js
  ✗ src/Header.tsx
  ✗ components/Header.tsx

IF YOU USE WRONG PATHS, THE FILES WILL BE REJECTED.
USE ONLY THE DISCOVERED DIRECTORIES LISTED ABOVE.
=======================================
"""
        
        # Build UI library constraints section
        ui_library_info = ""
        if tech_stack_context:
            repo_path = tech_stack_context.get("repo_path", "")
            
            if repo_path:
                # Detect UI library
                ui_library = self._detect_ui_dependencies(repo_path)
                
                # Extract component examples
                component_examples = self._extract_ui_component_examples(repo_path)
                
                if ui_library and ui_library.get("name") != "unknown":
                    ui_lib_name = ui_library.get("name", "Unknown")
                    
                    # Build component examples list
                    component_list = ""
                    if component_examples:
                        component_list = "\n".join(f"  {name}: {import_stmt}" 
                                                   for name, import_stmt in component_examples.items())
                    
                    ui_library_info = f"""
===== CRITICAL: UI LIBRARY REQUIREMENTS =====
UI Framework: {ui_lib_name}

AVAILABLE UI COMPONENTS - USE THESE EXACT IMPORTS:
{component_list if component_list else "  (No components extracted - check existing code)"}

MANDATORY IMPORT RULES:
1. DO NOT use Material-UI (@mui/material) - IT IS NOT INSTALLED
2. DO NOT use Ant Design (antd) - IT IS NOT INSTALLED  
3. DO NOT use Bootstrap or other UI libraries - THEY ARE NOT INSTALLED
4. USE ONLY the component imports listed above - NO OTHER COMPONENTS EXIST
5. For icons, use lucide-react: import {{ IconName }} from 'lucide-react'
6. For utilities, use: import {{ cn }} from '@/lib/utils'

CRITICAL RESTRICTIONS:
- DO NOT assume any shadcn/ui components exist beyond what's listed above
- DO NOT use hooks like 'use-toast', 'use-form' unless they're in the list
- DO NOT create imports for components that don't exist
- If you need a component not in the list, use native HTML elements instead
- ALWAYS include .tsx extension in ALL component imports

CORRECT EXAMPLES (based on this project):
  ✓ import {{ Button }} from '@/components/ui/button.tsx'
  ✓ import {{ Card }} from '@/components/ui/card.tsx'
  ✓ import {{ Activity, CheckCircle }} from 'lucide-react'
  ✓ import {{ cn }} from '@/lib/utils'

WRONG EXAMPLES (WILL CAUSE BUILD FAILURE):
  ✗ import {{ Container, Button }} from '@mui/material'
  ✗ import {{ Button }} from 'antd'
  ✗ import Button from '@material-ui/core/Button'
  ✗ import {{ Button }} from '@/components/ui/button'  (missing .tsx)
  ✗ import {{ Button }} from 'react-bootstrap'
  ✗ import {{ toast }} from '@/components/ui/use-toast'  (NOT in available list)
  ✗ import {{ Form }} from '@/components/ui/form'  (NOT in available list)

IF YOU USE WRONG IMPORTS, THE BUILD WILL FAIL.
USE ONLY THE COMPONENTS AVAILABLE IN THIS PROJECT.
=============================================
"""
        
        # Build import alias constraints section
        import_alias_info = ""
        if tech_stack_context:
            repo_path = tech_stack_context.get("repo_path", "")
            
            if repo_path:
                # Detect import aliases
                import_aliases = self._detect_import_aliases(repo_path)
                
                if import_aliases:
                    # Build examples of correct imports
                    alias_examples = []
                    for alias, base_path in import_aliases.items():
                        alias_examples.append(f"  {alias}/ → for imports from {base_path}")
                    
                    import_alias_info = f"""
===== CRITICAL: IMPORT PATH REQUIREMENTS =====
This project uses import path aliases configured in tsconfig.json:

CONFIGURED ALIASES:
{chr(10).join(alias_examples)}

⚠️ FIRST EXAMPLE - HOW TO IMPORT A PAGE:
If you create ContactUsPage.tsx in pages directory:
  ✓ CORRECT: import ContactUsPage from '@/pages/ContactUsPage.tsx'
  ✗ WRONG: import ContactUsPage from './pages/ContactUsPage.tsx'
  ✗ WRONG: import ContactUsPage from './pages/ContactUsPage'
  ✗ WRONG: import ContactUsPage from '../pages/ContactUsPage.tsx'

MANDATORY IMPORT RULES:
1. ALWAYS use the configured aliases for cross-directory imports
2. NEVER use relative paths like './pages/' or '../components/' 
3. Relative imports (./) are ONLY for files in the SAME directory
4. ALWAYS include file extension (.tsx, .jsx, .ts, .js) in ALL imports

WHEN TO USE ALIASES:
- Importing from pages/: use @/pages/FileName.tsx
- Importing from components/: use @/components/FileName.tsx  
- Importing from ANY different directory: use @ alias
- Importing components from ui/: use @/components/ui/componentname.tsx

WHEN TO USE RELATIVE IMPORTS:
- ONLY when importing a file in the SAME directory
- Example: App.tsx importing Header.tsx (both in src/)
- Use: import Header from './Header.tsx'

CORRECT IMPORT EXAMPLES:
  ✓ import ContactUsPage from '@/pages/ContactUsPage.tsx'  (different directory - use alias)
  ✓ import {{ Button }} from '@/components/ui/button.tsx'  (different directory - use alias)
  ✓ import {{ Header }} from '@/components/Header.tsx'  (different directory - use alias)
  ✓ import ContactForm from './ContactForm.tsx'  (SAME directory - use relative)

WRONG IMPORT EXAMPLES (WILL CAUSE BUILD FAILURE):
  ✗ import ContactUsPage from './pages/ContactUsPage.tsx'  (WRONG - use @/pages/)
  ✗ import ContactUsPage from './pages/ContactUsPage'  (WRONG - missing extension AND wrong path)
  ✗ import {{ Button }} from '../components/ui/button.tsx'  (WRONG - use @/components/)
  ✗ import {{ Header }} from 'components/Header'  (WRONG - use @/components/)

CRITICAL: For cross-directory imports, ALWAYS use @ alias, NEVER use ./
IF YOU USE WRONG IMPORT PATHS, ROLLUP WILL FAIL TO RESOLVE THEM.
=============================================
"""
                else:
                    # No aliases configured, use relative imports
                    import_alias_info = f"""
===== CRITICAL: IMPORT PATH REQUIREMENTS =====
This project does NOT use import path aliases.

USE RELATIVE IMPORTS ONLY:
  ✓ import {{ Button }} from './components/Button'
  ✓ import {{ Header }} from '../Header'

DO NOT USE ALIASES:
  ✗ import {{ Button }} from '@/components/Button'  (@ not configured)
  ✗ import {{ Button }} from '~/components/Button'  (~ not configured)
=============================================
"""
        
        # Add codebase file context if available
        codebase_info = ""
        has_broken_files = False
        broken_file_details = []
        
        if codebase_context.get("files"):
            codebase_info = "\n\nCurrent Codebase Files:\n"
            
            for filename, content in codebase_context["files"].items():
                # Check file integrity before assuming it's valid
                is_valid, reason = file_integrity_checker.check_file(filename, content)
                
                if not is_valid:
                    has_broken_files = True
                    broken_file_details.append(f"{filename}: {reason}")
                    print(f"[PLAN_GEN] ⚠️  File validation failed: {filename} - {reason}")
                    print(f"[PLAN_GEN] Will regenerate this file even if changes seem already implemented")
                
                codebase_info += f"\n--- {filename} ---\n{content}\n"
            
            # If broken files detected, add warning to prompt
            if has_broken_files:
                codebase_info += "\n\n⚠️  ATTENTION: The following files have integrity issues:\n"
                for detail in broken_file_details:
                    codebase_info += f"- {detail}\n"
                codebase_info += "\nThese files MUST be regenerated completely even if changes appear to exist.\n"
        
        intent_guidance = {
            "feature_request": "Create a detailed plan to implement the requested feature. Include file changes, code examples, and integration points.",
            "bug_fix": "Create a plan to detect and fix bugs. Include diagnostic steps, fix approach, and testing strategy.",
            "ui_change": "Create a plan to modify UI elements. Include specific CSS/styling changes, affected components, and visual description.",
            "competitive_analysis": "Create a plan to analyze competitors and provide insights. Include which aspects to analyze and expected outputs.",
            "refinement": "Create a plan to refine/iterate on the previous request based on the new feedback."
        }
        
        guidance = intent_guidance.get(intent, "Create a detailed implementation plan for this request.")
        
        prompt = f"""You are an AI assistant creating implementation plans for website maintenance and development.

User Intent: {intent}
User Request: "{user_message}"
Extracted Details: {json.dumps(entities, indent=2)}
{context}
{entity_info}
{tech_info}
{ui_library_info}
{import_alias_info}
{codebase_info}

Instructions: {guidance}

Respond with ONLY a JSON object in this exact format (no markdown, no additional text):
{{
    "summary": "Brief summary of what will be done",
    "steps": [
        {{
            "step_number": 1,
            "description": "Detailed description of this step",
            "action_type": "code_change|analysis|testing|deployment",
            "details": "Specific implementation details"
        }}
    ],
    "estimated_effort": "Low|Medium|High",
    "complexity": "low|medium|high",
    "affected_files": ["list", "of", "file", "paths"],
    "code_preview": {{
        "language": "python|javascript|css|html",
        "filename": "example.py",
        "code": "Sample code that will be implemented"
    }},
    "risks": ["potential risk 1", "potential risk 2"],
    "rollback_strategy": "How to rollback if something goes wrong",
    "success_criteria": "How to verify the change worked"
}}

Make the plan specific, actionable, and detailed. Include actual code examples in code_preview when applicable.
For UI changes, describe visual changes clearly.
For bug fixes, include diagnostic and testing steps.
"""
        return prompt
    
    def _parse_plan_response(self, response: str, intent: str, user_message: str) -> Dict:
        """Parse Gemini's plan generation response."""
        import re
        import uuid
        
        try:
            # Remove markdown code blocks if present
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*', '', response)
            response = response.strip()
            
            # Parse JSON
            plan_data = json.loads(response)
            
            # Add plan metadata
            plan_data["plan_id"] = str(uuid.uuid4())
            plan_data["intent"] = intent
            plan_data["original_request"] = user_message
            
            # Validate and set defaults
            plan_data.setdefault("summary", "Implementation plan")
            plan_data.setdefault("steps", [])
            plan_data.setdefault("estimated_effort", "Medium")
            plan_data.setdefault("complexity", "medium")
            plan_data.setdefault("affected_files", [])
            plan_data.setdefault("code_preview", None)
            plan_data.setdefault("risks", [])
            plan_data.setdefault("rollback_strategy", "Use git revert to undo changes")
            plan_data.setdefault("success_criteria", "Changes applied successfully")
            
            return plan_data
            
        except Exception as e:
            print(f"[PLAN_GENERATOR] Failed to parse plan response: {e}")
            print(f"[PLAN_GENERATOR] Raw response: {response}")
            return self._create_fallback_plan(user_message, intent)
    
    def _create_fallback_plan(self, user_message: str, intent: str) -> Dict:
        """Create a basic fallback plan when AI generation fails."""
        import uuid
        
        return {
            "plan_id": str(uuid.uuid4()),
            "intent": intent,
            "original_request": user_message,
            "summary": f"Plan to address: {user_message}",
            "steps": [
                {
                    "step_number": 1,
                    "description": "Analyze the request in detail",
                    "action_type": "analysis",
                    "details": "Review the request and determine specific actions needed"
                },
                {
                    "step_number": 2,
                    "description": "Implement the changes",
                    "action_type": "code_change",
                    "details": "Make necessary code modifications"
                },
                {
                    "step_number": 3,
                    "description": "Test the changes",
                    "action_type": "testing",
                    "details": "Verify changes work as expected"
                }
            ],
            "estimated_effort": "Medium",
            "complexity": "medium",
            "affected_files": [],
            "code_preview": None,
            "risks": ["AI plan generation failed - manual review recommended"],
            "rollback_strategy": "Use git revert to undo changes",
            "success_criteria": "User confirms changes meet requirements",
            "fallback_used": True
        }
    
    def _create_error_plan(self, user_message: str, intent: str) -> Dict:
        """Create an error plan when generation completely fails."""
        import uuid
        
        return {
            "plan_id": str(uuid.uuid4()),
            "intent": intent,
            "original_request": user_message,
            "summary": "Unable to generate plan",
            "error": "Plan generation failed. Please try rephrasing your request.",
            "steps": [],
            "estimated_effort": "Unknown",
            "complexity": "unknown",
            "affected_files": [],
            "code_preview": None,
            "risks": ["Plan generation failed"],
            "rollback_strategy": "N/A",
            "success_criteria": "N/A"
        }
    
    def refine_plan(self, original_plan: Dict, refinement_request: str) -> Dict:
        """
        Refine an existing plan based on user feedback.
        
        Args:
            original_plan: The original plan to refine
            refinement_request: User's refinement request
            
        Returns:
            Updated plan
        """
        prompt = f"""You are refining an implementation plan based on user feedback.

Original Plan:
{json.dumps(original_plan, indent=2)}

User Refinement Request: "{refinement_request}"

Update the plan to incorporate the user's feedback. Respond with ONLY a JSON object in the same format as the original plan, with the requested refinements applied.

Keep the same plan_id but update the relevant sections based on the feedback.
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            gemini_response = _query_gemini_api(messages=messages, timeout=60)
            
            if "error" in gemini_response:
                print(f"[PLAN_GENERATOR] Error refining plan: {gemini_response['error']}")
                return original_plan
            
            response_text = gemini_response.get("content") or gemini_response.get("response", "")
            refined_plan = self._parse_plan_response(
                response_text,
                original_plan["intent"],
                original_plan["original_request"]
            )
            
            # Preserve original plan_id
            refined_plan["plan_id"] = original_plan["plan_id"]
            refined_plan["refinement_count"] = original_plan.get("refinement_count", 0) + 1
            refined_plan["refinement_history"] = original_plan.get("refinement_history", [])
            refined_plan["refinement_history"].append(refinement_request)
            
            print(f"[PLAN_GENERATOR] Plan refined (iteration {refined_plan['refinement_count']})")
            return refined_plan
            
        except Exception as e:
            print(f"[PLAN_GENERATOR] Exception refining plan: {e}")
            return original_plan


# Global instance
plan_generator = PlanGenerator()
