import asyncio
import os
import subprocess
import tempfile
import google.generativeai as genai
from playwright.async_api import async_playwright
import requests

async def run_e2e_tests(url: str) -> list:
    """
    Analyzes a URL, generates a Playwright E2E test script using an LLM,
    and executes it to find functional bugs.
    """
    print("[E2E_TESTER] Starting E2E test generation for URL:", url)
    bugs = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, wait_until='networkidle')
            
            print("[E2E_TESTER] Analyzing page content...")
            content = await page.content()
            
            await browser.close()

            # Generate the test script using Gemini
            print("[E2E_TESTER] Generating Playwright script with AI...")
            script_code = await generate_playwright_script(content, url)

            if not script_code:
                print("[E2E_TESTER] AI failed to generate a test script.")
                return []

            # Execute the generated script
            print("[E2E_TESTER] Executing generated test script...")
            test_passed, test_output = await execute_test_script(script_code)

            if not test_passed:
                print(f"[E2E_TESTER] E2E test failed! Output: {test_output}")
                bugs.append({
                    "type": "functional_bug",
                    "severity": "high",
                    "description": "A critical user flow test failed.",
                    "details": f"The dynamically generated E2E test for {url} failed. This likely indicates a functional bug where an action does not lead to the expected outcome. Test output: {test_output}",
                    "data": {
                        "type": "Functional Bug",
                        "description": "A critical user flow test failed.",
                        "details": f"Test output: {test_output}"
                    }
                })
            else:
                print("[E2E_TESTER] E2E test passed successfully.")

    except Exception as e:
        print(f"[E2E_TESTER] An error occurred during E2E testing: {e}")
        bugs.append({
            "type": "test_framework_error",
            "severity": "medium",
            "description": "The E2E testing framework itself encountered an error.",
            "details": str(e),
            "data": {
                "type": "Test Framework Error",
                "description": "The E2E testing framework itself encountered an error.",
                "details": str(e)
            }
        })

    return bugs

def _create_prompt(page_content: str, url: str) -> str:
    """Creates the prompt for the AI model."""
    return f"""
    You are an expert QA engineer specializing in finding UI/UX bugs. Your task is to write a comprehensive Python Playwright script to thoroughly test the provided website content for common UI/UX issues and functional bugs.

    Analyze the HTML content below and identify multiple common user interaction paths and potential bug scenarios. For example, on an e-commerce site, this might include navigating categories, adding items to the cart, attempting checkout, and verifying product details. On a form, it might involve valid and invalid submissions.

    Write a robust, self-contained Python Playwright script to test these paths and validate the UI/UX.

    **Requirements:**
    1. The script must use the **async** version of Playwright.
    2. It must navigate to the URL: {url}
    3. It must include a variety of `expect()` assertions from `playwright.async_api.expect` to verify:
        - Element visibility and presence.
        - Correct text content.
        - Enabled/disabled states of interactive elements.
        - Successful navigation or URL changes.
        - Absence of unexpected error messages or elements.
    4. Actively look for common UI/UX issues such as:
        - Broken images or links.
        - Misaligned elements.
        - Missing content.
        - Unresponsive elements.
        - Console errors (e.g., by listening to `page.on("console")` and asserting no errors).
    5. The script should attempt to trigger potential error states (e.g., submitting a form with invalid data) and assert that appropriate error messages are displayed.
    6. Do not install browsers (`playwright install`). Assume they are already installed.
    5. Do not include `asyncio.run()` or any other event loop management in the script, as it will be executed within an existing event loop.
    6. For each `expect()` assertion, if it fails, ensure a clear and descriptive error message is printed to `stderr` explaining what was expected and what went wrong. This will help in debugging.
    7. Include comments in the script to explain the purpose of each major test step.
    8. Your response must be ONLY the Python code, enclosed in ```python ... ```. Do not include any other text, explanation, or formatting.

    **HTML Content:**
    ```html
    {page_content[:5000]} 
    ```
    """

async def generate_playwright_script(page_content: str, url: str) -> str | None:
    """Uses an AI model to generate a Playwright script, supporting both Google and OpenRouter APIs."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("[E2E_TESTER_AI] GEMINI_API_KEY not found.")
        return None

    try:
        prompt = _create_prompt(page_content, url)
        code = ""

        if api_key.startswith("sk-or-"):
            # Use OpenRouter
            print("[E2E_TESTER_AI] OpenRouter API key detected.")
            # Fetch all models from OpenRouter
            print("[E2E_TESTER_AI] Fetching available models from OpenRouter...")
            models_response = requests.get("https://openrouter.ai/api/v1/models")
            models_response.raise_for_status()
            models_data = models_response.json().get('data', [])

            # Define a priority list of model providers/families to try
            model_priority_list = [
                "google/gemini",    # First choice
                "anthropic/claude", # Fallback
                "openai/gpt"        # Second fallback
            ]

            code = None

            for provider in model_priority_list:
                selected_model_id = None
                # Find the first available model for the current provider
                for model in models_data:
                    if provider in model.get('id', ''):
                        selected_model_id = model['id']
                        break
                
                if not selected_model_id:
                    print(f"[E2E_TESTER_AI] No model found for provider: {provider}. Skipping.")
                    continue

                print(f"[E2E_TESTER_AI] Attempting to use model: {selected_model_id}")
                
                try:
                    # Attempt to generate the script with the selected model
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "HTTP-Referer": "http://localhost:3000",
                            "X-Title": "AI Engine Microservice",
                        },
                        json={
                            "model": selected_model_id,
                            "messages": [{"role": "user", "content": prompt}]
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    code = result['choices'][0]['message']['content']
                    
                    print(f"[E2E_TESTER_AI] Successfully generated script with {selected_model_id}.")
                    break  # Exit the loop on success

                except Exception as e:
                    print(f"[E2E_TESTER_AI] Model {selected_model_id} failed: {e}. Trying next provider.")
                    continue  # Go to the next provider in the list
            
            if not code:
                print("[E2E_TESTER_AI] All model providers failed.")
                return None
            response.raise_for_status()
            result = response.json()
            code = result['choices'][0]['message']['content']

        else:
            # Use native Google Gemini API
            print("[E2E_TESTER_AI] Google API key detected.")
            genai.configure(api_key=api_key)
            
            print("[E2E_TESTER_AI] Listing available models...")
            available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            if not available_models:
                print("[E2E_TESTER_AI] No models found that support 'generateContent'.")
                return None

            selected_model = available_models[0]
            print(f"[E2E_TESTER_AI] Using model: {selected_model.name}")
            model = genai.GenerativeModel(model_name=selected_model.name)
            
            response = await model.generate_content_async(prompt)
            code = response.text

        # Extract code from the response
        if '```python' in code:
            code = code.split('```python')[1].split('```')[0]
        
        return code.strip()

    except requests.exceptions.HTTPError as http_err:
        error_content = http_err.response.text
        print(f"[E2E_TESTER_AI] HTTPError occurred: {http_err}")
        print(f"[E2E_TESTER_AI] Response body: {error_content}")
        return None
    except Exception as e:
        print(f"[E2E_TESTER_AI] Failed to generate script: {e}")
        return None

async def execute_test_script(script_code: str) -> tuple[bool, str]:
    """Executes the generated Playwright script in a subprocess and returns the result.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
        tmp_file_name = tmp_file.name
        # Add necessary imports and structure to make it a runnable script
        full_script = f"""
import asyncio
from playwright.async_api import async_playwright, expect

async def main():
{chr(10).join([f'    {line}' for line in script_code.split(chr(10))])}

if __name__ == '__main__':
    asyncio.run(main())
"""
        tmp_file.write(full_script)

    process = await asyncio.create_subprocess_exec(
        'python3', tmp_file_name,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    os.remove(tmp_file_name)

    if process.returncode == 0:
        return True, stdout.decode()
    else:
        return False, stderr.decode()
