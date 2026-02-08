"""
Real-world Code Generator for AI Engine.
Generates complete, working code files based on project structure,
tech stack, and existing conventions.
"""

import os
import json
import re
import traceback
from typing import Dict, List, Optional, Any, Tuple
from ai_api import query_codegen_api
from validator import CodeValidator

class ProjectAnalyzer:
    """Analyzes the project structure, tech stack, and conventions."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.package_json = self._load_package_json()
        self.tsconfig = self._load_tsconfig()
        self.tech_stack = self._detect_tech_stack()
        self.ui_library = self._detect_ui_library()
        self.import_aliases = self._detect_import_aliases()
        
    def _load_package_json(self) -> Dict:
        """Load package.json to understand dependencies."""
        try:
            paths = [
                os.path.join(self.repo_path, "package.json"),
                os.path.join(self.repo_path, "ai-engine-ui", "package.json"),
                os.path.join(self.repo_path, "client", "package.json"),
                os.path.join(self.repo_path, "frontend", "package.json"),
            ]
            for path in paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            print(f"[ANALYZER] Failed to load package.json: {e}")
        return {}

    def _load_tsconfig(self) -> Dict:
        """Load tsconfig.json to understand aliases."""
        try:
            paths = [
                os.path.join(self.repo_path, "tsconfig.json"),
                os.path.join(self.repo_path, "jsconfig.json"),
                os.path.join(self.repo_path, "ai-engine-ui", "tsconfig.json"),
                os.path.join(self.repo_path, "client", "tsconfig.json"),
            ]
            for path in paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                         # Remove comments (standard JSON doesn't support them but tsconfig does)
                        content = re.sub(r'//.*?$', '', f.read(), flags=re.MULTILINE)
                        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                        return json.loads(content)
        except Exception as e:
            print(f"[ANALYZER] Failed to load tsconfig.json: {e}")
        return {}

    def _detect_tech_stack(self) -> Dict:
        """Detect framework, language, and key libraries."""
        deps = self.package_json.get("dependencies", {})
        dev_deps = self.package_json.get("devDependencies", {})
        all_deps = {**deps, **dev_deps}
        
        stack = {
            "framework": "unknown",
            "language": "javascript",
            "style": "css"
        }
        
        if "next" in all_deps:
            stack["framework"] = "nextjs"
        elif "react" in all_deps:
            stack["framework"] = "react"
        elif "vue" in all_deps:
            stack["framework"] = "vue"
            
        if "typescript" in all_deps or os.path.exists(os.path.join(self.repo_path, "tsconfig.json")):
            stack["language"] = "typescript"
            
        if "tailwindcss" in all_deps:
            stack["style"] = "tailwind"
            
        return stack

    def _detect_ui_library(self) -> Dict:
        """Detect configured UI library (shadcn, mui, etc)."""
        deps = self.package_json.get("dependencies", {})
        all_deps = {**deps, **self.package_json.get("devDependencies", {})}
        
        if "class-variance-authority" in all_deps and "tailwind-merge" in all_deps:
             return {"name": "shadcn/ui", "type": "copy-paste"}
        if "@mui/material" in all_deps:
            return {"name": "material-ui", "type": "library"}
        if "antd" in all_deps:
            return {"name": "ant-design", "type": "library"}
            
        return {"name": "none", "type": "custom"}

    def _detect_import_aliases(self) -> Dict[str, str]:
        """Extract path aliases from tsconfig."""
        aliases = {}
        compiler_opts = self.tsconfig.get("compilerOptions", {})
        paths = compiler_opts.get("paths", {})
        
        for alias, targets in paths.items():
            clean_alias = alias.replace("/*", "")
            if targets:
                clean_target = targets[0].replace("/*", "")
                aliases[clean_alias] = clean_target
                
        # Default alias if not found but usually present
        if not aliases and self.tech_stack["framework"] == "nextjs":
             if os.path.exists(os.path.join(self.repo_path, "@")):
                 aliases["@"] = "./"
                 
        return aliases

class CodeGenerator:
    """Generates robust code fixes using project context."""
    
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.analyzer = ProjectAnalyzer(repo_path)
        self.validator = CodeValidator()
        
    async def generate_fix(self, bug: Dict) -> Optional[Dict]:
        """Generate a complete file fix for a specific bug."""
        target_file = bug.get('file') or bug.get('target_file')
        if not target_file:
            print(f"[GENERATOR] No target file for bug: {bug.get('description')}")
            return None
            
        # 1. Load File Context
        file_content = ""
        full_path = os.path.join(self.repo_path, target_file)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
        else:
            print(f"[GENERATOR] Target file not found: {target_file}")
            # If it's a "create new file" task, we might proceed, but for bugs we usually need existing content
            # Proceeding with empty content if it seems to be a missing file issue
            
        # 2. Build Prompt
        prompt = self._build_prompt(bug, target_file, file_content)
        
        # 3. Query AI
        try:
            print(f"[GENERATOR] Generating fix for {target_file}...")
            response = query_codegen_api(prompt, language=self.analyzer.tech_stack['language'])
            
            # 4. Extract Code
            fixed_code = self._extract_code(response)
            if not fixed_code:
                print("[GENERATOR] Failed to extract code from AI response")
                return None
            
            fix = {
                "path": target_file,
                "content": fixed_code,
                "description": f"Fix for: {bug.get('description')}",
                "bug": bug
            }
            
            # 5. Validate
            print(f"[GENERATOR] Validating fix for {target_file}...")
            is_safe, warnings, errors = self.validator.validate_fix(fix)
            
            if is_safe:
                if warnings:
                    print(f"[GENERATOR] Fix validated with warnings: {warnings}")
                return fix
            else:
                print(f"[GENERATOR] Generated fix failed validation: {errors}")
                return None
        except Exception as e:
            print(f"[GENERATOR] Error generating fix: {e}")
            return None

    def _build_prompt(self, bug: Dict, filename: str, content: str) -> str:
        """Construct a 'Senior Engineer' prompt with strict constraints."""
        stack = self.analyzer.tech_stack
        ui = self.analyzer.ui_library
        aliases = self.analyzer.import_aliases
        
        alias_str = "\n".join([f"- {k} maps to {v}" for k,v in aliases.items()])
        
        prompt = f"""
You are a Senior Software Engineer working on a {stack['framework']} ({stack['language']}) project.
Your task is to FIX a specific bug in `{filename}`.

BUG REPORT:
Type: {bug.get('type')}
Description: {bug.get('description')}
Details: {bug.get('details')}

PROJECT CONSTRAINTS (STRICTLY ENFORCED):
1. **Tech Stack**: {stack['framework'].upper()}, {stack['language'].upper()}
2. **UI Library**: {ui['name']} (Type: {ui['type']})
   - DO NOT import components from libraries NOT installed.
   - If using shadcn/ui, import from '@/components/ui/...' (or correct alias).
3. **Import Aliases**:
{alias_str if alias_str else "   - No aliases detected. Use relative imports (./, ../)."}
4. **Style**: {stack['style']}

EXISTING FILE CONTENT:
```
{content}
```

INSTRUCTIONS:
1. Analyze the bug and the existing code.
2. Rewrite the COMPLETE file with the fix applied.
3. DO NOT return a diff or partial snippet. Return the FULL file.
4. Maintain existing imports and structure unless they are causing the bug.
5. Fix logical errors, UI issues, or missing error handling as requested.
6. Return ONLY the code. No markdown formatting if possible, or inside a single code block.

GENERATE THE FIXED FILE CONTENT NOW:
"""
        return prompt

    def _extract_code(self, response: str) -> str:
        """Clean markdown from response."""
        if "```" in response:
            # simple extraction
            lines = response.splitlines()
            code_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            if code_lines:
                return "\n".join(code_lines)
        return response.strip()

# Main Entry Point
async def prepare_fixes(issues: List[Dict], repo_path: str = None) -> List[Dict]:
    """
    Main function called by chatbot_executor.
    Analyzes issues and generates real-world code fixes.
    """
    if not repo_path:
        repo_path = os.getcwd()
        
    generator = CodeGenerator(repo_path)
    fixes = []
    
    print(f"[GENERATOR] Processing {len(issues)} issues with Real-Code Generator...")
    
    for issue in issues:
        # Skip non-bugs or purely informational things if configured
        # But for now, we try to fix everything classified as a bug
        if issue.get('type') in ['optimization', 'suggestion', 'info']:
            print(f"[GENERATOR] Skipping non-critical issue: {issue.get('description')}")
            continue
            
        fix = await generator.generate_fix(issue)
        if fix:
            fixes.append(fix)
            
    return fixes
