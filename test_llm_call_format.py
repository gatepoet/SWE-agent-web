#!/usr/bin/env python3
"""
Test script to verify the github_issues tool can be called in the format
that an LLM would use (similar to the error message in the PR).
"""

import subprocess
import sys

def test_llm_style_call():
    """Test calling the tool in the style that an LLM would use."""
    
    print("Testing LLM-style call format...")
    
    # This simulates how an LLM might generate the command based on the config
    # The error message showed: github_issues create [--owner gatepoet [--repo BlackJack-Coach [...
    
    # Test 1: Minimal call with required parameters
    print("\nTest 1: Minimal required parameters")
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "Test Issue"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # We expect this to fail because ghapi is not installed, but it should fail
        # with the right error (ModuleNotFoundError), not argparse error
        if "required: --owner" in result.stderr or "required: --repo" in result.stderr or "required: --title" in result.stderr:
            print("✗ FAILED: Got argparse error about missing required args")
            return False
        elif "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
            print("✓ PASSED: Got expected Python import error (ghapi not installed)")
            print("  This means argparse accepted the command correctly")
            return True
        else:
            print(f"? UNEXPECTED: Got different error")
            print(f"  Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

def test_llm_style_call_with_labels():
    """Test calling the tool with labels (array argument)."""
    
    print("\nTest 2: Call with labels (array argument)")
    
    # Test with multiple labels
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "Test Issue with Labels",
        "--labels", "bug", "high-priority", "module-coupling"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # We expect this to fail because ghapi is not installed
        if "required: --owner" in result.stderr or "required: --repo" in result.stderr or "required: --title" in result.stderr:
            print("✗ FAILED: Got argparse error about missing required args")
            return False
        elif "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
            print("✓ PASSED: Got expected Python import error (ghapi not installed)")
            print("  This means argparse accepted the command with labels correctly")
            return True
        else:
            print(f"? UNEXPECTED: Got different error")
            print(f"  Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

def test_llm_style_call_with_body():
    """Test calling the tool with body parameter."""
    
    print("\nTest 3: Call with body parameter")
    
    # Test with body parameter
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "Test Issue with Body",
        "--body", "This is a test issue body"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # We expect this to fail because ghapi is not installed
        if "required: --owner" in result.stderr or "required: --repo" in result.stderr or "required: --title" in result.stderr:
            print("✗ FAILED: Got argparse error about missing required args")
            return False
        elif "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
            print("✓ PASSED: Got expected Python import error (ghapi not installed)")
            print("  This means argparse accepted the command with body correctly")
            return True
        else:
            print(f"? UNEXPECTED: Got different error")
            print(f"  Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

def test_wrong_subcommand_params():
    """Test that parameters from wrong subcommands are rejected."""
    
    print("\nTest 4: Wrong subcommand parameters (should fail)")
    
    # This simulates the error in the PR where --issue-number was used with create
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "Test Issue",
        "--issue-number", "123"  # This is wrong for create command
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # We expect this to fail with unrecognized argument error
        if "unrecognized arguments: --issue-number" in result.stderr or \
           "unrecognized argument" in result.stderr:
            print("✓ PASSED: Correctly rejected wrong parameter for subcommand")
            return True
        elif "ModuleNotFoundError" in result.stderr or "No module named" in result.stderr:
            print("? UNEXPECTED: Got Python import error instead of argparse error")
            print("  This might mean the wrong parameter was silently ignored")
            return False
        else:
            print(f"? UNEXPECTED: Got different error")
            print(f"  Stderr: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

if __name__ == "__main__":
    tests = [
        test_llm_style_call,
        test_llm_style_call_with_labels,
        test_llm_style_call_with_body,
        test_wrong_subcommand_params,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} LLM-style call format tests passed")
    
    if passed == total:
        print("✓ All LLM-style call format tests passed!")
        print("\nThe github_issues tool is now properly configured for LLM usage.")
        sys.exit(0)
    else:
        print("✗ Some LLM-style call format tests failed!")
        sys.exit(1)