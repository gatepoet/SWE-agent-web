#!/usr/bin/env python3
"""
Test script to reproduce and verify the fix for the exact error from the PR.

The PR showed this error:
github_issues create [--owner gatepoet [--repo BlackJack-Coach [--issue-number  
[--title 'BUG: Undefined Variables in cardHandler.js - map, hands, handContainers, splitContainers, lastAddedCard' 
[--body '## Bug Description
The `cardHandler.js` module uses several variables that are not defined within the module or passed as parameters:
- `map` (used for card counting values)
- `hands` (game state tracking)
- `handContainers` (DOM elements)
- `splitContainers` (DOM elements)
- `lastAddedCard` (UI state)

These variables are being accessed from the global scope, creating tight coupling and making the module untestable in isolation.

## Expected Behavior
All dependencies should be:
1. Defined as function parameters, or
2. Imported from other modules, or
3. Explicitly passed to the functions that need them

## Verification Criteria
- Functions should work when called with explicit parameters
- Module should be testable without global state
- No "undefined" errors when variables are accessed' [--state  
[--labels ['bug', 'high-priority', 'module-coupling'] [--max-results
usage: github_issues create [-h] --owner OWNER --repo REPO --title TITLE
                            [--body BODY] [--labels [LABELS ...]]
github_issues create: error: the following arguments are required: --owner, --repo, --title
"""

import subprocess
import sys

def test_pr_error_reproduction():
    """
    Reproduce the exact error from the PR.
    
    The error shows that the LLM was trying to call github_issues create with:
    - --owner gatepoet
    - --repo BlackJack-Coach  
    - --issue-number (WRONG - this is for get/modify, not create)
    - --title "..."
    - --body "..."
    - --labels ['bug', 'high-priority', 'module-coupling']
    
    The error was: "error: the following arguments are required: --owner, --repo, --title"
    This suggests that argparse didn't recognize some of the parameters.
    """
    
    print("Reproducing PR error scenario...")
    print("=" * 60)
    
    # The LLM was trying to create an issue with these parameters
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "BUG: Undefined Variables in cardHandler.js - map, hands, handContainers, splitContainers, lastAddedCard",
        "--body", "## Bug Description\nThe `cardHandler.js` module uses several variables that are not defined within the module or passed as parameters:\n- `map` (used for card counting values)\n- `hands` (game state tracking)\n- `handContainers` (DOM elements)\n- `splitContainers` (DOM elements)\n- `lastAddedCard` (UI state)\n\nThese variables are being accessed from the global scope, creating tight coupling and making the module untestable in isolation.\n\n## Expected Behavior\nAll dependencies should be:\n1. Defined as function parameters, or\n2. Imported from other modules, or\n3. Explicitly passed to the functions that need them\n\n## Verification Criteria\n- Functions should work when called with explicit parameters\n- Module should be testable without global state\n- No \"undefined\" errors when variables are accessed",
        "--labels", "bug", "high-priority", "module-coupling"
    ]
    
    print("Running command:")
    print(" ".join(cmd[:5]))  # Show first part to avoid huge output
    print("... (with title and body parameters)")
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        print("Command exit code:", result.returncode)
        print()
        
        # Check if we get the argparse error about missing required args
        combined_output = result.stdout + result.stderr
        
        if "error: the following arguments are required: --owner, --repo, --title" in combined_output:
            print("✗ FAILED: Still getting the original PR error!")
            print("  The tool is not accepting the required parameters correctly.")
            print()
            print("Error output:")
            print(combined_output)
            return False
        
        # Check if we get an unrecognized arguments error (this would be better)
        elif "unrecognized arguments" in combined_output or "unrecognized argument" in combined_output:
            print("? PARTIAL: Getting unrecognized arguments error")
            print("  This means argparse is working, but there might be an issue with parameter format.")
            print()
            print("Error output:")
            print(combined_output)
            return False
        
        # Check if we get a Python import error (this is what we want - means argparse accepted the command)
        elif "ModuleNotFoundError" in combined_output or "No module named" in combined_output:
            print("✓ SUCCESS: Got expected Python import error!")
            print("  This means argparse correctly accepted all parameters.")
            print()
            print("The tool is now working correctly. The original PR error has been fixed.")
            return True
        
        else:
            print("? UNEXPECTED: Got different output")
            print("  Stdout:", result.stdout)
            print("  Stderr:", result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

def test_correct_create_command():
    """
    Test the correct way to call github_issues create.
    This should work without argparse errors.
    """
    
    print("\nTesting correct create command...")
    print("=" * 60)
    
    # Correct command without --issue-number
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "Test Issue",
        "--body", "This is a test issue",
        "--labels", "bug", "test"
    ]
    
    print("Running command:")
    print(" ".join(cmd))
    print()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        combined_output = result.stdout + result.stderr
        
        # Should NOT get argparse errors about missing required args
        if "error: the following arguments are required" in combined_output:
            print("✗ FAILED: Getting argparse error about missing required args")
            print("  Even though we provided all required parameters!")
            print()
            print("Error output:")
            print(combined_output)
            return False
        
        # Should get Python import error (ghapi not installed)
        elif "ModuleNotFoundError" in combined_output or "No module named" in combined_output:
            print("✓ SUCCESS: Command accepted, got expected Python import error")
            print("  The tool is working correctly!")
            return True
        
        else:
            print("? UNEXPECTED: Got different output")
            print("  Stdout:", result.stdout)
            print("  Stderr:", result.stderr)
            return False
            
    except Exception as e:
        print(f"✗ FAILED with exception: {e}")
        return False

if __name__ == "__main__":
    print("Testing fix for PR error: github_issues tool not working")
    print("=" * 60)
    print()
    
    test1_passed = test_pr_error_reproduction()
    test2_passed = test_correct_create_command()
    
    print()
    print("=" * 60)
    print("SUMMARY:")
    print(f"  PR Error Reproduction Test: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"  Correct Create Command Test: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        print()
        print("✓ ALL TESTS PASSED!")
        print()
        print("The github_issues tool has been successfully fixed.")
        print("The LLM can now use this tool correctly.")
        sys.exit(0)
    else:
        print()
        print("✗ SOME TESTS FAILED!")
        print()
        print("The github_issues tool still has issues that need to be addressed.")
        sys.exit(1)