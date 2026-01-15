"""
Chatbot Executor

Executes approved changes by coordinating with existing AI Engine systems.
Integrates with bug detection, feature implementation, competitive analysis, etc.
"""

import os
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime


class ChatbotExecutor:
    """Executes approved changes and integrates with existing systems."""
    
    def __init__(self):
        self.execution_history = []
    
    async def execute_change(self, change_data: Dict) -> Dict:
        """
        Execute an approved change.
        
        Args:
            change_data: Change data including plan and intent
            
        Returns:
            Execution result
        """
        plan = change_data.get("plan", {})
        intent = change_data.get("intent")
        change_id = change_data.get("change_id")
        
        print(f"[EXECUTOR] Executing change {change_id} with intent: {intent}")
        
        try:
            if intent == "bug_fix":
                result = await self._execute_bug_fix(plan, change_data)
            elif intent == "feature_request":
                result = await self._execute_feature_request(plan, change_data)
            elif intent == "ui_change":
                result = await self._execute_ui_change(plan, change_data)
            elif intent == "competitive_analysis":
                result = await self._execute_competitive_analysis(plan, change_data)
            else:
                result = {
                    "success": False,
                    "error": f"Unknown intent: {intent}",
                    "message": "I don't know how to execute this type of change yet."
                }
            
            # Record execution
            self.execution_history.append({
                "change_id": change_id,
                "intent": intent,
                "executed_at": datetime.now().isoformat(),
                "result": result
            })
            
            return result
            
        except Exception as e:
            print(f"[EXECUTOR] Execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Execution failed: {str(e)}"
            }
    
    async def _execute_bug_fix(self, plan: Dict, change_data: Dict) -> Dict:
        """Execute bug fix by triggering existing bug detection pipeline."""
        
        try:
            # Import existing bug detection modules
            from enhanced_bug_detector import EnhancedBugDetector
            from improved_fixer import ImprovedFixer
            from github_handler import clone_or_pull_repo
            
            print("[EXECUTOR] Starting bug detection and fixing process...")
            
            # Get repository path
            repo_path = clone_or_pull_repo()
            url = os.getenv("WEBSITE_URL")
            
            # Initialize bug detector
            detector = EnhancedBugDetector()
            
            # Detect bugs
            print("[EXECUTOR] Detecting bugs...")
            bugs = await detector.detect_bugs(url)
            
            if not bugs:
                return {
                    "success": True,
                    "message": "No bugs detected! Your website looks good.",
                    "bugs_found": 0
                }
            
            print(f"[EXECUTOR] Found {len(bugs)} bugs, generating fixes...")
            
            # Initialize fixer
            fixer = ImprovedFixer(repo_path)
            
            # Generate fixes
            all_fixes = []
            for bug in bugs:
                fixes = await fixer.generate_fix(bug)
                if fixes:
                    all_fixes.extend(fixes)
            
            return {
                "success": True,
                "message": f"Detected {len(bugs)} bugs and generated {len(all_fixes)} fixes. Review and apply from the main dashboard.",
                "bugs_found": len(bugs),
                "fixes_generated": len(all_fixes),
                "bugs": bugs,
                "fixes": all_fixes
            }
            
        except ImportError as e:
            print(f"[EXECUTOR] Import error: {e}")
            return {
                "success": False,
                "error": "Bug detection modules not available",
                "message": "Bug detection system is not fully configured. Please check your setup."
            }
        except Exception as e:
            print(f"[EXECUTOR] Bug fix execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Bug detection failed: {str(e)}"
            }
    
    async def _execute_feature_request(self, plan: Dict, change_data: Dict) -> Dict:
        """Execute feature request by integrating with feature implementation manager."""
        
        try:
            from feature_implementation_manager import feature_implementation_manager
            
            print("[EXECUTOR] Processing feature request...")
            
            # Create a feature record from the plan
            feature = {
                "id": plan.get("plan_id"),
                "name": plan.get("summary"),
                "description": plan.get("original_request"),
                "priority_score": 8,  # High priority from chatbot
                "complexity": plan.get("complexity", "medium"),
                "estimated_effort": plan.get("estimated_effort", "Medium"),
                "implementation_notes": "\n".join([
                    f"{step['step_number']}. {step['description']}"
                    for step in plan.get("steps", [])
                ])
            }
            
            # Select feature for implementation
            result = feature_implementation_manager.select_feature_for_implementation(
                feature=feature,
                analysis_results={},
                generate_plan=False  # We already have a plan from chatbot
            )
            
            # Save our custom plan to file storage
            plan_file = feature_implementation_manager.implementation_plans_dir / f"{plan['plan_id']}_plan.json"
            plan_with_metadata = {
                **plan,
                "feature_id": plan["plan_id"],
                "generated_at": datetime.now().isoformat(),
                "status": "draft",
                "source": "chatbot"
            }
            with open(plan_file, 'w') as f:
                json.dump(plan_with_metadata, f, indent=2)
            
            print(f"[EXECUTOR] Saved implementation plan to {plan_file}")
            
            return {
                "success": True,
                "message": f"Feature '{plan.get('summary')}' has been queued for implementation. Track progress in the Feature Implementation Status dashboard.",
                "feature_id": plan.get("plan_id"),
                "status": result.get("status"),
                "implementation_plan": plan
            }
            
        except ImportError as e:
            print(f"[EXECUTOR] Import error: {e}")
            return {
                "success": False,
                "error": "Feature implementation manager not available",
                "message": "Feature implementation system is not fully configured."
            }
        except Exception as e:
            print(f"[EXECUTOR] Feature request execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Feature implementation failed: {str(e)}"
            }
    
    async def _execute_ui_change(self, plan: Dict, change_data: Dict) -> Dict:
        """Execute UI change by generating code modifications."""
        
        try:
            from smart_generator import SmartGenerator
            from github_handler import clone_or_pull_repo
            
            print("[EXECUTOR] Processing UI change request...")
            
            repo_path = clone_or_pull_repo()
            generator = SmartGenerator(repo_path)
            
            # Extract code from plan
            code_preview = plan.get("code_preview", {})
            
            if not code_preview:
                return {
                    "success": False,
                    "error": "No code preview in plan",
                    "message": "I couldn't generate code for this UI change. Please provide more details."
                }
            
            # Create a fix-like structure for the generator
            ui_change = {
                "file": code_preview.get("filename", ""),
                "change_type": "ui_modification",
                "code": code_preview.get("code", ""),
                "description": plan.get("summary", ""),
                "language": code_preview.get("language", "css")
            }
            
            return {
                "success": True,
                "message": f"UI change planned: {plan.get('summary')}. Code has been generated and is ready for review.",
                "code_preview": code_preview,
                "affected_files": plan.get("affected_files", []),
                "note": "Review the code changes in the pending changes section before applying."
            }
            
        except ImportError as e:
            print(f"[EXECUTOR] Import error: {e}")
            return {
                "success": False,
                "error": "Code generator not available",
                "message": "Code generation system is not fully configured."
            }
        except Exception as e:
            print(f"[EXECUTOR] UI change execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"UI change generation failed: {str(e)}"
            }
    
    async def _execute_competitive_analysis(self, plan: Dict, change_data: Dict) -> Dict:
        """Execute competitive analysis request."""
        
        try:
            from competitive_analyzer import CompetitiveAnalyzer
            
            print("[EXECUTOR] Running competitive analysis...")
            
            # Get competitor URLs from environment
            competitor_urls_str = os.getenv("COMPETITOR_URLS", "")
            competitor_urls = [url.strip() for url in competitor_urls_str.split(",") if url.strip()]
            
            if not competitor_urls:
                return {
                    "success": False,
                    "error": "No competitor URLs configured",
                    "message": "Please configure COMPETITOR_URLS in your .env file to run competitive analysis."
                }
            
            own_site_url = os.getenv("WEBSITE_URL")
            
            # Run analysis
            analyzer = CompetitiveAnalyzer(depth="standard")
            analysis = await analyzer.analyze_competitors(own_site_url, competitor_urls, premium=True)
            
            return {
                "success": True,
                "message": f"Competitive analysis complete! Found {analysis.get('summary', {}).get('total_gaps', 0)} feature gaps.",
                "analysis": analysis,
                "competitors_analyzed": len(competitor_urls)
            }
            
        except ImportError as e:
            print(f"[EXECUTOR] Import error: {e}")
            return {
                "success": False,
                "error": "Competitive analyzer not available",
                "message": "Competitive analysis system is not fully configured."
            }
        except Exception as e:
            print(f"[EXECUTOR] Competitive analysis execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Competitive analysis failed: {str(e)}"
            }


# Global instance
chatbot_executor = ChatbotExecutor()
