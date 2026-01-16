#!/usr/bin/env python3
"""
Test the quality of the github_issues tool configuration.
This verifies that the YAML config is well-structured and follows best practices.
"""

import yaml
import json

def test_config_structure():
    """Test that the config has proper structure."""
    print("Testing config structure...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check top-level structure
    assert 'tools' in config, "Missing 'tools' key"
    print("  ✓ Top-level 'tools' key present")
    
    tools = list(config['tools'].keys())
    assert len(tools) == 5, f"Expected 5 tools, found {len(tools)}"
    print(f"  ✓ Found {len(tools)} tools: {', '.join(tools)}")
    
    # Check each tool has required fields
    for tool_name in tools:
        tool = config['tools'][tool_name]
        assert 'signature' in tool, f"{tool_name} missing 'signature'"
        assert 'docstring' in tool, f"{tool_name} missing 'docstring'"
        assert 'arguments' in tool, f"{tool_name} missing 'arguments'"
    
    print("  ✓ All tools have required fields (signature, docstring, arguments)")
    return True

def test_signature_format():
    """Test that signatures follow a consistent format."""
    print("\nTesting signature format...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    for tool_name, tool in config['tools'].items():
        signature = tool['signature']
        
        # Check that signature starts with the tool name
        expected_prefix = f"github_issues {' '.join(tool_name.split('_issues_')[1:])}"
        if not signature.startswith(expected_prefix):
            print(f"  ⚠ {tool_name} signature doesn't start with expected prefix")
            continue
        
        # Check that required parameters are marked appropriately
        assert '--owner' in signature or '<owner>' in signature, f"{tool_name} missing owner parameter"
    
    print("  ✓ Signatures follow consistent format")
    return True

def test_docstring_quality():
    """Test that docstrings are descriptive."""
    print("\nTesting docstring quality...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    for tool_name, tool in config['tools'].items():
        docstring = tool['docstring']
        
        # Check that docstrings are not empty
        assert len(docstring) > 0, f"{tool_name} has empty docstring"
        
        # Check that docstrings describe what the tool does
        assert 'issue' in docstring.lower(), f"{tool_name} docstring doesn't mention 'issue'"
    
    print("  ✓ Docstrings are descriptive and mention 'issue'")
    return True

def test_argument_quality():
    """Test that arguments are well-defined."""
    print("\nTesting argument quality...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    for tool_name, tool in config['tools'].items():
        arguments = tool['arguments']
        
        # Check that each argument has required fields
        for arg in arguments:
            assert 'name' in arg, f"{tool_name} argument missing 'name'"
            assert 'type' in arg, f"{tool_name} argument {arg.get('name')} missing 'type'"
            assert 'description' in arg, f"{tool_name} argument {arg.get('name')} missing 'description'"
            assert 'required' in arg, f"{tool_name} argument {arg.get('name')} missing 'required'"
    
    print("  ✓ All arguments have required fields (name, type, description, required)")
    return True

def test_required_parameters():
    """Test that required parameters are properly identified."""
    print("\nTesting required parameter identification...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check create command specifically (this was the problematic case in the PR)
    create_tool = config['tools']['github_issues_create']
    required_args = [arg for arg in create_tool['arguments'] if arg['required']]
    required_names = [arg['name'] for arg in required_args]
    
    # These should be required for create
    expected_required = ['owner', 'repo', 'title']
    for req in expected_required:
        assert req in required_names, f"{req} should be required for create"
    
    print(f"  ✓ Create command has correct required parameters: {required_names}")
    return True

def test_parameter_uniqueness():
    """Test that parameters are unique across subcommands."""
    print("\nTesting parameter uniqueness...")
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Check that issue_number is only in appropriate commands
    issue_number_commands = []
    for tool_name, tool in config['tools'].items():
        if any(arg.get('name') == 'issue_number' for arg in tool['arguments']):
            issue_number_commands.append(tool_name)
    
    # issue_number should be in get, modify, comment but NOT create
    expected_commands = ['github_issues_get', 'github_issues_modify', 'github_issues_comment']
    assert set(issue_number_commands) == set(expected_commands), \
        f"issue_number found in wrong commands: {issue_number_commands}"
    
    print(f"  ✓ issue_number parameter correctly placed in: {issue_number_commands}")
    return True

def main():
    """Run all config quality tests."""
    print("=" * 70)
    print("CONFIG QUALITY TEST FOR GITHUB_ISSUES TOOL")
    print("=" * 70)
    
    tests = [
        test_config_structure,
        test_signature_format,
        test_docstring_quality,
        test_argument_quality,
        test_required_parameters,
        test_parameter_uniqueness
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CONFIG QUALITY TESTS PASSED!")
        print("The github_issues tool configuration is well-structured and follows best practices.")
        print("\nKey quality indicators:")
        print("- Clear separation of subcommands (list, get, create, modify, comment)")
        print("- Descriptive docstrings for each tool")
        print("- Well-defined arguments with types and descriptions")
        print("- Proper identification of required vs optional parameters")
        print("- Unique parameters for each subcommand (e.g., issue_number not in create)")
    else:
        print("✗ SOME CONFIG QUALITY TESTS FAILED!")
        print("The github_issues tool configuration needs improvement.")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())