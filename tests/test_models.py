import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Load env from parent
load_dotenv('../.env')

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("No API key found!")
    sys.exit(1)

genai.configure(api_key=api_key)

models_to_try = [
    'gemini-2.0-flash-lite-preview-02-05', 
    'gemini-2.0-flash-exp', 
    'gemini-flash-latest', 
    'gemini-pro-latest',
    'gemini-2.0-flash'
]

print(f"Testing models with key: {api_key[:5]}...")

for m in models_to_try:
    try:
        print(f'Testing {m}...')
        model = genai.GenerativeModel(m)
        resp = model.generate_content('Hello')
        print(f'SUCCESS: {m}')
        break
    except Exception as e:
        print(f'FAILED: {m} - {e}')
