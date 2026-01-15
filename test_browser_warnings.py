#!/usr/bin/env python3
"""
Test script to check for browser warnings in the web interface.
This script will analyze the HTML and JavaScript files for common issues
that cause browser console warnings.
"""

import os
import re
from pathlib import Path

def check_password_field_in_form():
    """Check if password field is contained in a form"""
    html_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    
    if not html_file.exists():
        print("❌ HTML file not found")
        return False
    
    content = html_file.read_text()
    
    # Check if there's a password input
    has_password = "type=\"password\"" in content or 'type="password"' in content
    
    if not has_password:
        print("✓ No password field found - no warning expected")
        return True
    
    # Check if password is inside a <form> tag
    password_match = re.search(r'type="?password"?', content)
    if not password_match:
        return True
    
    password_pos = password_match.start()
    
    # Look backwards for <form> tag
    form_before = content[:password_pos]
    has_form_before = '<form' in form_before.lower()
    
    # Look forwards for </form> or > to close the form
    form_after_start = form_before.rfind('<form') + len('<form') if '<form' in form_before else -1
    if form_after_start > 0:
        # Find the closing > of the form tag
        form_tag_end = form_before.find('>', form_after_start)
        if form_tag_end > form_after_start:
            has_form_before = True
    
    if not has_form_before:
        print("❌ Password field is NOT contained in a <form> element")
        return False
    else:
        print("✓ Password field IS contained in a <form> element")
        return True

def check_wheel_event_listeners():
    """Check for non-passive wheel event listeners"""
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    
    if not js_file.exists():
        print("❌ JS file not found")
        return False
    
    content = js_file.read_text()
    
    # Look for wheel event listeners without passive: true
    wheel_patterns = [
        r'\.addEventListener\s*\(\s*["\']wheel["\']',
        r'addEventListener\s*\(\s*["\']wheel["\']'
    ]
    
    found_issues = []
    for pattern in wheel_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Check if passive: true is in the same addEventListener call
            context_start = max(0, match.start() - 100)
            context_end = min(len(content), match.end() + 200)
            context = content[context_start:context_end]
            
            # Find the closing parenthesis
            paren_count = 0
            listener_end = match.end()
            for i in range(match.end(), len(content)):
                if content[i] == '(':
                    paren_count += 1
                elif content[i] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        listener_end = i + 1
                        break
            
            listener_call = content[match.start():listener_end]
            if 'passive' not in listener_call.lower():
                found_issues.append(listener_call)
    
    if found_issues:
        print(f"❌ Found {len(found_issues)} non-passive wheel event listeners:")
        for issue in found_issues[:3]:  # Show first 3
            print(f"  - {issue[:100]}...")
        return False
    else:
        print("✓ No non-passive wheel event listeners found")
        return True

def check_forced_reflow_causes():
    """Check for common causes of forced reflows"""
    js_file = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    
    if not js_file.exists():
        print("❌ JS file not found")
        return False
    
    content = js_file.read_text()
    
    # Common patterns that can cause forced reflows
    patterns = [
        (r'\.style\.[a-zA-Z]+\s*=', 'Direct style manipulation'),
        (r'\.classList\.(add|remove|toggle)\s*\(\s*["\']', 'Class list manipulation'),
        (r'\.offset(Width|Height|Top|Left)\s*', 'Offset property access'),
        (r'\.scroll(Top|Left|Width|Height)\s*=', 'Scroll property manipulation'),
    ]
    
    issues_found = []
    for pattern, description in patterns:
        matches = re.findall(pattern, content)
        if matches:
            issues_found.append(f"{description}: {len(matches)} occurrences")
    
    if issues_found:
        print("⚠️  Potential forced reflow causes found:")
        for issue in issues_found[:5]:
            print(f"  - {issue}")
        return False
    else:
        print("✓ No obvious forced reflow patterns found")
        return True

def main():
    print("=" * 60)
    print("Browser Console Warnings Checker")
    print("=" * 60)
    
    results = []
    
    print("\n1. Checking password field in form...")
    results.append(check_password_field_in_form())
    
    print("\n2. Checking wheel event listeners...")
    results.append(check_wheel_event_listeners())
    
    print("\n3. Checking for forced reflow causes...")
    results.append(check_forced_reflow_causes())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed!")
        return 0
    else:
        print("❌ Some issues found that may cause browser warnings")
        return 1

if __name__ == "__main__":
    exit(main())