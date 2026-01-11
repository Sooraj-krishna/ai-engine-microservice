"""
Gemini API router for code generation.
Uses Gemini as the primary and only AI API.
"""

import os
from typing import List, Dict, Any

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Default to gemini-pro which is more widely available
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-pro")


def _get_available_models():
    """List available Gemini models and return the first one that supports generateContent."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # List all available models
        models = genai.list_models()
        available = []
        for m in models:
            # Check if model supports generateContent
            if 'generateContent' in m.supported_generation_methods:
                available.append(m.name.replace('models/', ''))
        
        return available
    except Exception as e:
        print(f"[ModelRouter] Could not list models: {e}")
        return []


def _query_gemini_api(
    messages: List[Dict[str, str]],
    model: str = None,
    timeout: int = 60,
) -> Dict[str, Any]:
    """
    Query Gemini API directly.
    Returns dict: { model_used, fallbacks_attempted, content, raw_response }
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not configured")
    
    try:
        import google.generativeai as genai
        from google.generativeai.types import HarmCategory, HarmBlockThreshold
    except ImportError:
        raise RuntimeError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Select model based on context size
    selected_model = model or GEMINI_MODEL
    
    # Get available models first
    available_models = _get_available_models()
    if available_models:
        print(f"[ModelRouter] Available models: {', '.join(available_models[:5])}...")
    
    # Convert messages format for Gemini
    # Gemini expects a single prompt or a list of Content objects
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System: {content}\n")
        elif role == "user":
            prompt_parts.append(f"User: {content}\n")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}\n")
    
    full_prompt = "".join(prompt_parts)
    
    # Build list of models to try
    # Priority: selected model -> available models -> common fallbacks
    models_to_try = [selected_model]
    
    # Add available models that match our preference
    if available_models:
        # Prefer models with "pro" or "flash" in name, or just use first available
        preferred_available = [m for m in available_models if "pro" in m.lower() or "flash" in m.lower()]
        if preferred_available:
            models_to_try.extend([m for m in preferred_available if m not in models_to_try])
        else:
            models_to_try.extend([m for m in available_models[:3] if m not in models_to_try])
    
    # Add common fallbacks as last resort
    common_fallbacks = ["gemini-pro", "gemini-1.5-pro", "gemini-1.5-flash", "models/gemini-pro"]
    models_to_try.extend([m for m in common_fallbacks if m not in models_to_try])
    
    last_error = None
    for model_name in models_to_try:
        try:
            # Remove 'models/' prefix if present
            clean_model_name = model_name.replace('models/', '')
            model_instance = genai.GenerativeModel(clean_model_name)
            
            # Configure safety settings to allow code generation
            safety_settings = {
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generate content with Gemini
            response = model_instance.generate_content(
                full_prompt,
                safety_settings=safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    top_p=0.8,
                    max_output_tokens=8192,  # Increased from 2048 to allow complete code responses
                )
            )
            
            content = response.text.strip() if response.text else ""
            
            if clean_model_name != selected_model:
                print(f"[ModelRouter] Successfully used model: {clean_model_name} (requested: {selected_model})")
            
            return {
                "model_used": f"gemini:{clean_model_name}",
                "fallbacks_attempted": [f"gemini:{m.replace('models/', '')}" for m in models_to_try[:models_to_try.index(model_name) + 1]],
                "content": content,
                "raw_response": {"text": content, "model": clean_model_name},
            }
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if "404" in error_str or "not found" in error_str or "not supported" in error_str:
                # Try next alternative
                print(f"[ModelRouter] Model {model_name} not available, trying next...")
                continue
            else:
                # Other error, don't retry
                raise RuntimeError(f"Gemini API error: {str(e)}")
    
    # All models failed
    error_msg = f"Gemini API error: All model alternatives failed. Last error: {str(last_error)}"
    if available_models:
        error_msg += f"\nAvailable models: {', '.join(available_models[:10])}"
    raise RuntimeError(error_msg)


def ask(
    *,
    messages: List[Dict[str, str]],
    min_context: int = 8000,
    preferred_models: List[str] | None = None,
    enable_free_fallback: bool | None = None,
    timeout: int = 60,
    prefer_gemini: bool | None = None,
) -> Dict[str, Any]:
    """
    Query Gemini API for code generation.
    Uses Gemini Pro for large contexts (100k+ tokens), Flash otherwise.
    Returns dict: { model_used, fallbacks_attempted, content, raw_response }
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("Gemini API key not configured")
    
    # Use Pro model for very large contexts, Flash for normal
    gemini_model = GEMINI_PRO_MODEL if min_context >= 100000 else GEMINI_MODEL
    print(f"[ModelRouter] Using Gemini ({gemini_model}) for context: {min_context} tokens")
    
    return _query_gemini_api(messages, model=gemini_model, timeout=timeout)
