# ✅ Debug Mode is Working!

## What Just Happened

We successfully tested the debug mode and created sample debug files!

## 📊 Test Results

### ✅ Test 1: Raw Code Generation

- **Prompt**: "Create a simple JavaScript function called 'greet'..."
- **Model Used**: gemini-2.5-flash
- **Generated Code**: ✅ Success!
- **Debug File Created**: `data/raw_generated_code/raw_code_20260111_123116_595685.json`

### ✅ Test 2: Validation Logging

- **Fixes Validated**: 1
- **Approved**: 1 (100%)
- **Rejected**: 0
- **Debug File Created**: `data/validation_results/validation_20260111_123116.json`

## 📁 Files Created

Both debug files are now in the `data/` folder:

1. **Raw Generated Code**:

   ```
   data/raw_generated_code/raw_code_20260111_123116_595685.json
   ```

   Contains:

   - `raw_response` - Exact text from Gemini:
     ```javascript
     function greet(name) {
       return "Hello, " + name;
     }
     ```
   - `model_used` - gemini:gemini-2.5-flash
   - `prompt` - The request sent to Gemini
   - `has_markdown` - true (had ``` markers)

2. **Validation Results**:

   ```
   data/validation_results/validation_20260111_123116.json
   ```

   Contains:

   - `is_safe` - true (passed validation)
   - `errors` - [] (no errors)
   - `content_preview` - The code that was validated
   - `approval_rate` - 100%

## 🎯 How to View Debug Files

### Option 1: Use the Viewer Script (Easiest)

```bash
./view_debug.sh           # View everything
./view_debug.sh raw       # View only raw code
./view_debug.sh validation # View only validation
```

### Option 2: Use Python Viewer

```bash
python3 view_debug.py           # View everything
python3 view_debug.py raw       # View only raw code
python3 view_debug.py stats     # View statistics
```

### Option 3: View JSON Directly

```bash
# View latest raw code
cat data/raw_generated_code/$(ls -t data/raw_generated_code/ | head -1)

# View latest validation
cat data/validation_results/$(ls -t data/validation_results/ | head -1)
```

### Option 4: Use jq for Pretty Formatting

```bash
# Extract just the code
jq -r '.raw_response' data/raw_generated_code/raw_code_*.json

# See validation errors (if any)
jq '.validation_results[] | select(.is_safe == false)' data/validation_results/*.json
```

## 🚀 Next Steps - How to Use in Real Workflow

Now that debug mode is confirmed working, here's what happens in your actual workflow:

### When You Run Your Normal Code Generation

For example, when you analyze a website and generate fixes:

```bash
# Your normal command
# (whatever triggers code generation in your system)
```

The system will **automatically** create debug files:

1. **After Gemini generates code**:

   - → File saved to `data/raw_generated_code/`
   - → Console prints: `[DEBUG] Saved raw generated code to: ...`

2. **After validation runs**:

   - → File saved to `data/validation_results/`
   - → Console prints: `[DEBUG] Saved validation results to: ...`

3. **View what happened**:
   ```bash
   ./view_debug.sh
   ```

### Example: Code Generation Failed

If code generation fails or is rejected:

```bash
# 1. Check console output for debug file paths
# Look for lines like:
# [DEBUG] Saved raw generated code to: data/raw_generated_code/raw_code_...json
# [DEBUG] Saved validation results to: data/validation_results/validation_...json

# 2. View the files
./view_debug.sh

# 3. Check what Gemini generated
./view_debug.sh raw
# → See the actual code before validation

# 4. Check why it was rejected
./view_debug.sh validation
# → See exact error messages

# 5. Extract the code to use manually (if it's good despite rejection)
jq -r '.processed_code' data/raw_generated_code/$(ls -t data/raw_generated_code/ | head -1) > my_fix.js
```

## 📋 What Information is Saved

### Raw Generated Code JSON

````json
{
  "timestamp": "2026-01-11T12:31:16.595715",
  "language": "javascript",
  "prompt": "...",                           ← What was sent to Gemini
  "model_used": "gemini:gemini-2.5-flash",  ← Which model responded
  "raw_response": "```javascript...",        ← EXACT response (with markdown)
  "processed_code": "function greet()...",   ← After removing ```
  "code_length": 69,
  "has_markdown": true
}
````

### Validation Results JSON

```json
{
  "timestamp": "2026-01-11T12:31:16.597754",
  "total_fixes": 1,
  "safe_fixes": 1,              ← How many passed
  "rejected_fixes": 0,          ← How many failed
  "approval_rate": 100.0,
  "validation_results": [
    {
      "fix_number": 1,
      "path": "utils/ai-test.js",
      "is_safe": true,           ← Did it pass?
      "warnings": [],
      "errors": [],              ← Why was it rejected (if any)
      "description": "...",
      "content_preview": "...",  ← First 1000 chars of code
      "content_length": 51,
      "bug_type": "test"
    }
  ]
}
```

## 💡 Pro Tips

1. **Check console output** - Debug file paths are printed
2. **Files are timestamped** - Easy to find latest with `ls -t`
3. **Debug mode is always on** - No need to enable it
4. **Use viewer scripts** - Easier than parsing JSON manually
5. **Extract code manually** - If validation rejects good code

## 🎬 Common Scenarios

### Scenario 1: Code generation works

- ✅ Debug file created
- ✅ Validation passes
- Result: Code is applied automatically

### Scenario 2: Code generation works but validation rejects

- ✅ Debug file created
- ❌ Validation fails
- **Solution**:
  1. `./view_debug.sh` to see both
  2. Check `errors` in validation to see why
  3. Extract code manually: `jq -r '.processed_code' ...`

### Scenario 3: Gemini doesn't generate code

- ⚠️ Debug file created but `raw_response` is empty
- **Solution**:
  1. `./view_debug.sh raw` to see the response
  2. Check `model_used` - API might be down
  3. Check `prompt` - might be malformed

## 🔧 Test Again Anytime

Run the test script anytime to verify debug mode:

```bash
python3 test_debug_mode.py
```

This will:

- Generate sample code
- Create debug files
- Validate the code
- Show you where files are saved

## ✅ Summary

**Debug mode is working!** Every time code is generated:

- Raw Gemini response → saved to `data/raw_generated_code/`
- Validation results → saved to `data/validation_results/`
- View anytime with: `./view_debug.sh`

**You can now see the code that Gemini generates BEFORE validation!** 🎉
