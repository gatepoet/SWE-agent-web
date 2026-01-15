#!/usr/bin/env python3
"""
Test script to validate HTML structure and basic functionality.
"""

import re
from pathlib import Path

def test_html_well_formed():
    """Basic test that HTML is well-formed"""
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    # Check for basic HTML structure
    assert '<!DOCTYPE html>' in content, "Missing DOCTYPE"
    assert '<html' in content and '</html>' in content, "Missing html tags"
    assert '<head>' in content and '</head>' in content, "Missing head tags"
    assert '<body>' in content and '</body>' in content, "Missing body tags"
    
    # Check for proper form nesting
    form_count = content.count('<form')
    closing_form_count = content.count('</form>')
    assert form_count == closing_form_count, f"Form tag mismatch: {form_count} opening, {closing_form_count} closing"
    
    print("✓ HTML structure is valid")
    return True

def test_javascript_syntax():
    """Basic test that JavaScript has no obvious syntax errors"""
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    content = js_file.read_text()
    
    # Check for basic JS structure
    assert 'function' in content, "No functions found"
    assert '{' in content and '}' in content, "Missing braces"
    assert '(' in content and ')' in content, "Missing parentheses"
    
    # Check that all opening braces have closing braces (rough check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert abs(open_braces - close_braces) <= 2, f"Brace mismatch: {open_braces} opening, {close_braces} closing"
    
    # Check that all opening parens have closing parens (rough check)
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert abs(open_parens - close_parens) <= 2, f"Paren mismatch: {open_parens} opening, {close_parens} closing"
    
    print("✓ JavaScript syntax appears valid")
    return True

def test_required_elements_exist():
    """Test that all required elements exist in the HTML"""
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    required_elements = [
        'id="githubToken"',
        'id="validateTokenBtn"',
        'id="github-repo-input"',
        'id="manualIssueText"',
        'id="chatMessages"',
        'id="activeRuns"',
    ]
    
    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)
    
    assert len(missing) == 0, f"Missing elements: {missing}"
    
    print(f"✓ All {len(required_elements)} required elements found")
    return True

def main():
    print("=" * 60)
    print("HTML/JS Validation Tests")
    print("=" * 60)
    
    tests = [
        ("HTML well-formed", test_html_well_formed),
        ("JavaScript syntax", test_javascript_syntax),
        ("Required elements exist", test_required_elements_exist),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results.append(result)
        except AssertionError as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All validation tests passed!")
        return 0
    else:
        print(f"❌ {len([r for r in results if not r])} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())