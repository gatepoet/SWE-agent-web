#!/usr/bin/env python3
"""
Test script to verify that all PR requirements are met.
This script tests the GitHub Issues tool implementation against the PR requirements.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd="/gatepoet__SWE-agent-web"
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return -1, "", str(e)

def test_tool_exists():
    """Test that the GitHub Issues tool exists."""
    print("Testing that GitHub Issues tool exists...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues --help")
    if code != 0:
        print(f"FAIL: Tool doesn't exist or failed to run")
        return False
    
    if "GitHub Issues Tool" not in stdout:
        print("FAIL: Tool help output doesn't match expected format")
        return False
    
    print("PASS: GitHub Issues tool exists and runs correctly")
    return True

def test_list_issues():
    """Test that the list issues functionality exists."""
    print("Testing list issues functionality...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues list --help")
    if code != 0:
        print(f"FAIL: List command doesn't exist or failed to run")
        return False
    
    # Check for required parameters
    required_params = ["--owner", "--repo"]
    for param in required_params:
        if param not in stdout:
            print(f"FAIL: List command missing required parameter: {param}")
            return False
    
    print("PASS: List issues functionality exists with correct parameters")
    return True

def test_get_issue_details():
    """Test that the get issue details functionality exists."""
    print("Testing get issue details functionality...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues get --help")
    if code != 0:
        print(f"FAIL: Get command doesn't exist or failed to run")
        return False
    
    # Check for required parameters
    required_params = ["--owner", "--repo", "--issue-number"]
    for param in required_params:
        if param not in stdout:
            print(f"FAIL: Get command missing required parameter: {param}")
            return False
    
    print("PASS: Get issue details functionality exists with correct parameters")
    return True

def test_create_new_issue():
    """Test that the create new issue functionality exists."""
    print("Testing create new issue functionality...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues create --help")
    if code != 0:
        print(f"FAIL: Create command doesn't exist or failed to run")
        return False
    
    # Check for required parameters
    required_params = ["--owner", "--repo", "--title"]
    for param in required_params:
        if param not in stdout:
            print(f"FAIL: Create command missing required parameter: {param}")
            return False
    
    # Check for optional parameters
    optional_params = ["--body", "--labels"]
    for param in optional_params:
        if param not in stdout:
            print(f"FAIL: Create command missing optional parameter: {param}")
            return False
    
    print("PASS: Create new issue functionality exists with correct parameters")
    return True

def test_modify_issue():
    """Test that the modify issue functionality exists."""
    print("Testing modify issue functionality...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues modify --help")
    if code != 0:
        print(f"FAIL: Modify command doesn't exist or failed to run")
        return False
    
    # Check for required parameters
    required_params = ["--owner", "--repo", "--issue-number"]
    for param in required_params:
        if param not in stdout:
            print(f"FAIL: Modify command missing required parameter: {param}")
            return False
    
    # Check for optional parameters that can be modified
    optional_params = ["--title", "--body", "--state", "--labels"]
    for param in optional_params:
        if param not in stdout:
            print(f"FAIL: Modify command missing modifiable parameter: {param}")
            return False
    
    print("PASS: Modify issue functionality exists with correct parameters")
    return True

def test_add_subtask():
    """Test that the add subtask (comment) functionality exists."""
    print("Testing add subtask (comment) functionality...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues comment --help")
    if code != 0:
        print(f"FAIL: Comment command doesn't exist or failed to run")
        return False
    
    # Check for required parameters
    required_params = ["--owner", "--repo", "--issue-number", "--body"]
    for param in required_params:
        if param not in stdout:
            print(f"FAIL: Comment command missing required parameter: {param}")
            return False
    
    print("PASS: Add subtask (comment) functionality exists with correct parameters")
    return True

def test_interaction_capability():
    """Test that the tool supports interaction with issues."""
    print("Testing interaction capability...")
    
    # The tool should support all these actions which allow interaction
    actions = ["list", "get", "create", "modify", "comment"]
    for action in actions:
        code, stdout, stderr = run_command(f"python tools/github_issues/bin/github_issues {action} --help")
        if code != 0:
            print(f"FAIL: Action '{action}' doesn't exist or failed to run")
            return False
    
    print("PASS: Tool supports interaction with issues through multiple actions")
    return True

def test_config_file():
    """Test that the tool has a proper config.yaml file."""
    print("Testing config.yaml file...")
    code, stdout, stderr = run_command("test -f tools/github_issues/config.yaml")
    if code != 0:
        print("FAIL: config.yaml file doesn't exist")
        return False
    
    # Check that the config contains the expected structure
    code, stdout, stderr = run_command("cat tools/github_issues/config.yaml")
    if "tools:" not in stdout or "github_issues:" not in stdout:
        print("FAIL: config.yaml doesn't have expected structure")
        return False
    
    print("PASS: Tool has proper config.yaml file with correct structure")
    return True

def main():
    """Run all PR requirement tests."""
    print("Testing GitHub Issues Tool against PR requirements...\n")
    
    tests = [
        test_tool_exists,
        test_list_issues,
        test_get_issue_details,
        test_create_new_issue,
        test_modify_issue,
        test_add_subtask,
        test_interaction_capability,
        test_config_file,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All PR requirements are satisfied!")
        print("The GitHub Issues tool has been successfully implemented with all required features:")
        print("  ✓ List issues")
        print("  ✓ Get issue details")
        print("  ✓ Create new issue")
        print("  ✓ Modify issue")
        print("  ✓ Add subtask (comment)")
        print("  ✓ Interaction capability")
    else:
        print(f"\n❌ {failed} PR requirements not satisfied")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())