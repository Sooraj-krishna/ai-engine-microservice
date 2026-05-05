import os
import re

tests_dir = "/home/devils_hell/Desktop/My Works/Project/ai-engine-microservice/tests"
src_path_fix = "import os\nimport sys\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))"

for filename in os.listdir(tests_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(tests_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace simple sys.path.append('src') or similar
        new_content = re.sub(r"sys\.path\.append\(['\"]src['\"]\)", src_path_fix, content)
        new_content = re.sub(r"sys\.path\.append\(os\.path\.join\(os\.path\.dirname\(__file__\), \"\.\.\"\)\)", src_path_fix, new_content)
        
        if new_content != content:
            with open(filepath, 'w') as f:
                f.write(new_content)
            print(f"Updated {filename}")
