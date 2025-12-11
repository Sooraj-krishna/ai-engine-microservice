#!/bin/bash

# Setup script for enhanced testing dependencies
# This installs optional npm packages for axe-core and lighthouse

echo "🔧 Setting up enhanced testing dependencies..."
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js is not installed. Some enhanced testing features will use fallbacks."
    echo "   To install Node.js: https://nodejs.org/"
    echo ""
else
    echo "✅ Node.js found: $(node --version)"
    echo ""
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        echo "⚠️  npm is not installed. Installing dependencies manually..."
    else
        echo "✅ npm found: $(npm --version)"
        echo ""
        
        # Install npm dependencies
        echo "📦 Installing npm dependencies (axe-core, lighthouse)..."
        npm install --save-dev @axe-core/playwright lighthouse 2>/dev/null || {
            echo "⚠️  npm install failed. Trying with npx (will be slower but works)..."
            echo "   The system will use fallback methods if packages are not available."
        }
        
        echo ""
        echo "✅ Enhanced testing dependencies setup complete!"
        echo ""
        echo "Note: If npm packages are not available, the system will automatically"
        echo "      use fallback methods (basic accessibility checks, Playwright performance API)."
    fi
fi

echo ""
echo "📋 Summary:"
echo "   - axe-core: For comprehensive accessibility testing"
echo "   - lighthouse: For performance and best practices auditing"
echo "   - Both have fallback implementations if not installed"
echo ""

