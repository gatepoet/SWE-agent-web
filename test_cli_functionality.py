#!/usr/bin/env python3
"""
Test script to verify CLI functionality of the GitHub Issues tool.
This tests the command-line interface without making actual API calls.
"""

import subprocess
import sys
import os

def test_cli_help():
    """Test that help message works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "GitHub Issues Tool" in result.stdout
    print("✓ Help message works")

def test_cli_list_help():
    """Test that list command help works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "list", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "--owner" in result.stdout and "--repo" in result.stdout
    print("✓ List command help works")

def test_cli_get_help():
    """Test that get command help works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "get", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "--issue-number" in result.stdout
    print("✓ Get command help works")

def test_cli_create_help():
    """Test that create command help works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "create", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "--title" in result.stdout and "--body" in result.stdout
    print("✓ Create command help works")

def test_cli_modify_help():
    """Test that modify command help works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "modify", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "--title" in result.stdout and "--body" in result.stdout
    print("✓ Modify command help works")

def test_cli_comment_help():
    """Test that comment command help works."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues", "comment", "--help"], 
                          capture_output=True, text=True)
    assert result.returncode == 0
    assert "--body" in result.stdout and "--issue-number" in result.stdout
    print("✓ Comment command help works")

def test_cli_missing_command():
    """Test that missing command shows error."""
    result = subprocess.run(["./tools/github_issues/bin/github_issues"], 
                          capture_output=True, text=True)
    assert result.returncode != 0
    print("✓ Missing command shows error")

if __name__ == "__main__":
    os.chdir("/gatepoet__SWE-agent-web")
    
    print("Testing CLI functionality...")
    test_cli_help()
    test_cli_list_help()
    test_cli_get_help()
    test_cli_create_help()
    test_cli_modify_help()
    test_cli_comment_help()
    test_cli_missing_command()
    
    print("\n✅ All CLI tests passed!")