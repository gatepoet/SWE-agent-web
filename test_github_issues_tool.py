#!/usr/bin/env python3
"""
Test script for GitHub Issues tool.
This script tests the command-line interface of the github_issues tool.
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

def test_help():
    """Test the help command."""
    print("Testing help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues --help")
    if code != 0:
        print(f"FAIL: Help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "GitHub Issues Tool" not in stdout:
        print("FAIL: Help output doesn't contain expected text")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: Help command works correctly")
    return True

def test_list_help():
    """Test the list help command."""
    print("Testing list help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues list --help")
    if code != 0:
        print(f"FAIL: List help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "--owner" not in stdout or "--repo" not in stdout:
        print("FAIL: List help output doesn't contain expected arguments")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: List help command works correctly")
    return True

def test_get_help():
    """Test the get help command."""
    print("Testing get help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues get --help")
    if code != 0:
        print(f"FAIL: Get help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "--issue-number" not in stdout:
        print("FAIL: Get help output doesn't contain expected arguments")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: Get help command works correctly")
    return True

def test_create_help():
    """Test the create help command."""
    print("Testing create help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues create --help")
    if code != 0:
        print(f"FAIL: Create help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "--title" not in stdout or "--body" not in stdout:
        print("FAIL: Create help output doesn't contain expected arguments")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: Create help command works correctly")
    return True

def test_modify_help():
    """Test the modify help command."""
    print("Testing modify help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues modify --help")
    if code != 0:
        print(f"FAIL: Modify help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "--issue-number" not in stdout or "--state" not in stdout:
        print("FAIL: Modify help output doesn't contain expected arguments")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: Modify help command works correctly")
    return True

def test_comment_help():
    """Test the comment help command."""
    print("Testing comment help command...")
    code, stdout, stderr = run_command("python tools/github_issues/bin/github_issues comment --help")
    if code != 0:
        print(f"FAIL: Comment help command failed with code {code}")
        print(f"stderr: {stderr}")
        return False
    
    if "--body" not in stdout:
        print("FAIL: Comment help output doesn't contain expected arguments")
        print(f"stdout: {stdout}")
        return False
    
    print("PASS: Comment help command works correctly")
    return True

def main():
    """Run all tests."""
    print("Testing GitHub Issues Tool...\n")
    
    tests = [
        test_help,
        test_list_help,
        test_get_help,
        test_create_help,
        test_modify_help,
        test_comment_help,
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
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())