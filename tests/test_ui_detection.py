"""Test script to verify UI library detection in prompt generation"""
import sys
sys.path.insert(0, '/home/devils_hell/ai-engine-microservice/src')

from chatbot_plan_generator import plan_generator

# Mock tech stack context as if called from chatbot_manager
tech_stack_context = {
    "tech_stack": {
        "framework": "nextjs",
        "language": "typescript"
    },
    "project_structure": {
        "top_code_directories": [
            "ai-engine-ui/src/components",
            "ai-engine-ui/src/app"
        ]
    },
    "repo_path": "/home/devils_hell/ai-engine-microservice/ai-engine-ui"
}

# Build a test prompt
prompt = plan_generator._build_plan_prompt(
    intent="feature_request",
    user_message="create a profile page with user information",
    entities={"type": "page", "name": "profile"},
    tech_stack_context=tech_stack_context
)

# Check if UI library info is in the prompt
print("=" * 80)
print("TESTING UI LIBRARY DETECTION IN PROMPT")
print("=" * 80)

if "shadcn/ui" in prompt:
    print("✓ SUCCESS: shadcn/ui detected in prompt")
else:
    print("✗ FAIL: shadcn/ui NOT found in prompt")

if "@/components/ui/button" in prompt:
    print("✓ SUCCESS: Correct Button import pattern found")
else:
    print("✗ FAIL: Button import pattern NOT found")

if "@mui/material" in prompt and "DO NOT use Material-UI" in prompt:
    print("✓ SUCCESS: Material-UI warning present")
else:
    print("✗ FAIL: Material-UI warning NOT found")

if "lucide-react" in prompt:
    print("✓ SUCCESS: lucide-react icon library mentioned")
else:
    print("✗ FAIL: lucide-react NOT mentioned")

print("\n" + "=" * 80)
print("PROMPT EXCERPT (UI Library Section):")
print("=" * 80)

# Extract and display the UI library section
if "===== CRITICAL: UI LIBRARY REQUIREMENTS =====" in prompt:
    start = prompt.find("===== CRITICAL: UI LIBRARY REQUIREMENTS =====")
    end = prompt.find("=============================================", start) + 45
    print(prompt[start:end])
else:
    print("UI library section not found in prompt!")

print("\n" + "=" * 80)
