"""
Test for browser code detection in fix_tester.py
Ensures that browser JavaScript code is correctly identified and validated appropriately.
"""

import pytest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fix_tester import FixTester


def test_browser_code_detection():
    """Test that browser-specific code is detected correctly."""
    tester = FixTester()
    
    # Test 1: Browser code with window
    browser_code_1 = """
    window.addEventListener('DOMContentLoaded', () => {
        console.log('Page loaded');
    });
    """
    result = tester.check_basic_syntax(browser_code_1)
    assert result['valid'], f"Browser code should be valid: {result.get('error', '')}"
    
    # Test 2: Browser code with document
    browser_code_2 = """
    document.querySelector('.button').addEventListener('click', () => {
        document.getElementById('content').innerHTML = 'Updated!';
    });
    """
    result = tester.check_basic_syntax(browser_code_2)
    assert result['valid'], f"Browser code should be valid: {result.get('error', '')}"
    
    # Test 3: React/JSX code
    react_code = """
    import React from 'react';
    
    export default function App() {
        return <div className="app">Hello World</div>;
    }
    """
    result = tester.check_basic_syntax(react_code)
    assert result['valid'], f"React code should be valid: {result.get('error', '')}"
    
    # Test 4: Invalid code - unbalanced braces
    invalid_code = """
    function test() {
        console.log('missing closing brace');
    """
    result = tester.check_basic_syntax(invalid_code)
    assert not result['valid'], "Invalid code should be detected"
    assert 'bracket' in result.get('error', '').lower() or 'brace' in result.get('error', '').lower()
    
    # Test 5: Valid plain JavaScript
    valid_js = """
    function greet(name) {
        return `Hello, ${name}!`;
    }
    """
    result = tester.check_basic_syntax(valid_js)
    assert result['valid'], f"Valid JavaScript should pass: {result.get('error', '')}"


def test_syntax_check_with_strings():
    """Test that strings don't interfere with bracket matching."""
    tester = FixTester()
    
    code_with_strings = """
    const message = "This has { braces } in a string";
    const obj = { key: "value" };
    """
    result = tester.check_basic_syntax(code_with_strings)
    assert result['valid'], f"Code with strings should be valid: {result.get('error', '')}"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
