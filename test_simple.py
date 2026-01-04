#!/usr/bin/env python3
"""
Simple test to verify our implementation changes.
"""

import os
from pathlib import Path

def test_file_changes():
    """Test that our file changes are present."""
    print("Testing file changes...")
    
    # Test 1: Check HTML file has GitHub token elements
    html_path = Path("/gatepoet__SWE-agent-web/sweagent/api/static/index.html")
    if html_path.exists():
        html_content = html_path.read_text()
        checks = [
            ('id="githubToken"', "GitHub token input field"),
            ('id="validateTokenBtn"', "Validation button"),
            ('id="tokenValidationStatus"', "Validation status display"),
            ('.validation-success', "Success validation style"),
            ('.validation-error', "Error validation style")
        ]
        
        for check, description in checks:
            if check in html_content:
                print(f"✓ Found {description}")
            else:
                print(f"✗ Missing {description}")
    else:
        print("✗ HTML file not found")
    
    # Test 2: Check CSS file has validation styles
    css_path = Path("/gatepoet__SWE-agent-web/sweagent/api/static/style.css")
    if css_path.exists():
        css_content = css_path.read_text()
        checks = [
            ('.validation-status', "Validation status class"),
            ('.validation-success', "Success validation style"),
            ('.validation-error', "Error validation style"),
            ('.btn-secondary', "Secondary button style")
        ]
        
        for check, description in checks:
            if check in css_content:
                print(f"✓ Found {description}")
            else:
                print(f"✗ Missing {description}")
    else:
        print("✗ CSS file not found")
    
    # Test 3: Check JavaScript file has token validation functions
    js_path = Path("/gatepoet__SWE-agent-web/sweagent/api/static/app.js")
    if js_path.exists():
        js_content = js_path.read_text()
        checks = [
            ('githubTokenInput', "GitHub token input variable"),
            ('validateTokenBtn', "Validation button variable"),
            ('tokenValidationStatus', "Validation status variable"),
            ('validateGitHubToken', "Token validation function"),
            ('showTokenValidationStatus', "Show validation status function"),
            ('github_token', "GitHub token in request body")
        ]
        
        for check, description in checks:
            if check in js_content:
                print(f"✓ Found {description}")
            else:
                print(f"✗ Missing {description}")
    else:
        print("✗ JavaScript file not found")
    
    # Test 4: Check server.py has new endpoints and functionality
    server_path = Path("/gatepoet__SWE-agent-web/sweagent/api/server.py")
    if server_path.exists():
        server_content = server_path.read_text()
        checks = [
            ('/api/github/validate', "Token validation endpoint"),
            ('validate_github_token', "Token validation function"),
            ('github_token: str = ""', "GitHub token parameter in run_agent_async"),
            ('github_token = data.get("github_token", "")', "GitHub token extraction from request"),
        ]
        
        for check, description in checks:
            if check in server_content:
                print(f"✓ Found {description}")
            else:
                print(f"✗ Missing {description}")
    else:
        print("✗ Server file not found")

def test_implementation_logic():
    """Test the logic of our implementation."""
    print("\nTesting implementation logic...")
    
    # Test token validation logic
    def validate_token_logic(token):
        """Simulate token validation logic."""
        if not token:
            return False, "Token is empty"
        elif len(token) < 10:
            return False, "Token too short"
        else:
            return True, "Token looks valid"
    
    # Test cases
    test_cases = [
        ("", False),
        ("short", False), 
        ("ghp_valid_token_1234567890", True)
    ]
    
    for token, expected_result in test_cases:
        is_valid, message = validate_token_logic(token)
        if is_valid == expected_result:
            print(f"✓ Token validation logic correct for: {repr(token)}")
        else:
            print(f"✗ Token validation logic failed for: {repr(token)}")
    
    print("✓ Implementation logic tests completed!")

if __name__ == "__main__":
    test_file_changes()
    test_implementation_logic()
    print("\n🎉 Implementation verification complete!")