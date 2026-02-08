import os
import asyncio
import time
import json
import httpx
from pathlib import Path
from playwright.async_api import async_playwright

class CanaryTester:
    def __init__(self, timeout=30000):
        self.timeout = timeout
        self.suites_dir = Path(__file__).parent / "canary_suites"

    def _load_suite(self, suite_name: str):
        """Load a test suite from JSON file."""
        suite_path = self.suites_dir / f"{suite_name}.json"
        if not suite_path.exists():
            print(f"[CANARY] [WARNING] Suite {suite_name} not found at {suite_path}")
            return None
        
        try:
            with open(suite_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[CANARY] [ERROR] Failed to load suite {suite_name}: {e}")
            return None

    async def run_test_suite(self, suite_name: str, target_base_url: str):
        """Run a full test suite containing multiple checks."""
        suite = self._load_suite(suite_name)
        if not suite:
            # Fallback to basic smoke test if suite doesn't exist
            return await self.run_smoke_test(target_base_url)

        print(f"[CANARY] Running suite '{suite_name}' against {target_base_url}...")
        results = {
            "suite_name": suite_name,
            "success": True,
            "checks": [],
            "timestamp": time.time()
        }

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_page()
            
            for check in suite.get("checks", []):
                check_type = check.get("type")
                check_name = check.get("name", "Unnamed check")
                print(f"[CANARY]  -> Running {check_type}: {check_name}")
                
                check_result = {"name": check_name, "type": check_type, "success": False}
                
                try:
                    path = check.get("path", "")
                    if path.startswith("http"):
                        url = path
                    else:
                        url = f"{target_base_url.rstrip('/')}/{path.lstrip('/')}"
                    
                    if check_type == "ui_exists":
                        await context.goto(url, timeout=self.timeout)
                        selector = check.get("selector")
                        count = await context.locator(selector).count()
                        if count > 0:
                            check_result["success"] = True
                        else:
                            check_result["error"] = f"Selector '{selector}' not found on {url}"

                    elif check_type == "ui_text":
                        await context.goto(url, timeout=self.timeout)
                        selector = check.get("selector")
                        expected_text = check.get("text", "")
                        text_content = await context.locator(selector).text_content()
                        if expected_text in (text_content or ""):
                            check_result["success"] = True
                        else:
                            check_result["error"] = f"Text '{expected_text}' not found in '{selector}'"

                    elif check_type == "api_health":
                        async with httpx.AsyncClient() as client:
                            response = await client.get(url, timeout=10.0)
                            if response.status_code == check.get("expected_status", 200):
                                check_result["success"] = True
                                # Optional JSON field check
                                expected_json = check.get("expected_json", {})
                                if expected_json:
                                    actual_json = response.json()
                                    for key, val in expected_json.items():
                                        if actual_json.get(key) != val:
                                            check_result["success"] = False
                                            check_result["error"] = f"JSON mismatch for {key}: expected {val}, got {actual_json.get(key)}"
                                            break
                            else:
                                check_result["error"] = f"Status code {response.status_code} != {check.get('expected_status', 200)}"

                except Exception as e:
                    check_result["error"] = str(e)
                
                results["checks"].append(check_result)
                if not check_result["success"]:
                    results["success"] = False

            await browser.close()

        if results["success"]:
            print(f"[CANARY] ✅ Suite '{suite_name}' passed!")
        else:
            errors = [c.get("error") for c in results["checks"] if not c["success"]]
            print(f"[CANARY] ❌ Suite '{suite_name}' failed: {errors}")

        return results

    async def run_smoke_test(self, url: str):
        """
        Run a basic smoke test against the provided URL.
        Checks for:
        1. Page load success (2xx/3xx status)
        2. Basic rendering (at least one H1 or main tag)
        """
        print(f"[CANARY] Starting smoke test for {url}...")
        results = {
            "url": url,
            "success": False,
            "errors": [],
            "timestamp": time.time()
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Navigate to URL
                response = await page.goto(url, timeout=self.timeout)
                
                if not response:
                    results["errors"].append("Failed to get response from URL")
                elif response.status >= 400:
                    results["errors"].append(f"Server returned error status: {response.status}")
                else:
                    # Basic rendering check
                    h1_count = await page.locator("h1").count()
                    body_content = await page.content()
                    
                    if h1_count == 0 and len(body_content) < 500:
                        results["errors"].append("Page seems empty or failed to render")

                await browser.close()
                
                if not results["errors"]:
                    results["success"] = True
                    print(f"[CANARY] ✅ Smoke test passed for {url}")
                else:
                    print(f"[CANARY] ❌ Smoke test failed for {url}: {results['errors']}")
                    
        except Exception as e:
            results["errors"].append(f"Canary test execution failed: {str(e)}")
            print(f"[CANARY] [ERROR] {e}")

        return results

# Singleton instance
canary_tester = CanaryTester()

if __name__ == "__main__":
    # Test local
    async def main():
        tester = CanaryTester()
        res = await tester.run_smoke_test("http://localhost:3000")
        print(res)
    
    asyncio.run(main())
