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
                     conversation_history: List[Dict] = None) -> Dict:
        """
        Generate an implementation plan based on user intent.
        
        Args:
            intent: Detected intent category
            user_message: Original user message
            entities: Extracted entities from intent detection
            conversation_history: Previous conversation for context
            
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
        prompt = self._build_plan_prompt(intent, user_message, entities, conversation_history)
        
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
    
    def _build_plan_prompt(self, intent: str, user_message: str, entities: Dict,
                          conversation_history: List[Dict] = None) -> str:
        """Build prompt for plan generation."""
        
        context = ""
        if conversation_history and len(conversation_history) > 0:
            context = "\n\nConversation context:\n"
            for msg in conversation_history[-3:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role.upper()}: {content}\n"
        
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
