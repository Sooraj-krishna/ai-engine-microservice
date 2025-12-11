"""
AI API client for dynamic code generation.
Uses OpenRouter as the sole backend.
"""

import os
from typing import Dict, Any

from model_router import ask

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def query_codegen_api(prompt, language="python"):
    """
    Query OpenRouter for intelligent code generation with automatic model selection.
    """
    return query_openrouter_codegen(prompt, language)

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

def query_openrouter_codegen(prompt, language="python"):
    """Generate code using OpenRouter with model auto-selection and fallback."""
    if not OPENROUTER_API_KEY:
        raise Exception("OpenRouter API key not configured")

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

        print(f"[SUCCESS] OpenRouter generated {len(generated_code)} chars of {language} code using {result.get('model_used')}")
        return generated_code

    except Exception as e:
        raise Exception(f"OpenRouter API Error: {str(e)}")

def test_openrouter_connection():
    """Test if OpenRouter API is working correctly."""
    try:
        if not OPENROUTER_API_KEY:
            print("[ERROR] OpenRouter API key not configured")
            return False

        messages = [{"role": "user", "content": "Respond with 'hello'"}]
        result = ask(messages=messages, min_context=2000)
        if result and result.get("content"):
            print(f"[SUCCESS] OpenRouter API connection successful via {result.get('model_used')}")
            return True
        print("[ERROR] OpenRouter API returned empty response")
        return False
    except Exception as e:
        print(f"[ERROR] OpenRouter API connection failed: {e}")
        return False
