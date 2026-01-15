#!/usr/bin/env python3
"""
Comprehensive test to verify all browser warning fixes.
This simulates checking for the specific warnings mentioned in the PR.
"""

import re
from pathlib import Path

def check_password_field_warning():
    """
    Check for the password field not contained in a form warning.
    
    Browser warning: [DOM] Password field is not contained in a form
    """
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    # Find password input
    password_patterns = [r'type="password"', r"type='password'"]
    password_match = None
    for pattern in password_patterns:
        match = re.search(pattern, content)
        if match:
            password_match = match
            break
    
    if not password_match:
        print("✓ No password field found - no warning expected")
        return True
    
    password_pos = password_match.start()
    
    # Check backwards for <form> tag
    form_before = content[:password_pos]
    has_form_tag = '<form' in form_before.lower()
    
    if not has_form_tag:
        print("❌ Password field is NOT contained in a <form> element")
        return False
    
    # Check that the form tag is properly closed before the password field
    last_form_pos = form_before.rfind('<form')
    if last_form_pos > 0:
        # Find the closing > of the form tag
        form_tag_end = form_before.find('>', last_form_pos)
        if form_tag_end > last_form_pos and form_tag_end < password_pos:
            print("✓ Password field IS contained in a properly structured <form> element")
            return True
    
    print("❌ Password field structure is incorrect")
    return False

def check_forced_reflow_optimizations():
    """
    Check for optimizations to reduce forced reflows.
    
    Browser warning: [Violation] Forced reflow while executing JavaScript took XXXms
    """
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    content = js_file.read_text()
    
    # Check for smoothScrollToBottom function (our optimization)
    has_smooth_scroll = 'function smoothScrollToBottom' in content
    if not has_smooth_scroll:
        print("❌ smoothScrollToBottom optimization function not found")
        return False
    
    # Check for requestAnimationFrame usage
    has_rAF = 'requestAnimationFrame' in content
    if not has_rAF:
        print("❌ requestAnimationFrame not used for scroll optimization")
        return False
    
    # Count direct scrollTop assignments (should be minimal)
    direct_scroll_patterns = [
        r'\.scrollTop\s*=\s*[^;]+;',
        r'\.scrollLeft\s*=\s*[^;]+;'
    ]
    
    direct_assignments = 0
    for pattern in direct_scroll_patterns:
        matches = re.findall(pattern, content)
        direct_assignments += len(matches)
    
    # We expect only the one inside smoothScrollToBottom
    if direct_assignments > 1:
        print(f"⚠️  Found {direct_assignments} direct scroll assignments (expected ~1)")
        return False
    
    # Count calls to our optimization function
    smooth_scroll_calls = content.count('smoothScrollToBottom(')
    if smooth_scroll_calls < 2:
        print(f"❌ Only {smooth_scroll_calls} calls to smoothScrollToBottom (expected >= 2)")
        return False
    
    print(f"✓ Forced reflow optimizations implemented ({smooth_scroll_calls} optimized scroll operations)")
    return True

def check_wheel_event_listener_warning():
    """
    Check for non-passive wheel event listeners.
    
    Browser warning: [Violation] Added non-passive event listener to a scroll-blocking 'wheel' event
    """
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    content = js_file.read_text()
    
    # Check for wheel event listeners without passive flag
    wheel_patterns = [
        r'addEventListener\s*\(\s*["\']wheel["\']\s*,\s*.+?\s*,\s*(?!.*passive)\s*\)'
    ]
    
    issues_found = []
    for pattern in wheel_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            issues_found.extend(matches)
    
    if issues_found:
        print(f"❌ Found {len(issues_found)} non-passive wheel event listeners")
        return False
    
    # Note: The warning might still appear from external libraries (like GitHub's auto-complete)
    # but we can't fix those. Our code doesn't add any.
    print("✓ No non-passive wheel event listeners in our code")
    return True

def check_button_type_prevents_form_submission():
    """
    Check that the validate button has type="button" to prevent form submission.
    
    This is important because we wrapped the password field in a form,
    and we don't want the form to submit when the button is clicked.
    """
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    content = html_file.read_text()
    
    # Find validate button
    validate_btn_pattern = r'<button\s+id="validateTokenBtn"[^>]*>'
    match = re.search(validate_btn_pattern, content)
    
    if not match:
        print("❌ Validate button not found")
        return False
    
    btn_html = match.group(0)
    
    # Check for type="button" or type='button'
    has_button_type = 'type="button"' in btn_html.lower() or "type='button'" in btn_html.lower()
    
    if not has_button_type:
        print("❌ Validate button missing type='button' attribute")
        return False
    
    print("✓ Validate button has type='button' to prevent form submission")
    return True

def main():
    print("=" * 70)
    print("Comprehensive Browser Warning Fix Verification")
    print("=" * 70)
    
    tests = [
        ("Password field in form (DOM warning)", check_password_field_warning),
        ("Forced reflow optimizations", check_forced_reflow_optimizations),
        ("Wheel event listener (performance warning)", check_wheel_event_listener_warning),
        ("Button type prevents form submission", check_button_type_prevents_form_submission),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}...")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✓ All {total} tests passed!")
        print("\nSummary of fixes:")
        print("1. ✓ Password field wrapped in <form> element")
        print("2. ✓ Scroll operations optimized with requestAnimationFrame")
        print("3. ✓ No non-passive wheel event listeners in our code")
        print("4. ✓ Validate button has type='button' to prevent form submission")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed out of {total}")
        return 1

if __name__ == "__main__":
    exit(main())