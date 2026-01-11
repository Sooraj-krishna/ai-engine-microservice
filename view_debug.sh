#!/bin/bash

# Code Generation Debug Viewer
# Quick script to view the latest debug files

echo "======================================"
echo "Code Generation Debug Viewer"
echo "======================================"
echo ""

# Check if debug directories exist
if [ ! -d "data/raw_generated_code" ]; then
    echo "❌ Debug directory not found: data/raw_generated_code"
    echo "Run: mkdir -p data/raw_generated_code data/validation_results"
    exit 1
fi

# Count files
RAW_COUNT=$(ls data/raw_generated_code/ 2>/dev/null | wc -l)
VAL_COUNT=$(ls data/validation_results/ 2>/dev/null | wc -l)

echo "📊 Debug Files Summary:"
echo "  - Raw generated code files: $RAW_COUNT"
echo "  - Validation result files: $VAL_COUNT"
echo ""

# Function to display raw code
view_raw_code() {
    LATEST_RAW=$(ls -t data/raw_generated_code/ 2>/dev/null | head -1)
    
    if [ -z "$LATEST_RAW" ]; then
        echo "❌ No raw generated code files found"
        return
    fi
    
    echo "======================================"
    echo "📄 Latest Raw Generated Code"
    echo "======================================"
    echo "File: data/raw_generated_code/$LATEST_RAW"
    echo ""
    
    if command -v jq &> /dev/null; then
        # Use jq for pretty formatting
        echo "⏰ Timestamp:"
        jq -r '.timestamp' "data/raw_generated_code/$LATEST_RAW"
        echo ""
        
        echo "🤖 Model Used:"
        jq -r '.model_used' "data/raw_generated_code/$LATEST_RAW"
        echo ""
        
        echo "💻 Language:"
        jq -r '.language' "data/raw_generated_code/$LATEST_RAW"
        echo ""
        
        echo "📝 Prompt (truncated):"
        jq -r '.prompt' "data/raw_generated_code/$LATEST_RAW" | head -5
        echo "..."
        echo ""
        
        echo "✨ Raw Response:"
        echo "----------------------------------------"
        jq -r '.raw_response' "data/raw_generated_code/$LATEST_RAW"
        echo "----------------------------------------"
        echo ""
        
        echo "🔧 Processed Code:"
        echo "----------------------------------------"
        jq -r '.processed_code' "data/raw_generated_code/$LATEST_RAW"
        echo "----------------------------------------"
    else
        # Fallback without jq
        echo "⚠️  Install 'jq' for better formatting: sudo apt-get install jq"
        echo ""
        cat "data/raw_generated_code/$LATEST_RAW"
    fi
}

# Function to display validation results
view_validation() {
    LATEST_VAL=$(ls -t data/validation_results/ 2>/dev/null | head -1)
    
    if [ -z "$LATEST_VAL" ]; then
        echo "❌ No validation result files found"
        return
    fi
    
    echo ""
    echo "======================================"
    echo "✅ Latest Validation Results"
    echo "======================================"
    echo "File: data/validation_results/$LATEST_VAL"
    echo ""
    
    if command -v jq &> /dev/null; then
        echo "📊 Summary:"
        jq '{
            timestamp,
            total_fixes,
            safe_fixes,
            rejected_fixes,
            approval_rate
        }' "data/validation_results/$LATEST_VAL"
        echo ""
        
        # Show rejected fixes
        REJECTED=$(jq '[.validation_results[] | select(.is_safe == false)] | length' "data/validation_results/$LATEST_VAL")
        
        if [ "$REJECTED" -gt 0 ]; then
            echo "❌ Rejected Fixes ($REJECTED):"
            echo "----------------------------------------"
            jq -r '.validation_results[] | select(.is_safe == false) | 
                "Fix #\(.fix_number): \(.path)\n  Bug Type: \(.bug_type)\n  Errors: \(.errors | join(", "))\n  Content Preview:\n\(.content_preview)\n"' \
                "data/validation_results/$LATEST_VAL"
            echo "----------------------------------------"
        else
            echo "✅ All fixes passed validation!"
        fi
        
        # Show approved fixes
        APPROVED=$(jq '[.validation_results[] | select(.is_safe == true)] | length' "data/validation_results/$LATEST_VAL")
        
        if [ "$APPROVED" -gt 0 ]; then
            echo ""
            echo "✅ Approved Fixes ($APPROVED):"
            echo "----------------------------------------"
            jq -r '.validation_results[] | select(.is_safe == true) | 
                "Fix #\(.fix_number): \(.path)\n  Bug Type: \(.bug_type)\n  Description: \(.description)"' \
                "data/validation_results/$LATEST_VAL"
            echo "----------------------------------------"
        fi
    else
        echo "⚠️  Install 'jq' for better formatting: sudo apt-get install jq"
        echo ""
        cat "data/validation_results/$LATEST_VAL"
    fi
}

# Main menu
case "${1:-all}" in
    raw)
        view_raw_code
        ;;
    validation)
        view_validation
        ;;
    all)
        view_raw_code
        view_validation
        ;;
    list)
        echo "📁 Raw Generated Code Files:"
        ls -lht data/raw_generated_code/ | head -10
        echo ""
        echo "📁 Validation Result Files:"
        ls -lht data/validation_results/ | head -10
        ;;
    clean)
        echo "🧹 Cleaning old debug files (keeping last 10)..."
        cd data/raw_generated_code && ls -t | tail -n +11 | xargs -r rm
        cd ../../
        cd data/validation_results && ls -t | tail -n +11 | xargs -r rm
        cd ../../
        echo "✅ Cleanup complete"
        ;;
    help|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  all         - View latest raw code and validation (default)"
        echo "  raw         - View only raw generated code"
        echo "  validation  - View only validation results"
        echo "  list        - List all debug files"
        echo "  clean       - Remove old debug files (keep last 10)"
        echo "  help        - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # View everything"
        echo "  $0 raw          # View only raw code"
        echo "  $0 validation   # View only validation results"
        echo "  $0 list         # List all debug files"
        ;;
esac

echo ""
echo "======================================"
echo "Tip: Use 'jq' for JSON formatting:"
echo "  jq '.' data/raw_generated_code/\$(ls -t data/raw_generated_code/ | head -1)"
echo "======================================"
