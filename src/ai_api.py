"""
AI API client for dynamic code generation.
Uses Gemini API exclusively with caching and prompt optimization.
"""

import os
from typing import Dict, Any

from model_router import ask
from ai_cache import ai_cache
from prompt_optimizer import prompt_optimizer

def query_codegen_api(prompt, language="python"):
    """
    Query Gemini API for intelligent code generation with caching.
    """
    return query_gemini_codegen(prompt, language)

def _build_prompt(prompt, language):
    """Build an optimized prompt using prompt optimizer."""
    # Try to use optimized template
    try:
        optimized = prompt_optimizer.optimize_prompt(
            "fix_generation",
            bug_description=prompt,
            line=0,
            code="",
            original_prompt=f"""
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
        )
        return optimized
    except:
        # Fallback to standard prompt
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
    """Generate code using Gemini API with caching."""
    try:
        # Check cache first
        cache_key = f"{language}:{prompt}"
        cached_response = ai_cache.get(cache_key, model="codegen")
        if cached_response:
            print(f"[AI_CACHE] Using cached code generation")
            return cached_response
        
        messages = [
            {"role": "system", "content": "You are a helpful AI developer that returns only code."},
            {"role": "user", "content": _build_prompt(prompt, language)},
        ]
        result: Dict[str, Any] = ask(
            messages=messages,
            min_context=8000 if language.lower() in ("javascript", "typescript") else 4000,
        )
        generated_code = (result.get("content") or "").strip()
        
        # SAVE RAW GENERATED CODE FOR DEBUGGING (before any processing)
        save_raw_generated_code = os.getenv('SAVE_RAW_GENERATED_CODE', 'true').lower() == 'true'
        if save_raw_generated_code:
            try:
                import json
                from datetime import datetime
                from pathlib import Path
                
                # Use absolute path - go up from src/ to project root
                project_root = Path(__file__).parent.parent
                debug_folder = project_root / "data" / "raw_generated_code"
                debug_folder.mkdir(parents=True, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                debug_file = debug_folder / f"raw_code_{timestamp}.json"
                
                debug_data = {
                    "timestamp": datetime.now().isoformat(),
                    "language": language,
                    "prompt": prompt[:500] + "..." if len(prompt) > 500 else prompt,
                    "model_used": result.get('model_used', 'unknown'),
                    "raw_response": result.get("content") or "",
                    "processed_code": generated_code,
                    "code_length": len(generated_code),
                    "has_markdown": "```" in (result.get("content") or "")
                }
                
                with open(debug_file, 'w', encoding='utf-8') as f:
                    json.dump(debug_data, f, indent=2)
                
                print(f"[DEBUG] Saved raw generated code to: {debug_file}")
            except Exception as debug_error:
                print(f"[WARNING] Failed to save raw generated code: {debug_error}")
                import traceback
                print(f"[DEBUG] Traceback: {traceback.format_exc()}")
        
        # Clean up common formatting issues
        if generated_code.startswith("```"):
            lines = generated_code.split("\n")
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            generated_code = "\n".join(lines)
        
        # Cache the response
        ai_cache.set(cache_key, generated_code, model="codegen")
        
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
