#!/usr/bin/env python3
"""
Test script to verify argparse functionality of github_issues tool.
This tests that the command-line interface works correctly.
"""

import subprocess
import sys

def run_command(cmd, expected_exit_code=0):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == expected_exit_code, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {' '.join(cmd)}")
        return False, "", "Timeout"
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def test_help_output():
    """Test that help output works."""
    print("Testing help output...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "--help"])
    
    if success:
        print("✓ Help command works")
        return True
    else:
        print(f"✗ Help command failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def test_create_help():
    """Test that create subcommand help works."""
    print("\nTesting create subcommand help...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "create", "--help"])
    
    if success:
        print("✓ Create help works")
        # Check that required arguments are present
        if "--owner" in stdout and "--repo" in stdout and "--title" in stdout:
            print("✓ Required arguments present in help")
            return True
        else:
            print("✗ Required arguments not present in help")
            return False
    else:
        print(f"✗ Create help failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def test_missing_required_args():
    """Test that missing required arguments produce proper error."""
    print("\nTesting missing required arguments...")
    # Try to create an issue without required args
    success, stdout, stderr = run_command(
        ["./tools/github_issues/bin/github_issues", "create"],
        expected_exit_code=2  # argparse error exit code
    )
    
    if success:
        print("✓ Missing required arguments properly rejected with correct exit code")
        # Check that the error message mentions the missing args
        combined_output = stdout + stderr
        if "--owner" in combined_output and "--repo" in combined_output and "--title" in combined_output:
            print("✓ Error message correctly identifies missing arguments")
            return True
        else:
            print(f"✗ Error message doesn't identify missing arguments properly")
            print(f"Stderr: {stderr}")
            return False
    else:
        print(f"✗ Should have failed with exit code 2 but got different exit code")
        return False

def test_list_help():
    """Test that list subcommand help works."""
    print("\nTesting list subcommand help...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "list", "--help"])
    
    if success:
        print("✓ List help works")
        return True
    else:
        print(f"✗ List help failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def test_get_help():
    """Test that get subcommand help works."""
    print("\nTesting get subcommand help...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "get", "--help"])
    
    if success:
        print("✓ Get help works")
        return True
    else:
        print(f"✗ Get help failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def test_modify_help():
    """Test that modify subcommand help works."""
    print("\nTesting modify subcommand help...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "modify", "--help"])
    
    if success:
        print("✓ Modify help works")
        return True
    else:
        print(f"✗ Modify help failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def test_comment_help():
    """Test that comment subcommand help works."""
    print("\nTesting comment subcommand help...")
    success, stdout, stderr = run_command(["./tools/github_issues/bin/github_issues", "comment", "--help"])
    
    if success:
        print("✓ Comment help works")
        return True
    else:
        print(f"✗ Comment help failed")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

if __name__ == "__main__":
    tests = [
        test_help_output,
        test_create_help,
        test_missing_required_args,
        test_list_help,
        test_get_help,
        test_modify_help,
        test_comment_help,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All argparse functionality tests passed!")
        sys.exit(0)
    else:
        print("✗ Some argparse functionality tests failed!")
        sys.exit(1)