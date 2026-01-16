#!/usr/bin/env python3
"""
Test script to reproduce the github_issues tool issue.
This simulates how the LLM would call the tool.
"""

import subprocess
import sys

def test_github_issues_create():
    """Test the create command with various parameter formats."""
    
    # Test 1: Minimal required parameters (should work)
    print("Test 1: Minimal required parameters")
    cmd = ["./tools/github_issues/bin/github_issues", "create", "--owner", "gatepoet", "--repo", "test-repo", "--title", "Test Issue"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Command timed out")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: With body and labels (more realistic usage)
    print("\nTest 2: With body and labels")
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "test-repo",
        "--title", "Test Issue with Body and Labels",
        "--body", "This is a test issue body",
        "--labels", "bug", "enhancement"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"Exit code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("Command timed out")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_github_issues_create()