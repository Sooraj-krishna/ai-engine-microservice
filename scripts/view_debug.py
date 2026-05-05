#!/usr/bin/env python3
"""
Code Generation Debug Viewer (Python version)
Alternative to view_debug.sh for those who prefer Python
"""

import json
import os
from pathlib import Path
from datetime import datetime
import sys

# Directories
RAW_CODE_DIR = Path("data/raw_generated_code")
VALIDATION_DIR = Path("data/validation_results")

def get_latest_file(directory):
    """Get the most recent file in a directory"""
    if not directory.exists():
        return None
    files = list(directory.glob("*.json"))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def view_raw_code():
    """View the latest raw generated code"""
    latest = get_latest_file(RAW_CODE_DIR)
    
    if not latest:
        print("❌ No raw generated code files found")
        print(f"   Expected location: {RAW_CODE_DIR}")
        return
    
    print_header("📄 Latest Raw Generated Code")
    print(f"File: {latest}")
    print()
    
    with open(latest, 'r') as f:
        data = json.load(f)
    
    print("⏰ Timestamp:", data.get('timestamp', 'N/A'))
    print("🤖 Model Used:", data.get('model_used', 'N/A'))
    print("💻 Language:", data.get('language', 'N/A'))
    print("📏 Code Length:", data.get('code_length', 'N/A'), "characters")
    print("📝 Has Markdown:", "Yes" if data.get('has_markdown') else "No")
    print()
    
    print("📋 Prompt (first 300 chars):")
    print("-" * 70)
    prompt = data.get('prompt', '')
    print(prompt[:300])
    if len(prompt) > 300:
        print("...")
    print("-" * 70)
    print()
    
    print("✨ Raw Response from Gemini:")
    print("-" * 70)
    print(data.get('raw_response', '(empty)'))
    print("-" * 70)
    print()
    
    print("🔧 Processed Code (after cleanup):")
    print("-" * 70)
    print(data.get('processed_code', '(empty)'))
    print("-" * 70)

def view_validation():
    """View the latest validation results"""
    latest = get_latest_file(VALIDATION_DIR)
    
    if not latest:
        print("❌ No validation result files found")
        print(f"   Expected location: {VALIDATION_DIR}")
        return
    
    print_header("✅ Latest Validation Results")
    print(f"File: {latest}")
    print()
    
    with open(latest, 'r') as f:
        data = json.load(f)
    
    print("📊 Summary:")
    print(f"  ⏰ Timestamp: {data.get('timestamp', 'N/A')}")
    print(f"  📝 Total Fixes: {data.get('total_fixes', 0)}")
    print(f"  ✅ Safe Fixes: {data.get('safe_fixes', 0)}")
    print(f"  ❌ Rejected Fixes: {data.get('rejected_fixes', 0)}")
    print(f"  📈 Approval Rate: {data.get('approval_rate', 0):.1f}%")
    print()
    
    results = data.get('validation_results', [])
    
    # Show rejected fixes
    rejected = [r for r in results if not r.get('is_safe')]
    if rejected:
        print(f"❌ Rejected Fixes ({len(rejected)}):")
        print("-" * 70)
        for r in rejected:
            print(f"\nFix #{r.get('fix_number')}: {r.get('path')}")
            print(f"  Bug Type: {r.get('bug_type', 'N/A')}")
            print(f"  Description: {r.get('description', 'N/A')[:100]}")
            print(f"  Errors:")
            for error in r.get('errors', []):
                print(f"    • {error}")
            if r.get('warnings'):
                print(f"  Warnings:")
                for warning in r.get('warnings', []):
                    print(f"    ⚠️  {warning}")
            print(f"  Code Preview:")
            preview = r.get('content_preview', '')
            print("    " + "\n    ".join(preview.split('\n')[:10]))
            if len(preview.split('\n')) > 10:
                print("    ...")
        print("-" * 70)
    
    # Show approved fixes
    approved = [r for r in results if r.get('is_safe')]
    if approved:
        print(f"\n✅ Approved Fixes ({len(approved)}):")
        print("-" * 70)
        for r in approved:
            print(f"\nFix #{r.get('fix_number')}: {r.get('path')}")
            print(f"  Bug Type: {r.get('bug_type', 'N/A')}")
            print(f"  Description: {r.get('description', 'N/A')[:100]}")
            print(f"  Content Length: {r.get('content_length', 0)} characters")
            if r.get('warnings'):
                print(f"  Warnings:")
                for warning in r.get('warnings', []):
                    print(f"    ⚠️  {warning}")
        print("-" * 70)
    
    if not approved and not rejected:
        print("ℹ️  No validation results found")

def list_files():
    """List all debug files"""
    print_header("📁 Debug Files")
    
    print("\n📄 Raw Generated Code Files:")
    if RAW_CODE_DIR.exists():
        files = sorted(RAW_CODE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            for i, f in enumerate(files[:10], 1):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                size = f.stat().st_size
                print(f"  {i}. {f.name}")
                print(f"     Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}, Size: {size} bytes")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
        else:
            print("  (no files)")
    else:
        print("  (directory not found)")
    
    print("\n✅ Validation Result Files:")
    if VALIDATION_DIR.exists():
        files = sorted(VALIDATION_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            for i, f in enumerate(files[:10], 1):
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                size = f.stat().st_size
                print(f"  {i}. {f.name}")
                print(f"     Modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}, Size: {size} bytes")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more")
        else:
            print("  (no files)")
    else:
        print("  (directory not found)")

def show_stats():
    """Show statistics"""
    print_header("📊 Debug Statistics")
    
    raw_count = len(list(RAW_CODE_DIR.glob("*.json"))) if RAW_CODE_DIR.exists() else 0
    val_count = len(list(VALIDATION_DIR.glob("*.json"))) if VALIDATION_DIR.exists() else 0
    
    print(f"\n📈 File Counts:")
    print(f"  Raw generated code files: {raw_count}")
    print(f"  Validation result files: {val_count}")
    
    if val_count > 0:
        # Aggregate validation stats
        total_fixes = 0
        total_safe = 0
        total_rejected = 0
        
        for val_file in VALIDATION_DIR.glob("*.json"):
            with open(val_file, 'r') as f:
                data = json.load(f)
                total_fixes += data.get('total_fixes', 0)
                total_safe += data.get('safe_fixes', 0)
                total_rejected += data.get('rejected_fixes', 0)
        
        print(f"\n📊 Validation Statistics (all time):")
        print(f"  Total fixes validated: {total_fixes}")
        print(f"  Total approved: {total_safe}")
        print(f"  Total rejected: {total_rejected}")
        if total_fixes > 0:
            approval_rate = (total_safe / total_fixes) * 100
            print(f"  Overall approval rate: {approval_rate:.1f}%")

def help_menu():
    """Show help menu"""
    print("""
Code Generation Debug Viewer (Python)

Usage: python3 view_debug.py [command]

Commands:
  all         - View latest raw code and validation (default)
  raw         - View only raw generated code
  validation  - View only validation results
  list        - List all debug files
  stats       - Show statistics
  help        - Show this help message

Examples:
  python3 view_debug.py              # View everything
  python3 view_debug.py raw          # View only raw code
  python3 view_debug.py validation   # View only validation results
  python3 view_debug.py list         # List all debug files

File Locations:
  Raw code: data/raw_generated_code/
  Validation: data/validation_results/

Alternative:
  Use the bash script: ./view_debug.sh
    """)

def main():
    """Main entry point"""
    command = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if command == 'raw':
        view_raw_code()
    elif command == 'validation':
        view_validation()
    elif command == 'list':
        list_files()
    elif command == 'stats':
        show_stats()
    elif command == 'help':
        help_menu()
    elif command == 'all':
        view_raw_code()
        view_validation()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python3 view_debug.py help' for usage")
        sys.exit(1)

if __name__ == '__main__':
    main()
