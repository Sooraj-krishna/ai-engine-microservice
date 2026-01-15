"""
Chatbot Intent Detector

Uses Gemini AI to detect user intent from natural language messages.
Categorizes requests and extracts relevant entities.
"""

import os
from typing import Dict, List, Optional
from model_router import _query_gemini_api


class IntentDetector:
    """Detects user intent from chat messages using AI."""
    
    # Intent categories
    FEATURE_REQUEST = "feature_request"
    BUG_FIX = "bug_fix"
    UI_CHANGE = "ui_change"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    STATUS_INQUIRY = "status_inquiry"
    GENERAL_QUESTION = "general_question"
    REFINEMENT = "refinement"
    
    def __init__(self):
        self.conversation_context = []
    
    def detect_intent(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Detect user intent from message.
        
        Args:
            user_message: User's message
            conversation_history: Previous conversation messages for context
            
        Returns:
            {
                "intent": str,
                "confidence": float,
                "entities": dict,
                "requires_clarification": bool,
                "clarification_questions": list
            }
        """
        # Build prompt for intent detection
        prompt = self._build_intent_detection_prompt(user_message, conversation_history)
        
        try:
            # Query Gemini for intent detection
            messages = [{"role": "user", "content": prompt}]
            print(f"[INTENT_DETECTOR] Calling Gemini for intent detection...")
            gemini_response = _query_gemini_api(messages=messages, timeout=30)
            
            print(f"[INTENT_DETECTOR] Gemini response keys: {gemini_response.keys()}")
            
            # Check for error in response
            if "error" in gemini_response:
                print(f"[INTENT_DETECTOR] Error in Gemini response: {gemini_response['error']}")
                return self._fallback_intent_detection(user_message)
            
            # Extract text from Gemini response (model_router returns 'content' not 'response')
            gemini_text = gemini_response.get("content") or gemini_response.get("response", "")
            if not gemini_text:
                print(f"[INTENT_DETECTOR] Empty response from Gemini, using fallback")
                return self._fallback_intent_detection(user_message)
                
            print(f"[INTENT_DETECTOR] Gemini response text (first 200 chars): {gemini_text[:200]}")
            intent_data = self._parse_intent_response(gemini_text)
            
            print(f"[INTENT_DETECTOR] Detected intent: {intent_data['intent']} (confidence: {intent_data['confidence']})")
            return intent_data
            
        except RuntimeError as e:
            print(f"[INTENT_DETECTOR] Runtime error from Gemini: {e}")
            return self._fallback_intent_detection(user_message)
            
        except Exception as e:
            print(f"[INTENT_DETECTOR] Exception: {e}")
            return self._fallback_intent_detection(user_message)
    
    def _build_intent_detection_prompt(self, user_message: str, 
                                      conversation_history: List[Dict] = None) -> str:
        """Build prompt for intent detection."""
        
        context = ""
        if conversation_history and len(conversation_history) > 0:
            context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role.upper()}: {content}\n"
        
        prompt = f"""You are an intent detection system for an AI-powered website maintenance chatbot.

Analyze the user's message and determine their intent. Classify it into one of these categories:

1. **feature_request**: User wants to add a new feature to their website
2. **bug_fix**: User reports a bug or wants automated bug detection
3. **ui_change**: User wants to modify UI elements (colors, sizes, layout, etc.)
4. **competitive_analysis**: User wants insights about competitor websites
5. **status_inquiry**: User asks about implementation status or progress
6. **general_question**: General questions about the system or capabilities
7. **refinement**: User is refining/iterating on a previous request (e.g., "make it bigger", "change color to blue")

{context}

Current user message: "{user_message}"

Respond with ONLY a JSON object in this exact format (no markdown, no additional text):
{{
    "intent": "category_name",
    "confidence": 0.95,
    "entities": {{
        "feature_type": "extracted feature if applicable",
        "ui_element": "extracted UI element if applicable",
        "priority": "high/medium/low if mentioned",
        "details": "any additional extracted details"
    }},
    "requires_clarification": false,
    "clarification_questions": []
}}

If the request is ambiguous, set requires_clarification to true and provide relevant questions.
"""
        return prompt
    
    def _parse_intent_response(self, response: str) -> Dict:
        """Parse Gemini's intent detection response."""
        import json
        import re
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            response = re.sub(r'```json\s*', '', response)
            response = re.sub(r'```\s*', '', response)
            response = response.strip()
            
            # Parse JSON
            intent_data = json.loads(response)
            
            # Validate required fields
            if "intent" not in intent_data:
                raise ValueError("Missing 'intent' field")
            
            # Set defaults
            intent_data.setdefault("confidence", 0.8)
            intent_data.setdefault("entities", {})
            intent_data.setdefault("requires_clarification", False)
            intent_data.setdefault("clarification_questions", [])
            
            return intent_data
            
        except Exception as e:
            print(f"[INTENT_DETECTOR] Failed to parse response: {e}")
            print(f"[INTENT_DETECTOR] Raw response: {response}")
            return self._fallback_intent_detection(response)
    
    def _fallback_intent_detection(self, user_message: str) -> Dict:
        """Fallback rule-based intent detection when AI fails."""
        
        message_lower = user_message.lower()
        
        # Rule-based intent detection
        if any(keyword in message_lower for keyword in ["add", "create", "implement", "feature", "functionality"]):
            intent = self.FEATURE_REQUEST
            confidence = 0.6
        elif any(keyword in message_lower for keyword in ["fix", "bug", "error", "broken", "issue", "problem"]):
            intent = self.BUG_FIX
            confidence = 0.6
        elif any(keyword in message_lower for keyword in ["color", "size", "font", "layout", "style", "css", "ui", "design"]):
            intent = self.UI_CHANGE
            confidence = 0.6
        elif any(keyword in message_lower for keyword in ["competitor", "competition", "analyze", "compare"]):
            intent = self.COMPETITIVE_ANALYSIS
            confidence = 0.6
        elif any(keyword in message_lower for keyword in ["status", "progress", "how is", "what's the"]):
            intent = self.STATUS_INQUIRY
            confidence = 0.6
        else:
            intent = self.GENERAL_QUESTION
            confidence = 0.5
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": {},
            "requires_clarification": False,
            "clarification_questions": [],
            "fallback_used": True
        }


# Global instance
intent_detector = IntentDetector()
