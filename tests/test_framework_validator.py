"""
Tests for FrameworkValidator.
Verifies Next.js and Vite specific validation rules.
"""

import sys
import os
from pathlib import Path

# Add src to path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from framework_validator import framework_validator

def test_nextjs_use_client_validation():
    print("\nTesting Next.js 'use client' validation...")
    
    # Page using useState without 'use client'
    bad_page = """
import { useState } from 'react';

export default function Page() {
    const [count, setCount] = useState(0);
    return <div>{count}</div>;
}
    """
    
    issues = framework_validator._validate_nextjs_rules("app/components/Counter.tsx", bad_page)
    assert any(issue['type'] == 'missing_use_client' for issue in issues)
    print("✅ Correctly identified missing 'use client'")

    # Page using useState WITH 'use client'
    good_page = """'use client';
import { useState } from 'react';

export default function Page() {
    const [count, setCount] = useState(0);
    return <div>{count}</div>;
}
    """
    issues = framework_validator._validate_nextjs_rules("app/components/Counter.tsx", good_page)
    assert not any(issue['type'] == 'missing_use_client' for issue in issues)
    print("✅ Correctly identified valid 'use client' usage")

def test_nextjs_default_export_validation():
    print("\nTesting Next.js default export validation...")
    
    # page.tsx without default export
    bad_page = """
export function Page() {
    return <div>Hello</div>;
}
    """
    issues = framework_validator._validate_nextjs_rules("app/dashboard/page.tsx", bad_page)
    assert any(issue['type'] == 'missing_default_export' for issue in issues)
    print("✅ Correctly identified missing default export in page.tsx")

def test_vite_env_validation():
    print("\nTesting Vite env validation...")
    
    # File using process.env
    bad_code = """
const apiKey = process.env.VITE_API_KEY;
    """
    issues = framework_validator._validate_vite_rules("src/api.ts", bad_code)
    assert any(issue['type'] == 'vite_env_usage' for issue in issues)
    print("✅ Correctly identified process.env usage in Vite")

def test_vite_jsx_extension_validation():
    print("\nTesting Vite JSX extension validation...")
    
    # .ts file containing JSX
    bad_code = """
export const Component = () => <div>Hello</div>;
    """
    issues = framework_validator._validate_vite_rules("src/Component.ts", bad_code)
    assert any(issue['type'] == 'vite_extension_mismatch' for issue in issues)
    print("✅ Correctly identified JSX in .ts file for Vite")

if __name__ == "__main__":
    try:
        test_nextjs_use_client_validation()
        test_nextjs_default_export_validation()
        test_vite_env_validation()
        test_vite_jsx_extension_validation()
        print("\n🎉 All framework validation tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)
