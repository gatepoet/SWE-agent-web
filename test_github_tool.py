#!/usr/bin/env python3
"""
Test script for GitHub Issues tool.
This tests the basic functionality without requiring actual GitHub API calls.
"""

import subprocess
import json
import sys

def test_help():
    """Test that help works."""
    print("Testing help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: Help command works")
    return True

def test_list_help():
    """Test that list subcommand help works."""
    print("Testing list help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "list", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: List help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: List help command works")
    return True

def test_get_help():
    """Test that get subcommand help works."""
    print("Testing get help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "get", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Get help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: Get help command works")
    return True

def test_create_help():
    """Test that create subcommand help works."""
    print("Testing create help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "create", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Create help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: Create help command works")
    return True

def test_modify_help():
    """Test that modify subcommand help works."""
    print("Testing modify help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "modify", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Modify help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: Modify help command works")
    return True

def test_comment_help():
    """Test that comment subcommand help works."""
    print("Testing comment help...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "comment", "--help"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Comment help command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    print("PASS: Comment help command works")
    return True

def test_invalid_command():
    """Test that invalid commands fail gracefully."""
    print("Testing invalid command...")
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "invalid_command"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("FAIL: Invalid command should have failed")
        return False
    
    print("PASS: Invalid command fails as expected")
    return True

def main():
    """Run all tests."""
    print("Running GitHub Issues tool tests...\n")
    
    tests = [
        test_help,
        test_list_help,
        test_get_help,
        test_create_help,
        test_modify_help,
        test_comment_help,
        test_invalid_command,
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