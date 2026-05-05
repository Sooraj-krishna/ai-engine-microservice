#!/usr/bin/env python3
"""
Quick test script to verify debug logging works
This will trigger code generation and create debug files
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv('src/.env')  # Load from src/.env
load_dotenv('.env')       # Also try root .env

# Set environment variables to ensure debug mode is on
os.environ['SAVE_RAW_GENERATED_CODE'] = 'true'
os.environ['SAVE_VALIDATION_DEBUG'] = 'true'

# Verify API key is loaded
if not os.getenv('GEMINI_API_KEY'):
    print("❌ Error: GEMINI_API_KEY not found in environment")
    print("   Please check src/.env or .env file")
    sys.exit(1)

print("=" * 70)
print("Testing Code Generation Debug Mode")
print("=" * 70)
print()

# Test 1: Import and test AI API
print("Test 1: Testing AI API code generation...")
print("-" * 70)

try:
    from ai_api import query_codegen_api
    
    # Generate a simple function
    prompt = "Create a simple JavaScript function called 'greet' that takes a name parameter and returns 'Hello, ' + name"
    
    print(f"Prompt: {prompt}")
    print()
    print("Calling Gemini API...")
    
    result = query_codegen_api(prompt, language="javascript")
    
    print()
    print("✅ Code generation successful!")
    print()
    print("Generated code:")
    print("-" * 70)
    print(result)
    print("-" * 70)
    print()
    
    # Check if debug file was created
    import glob
    raw_files = glob.glob("data/raw_generated_code/raw_code_*.json")
    if raw_files:
        latest_raw = max(raw_files, key=os.path.getmtime)
        print(f"✅ Debug file created: {latest_raw}")
        print()
        print("You can now view it with:")
        print(f"  cat {latest_raw}")
        print("  or")
        print("  ./view_debug.sh")
    else:
        print("⚠️  No debug file found (check SAVE_RAW_GENERATED_CODE environment variable)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 2: Test validation
print("Test 2: Testing validation with debug logging...")
print("-" * 70)

try:
    from validator import CodeValidator
    
    validator = CodeValidator()
    
    # Create a test fix
    test_fix = {
        "path": "utils/ai-test.js",
        "content": result,
        "description": "Test fix for debug mode",
        "bug": {"type": "test", "description": "Testing debug mode"}
    }
    
    # Validate it
    fixes = [test_fix]
    safe_fixes = validator.validate_all_fixes(fixes)
    
    print()
    if safe_fixes:
        print(f"✅ Validation passed! {len(safe_fixes)} fix(es) approved")
    else:
        print("⚠️  Validation rejected the fix (this is OK for testing)")
    
    # Check if validation debug file was created
    val_files = glob.glob("data/validation_results/validation_*.json")
    if val_files:
        latest_val = max(val_files, key=os.path.getmtime)
        print()
        print(f"✅ Validation debug file created: {latest_val}")
        print()
        print("You can view it with:")
        print(f"  cat {latest_val}")
        print("  or")
        print("  ./view_debug.sh validation")
    else:
        print("⚠️  No validation debug file found")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 70)
print("✅ Test Complete!")
print("=" * 70)
print()
print("Next steps:")
print("1. View debug files: ./view_debug.sh")
print("2. View only raw code: ./view_debug.sh raw")
print("3. View only validation: ./view_debug.sh validation")
print("4. Or use Python viewer: python3 view_debug.py")
print()
print("Debug file locations:")
print(f"  Raw code: data/raw_generated_code/")
print(f"  Validation: data/validation_results/")
