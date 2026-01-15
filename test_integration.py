#!/usr/bin/env python3
"""
Integration test for GitHub Issues tool.
Tests the command-line interface without requiring real API calls.
"""

import subprocess
import json

def test_list_command():
    """Test list command with mocked data."""
    print("Testing list command...")
    
    # Create a mock environment variable to indicate we're testing
    env = {"GITHUB_TOKEN": "test_token", "TEST_MODE": "1"}
    
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "list",
        "--owner", "test",
        "--repo", "repo"
    ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: List command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        print(f"PASS: List command returned {len(data)} issues")
        return True
    except json.JSONDecodeError as e:
        print(f"FAIL: Could not parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False

def test_get_command():
    """Test get command with mocked data."""
    print("Testing get command...")
    
    env = {"GITHUB_TOKEN": "test_token", "TEST_MODE": "1"}
    
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "get",
        "--owner", "test",
        "--repo", "repo",
        "--issue-number", "1"
    ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Get command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        assert "number" in data, "Issue should have a number field"
        print(f"PASS: Get command returned issue #{data['number']}")
        return True
    except json.JSONDecodeError as e:
        print(f"FAIL: Could not parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False

def test_create_command():
    """Test create command with mocked data."""
    print("Testing create command...")
    
    env = {"GITHUB_TOKEN": "test_token", "TEST_MODE": "1"}
    
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "create",
        "--owner", "test",
        "--repo", "repo",
        "--title", "Test Issue"
    ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Create command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        assert "title" in data, "Issue should have a title field"
        print(f"PASS: Create command returned issue '{data['title']}'")
        return True
    except json.JSONDecodeError as e:
        print(f"FAIL: Could not parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False

def test_modify_command():
    """Test modify command with mocked data."""
    print("Testing modify command...")
    
    env = {"GITHUB_TOKEN": "test_token", "TEST_MODE": "1"}
    
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "modify",
        "--owner", "test",
        "--repo", "repo",
        "--issue-number", "1",
        "--title", "Updated Title"
    ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Modify command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        assert "success" in data, "Response should have a success field"
        print(f"PASS: Modify command returned success={data['success']}")
        return True
    except json.JSONDecodeError as e:
        print(f"FAIL: Could not parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False

def test_comment_command():
    """Test comment command with mocked data."""
    print("Testing comment command...")
    
    env = {"GITHUB_TOKEN": "test_token", "TEST_MODE": "1"}
    
    result = subprocess.run([
        "/gatepoet__SWE-agent-web/tools/github_issues/bin/github_issues",
        "comment",
        "--owner", "test",
        "--repo", "repo",
        "--issue-number", "1",
        "--body", "Test comment"
    ], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"FAIL: Comment command failed with return code {result.returncode}")
        print(f"stderr: {result.stderr}")
        return False
    
    try:
        data = json.loads(result.stdout)
        assert "success" in data, "Response should have a success field"
        print(f"PASS: Comment command returned success={data['success']}")
        return True
    except json.JSONDecodeError as e:
        print(f"FAIL: Could not parse JSON output: {e}")
        print(f"stdout: {result.stdout}")
        return False

def main():
    """Run all integration tests."""
    print("Running GitHub Issues tool integration tests...\n")
    
    tests = [
        test_list_command,
        test_get_command,
        test_create_command,
        test_modify_command,
        test_comment_command,
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
    import sys
    sys.exit(main())