#!/usr/bin/env python3
"""
Test script to validate the github_issues config.
"""

import yaml

def test_config_structure():
    """Test that the config has the correct structure."""
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("Config loaded successfully!")
    print("\nTools found:")
    for tool_name in config['tools'].keys():
        print(f"  - {tool_name}")
    
    # Check that all tools have the required fields
    required_fields = ['signature', 'docstring', 'arguments']
    
    for tool_name, tool_config in config['tools'].items():
        print(f"\nChecking {tool_name}...")
        for field in required_fields:
            if field not in tool_config:
                print(f"  ERROR: Missing required field '{field}'")
                return False
            else:
                print(f"  ✓ Has '{field}'")
        
        # Check arguments structure
        for arg in tool_config['arguments']:
            if 'name' not in arg:
                print(f"  ERROR: Argument missing 'name' field")
                return False
            
            if 'type' not in arg:
                print(f"  ERROR: Argument '{arg['name']}' missing 'type' field")
                return False
            
            # Check for array arguments with argument_format
            if arg.get('type') == 'array':
                if 'argument_format' not in arg:
                    print(f"  WARNING: Array argument '{arg['name']}' missing 'argument_format'")
                else:
                    print(f"  ✓ Array argument '{arg['name']}' has argument_format: {arg['argument_format']}")
    
    print("\n✓ All checks passed!")
    return True

def test_signature_format():
    """Test that signatures follow the expected format."""
    
    with open('tools/github_issues/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    print("\nChecking signature formats...")
    for tool_name, tool_config in config['tools'].items():
        signature = tool_config['signature']
        print(f"{tool_name}: {signature}")
        
        # Check that signatures start with the tool name
        if not signature.startswith(tool_name.replace('_', ' ')):
            print(f"  WARNING: Signature doesn't start with tool name")
    
    return True

if __name__ == "__main__":
    success = test_config_structure() and test_signature_format()
    if success:
        print("\n✓ All validation tests passed!")
    else:
        print("\n✗ Some validation tests failed!")
        exit(1)