"""
Feature Implementation Manager - Manages feature selection and implementation planning
from competitive analysis results.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from model_router import _query_gemini_api


class FeatureImplementationManager:
    """Manages feature selection, implementation planning, and tracking."""
    
    def __init__(self, storage_dir: str = "./feature_implementations"):
        """
        Initialize the feature implementation manager.
        
        Args:
            storage_dir: Directory to store implementation data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.selected_features_file = self.storage_dir / "selected_features.json"
        self.implementation_plans_dir = self.storage_dir / "plans"
        self.implementation_plans_dir.mkdir(parents=True, exist_ok=True)
    
    def select_feature_for_implementation(
        self, 
        feature: Dict, 
        analysis_results: Dict,
        generate_plan: bool = True
    ) -> Dict:
        """
        Select a feature for future implementation.
        
        Args:
            feature: The selected feature data
            analysis_results: Full competitive analysis results
            generate_plan: Whether to generate implementation plan
            
        Returns:
            Selection result with status and next steps
        """
        feature_id = feature.get("id")
        feature_name = feature.get("name")
        
        # Load existing selections
        selected_features = self._load_selected_features()
        
        # Check if already selected
        if any(f["id"] == feature_id for f in selected_features):
            return {
                "status": "already_selected",
                "message": f"Feature '{feature_name}' is already in the implementation queue",
                "feature": feature
            }
        
        # Create selection record
        selection = {
            "id": feature_id,
            "feature_name": feature_name,
            "category": feature.get("category"),
            "priority_score": feature.get("priority_score"),
            "estimated_effort": feature.get("estimated_effort"),
            "business_impact": feature.get("business_impact"),
            "selected_at": datetime.now().isoformat(),
            "status": "selected",
            "implementation_status": "pending",
            "full_feature_data": feature
        }
        
        # Add to selected features
        selected_features.append(selection)
        self._save_selected_features(selected_features)
        
        result = {
            "status": "success",
            "message": f"Feature '{feature_name}' selected for implementation",
            "feature": feature,
            "selection_id": feature_id,
            "next_steps": []
        }
        
        # Generate implementation plan if requested
        if generate_plan:
            plan = self.generate_implementation_plan(feature, analysis_results)
            if plan:
                result["implementation_plan"] = plan
                result["next_steps"].append("Review generated implementation plan")
        else:
            result["next_steps"].append("Generate implementation plan")
        
        return result
    
    def _validate_and_resolve_file_paths(self, affected_files: List[str], repo_path: str) -> List[str]:
        """
        Validate and resolve file paths to actual files in repo.
        Prevents creating new files when existing files should be modified.
        
        Args:
            affected_files: List of file paths from plan (may be hallucinated)
            repo_path: Path to repository
            
        Returns:
            List of validated, existing file paths
        """
        import os
        valid_files = []
        
        for filepath in affected_files:
            full_path = os.path.join(repo_path, filepath)
            
            if os.path.exists(full_path):
                # File exists - use it!
                print(f"[PATH_VALIDATOR] ✅ {filepath} exists")
                valid_files.append(filepath)
            else:
                # File doesn't exist - try to find similar file
                print(f"[PATH_VALIDATOR] ⚠️  {filepath} doesn't exist, searching for similar files...")
                similar = self._find_similar_file(filepath, repo_path)
                if similar:
                    print(f"[PATH_VALIDATOR] ✅ Found {similar} instead")
                    valid_files.append(similar)
                else:
                    print(f"[PATH_VALIDATOR] ❌ No match found for {filepath}, skipping")
        
        return valid_files
    
    def _find_similar_file(self, target_filename: str, repo_path: str) -> str:
        """
        Find actual file matching the intent of target_filename.
        Searches for all file variants (.js → .tsx) in ALL discovered directories.
        
        Args:
            target_filename: Desired filename (may not exist)
            repo_path: Repository path
            
        Returns:
            Path to similar existing file, or None
        """
        import os
        basename = os.path.basename(target_filename)
        name_no_ext = os.path.splitext(basename)[0]
        basename_lower = basename.lower()
        
        # Generate all possible file variants
        file_variants = [
            f"{name_no_ext}.tsx",  # React TypeScript
            f"{name_no_ext}.ts",   # TypeScript
            f"{name_no_ext}.jsx",  # React JavaScript
            f"{name_no_ext}.js",   # JavaScript
            f"{name_no_ext}.vue",  # Vue
            basename                # Original
        ]
        
        # For CSS files, check common locations
        if basename_lower.endswith('.css'):
            search_paths = [
                "client/src/index.css",
                "client/src/globals.css",
                "client/src/app/globals.css",
                "src/index.css",
                "src/globals.css",
                "app/globals.css",
                "styles/globals.css",
                "styles/global.css"
            ]
            
            is_main_css = any(name in basename_lower for name in ['global', 'index', 'main', 'style'])
            
            for search_path in search_paths:
                full_path = os.path.join(repo_path, search_path)
                if os.path.exists(full_path):
                    if is_main_css:
                        return search_path
                    elif basename_lower in search_path.lower():
                        return search_path
            
            # Return first existing CSS
            for search_path in search_paths:
                full_path = os.path.join(repo_path, search_path)
                if os.path.exists(full_path):
                    return search_path
        
        # For JS/TS/React files - COMPREHENSIVE SEARCH
        if any(basename_lower.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx', '.vue']):
            # Search directories in order of likelihood
            search_dirs = [
                'client/src/components',
                'client/src/components/ui',
                'client/src/pages',
                'client/src',
                'src/components',
                'src/pages',
                'src',
                'app/components',
                'app',
                'components',
                'pages'
            ]
            
            # First, try exact match in each directory
            for search_dir in search_dirs:
                for variant in file_variants:
                    full_path = os.path.join(repo_path, search_dir, variant)
                    if os.path.exists(full_path):
                        return os.path.join(search_dir, variant)
            
            # Second, walk the entire src tree looking for matching filename
            src_dirs = ['client/src', 'src', 'app']
            for src_dir in src_dirs:
                src_full = os.path.join(repo_path, src_dir)
                if os.path.exists(src_full):
                    for root, dirs, files in os.walk(src_full):
                        for variant in file_variants:
                            if variant in files:
                                rel_path = os.path.relpath(os.path.join(root, variant), repo_path)
                                print(f"[PATH_VALIDATOR] 🔍 Found {rel_path} via recursive search")
                                return rel_path
        
        return None
    
    def _is_valid_new_file_path(self, filepath: str, repo_path: str, project_structure: Dict = None) -> bool:
        """
        Check if a new file path is valid using discovered project structure.
        100% dynamic - no hardcoded paths.
        
        Args:
            filepath: Path for new file
            repo_path: Repository root
            project_structure: Discovered project structure from CodeAnalyzer
            
        Returns:
            True if path is valid for new file creation
        """
        import os
        
        # Must have a directory and filename
        if '/' not in filepath:
            return False
        
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        
        # Filename must have extension
        if '.' not in filename:
            return False
        
        # Check if directory structure exists
        full_dir = os.path.join(repo_path, directory)
        
        # Directory exists - always valid
        if os.path.exists(full_dir):
            return True
        
        # Use discovered directories if available
        if project_structure:
            discovered_dirs = project_structure.get('directories', {})
            top_dirs = project_structure.get('top_code_directories', [])
            
            # Check if new file is under a discovered directory
            all_discovered = list(discovered_dirs.keys()) + top_dirs
            
            for discovered_dir in all_discovered:
                # New file under existing directory
                if filepath.startswith(discovered_dir + '/'):
                    return True
                
                # New file in sibling directory (e.g., pages next to components)
                discovered_parent = os.path.dirname(discovered_dir)
                new_file_parent = os.path.dirname(directory)
                if discovered_parent == new_file_parent:
                    return True
            
            # Check if parent directory exists (one level up)
            parent_dir = os.path.dirname(full_dir)
            if os.path.exists(parent_dir):
                return True
        
        # Fallback: Check if parent directory exists
        parent_dir = os.path.dirname(full_dir)
        if os.path.exists(parent_dir):
            return True
        
        # Last resort: Hardcoded patterns (only if no structure available)
        if not project_structure:
            common_patterns = ['client/src/', 'src/', 'app/', 'pages/', 'components/']
            for pattern in common_patterns:
                if filepath.startswith(pattern):
                    return True
        
        return False

    
    def generate_implementation_plan(self, feature: Dict, analysis_results: Dict) -> Optional[Dict]:
        """
        Generate an AI-powered implementation plan for the selected feature.
        
        Args:
            feature: The feature to implement
            analysis_results: Competitive analysis results for context
            
        Returns:
            Implementation plan or None if generation fails
        """
        feature_id = feature.get("id")
        feature_name = feature.get("name")
        
        print(f"[FEATURE_IMPL] Generating implementation plan for: {feature_name}")
        
        # Build context from competitive analysis
        competitors_context = ""
        if feature.get("found_in"):
            competitors_context = f"This feature is found in: {', '.join(feature['found_in'])}"
        
        implementation_notes = feature.get("implementation_notes", "")
        
        # Create prompt for AI
        prompt = f"""
Generate a detailed implementation plan for adding this feature to our website:

Feature: {feature_name}
Category: {feature.get('category')}
Priority: {feature.get('priority_score')}/10
Estimated Effort: {feature.get('estimated_effort')}
Business Impact: {feature.get('business_impact')}

Context:
{competitors_context}

Implementation Notes from Analysis:
{implementation_notes}

Please provide a JSON response with the following structure:
{{
    "feature_name": "{feature_name}",
    "overview": "Brief overview of what needs to be implemented",
    "requirements": [
        {{"id": 1, "requirement": "requirement description", "type": "functional/technical/ui"}}
    ],
    "implementation_steps": [
        {{"step": 1, "task": "task description", "estimated_hours": 2, "dependencies": []}}
    ],
    "technical_considerations": [
        "consideration 1",
        "consideration 2"
    ],
    "files_to_modify": [
        {{"file": "path/to/file.ext", "changes": "description of changes needed"}}
    ],
    "testing_strategy": [
        {{"test_type": "unit/integration/e2e", "description": "what to test"}}
    ],
    "rollout_plan": {{
        "phases": ["phase 1", "phase 2"],
        "estimated_timeline": "time estimate",
        "success_metrics": ["metric 1", "metric 2"]
    }}
}}

CRITICAL REQUIREMENTS FOR files_to_modify:
1. If creating NEW components/pages, you MUST include the main app routing file (App.tsx, app.tsx, or routes file)
2. ALWAYS ensure new components are wired into the existing application
3. DO NOT create orphan files that aren't imported anywhere
4. For React apps: include App.tsx updates for imports and routing
5. For API features: include the main API index file
6. Example: If creating "ProductList.tsx", also include "App.tsx" with routing changes

Example files_to_modify for a new feature:
[
  {{"file": "src/components/ProductList.tsx", "changes": "Create new product list component"}},
  {{"file": "src/App.tsx", "changes": "Import ProductList and add route for /products"}}
]

Make the plan practical and actionable.
"""
        
        try:
            # Query AI for implementation plan
            response = _query_gemini_api(
                messages=[{"role": "user", "content": prompt}],
                model=None,
                timeout=60
            )
            
            if not response or "error" in response:
                print(f"[ERROR] Failed to generate implementation plan: {response}")
                return None
            
            # Parse AI response
            ai_text = response.get("text", "")
            
            # Try to extract JSON from response
            plan_data = None
            if "```json" in ai_text:
                json_start = ai_text.find("```json") + 7
                json_end = ai_text.find("```", json_start)
                json_str = ai_text[json_start:json_end].strip()
                plan_data = json.loads(json_str)
            else:
                # Try to parse as direct JSON
                plan_data = json.loads(ai_text)
            
            if plan_data:
                # Enhance plan with metadata
                plan_data["feature_id"] = feature_id
                plan_data["generated_at"] = datetime.now().isoformat()
                plan_data["status"] = "draft"
                
                # Save plan to file
                plan_file = self.implementation_plans_dir / f"{feature_id}_plan.json"
                with open(plan_file, 'w') as f:
                    json.dump(plan_data, f, indent=2)
                
                print(f"[SUCCESS] Implementation plan generated and saved to {plan_file}")
                return plan_data
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse AI response as JSON: {e}")
        except Exception as e:
            print(f"[ERROR] Failed to generate implementation plan: {e}")
        
        return None
    
    async def execute_implementation(self, feature_id: str) -> Dict:
        """
        Execute the implementation by actually generating and writing code.
        
        Args:
            feature_id: ID of the feature to implement
            
        Returns:
            Execution result with files written and PR URL
        """
        print(f"[FEATURE_IMPL] Starting execution for feature: {feature_id}")
        
        # Get implementation plan and feature data
        plan = self.get_implementation_plan(feature_id)
        if not plan:
            return {
                "success": False,
                "error": "No implementation plan found",
                "message": "Please generate an implementation plan first"
            }
        
        feature = self._get_feature_by_id(feature_id)
        if not feature:
            return {
                "success": False,
                "error": "Feature not found",
                "message": f"Could not find feature {feature_id}"
            }
        
        try:
            # Analyze codebase for tech stack and structure context
            codebase_context = {}
            try:
                from github_handler import clone_or_pull_repo
                from code_analyzer import CodeAnalyzer
                
                print(f"[FEATURE_IMPL] Analyzing codebase...")
                repo_path = clone_or_pull_repo()
                analyzer = CodeAnalyzer(repo_path)
                analyzer.analyze_repository()
                
                codebase_summary = analyzer.get_codebase_summary()
                codebase_context = {
                    "repo_path": repo_path,
                    "tech_stack": codebase_summary.get('tech_stack', {}),
                    "project_structure": codebase_summary.get('project_structure', {})
                }
                
                print(f"[FEATURE_IMPL] Tech stack: {codebase_context['tech_stack']}")
                print(f"[FEATURE_IMPL] Structure: {codebase_context['project_structure']['structure_type']}")
                
            except Exception as e:
                print(f"[FEATURE_IMPL] Failed to analyze codebase: {e}")
                # Continue without codebase context
            
            # Generate code for each file in the plan
            generated_files = []
            files_to_modify = plan.get("files_to_modify", [])
            
            print(f"[FEATURE_IMPL] Plan keys: {plan.keys()}")
            print(f"[FEATURE_IMPL] Files to modify: {files_to_modify}")
            
            # FALLBACK: If plan came from chatbot, it has 'affected_files' not 'files_to_modify'
            if not files_to_modify and plan.get("affected_files"):
                print(f"[FEATURE_IMPL] Converting chatbot plan format to execution format...")
                
                # CRITICAL: Validate file paths against actual repo
                affected_files = plan.get("affected_files", [])
                repo_path = codebase_context.get("repo_path", "")
                
                all_files = []
                if repo_path:
                    print(f"[FEATURE_IMPL] Validating {len(affected_files)} file paths...")
                    valid_file_paths = self._validate_and_resolve_file_paths(affected_files, repo_path)
                    
                    if not valid_file_paths and affected_files: # Only error if chatbot suggested files but none were valid
                        error_msg = f"Chatbot suggested files {affected_files} but none exist in repository"
                        print(f"[ERROR] {error_msg}")
                        return {
                            "success": False,
                            "error": "Invalid file paths",
                            "message": error_msg
                        }
                    
                    print(f"[FEATURE_IMPL] ✅ Validated to {len(valid_file_paths)} actual files: {valid_file_paths}")
                    
                    # CRITICAL: Separate new files from existing files
                    existing_files = []
                    new_files = []
                    
                    for filepath in affected_files:
                        if filepath in valid_file_paths:
                            # File exists - will modify
                            existing_files.append(filepath)
                        else:
                            # File doesn't exist - will create
                            # Validate the path structure is reasonable using discovered directories
                            project_structure = codebase_context.get('project_structure', {})
                            if self._is_valid_new_file_path(filepath, repo_path, project_structure):
                                print(f"[FEATURE_IMPL] 📄 Will create new file: {filepath}")
                                new_files.append(filepath)
                            else:
                                print(f"[FEATURE_IMPL] ⚠️  Invalid path for new file: {filepath}")
                    
                    # Combine for file modification list
                    all_files = existing_files + new_files
                    print(f"[FEATURE_IMPL] Files: {len(existing_files)} existing, {len(new_files)} new")
                else:
                    print(f"[WARNING] No repo_path for validation, using chatbot paths as-is")
                    all_files = affected_files
                
                files_to_modify = [
                    {"file": filepath, "changes": f"Implement {plan.get('summary', 'changes')}"}
                    for filepath in all_files
                ]
                print(f"[FEATURE_IMPL] Converted to {len(files_to_modify)} files")
            
            if not files_to_modify:
                error_msg = f"No files to modify in plan. Plan has: {list(plan.keys())}"
                print(f"[ERROR] {error_msg}")
                return {
                    "success": False,
                    "error": "No files to modify in plan",
                    "message": error_msg
                }
            
            print(f"[FEATURE_IMPL] Generating code for {len(files_to_modify)} files...")
            
            # NEW: Build list of files being created in this batch
            # These should be allowed for imports even though they don't exist yet
            files_being_created = [f.get("file") for f in files_to_modify]
            print(f"[FEATURE_IMPL] 📝 Files being created in this PR: {files_being_created}")
            
            # Update codebase_context to include files being created
            if codebase_context:
                codebase_context['files_being_created'] = files_being_created
            else:
                codebase_context = {'files_being_created': files_being_created}
            
            for file_spec in files_to_modify:
                try:
                    code = await self._generate_file_code(file_spec, plan, feature, codebase_context)
                    generated_files.append({
                        "path": file_spec.get("file"),
                        "content": code,
                        "description": file_spec.get("changes", "Code changes")
                    })
                    print(f"[FEATURE_IMPL] Generated code for {file_spec.get('file')}")
                except Exception as e:
                    print(f"[ERROR] Failed to generate code for {file_spec.get('file')}: {e}")
                    continue
            
            if not generated_files:
                return {
                    "success": False,
                    "error": "Code generation failed",
                    "message": "Failed to generate code for any files"
                }
            
           
            # ROUTING VALIDATION - Auto-fix orphaned pages
            print("[FEATURE_IMPL] 🔍 Validating routing...")
            try:
                from routing_validator import routing_validator
                file_contents_dict = {f["path"]: f["content"] for f in generated_files}
                validation_result = routing_validator.validate_routing(
                    generated_files=file_contents_dict,
                    repo_path=codebase_context.get('repo_path', ''),
                    tech_stack=codebase_context.get('tech_stack', {})
                )
                if validation_result['needs_fix']:
                    print(f"[ROUTING_VALIDATOR] ⚠️  Routing issues: {validation_result['issues']}")
                    for fix in validation_result['fixes']:
                        existing = next((f for f in generated_files if f["path"] == fix['path']), None)
                        if existing:
                            existing['content'] = fix['content']
                        else:
                            generated_files.append({"path": fix['path'], "content": fix['content'], "description": "Auto-generated routing fix"})
                        print(f"[ROUTING_VALIDATOR] ✅ Fixed routing in {fix['path']}")
                    print(f"[ROUTING_VALIDATOR] 🎉 Applied {len(validation_result['fixes'])} routing fixes!")
                elif validation_result['new_pages']:
                    print(f"[ROUTING_VALIDATOR] ✅ All {len(validation_result['new_pages'])} pages properly routed")
            except Exception as e:
                print(f"[ROUTING_VALIDATOR] ⚠️  Validation failed: {e}")
            
            # BUILD VALIDATION - Catch import mismatches and naming issues
            print("[FEATURE_IMPL] 🏗️  Validating builds...")
            try:
                from build_validator import build_validator
                from codebase_constraint_builder import CodebaseConstraintBuilder
                
                file_contents_dict = {f["path"]: f["content"] for f in generated_files}
                repo_path = codebase_context.get('repo_path', '')
                
                build_result = build_validator.validate_imports(
                    generated_files=file_contents_dict,
                    repo_path=repo_path
                )
                
                if not build_result['valid']:
                    print(f"[BUILD_VALIDATOR] ⚠️  Found {len(build_result['issues'])} build issues:")
                    for issue in build_result['issues'][:5]:  # Show first 5
                        print(f"  - {issue['type']}: {issue['message']}")
                    
                    # NEW: Check for hallucinated imports (imports to non-existent files)
                    hallucinated_imports = []
                    for issue in build_result['issues']:
                        if issue['type'] == 'unresolved_import':
                            import_path = issue.get('import_path', '')
                            
                            # Check if this file exists in codebase or was generated
                            file_exists = False
                            
                            # Check in generated files
                            for gen_file in generated_files:
                                if import_path in gen_file['path'] or gen_file['path'].endswith(import_path):
                                    file_exists = True
                                    break
                            
                            # Check in existing codebase
                            if not file_exists and repo_path:
                                try:
                                    constraint_builder = CodebaseConstraintBuilder(repo_path)
                                    existing_files = constraint_builder.get_existing_files_list()
                                    
                                    for existing_file in existing_files:
                                        if import_path in existing_file or existing_file.endswith(import_path):
                                            file_exists = True
                                            break
                                except:
                                    pass
                            
                            if not file_exists:
                                print(f"[BUILD_VALIDATOR] 🚨 HALLUCINATED IMPORT DETECTED: {import_path}")
                                print(f"[BUILD_VALIDATOR]    File: {issue.get('file')}")
                                hallucinated_imports.append(issue)
                    
                    if hallucinated_imports:
                        # Files with hallucinated imports need regeneration, not fixing
                        print(f"[BUILD_VALIDATOR] 🔄 {len(hallucinated_imports)} file(s) have hallucinated imports - regenerating with STRICT constraints...")
                        
                        # Group issues by file
                        issues_by_file = {}
                        for issue in hallucinated_imports:
                            file_path = issue.get('file')
                            if file_path not in issues_by_file:
                                issues_by_file[file_path] = []
                            issues_by_file[file_path].append(issue)
                        
                        # Regenerate files with hallucinated imports (max 2 attempts per file)
                        for file_path, file_issues in issues_by_file.items():
                            print(f"[BUILD_VALIDATOR] Regenerating {file_path} (found {len(file_issues)} halluci nated imports)")
                            
                            # Find file spec
                            file_spec = None
                            for f in files_to_modify:
                                if f.get('file') == file_path:
                                    file_spec = f
                                    break
                            
                            if file_spec:
                                try:
                                    # Regenerate with explicit warning about hallucinated imports
                                    print(f"[BUILD_VALIDATOR] ⛔ STRICT MODE: Listing exact import violations...")
                                    violated_imports = [issue.get('import_path') for issue in file_issues]
                                    print(f"[BUILD_VALIDATOR]    Invalid imports: {violated_imports}")
                                    
                                    new_code = await self._generate_file_code(
                                        file_spec=file_spec,
                                        plan=plan,
                                        feature=feature,
                                        codebase_context=codebase_context
                                    )
                                    
                                    # Update the generated file
                                    for gen_file in generated_files:
                                        if gen_file['path'] == file_path:
                                            gen_file['content'] = new_code
                                            print(f"[BUILD_VALIDATOR] ✅ Regenerated {file_path}")
                                            break
                                            
                                except Exception as e:
                                    print(f"[BUILD_VALIDATOR] ⚠️  Regeneration failed for {file_path}: {e}")
                        
                        # Re-validate after regeneration
                        file_contents_dict = {f["path"]: f["content"] for f in generated_files}
                        revalidation = build_validator.validate_imports(file_contents_dict, repo_path=repo_path)
                        
                        if revalidation['valid']:
                            print("[BUILD_VALIDATOR] ✅ All hallucinated imports fixed through regeneration!")
                        else:
                            remaining_issues = len(revalidation['issues'])
                            print(f"[BUILD_VALIDATOR] ⚠️  Still have {remaining_issues} issues after regeneration")
                            
                            # Try standard auto-fixes for remaining issues
                            fixed_files = build_validator.generate_fixes(revalidation['issues'], file_contents_dict)
                            if fixed_files:
                                for fixed_path, fixed_content in fixed_files.items():
                                    existing = next((f for f in generated_files if f["path"] == fixed_path), None)
                                    if existing:
                                        existing['content'] = fixed_content
                                print(f"[BUILD_VALIDATOR] ✅ Applied {len(fixed_files)} additional auto-fixes")
                    else:
                        # No hallucinated imports -  try standard auto-fixes
                        print("[BUILD_VALIDATOR] 🔧 Attempting auto-fixes...")
                        fixed_files = build_validator.generate_fixes(build_result['issues'], file_contents_dict)
                        
                        if fixed_files:
                            print(f"[BUILD_VALIDATOR] ✅ Auto-fixed {len(fixed_files)} files")
                            # Apply fixes
                            for fixed_path, fixed_content in fixed_files.items():
                                existing = next((f for f in generated_files if f["path"] == fixed_path), None)
                                if existing:
                                    existing['content'] = fixed_content
                                    print(f"[BUILD_VALIDATOR]   ✓ Updated {fixed_path}")
                            
                            # Re-validate after fixes
                            file_contents_dict = {f["path"]: f["content"] for f in generated_files}
                            revalidation = build_validator.validate_imports(file_contents_dict, repo_path=repo_path)
                            
                            if revalidation['valid']:
                                print("[BUILD_VALIDATOR] ✅ All build issues resolved!")
                            else:
                                print(f"[BUILD_VALIDATOR] ⚠️  Still have {len(revalidation['issues'])} unresolved issues")
                                # Continue anyway but log the issues
                        else:
                            print("[BUILD_VALIDATOR] ⚠️  Could not auto-fix all issues")
                else:
                    print("[BUILD_VALIDATOR] ✅ Build validation passed - no issues found!")
                    
            except Exception as e:
                print(f"[BUILD_VALIDATOR] ⚠️  Build validation failed: {e}")
                import traceback
                traceback.print_exc()

            
            
            # Write files to repository and create PR
            from github_handler import submit_fix_pr
            
            print(f"[FEATURE_IMPL] Submitting PR with {len(generated_files)} files...")
            pr_url = submit_fix_pr(generated_files)
            
            if pr_url:
                # Update feature status to completed
                self.update_feature_status(
                    feature_id, 
                    "completed",
                    f"Implementation completed. PR: {pr_url}"
                )
                
                return {
                    "success": True,
                    "message": f"Feature implemented successfully! {len(generated_files)} files modified.",
                    "files_written": [f["path"] for f in generated_files],
                    "pr_url": pr_url,
                    "feature_name": plan.get("feature_name")
                }
            else:
                return {
                    "success": False,
                    "error": "PR creation failed",
                    "message": "Code was generated but failed to create PR. Check GitHub credentials."
                }
                
        except Exception as e:
            print(f"[ERROR] Feature execution failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Update status to pending with error note
            self.update_feature_status(
                feature_id,
                "pending",
                f"Execution failed: {str(e)}"
            )
            
            return {
                "success": False,
                "error": str(e),
                "message": f"Feature execution failed: {str(e)}"
            }
    
    async def _generate_file_code(self, file_spec: Dict, plan: Dict, feature: Dict, codebase_context: Dict = None) -> str:
        """
        Generate actual production-ready code for a file based on the plan.
        
        Args:
            file_spec: File specification from the plan
            plan: Full implementation plan
            feature: Feature data
            codebase_context: Tech stack and project structure info
            
        Returns:
            Generated code as string
        """
        filename = file_spec.get("file")
        changes_needed = file_spec.get("changes")
        
        # READ EXISTING FILE CONTENT FIRST
        existing_code = ""
        try:
            import os
            repo_path = codebase_context.get('repo_path') if codebase_context else None
            if repo_path:
                file_path = os.path.join(repo_path, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        existing_code = f.read()
                    print(f"[FEATURE_IMPL] Read {len(existing_code)} chars from existing {filename}")
                else:
                    print(f"[FEATURE_IMPL] File {filename} doesn't exist yet, will create new")
        except Exception as e:
            print(f"[FEATURE_IMPL] Could not read existing file: {e}")
        
        # Extract tech stack and structure info
        tech_stack_info = ""
        codebase_constraints = ""  # NEW: Add comprehensive constraints
        
        if codebase_context:
            tech_stack = codebase_context.get('tech_stack', {})
            project_structure = codebase_context.get('project_structure', {})
            repo_path = codebase_context.get('repo_path', '')
            
            tech_stack_info = f"""\n\nCODEBASE CONTEXT:
Framework: {tech_stack.get('framework', 'unknown')}
Language: {tech_stack.get('language', 'javascript')}
Project Structure: {project_structure.get('structure_type', 'unknown')}

IMPORTANT CODE GENERATION RULES:
- Generate {tech_stack.get('language', 'JavaScript').upper()} code
- Use proper file extension: {'.tsx' if tech_stack.get('language') == 'typescript' and 'react' in tech_stack.get('framework', '') else '.ts' if tech_stack.get('language') == 'typescript' else '.jsx' if 'react' in tech_stack.get('framework', '') else '.js'}
- Match the existing codebase patterns
- Use {tech_stack.get('framework', 'vanilla JS')} syntax if applicable
"""
            
            # NEW: Build comprehensive constraints to prevent hallucinated imports
            if repo_path:
                try:
                    from codebase_constraint_builder import CodebaseConstraintBuilder
                    
                    print(f"[FEATURE_IMPL] 🔒 Building codebase constraints to prevent hallucinated imports...")
                    constraint_builder = CodebaseConstraintBuilder(repo_path)
                    
                    # NEW: Add files being created in this PR to the allowed imports
                    files_being_created = codebase_context.get('files_being_created', [])
                    codebase_constraints = "\n\n" + constraint_builder.build_complete_constraints(
                        tech_stack, 
                        files_being_created=files_being_created
                    )
                    
                    if files_being_created:
                        print(f"[FEATURE_IMPL] ℹ️  Allowing imports from {len(files_being_created)} files being created in this PR")
                    
                    print(f"[FEATURE_IMPL] ✅ Constraint builder loaded ({len(codebase_constraints)} chars)")
                    
                except Exception as e:
                    print(f"[FEATURE_IMPL] ⚠️  Could not build codebase constraints: {e}")
                    import traceback
                    traceback.print_exc()

        
        # Build prompt based on whether file exists
        if existing_code:
            # File exists - ask for MODIFICATIONS
            prompt = f"""You are modifying an EXISTING file. Your job is to ADD or MODIFY code while PRESERVING all existing functionality.

File: {filename}
Changes Needed: {changes_needed}
{tech_stack_info}
{codebase_constraints}

Feature Context:
Name: {plan.get('feature_name')}
Overview: {plan.get('overview')}

Requirements:
"""
            # Add requirements
            for req in plan.get("requirements", [])[:5]:
                prompt += f"- {req.get('requirement')}\n"
            
            prompt += f"""

=== CURRENT FILE CONTENT ===
{existing_code}
=== END CURRENT FILE CONTENT ===

<modification_strategy>
1. Start with existing code as your base
2. ADD new functionality by integrating into existing structure  
3. MODIFY only specific sections that need changes
4. Return COMPLETE file with integrated changes
</modification_strategy>

<validation_requirements>
Your code will be automatically validated for:
✓ Security: No eval(), innerHTML, document.write()
✓ Syntax: Valid TypeScript/JSX compliance
✓ Imports: All paths must resolve correctly
✓ Naming: Component name MUST match filename
✓ No duplicate function/variable names
</validation_requirements>

<example>
Task: Add logout button to existing Navbar
Existing: export default function Navbar() {{ return <nav><Link to="/home">Home</Link></nav>; }}
Correct Output: export default function Navbar() {{ return <nav><Link to="/home">Home</Link><button>Logout</button></nav>; }}
</example>

CRITICAL IMPORT AND NAMING REQUIREMENTS:
1. Component name MUST match filename:
   File: ProfilePage.tsx → export default function ProfilePage()
2. Import paths MUST use file's actual name:
   ✅ import ProfilePage from '@/pages/ProfilePage'
   ❌ import Profile from '@/pages/Profile'
3. Use path aliases: @/components/, @/pages/ (not ../../)

For NEW components/pages, you MUST also update the main app file (App.tsx) to import and route them.
 to:
  * Add imports for the new components (with EXACT filename match)
  * Add routes if using React Router
  * Include the component in the render/return statement
- If creating NEW pages, update the routing configuration
- If creating NEW API endpoints, update the API index file
- Ensure all new files are CONNECTED and INTEGRATED into the existing application
- Don't just create orphan files - wire them into the app!
"""
            
            # Add JSX example without f-string to avoid syntax errors
            prompt += """
Example for React Router (add to App.tsx):
// Import at top (COMPONENT NAME MUST MATCH FILENAME):
import ProfilePage from '@/pages/ProfilePage';  // ✅ Matches ProfilePage.tsx
// Add route:
<Route path="/profile" element={<ProfilePage />} />

Example for direct inclusion (add to App.tsx):
Add the component in the return statement

Respond with ONLY the code, no explanations or markdown formatting.

"""
        else:
            # New file - generate from scratch
            prompt = f"""Generate code for this NEW file:

File: {filename}
Purpose: {changes_needed}
{tech_stack_info}
{codebase_constraints}

Feature Context:
Name: {plan.get('feature_name')}
Overview: {plan.get('overview')}

Requirements:
"""
            # Add requirements
            for req in plan.get("requirements", [])[:5]:
                prompt += f"- {req.get('requirement')}\n"
            
            prompt += f"""

Implementation Guidelines:
"""
            # Add relevant steps
            for step in plan.get("implementation_steps", [])[:3]:
                if filename in step.get("task", ""):
                    prompt += f"- {step.get('task')}\n"
            
            prompt += f"""

CRITICAL NAMING AND IMPORT REQUIREMENTS:
⚠️  FOLLOW THESE RULES TO PREVENT BUILD FAILURES:

1. **Component Name MUST EXACTLY Match Filename:**
   - Filename: {os.path.basename(filename)}
   - Component Name: {os.path.splitext(os.path.basename(filename))[0]}
   - ✅ Your component MUST be named: {os.path.splitext(os.path.basename(filename))[0]}
   - Export as: export default {os.path.splitext(os.path.basename(filename))[0]}

2. **When This File Gets Imported:**
   - It will be imported as: import {os.path.splitext(os.path.basename(filename))[0]} from '@/...'
   - The component name MUST match this import exactly

3. **Component Structure:**
   ```
   function {os.path.splitext(os.path.basename(filename))[0]}() {{
     // component code
   }}
   
   export default {os.path.splitext(os.path.basename(filename))[0]};
   ```

4. **NO Shortcuts or Abbreviations:**
   - If filename is "ProfilePage.tsx", component MUST be "ProfilePage", NOT "Profile"
   - If filename is "UserDashboard.tsx", component MUST be "UserDashboard", NOT "Dashboard"

IMPORTANT:
- Generate COMPLETE, working code for this NEW file
- Include all necessary imports, functions, and logic
- Make it production-ready and error-free
- Follow best practices for {filename.split('.')[-1]} files
- Add proper error handling
- RESPECT the tech stack and file extension shown above
- Generate code matching the detected framework and language

CRITICAL INTEGRATION REQUIREMENTS:
- If this is a NEW component/page, ensure it will be imported and used
- If this is being added to a React app, it should be importable
- Follow the existing project structure and naming conventions
- Ensure proper exports (default export for React components)
- Component name = Filename (without extension) - NO EXCEPTIONS

Respond with ONLY the code, no explanations or markdown formatting.
"""

        
        try:
            response = _query_gemini_api(
                messages=[{"role": "user", "content": prompt}],
                timeout=60
            )
            
            if "error" in response:
                raise Exception(f"Gemini API error: {response['error']}")
            
            # Extract code from response
            code = response.get("content") or response.get("response", "")
            
            # Clean up markdown code blocks if present
            if not code or len(code.strip()) < 10:
                print(f"[ERROR] No code generated for {filename}")
                return existing_code if existing_code else ""
            
            # CRITICAL: Remove markdown code fences that AI sometimes adds
            import re
            # Remove opening fence (```typescript, ```tsx, etc.)
            code = re.sub(r'^```\w*\s*\n?', '', code.strip())
            # Remove closing fence
            code = re.sub(r'\n?```\s*$', '', code.strip())
            # Remove any standalone ``` lines
            lines = code.split('\n')
            code = '\n'.join(line for line in lines if line.strip() != '```')
            
            return code.strip()
            
        except Exception as e:
            error_msg = f"Code generation failed for {filename}: {e}"
            print(f"[ERROR] {error_msg}")
            
            # Check if this is a quota/API error that should stop execution
            if "quota" in str(e).lower() or "429" in str(e) or "rate limit" in str(e).lower():
                print(f"[FEATURE_IMPL] ⛔ QUOTA/API ERROR - Cannot proceed with PR creation")
                # Re-raise to stop PR creation entirely
                raise Exception(f"Cannot create PR: {error_msg}")
            
            # For other errors, try to return existing code if available
            if existing_code:
                print(f"[FEATURE_IMPL] Returning existing code due to generation failure")
                return existing_code
            
            # If no existing code and it's not a file we're creating, this is critical
            print(f"[FEATURE_IMPL] ⛔ CRITICAL: No code available for {filename}")
            raise Exception(f"Cannot generate required file {filename}: {error_msg}")


    
    def _get_feature_by_id(self, feature_id: str) -> Optional[Dict]:
        """
        Get feature data by ID.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            Feature data or None if not found
        """
        features = self._load_selected_features()
        for feature in features:
            if feature["id"] == feature_id:
                return feature
        return None
    
    def get_selected_features(self, status_filter: Optional[str] = None) -> List[Dict]:
        """
        Get all selected features, optionally filtered by status.
        
        Args:
            status_filter: Filter by implementation_status (pending/in_progress/completed/cancelled)
            
        Returns:
            List of selected features
        """
        features = self._load_selected_features()
        
        if status_filter:
            features = [f for f in features if f.get("implementation_status") == status_filter]
        
        return features
    
    def update_feature_status(self, feature_id: str, new_status: str, notes: str = "") -> Dict:
        """
        Update the implementation status of a feature.
        
        Args:
            feature_id: ID of the feature
            new_status: New status (pending/in_progress/completed/cancelled)
            notes: Optional notes about the status change
            
        Returns:
            Updated feature data
        """
        valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        features = self._load_selected_features()
        
        # Find and update feature
        updated_feature = None
        for feature in features:
            if feature["id"] == feature_id:
                feature["implementation_status"] = new_status
                feature["status_updated_at"] = datetime.now().isoformat()
                
                if notes:
                    if "status_history" not in feature:
                        feature["status_history"] = []
                    feature["status_history"].append({
                        "status": new_status,
                        "notes": notes,
                        "timestamp": datetime.now().isoformat()
                    })
                
                updated_feature = feature
                break
        
        if not updated_feature:
            raise ValueError(f"Feature {feature_id} not found")
        
        self._save_selected_features(features)
        return updated_feature
    
    def get_implementation_plan(self, feature_id: str) -> Optional[Dict]:
        """
        Retrieve the implementation plan for a feature.
        
        Args:
            feature_id: ID of the feature
            
        Returns:
            Implementation plan or None if not found
        """
        plan_file = self.implementation_plans_dir / f"{feature_id}_plan.json"
        
        if plan_file.exists():
            with open(plan_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def prioritize_features(self, features: List[Dict]) -> List[Dict]:
        """
        Prioritize features based on multiple factors.
        
        Args:
            features: List of selected features
            
        Returns:
            Sorted list of features by priority
        """
        def calculate_priority_score(feature):
            # Weight different factors
            priority = feature.get("priority_score", 5) * 10  # 0-100
            
            # Business impact multiplier
            impact_multipliers = {"high": 1.3, "medium": 1.0, "low": 0.7}
            impact = feature.get("business_impact", "medium")
            priority *= impact_multipliers.get(impact, 1.0)
            
            # Effort divisor (lower effort = higher priority)
            effort_divisors = {"Low": 1.0, "Medium": 0.8, "High": 0.6}
            effort = feature.get("estimated_effort", "Medium")
            priority *= effort_divisors.get(effort, 0.8)
            
            return priority
        
        return sorted(features, key=calculate_priority_score, reverse=True)
    
    def get_implementation_summary(self) -> Dict:
        """
        Get a summary of all feature implementations.
        
        Returns:
            Summary statistics
        """
        features = self._load_selected_features()
        
        summary = {
            "total_selected": len(features),
            "by_status": {
                "pending": len([f for f in features if f.get("implementation_status") == "pending"]),
                "in_progress": len([f for f in features if f.get("implementation_status") == "in_progress"]),
                "completed": len([f for f in features if f.get("implementation_status") == "completed"]),
                "cancelled": len([f for f in features if f.get("implementation_status") == "cancelled"])
            },
            "by_priority": {
                "high": len([f for f in features if f.get("priority_score", 0) >= 7]),
                "medium": len([f for f in features if 4 <= f.get("priority_score", 0) < 7]),
                "low": len([f for f in features if f.get("priority_score", 0) < 4])
            },
            "by_effort": {
                "Low": len([f for f in features if f.get("estimated_effort") == "Low"]),
                "Medium": len([f for f in features if f.get("estimated_effort") == "Medium"]),
                "High": len([f for f in features if f.get("estimated_effort") == "High"])
            },
            "features": features
        }
        
        return summary
    
    # Private helper methods
    
    def _load_selected_features(self) -> List[Dict]:
        """Load selected features from storage."""
        if self.selected_features_file.exists():
            with open(self.selected_features_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_selected_features(self, features: List[Dict]):
        """Save selected features to storage."""
        with open(self.selected_features_file, 'w') as f:
            json.dump(features, f, indent=2)


# Global instance
feature_implementation_manager = FeatureImplementationManager()
