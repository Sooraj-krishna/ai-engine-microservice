import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from canary_tester import canary_tester

async def test_suites():
    print("Testing Canary Test Suites...")
    
    # Test default_suite against localhost (assuming it's running)
    # If not running, it should fail gracefully
    target_url = "http://localhost:3000"
    
    print(f"\n[TEST] Running default_suite against {target_url}")
    results = await canary_tester.run_test_suite("default_suite", target_url)
    
    print("\n[RESULTS]")
    print(f"Suite: {results.get('suite_name')}")
    print(f"Overall Success: {results.get('success')}")
    for check in results.get("checks", []):
        status = "✅" if check["success"] else "❌"
        print(f" {status} {check['name']} ({check['type']})")
        if not check["success"]:
            print(f"    Error: {check.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_suites())
