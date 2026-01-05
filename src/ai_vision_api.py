"""
AI API wrapper for Gemini Vision API
"""

import google.generativeai as genai
import os
import base64
from typing import Optional


async def query_gemini_vision_api(prompt: str, image_b64: str) -> Optional[str]:
    """
    Query Gemini Vision API with text and image.
    
    Args:
        prompt: Text prompt for the AI
        image_b64: Base64 encoded image
        
    Returns:
        AI response text or None if failed
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("[ERROR] GEMINI_API_KEY not found")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Decode base64 image
        image_data = base64.b64decode(image_b64)
        
        # Create image part
        image_part = {
            'mime_type': 'image/png',
            'data': image_data
        }
        
        # Generate content
        response = model.generate_content([prompt, image_part])
        
        return response.text
        
    except Exception as e:
        print(f"[ERROR] Gemini Vision API call failed: {e}")
        return None
