"""
Chatbot Manager

Main orchestration layer for the AI chatbot.
Handles conversation flow, intent detection, plan generation, and response formatting.
"""

from typing import Dict, List, Optional
from datetime import datetime
from chat_storage import chat_storage
from chatbot_intent_detector import intent_detector
from chatbot_plan_generator import plan_generator


class ChatbotManager:
    """Main chatbot orchestration and conversation management."""
    
    def __init__(self):
        self.storage = chat_storage
        self.intent_detector = intent_detector
        self.plan_generator = plan_generator
    
    def create_session(self, user_id: str = "default") -> Dict:
        """
        Create a new chat session.
        
        Args:
            user_id: User identifier
            
        Returns:
            Session data with welcome message
        """
        session = self.storage.create_session(user_id)
        
        # Add welcome message
        welcome_message = self._get_welcome_message()
        self.storage.add_message(
            session["session_id"],
            "assistant",
            welcome_message,
            {"message_type": "welcome"}
        )
        
        # Reload session to get the welcome message
        session = self.storage.load_session(session["session_id"])
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.storage.load_session(session_id)
    
    def get_all_sessions(self, user_id: Optional[str] = None) -> List[Dict]:
        """Get all sessions, optionally filtered by user."""
        return self.storage.get_all_sessions(user_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        return self.storage.delete_session(session_id)
    
    async def process_message(self, session_id: str, user_message: str) -> Dict:
        """
        Process a user message and generate response.
        
        Args:
            session_id: Session ID
            user_message: User's message
            
        Returns:
            {
                "response": str,
                "intent": str,
                "plan": Dict (if plan was generated),
                "requires_approval": bool,
                "metadata": Dict
            }
        """
        # Load session
        session = self.storage.load_session(session_id)
        if not session:
            return {
                "error": "Session not found",
                "response": "Sorry, I couldn't find your session. Please start a new conversation."
            }
        
        # Save user message
        self.storage.add_message(session_id, "user", user_message)
        
        # Get conversation history for context
        conversation_history = session["conversation_history"]
        
        # Detect intent
        print(f"[CHATBOT] Processing message: {user_message[:50]}...")
        intent_data = self.intent_detector.detect_intent(user_message, conversation_history)
        
        # Update session context
        session = self.storage.load_session(session_id)
        session["context"]["current_intent"] = intent_data["intent"]
        session["metadata"]["last_intent"] = intent_data["intent"]
        self.storage.save_session(session)
        
        # Check if clarification is needed
        if intent_data.get("requires_clarification"):
            response = self._format_clarification_response(intent_data)
            self.storage.add_message(
                session_id,
                "assistant",
                response["response"],
                {"message_type": "clarification", "intent_data": intent_data}
            )
            return response
        
        # Handle based on intent
        intent = intent_data["intent"]
        
        if intent == self.intent_detector.STATUS_INQUIRY:
            response = self._handle_status_inquiry(session_id, user_message, intent_data)
        elif intent == self.intent_detector.GENERAL_QUESTION:
            response = self._handle_general_question(session_id, user_message, intent_data)
        elif intent == self.intent_detector.REFINEMENT:
            response = await self._handle_refinement(session_id, user_message, intent_data)
        else:
            # For actionable intents, generate a plan
            response = await self._handle_actionable_intent(
                session_id, user_message, intent_data, conversation_history
            )
        
        # Save assistant response
        self.storage.add_message(
            session_id,
            "assistant",
            response["response"],
            {
                "message_type": "response",
                "intent": intent,
                "has_plan": "plan" in response
            }
        )
        
        return response
    
    async def _handle_actionable_intent(self, session_id: str, user_message: str,
                                       intent_data: Dict, conversation_history: List[Dict]) -> Dict:
        """Handle intents that require action (feature, bug fix, UI change, etc.)."""
        
        intent = intent_data["intent"]
        entities = intent_data.get("entities", {})
        
        # CRITICAL: Detect tech stack BEFORE generating plan
        print(f"[CHATBOT] Detecting tech stack for intent: {intent}")
        tech_stack_context = await self._detect_tech_stack()
        
        if tech_stack_context:
            tech_stack = tech_stack_context.get("tech_stack", {})
            print(f"[CHATBOT] Tech stack detected: {tech_stack.get('framework')} + {tech_stack.get('language')}")
        else:
            print(f"[CHATBOT] No tech stack detected, using defaults")
        
        # Generate implementation plan WITH tech stack context
        print(f"[CHATBOT] Generating plan for intent: {intent}")
        plan = self.plan_generator.generate_plan(
            intent, user_message, entities, conversation_history,
            tech_stack_context=tech_stack_context  # NEW: Pass tech stack
        )
        
        if "error" in plan:
            return {
                "response": plan.get("summary", "I couldn't create a plan for that request. Could you provide more details?"),
                "intent": intent,
                "error": plan["error"]
            }
        
        # Save as pending change
        change_id = self.storage.save_pending_change(session_id, {
            "plan": plan,
            "intent": intent,
            "user_request": user_message
        })
        
        # Format response with plan
        response_text = self._format_plan_response(plan, change_id)
        
        return {
            "response": response_text,
            "intent": intent,
            "plan": plan,
            "plan_id": change_id,  # Frontend expects plan_id, not change_id
            "change_id": change_id,  # Keep for backwards compatibility
            "requires_approval": True,
            "metadata": {
                "confidence": intent_data.get("confidence"),
                "entities": entities
            }
        }
    
    async def _handle_refinement(self, session_id: str, user_message: str,
                                intent_data: Dict) -> Dict:
        """Handle refinement of existing plan."""
        
        # Get pending changes for this session
        pending_changes = self.storage.get_session_pending_changes(session_id)
        
        if not pending_changes:
            return {
                "response": "I don't have any pending changes to refine. Could you describe what you'd like to do?",
                "intent": "refinement"
            }
        
        # Get the most recent pending change
        latest_change = pending_changes[-1]
        original_plan = latest_change.get("plan", {})
        
        # Refine the plan
        print(f"[CHATBOT] Refining plan: {latest_change['change_id']}")
        refined_plan = self.plan_generator.refine_plan(original_plan, user_message)
        
        # Update the pending change
        change_id = latest_change["change_id"]
        self.storage.save_pending_change(session_id, {
            "plan": refined_plan,
            "intent": latest_change["intent"],
            "user_request": latest_change["user_request"],
            "refinement_of": change_id
        })
        
        # Format response
        response_text = f"I've updated the plan based on your feedback:\n\n" + self._format_plan_response(refined_plan, change_id)
        
        return {
            "response": response_text,
            "intent": "refinement",
            "plan": refined_plan,
            "change_id": change_id,
            "requires_approval": True
        }
    
    def _handle_status_inquiry(self, session_id: str, user_message: str,
                               intent_data: Dict) -> Dict:
        """Handle status inquiry about implementations."""
        
        # Get pending changes
        pending_changes = self.storage.get_session_pending_changes(session_id)
        
        if not pending_changes:
            response = "You don't have any pending changes right now. What would you like me to help you with?"
        else:
            response = f"You have {len(pending_changes)} pending change(s):\n\n"
            for i, change in enumerate(pending_changes, 1):
                plan = change.get("plan", {})
                response += f"{i}. {plan.get('summary', 'Unnamed plan')} - Status: {change.get('status', 'pending')}\n"
        
        return {
            "response": response,
            "intent": "status_inquiry",
            "pending_changes": pending_changes
        }
    
    def _handle_general_question(self, session_id: str, user_message: str,
                                intent_data: Dict) -> Dict:
        """Handle general questions about the system."""
        
        # Simple FAQ-style responses
        message_lower = user_message.lower()
        
        if "what can" in message_lower or "help" in message_lower or "do" in message_lower:
            response = """I can help you with:
            
🔧 **Fix Bugs**: Detect and fix issues in your website
✨ **Add Features**: Implement new functionality
🎨 **Modify UI**: Change colors, layouts, fonts, and styling
📊 **Analyze Competitors**: See what features competitors have
📈 **Track Progress**: Check status of implementations

Just describe what you need in natural language, and I'll create a plan for you to review!"""
        else:
            response = "I'm your AI assistant for website maintenance. I can help you fix bugs, add features, modify UI, and analyze competitors. What would you like to do?"
        
        return {
            "response": response,
            "intent": "general_question"
        }
    
    def _format_clarification_response(self, intent_data: Dict) -> Dict:
        """Format response when clarification is needed."""
        
        questions = intent_data.get("clarification_questions", [])
        response = "I need a bit more information to help you with that:\n\n"
        for i, question in enumerate(questions, 1):
            response += f"{i}. {question}\n"
        
        return {
            "response": response,
            "intent": intent_data["intent"],
            "requires_clarification": True,
            "clarification_questions": questions
        }
    
    def _format_plan_response(self, plan: Dict, change_id: str) -> str:
        """Format plan as a user-friendly message."""
        
        response = f"**{plan.get('summary', 'Implementation Plan')}**\n\n"
        
        # Add steps
        steps = plan.get("steps", [])
        if steps:
            response += "**Steps:**\n"
            for step in steps:
                step_num = step.get("step_number", "")
                desc = step.get("description", "")
                response += f"{step_num}. {desc}\n"
            response += "\n"
        
        # Add effort and complexity
        effort = plan.get("estimated_effort", "Unknown")
        complexity = plan.get("complexity", "unknown")
        response += f"**Effort**: {effort} | **Complexity**: {complexity}\n\n"
        
        # Add affected files
        affected_files = plan.get("affected_files", [])
        if affected_files:
            response += f"**Affected Files**: {', '.join(affected_files[:5])}"
            if len(affected_files) > 5:
                response += f" and {len(affected_files) - 5} more"
            response += "\n\n"
        
        # Add risks
        risks = plan.get("risks", [])
        if risks:
            response += "**Risks**:\n"
            for risk in risks[:3]:
                response += f"- {risk}\n"
            response += "\n"
        
        response += "Would you like me to proceed with this plan? (Click Apply to confirm)"
        
        return response
    
    async def _detect_tech_stack(self) -> Dict:
        """
        Detect project tech stack and structure before generating plan.
        This ensures AI generates correct file types (.tsx vs .js) and paths.
        
        Returns:
            Dict with tech_stack, project_structure, and repo_path
        """
        try:
            from github_handler import clone_or_pull_repo
            from code_analyzer import CodeAnalyzer
            import os
            
            # Check if GITHUB_REPO is configured
            github_repo = os.getenv("GITHUB_REPO")
            if not github_repo:
                print("[CHATBOT] GITHUB_REPO not configured, skipping tech stack detection")
                return {}
            
            print("[CHATBOT] Cloning/pulling repository for tech stack analysis...")
            repo_path = clone_or_pull_repo()
            
            if not repo_path or not os.path.exists(repo_path):
                print(f"[CHATBOT] Repository not accessible: {repo_path}")
                return {}
            
            print(f"[CHATBOT] Analyzing codebase at {repo_path}...")
            analyzer = CodeAnalyzer(repo_path)
            analyzer.analyze_repository()
            
            summary = analyzer.get_codebase_summary()
            tech_stack = summary.get("tech_stack", {})
            structure = summary.get("project_structure", {})
            
            print(f"[CHATBOT] ✅ Detected: {tech_stack.get('framework', 'unknown')} + " +
                  f"{tech_stack.get('language', 'javascript')} in {structure.get('structure_type', 'unknown')}")
            
            return {
                "tech_stack": tech_stack,
                "project_structure": structure,
                "repo_path": repo_path
            }
            
        except Exception as e:
            print(f"[CHATBOT] Tech stack detection failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _get_welcome_message(self) -> str:
        """Get welcome message for new sessions."""
        
        return """👋 Hi! I'm your AI assistant for website maintenance and development.

I can help you with:
- 🔧 Fixing bugs and issues
- ✨ Adding new features
- 🎨 Modifying UI and styling
- 📊 Analyzing competitors
- 📈 Tracking implementation progress

Just tell me what you'd like to do, and I'll create a detailed plan for your approval!

**Example requests:**
- "Add dark mode to my website"
- "Fix accessibility issues"
- "Make the header blue and bigger"
- "Analyze my competitors and suggest features"

What would you like to work on today?"""


# Global instance
chatbot_manager = ChatbotManager()
