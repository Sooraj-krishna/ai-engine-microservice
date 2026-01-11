"""
Prompt Optimizer - Compresses and optimizes AI prompts for efficiency.
"""

import re
from typing import Dict


class PromptOptimizer:
    """Optimizes AI prompts to reduce tokens and improve efficiency."""
    
    # Compressed prompt templates
    TEMPLATES = {
        "bug_analysis": """Analyze code for bugs.
File: {file}
Code: {code}
Context: {context}
Return JSON: {{"bugs":[{{"type":"","line":0,"severity":"","description":"","fix_suggestion":""}}]}}""",
        
        "fix_generation": """Fix bug in code.
Bug: {bug_description}
Location: Line {line}
Code:
{code}
Return fixed code only, no explanations.""",
        
        "code_validation": """Validate code safety.
Code: {code}
Check: syntax, dangerous patterns, logic errors
Return JSON: {{"safe":true/false,"issues":[]}}""",
        
        "feature_extraction": """Extract features from {url}.
Return JSON: {{"ui_components":[{{"name":"","type":""}}],"ux_patterns":[...]}}
Focus on UX/functionality enhancements.""",
        
        "seo_analysis": """Analyze SEO for {url}.
Return JSON: {{"score":0-100,"meta":{{"title":"","desc":""}},"og":{{}},"issues":[]}}""",
        
        "accessibility_check": """Check accessibility.
HTML: {html}
Return JSON: {{"score":0-100,"aria":{{}},"semantic":{{}},"issues":[{{"level":"A/AA/AAA","issue":""}}]}}"""
    }
    
    # Few-shot examples for better output quality
    EXAMPLES = {
        "bug_analysis": """Example:
Input: function add(a,b){return a+b}
Output: {{"bugs":[{{"type":"missing_validation","line":1,"severity":"medium","description":"No input validation","fix_suggestion":"Add type checking"}}]}}""",
        
        "feature_extraction": """Example:
Input: E-commerce site screenshot
Output: {{"ui_components":[{{"name":"Product Grid","type":"grid"}},{{"name":"Search Bar","type":"input"}}],"ux_patterns":[{{"name":"Quick View","type":"modal"}}]}}"""
    }
    
    def __init__(self):
        self.compression_stats = {
            "original_tokens": 0,
            "compressed_tokens": 0,
            "savings_percentage": 0
        }
    
    def optimize_prompt(self, template_name: str, **kwargs) -> str:
        """
        Optimize a prompt using templates and compression.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Variables to fill in the template
            
        Returns:
            Optimized prompt string
        """
        if template_name not in self.TEMPLATES:
            # Fallback to basic compression
            return self._compress_generic_prompt(kwargs.get("prompt", ""))
        
        # Use template
        template = self.TEMPLATES[template_name]
        
        # Add few-shot example if available
        if template_name in self.EXAMPLES and kwargs.get("include_example", True):
            template = self.EXAMPLES[template_name] + "\n\n" + template
        
        # Fill template
        prompt = template.format(**kwargs)
        
        # Track compression stats
        original_length = len(kwargs.get("original_prompt", prompt))
        compressed_length = len(prompt)
        
        self.compression_stats["original_tokens"] += original_length
        self.compression_stats["compressed_tokens"] += compressed_length
        
        if self.compression_stats["original_tokens"] > 0:
            savings = (1 - self.compression_stats["compressed_tokens"] / self.compression_stats["original_tokens"]) * 100
            self.compression_stats["savings_percentage"] = round(savings, 1)
        
        return prompt
    
    def _compress_generic_prompt(self, prompt: str) -> str:
        """Compress a generic prompt by removing unnecessary words."""
        # Remove extra whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        
        # Remove filler words
        filler_words = [
            r'\bplease\b', r'\bkindly\b', r'\bthank you\b',
            r'\bI would like\b', r'\bCould you\b', r'\bWould you\b'
        ]
        for filler in filler_words:
            prompt = re.sub(filler, '', prompt, flags=re.IGNORECASE)
        
        # Compress common phrases
        replacements = {
            "Return a JSON object with": "Return JSON:",
            "Provide a detailed": "Provide",
            "Make sure to": "",
            "It is important that": "",
            "Focus on identifying": "Identify"
        }
        
        for old, new in replacements.items():
            prompt = prompt.replace(old, new)
        
        # Clean up
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        return prompt
    
    def get_stats(self) -> Dict:
        """Get compression statistics."""
        return {
            **self.compression_stats,
            "estimated_cost_savings": f"{self.compression_stats['savings_percentage']}%"
        }
    
    def reset_stats(self) -> None:
        """Reset compression statistics."""
        self.compression_stats = {
            "original_tokens": 0,
            "compressed_tokens": 0,
            "savings_percentage": 0
        }


# Global prompt optimizer instance
prompt_optimizer = PromptOptimizer()
