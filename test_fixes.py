#!/usr/bin/env python3
"""
Test script to verify that the browser warning fixes are working correctly.
This tests both the structure and functionality of the changes.
"""

import os
import re
from pathlib import Path

def test_password_in_form():
    """Test that password field is properly wrapped in a form"""
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    # Check that password input exists
    assert 'type="password"' in content or "type='password'" in content, "Password field not found"
    
    # Check that it's wrapped in a form
    password_pos = content.find('type="password"') if 'type="password"' in content else content.find("type='password'")
    form_before = content[:password_pos]
    assert '<form' in form_before.lower(), "Password field not wrapped in <form>"
    
    # Check that the button has type="button" to prevent form submission
    validate_btn_pos = content.find('id="validateTokenBtn"')
    btn_section = content[validate_btn_pos:validate_btn_pos+200]
    assert 'type="button"' in btn_section or "type='button'" in btn_section, "Validate button should have type='button'"
    
    print("✓ Password field properly wrapped in form with correct button type")
    return True

def test_smooth_scroll_function():
    """Test that smoothScrollToBottom function exists and is used"""
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    content = js_file.read_text()
    
    # Check that the helper function exists
    assert 'function smoothScrollToBottom' in content, "smoothScrollToBottom function not found"
    assert 'requestAnimationFrame' in content, "requestAnimationFrame not used"
    
    # Check that it's being called instead of direct scrollTop assignments
    # Count occurrences of the helper vs direct assignments
    smooth_scroll_calls = content.count('smoothScrollToBottom(')
    direct_scroll_assignments = content.count('.scrollTop =')
    
    # We should have more calls to smoothScrollToBottom than direct assignments
    assert smooth_scroll_calls >= 2, f"Not enough smoothScrollToBottom calls: {smooth_scroll_calls}"
    assert direct_scroll_assignments <= 1, f"Too many direct scrollTop assignments: {direct_scroll_assignments}"
    
    print(f"✓ Smooth scrolling optimization implemented ({smooth_scroll_calls} calls)")
    return True

def test_no_non_passive_wheel_listeners():
    """Test that we don't add non-passive wheel event listeners"""
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    content = js_file.read_text()
    
    # Check for wheel event listeners without passive flag
    wheel_patterns = [
        r'addEventListener\s*\(\s*["\']wheel["\']\s*,\s*.+?\s*,\s*(?!.*passive)\s*\)'
    ]
    
    for pattern in wheel_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        assert len(matches) == 0, f"Found non-passive wheel event listeners: {matches}"
    
    print("✓ No non-passive wheel event listeners found")
    return True

def test_form_structure():
    """Test that the form has proper structure"""
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    # Find the form
    form_start = content.find('<form id="githubTokenForm">')
    assert form_start != -1, "GitHub token form not found"
    
    # Find the closing form tag
    form_end = content.find('</form>', form_start)
    assert form_end != -1, "Closing </form> tag not found"
    
    # Extract form content
    form_content = content[form_start:form_end]
    
    # Check that it contains the password input and button
    assert 'type="password"' in form_content or "type='password'" in form_content, "Password field not in form"
    assert 'id="validateTokenBtn"' in form_content, "Validate button not in form"
    
    print("✓ Form structure is correct")
    return True

def main():
    print("=" * 60)
    print("Testing Browser Warning Fixes")
    print("=" * 60)
    
    tests = [
        ("Password field in form", test_password_in_form),
        ("Smooth scroll optimization", test_smooth_scroll_function),
        ("No non-passive wheel listeners", test_no_non_passive_wheel_listeners),
        ("Form structure validation", test_form_structure),
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
        print("✓ All tests passed!")
        return 0
    else:
        print(f"❌ {len([r for r in results if not r])} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())