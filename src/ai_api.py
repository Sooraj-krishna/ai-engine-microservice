"""
AI API client for dynamic code generation.
Uses Gemini API exclusively.
"""

import os
from typing import Dict, Any

from model_router import ask

def query_codegen_api(prompt, language="python"):
    """
    Query Gemini API for intelligent code generation.
    """
    return query_gemini_codegen(prompt, language)

def _build_prompt(prompt, language):
    """Build a consistent prompt."""
    return f"""
You are an expert software developer. Generate clean, production-ready {language} code for the following task:

TASK: {prompt}

REQUIREMENTS:
- Write clean, maintainable code
- Include helpful comments
- Follow best practices for {language}
- Make the code ready to use in a real project
- If it's a React/JavaScript component, make it functional and modern
- If it's Python, use proper error handling
- Return ONLY the code, no explanations or markdown

CODE:
"""
        
def query_gemini_codegen(prompt, language="python"):
    """Generate code using Gemini API."""
    try:
        messages = [
            {"role": "system", "content": "You are a helpful AI developer that returns only code."},
            {"role": "user", "content": _build_prompt(prompt, language)},
        ]
        result: Dict[str, Any] = ask(
            messages=messages,
            min_context=8000 if language.lower() in ("javascript", "typescript") else 4000,
        )
        generated_code = (result.get("content") or "").strip()
        
        # Clean up common formatting issues
        if generated_code.startswith("```"):
            lines = generated_code.split("\n")
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            generated_code = "\n".join(lines)
        
        model_used = result.get('model_used', 'unknown')
        print(f"[SUCCESS] Generated {len(generated_code)} chars of {language} code using {model_used}")
        return generated_code
        
    except Exception as e:
        raise Exception(f"Gemini API Error: {str(e)}")

def test_gemini_connection():
    """Test if Gemini API is working correctly."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[ERROR] Gemini API key not configured")
            return False

        messages = [{"role": "user", "content": "Respond with 'hello'"}]
        result = ask(messages=messages, min_context=2000)
        if result and result.get("content"):
            print(f"[SUCCESS] Gemini API connection successful via {result.get('model_used')}")
            return True
            print("[ERROR] Gemini API returned empty response")
            return False
    except Exception as e:
        print(f"[ERROR] Gemini API connection failed: {e}")
        return False
