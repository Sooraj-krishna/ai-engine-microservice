"""Test script to verify import alias detection"""
import sys
sys.path.insert(0, '/home/devils_hell/ai-engine-microservice/src')

from chatbot_plan_generator import plan_generator

# Test with a real client repo path (will be populated when chatbot runs)
test_repo_path = "/home/devils_hell/ai-engine-microservice/ai-engine-ui"

print("=" * 80)
print("TESTING IMPORT ALIAS DETECTION")
print("=" * 80)

# Test detection
aliases = plan_generator._detect_import_aliases(test_repo_path)
print(f"\nDetected aliases: {aliases}")

if "@" in aliases:
    print("✓ SUCCESS: @ alias detected")
else:
    print("✗ FAIL: @ alias NOT detected")

# Test prompt integration
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
    "repo_path": test_repo_path
}

prompt = plan_generator._build_plan_prompt(
    intent="feature_request",
    user_message="create a contact page",
    entities={"type": "page", "name": "contact"},
    tech_stack_context=tech_stack_context
)

print("\n" + "=" * 80)
print("CHECKING PROMPT INTEGRATION")
print("=" * 80)

if "IMPORT PATH REQUIREMENTS" in prompt:
    print("✓ SUCCESS: Import path section found in prompt")
else:
    print("✗ FAIL: Import path section NOT in prompt")

if "DO NOT use incorrect aliases" in prompt:
    print("✓ SUCCESS: Warning about incorrect aliases present")
else:
    print("✗ FAIL: Warning NOT present")

# Extract and display the import alias section
if "===== CRITICAL: IMPORT PATH REQUIREMENTS =====" in prompt:
    start = prompt.find("===== CRITICAL: IMPORT PATH REQUIREMENTS =====")
    end = prompt.find("=============================================", start) + 45
    print("\n" + "=" * 80)
    print("PROMPT EXCERPT (Import Alias Section):")
    print("=" * 80)
    print(prompt[start:end])
else:
    print("\nImport alias section not found!")

print("\n" + "=" * 80)
