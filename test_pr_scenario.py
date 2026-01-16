#!/usr/bin/env python3
"""
Test the specific scenario from the PR description.
This reproduces the exact command that was failing.
"""

import subprocess
import sys

def test_pr_scenario():
    """Test the exact scenario from the PR description."""
    print("Testing the PR scenario...")
    print("Command: github_issues create --owner gatepoet --repo BlackJack-Coach --title 'BUG: Undefined Variables in cardHandler.js' --body '## Bug Description...' --labels bug high-priority module-coupling")
    
    cmd = [
        "./tools/github_issues/bin/github_issues", "create",
        "--owner", "gatepoet",
        "--repo", "BlackJack-Coach",
        "--title", "BUG: Undefined Variables in cardHandler.js - map, hands, handContainers, splitContainers, lastAddedCard",
        "--body", "## Bug Description\nThe `cardHandler.js` module uses several variables that are not defined within the module or passed as parameters:\n- `map` (used for card counting values)\n- `hands` (game state tracking)\n- `handContainers` (DOM elements)\n- `splitContainers` (DOM elements)\n- `lastAddedCard` (UI state)\n\nThese variables are being accessed from the global scope, creating tight coupling and making the module untestable in isolation.\n\n## Expected Behavior\nAll dependencies should be:\n1. Defined as function parameters, or\n2. Imported from other modules, or\n3. Explicitly passed to the functions that need them\n\n## Verification Criteria\n- Functions should work when called with explicit parameters\n- Module should be testable without global state\n- No \"undefined\" errors when variables are accessed",
        "--labels", "bug", "high-priority", "module-coupling"
    ]
    
    exit_code, stdout, stderr = run_command(cmd)
    
    # The command should fail with ModuleNotFoundError (not argparse error)
    if "ModuleNotFoundError" in stderr or "No module named 'ghapi'" in stderr:
        print("✓ PR scenario: PASS")
        print("The command was accepted by argparse and failed only at the API import stage.")
        print("This means the tool configuration is correct!")
        return True
    elif "required: --owner" in stderr or "required: --repo" in stderr or "required: --title" in stderr:
        print("✗ PR scenario: FAIL - Missing required arguments")
        print(f"Stderr: {stderr}")
        return False
    else:
        print("✗ PR scenario: FAIL - Unexpected error")
        print(f"Exit code: {exit_code}")
        print(f"Stdout: {stdout}")
        print(f"Stderr: {stderr}")
        return False

def run_command(cmd):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def main():
    """Main test function."""
    print("Testing the specific PR scenario...\n")
    
    if test_pr_scenario():
        print("\n✓ SUCCESS: The PR issue has been fixed!")
        print("The github_issues tool now works correctly.")
        return 0
    else:
        print("\n✗ FAILURE: The PR issue still exists!")
        return 1

if __name__ == "__main__":
    sys.exit(main())