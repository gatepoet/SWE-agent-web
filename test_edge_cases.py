#!/usr/bin/env python3
"""
Test edge cases and error handling for the GitHub Issues tool.
"""

import sys
sys.path.insert(0, '/gatepoet__SWE-agent-web/tools/github_issues/bin')

from github_issues import set_api_class

class MockApi:
    """Mock GitHub API that simulates some error conditions."""
    def __init__(self, token=""):
        self.token = token
        self.issues = type('', (), {
            'list_for_repo': self.list_for_repo,
            'get': self.get,
            'create': self.create,
            'update': self.update,
            'create_comment': self.create_comment
        })()
    
    def list_for_repo(self, owner, repo, state="open", per_page=100):
        """Mock list_for_repo - returns empty list for edge case."""
        if owner == "empty_repo":
            return []
        return [{"number": 1, "title": "Test Issue", "state": state}]
    
    def get(self, owner, repo, issue_number):
        """Mock get - returns None for non-existent issue."""
        if issue_number == 999:
            return None
        return {"number": issue_number, "title": f"Issue #{issue_number}", "state": "open"}
    
    def create(self, owner, repo, **kwargs):
        """Mock create - handles empty title."""
        if not kwargs.get("title"):
            return None
        return {"number": 42, "title": kwargs["title"], "state": "open"}
    
    def update(self, owner, repo, issue_number, **kwargs):
        """Mock update - returns False for invalid updates."""
        if issue_number < 0:
            return False
        return True
    
    def create_comment(self, owner, repo, issue_number, body):
        """Mock create_comment - handles empty body."""
        if not body or not body.strip():
            return False
        return True

def test_empty_results():
    """Test handling of empty results."""
    print("Testing: Empty results...")
    set_api_class(MockApi)
    
    from github_issues import list_issues
    issues = list_issues("empty_repo", "test_repo", "open", 10)
    assert issues == []
    print("✓ Empty results handled correctly")

def test_nonexistent_issue():
    """Test handling of non-existent issue."""
    print("Testing: Non-existent issue...")
    set_api_class(MockApi)
    
    from github_issues import get_issue_details
    issue = get_issue_details("test_owner", "test_repo", 999)
    assert issue is None
    print("✓ Non-existent issue handled correctly")

def test_invalid_create():
    """Test handling of invalid create request."""
    print("Testing: Invalid create request...")
    set_api_class(MockApi)
    
    from github_issues import create_issue
    issue = create_issue("test_owner", "test_repo", "", "")
    assert issue is None
    print("✓ Invalid create request handled correctly")

def test_invalid_modify():
    """Test handling of invalid modify request."""
    print("Testing: Invalid modify request...")
    set_api_class(MockApi)
    
    from github_issues import modify_issue
    success = modify_issue("test_owner", "test_repo", -1, title="Test")
    assert success == False
    print("✓ Invalid modify request handled correctly")

def test_invalid_comment():
    """Test handling of invalid comment."""
    print("Testing: Invalid comment...")
    set_api_class(MockApi)
    
    from github_issues import add_comment
    success = add_comment("test_owner", "test_repo", 123, "   ")
    assert success == False
    print("✓ Invalid comment handled correctly")

def test_json_output():
    """Test that JSON output is valid."""
    print("Testing: JSON output format...")
    import json
    
    set_api_class(MockApi)
    from github_issues import list_issues, get_issue_details
    
    # Test list output can be parsed as JSON
    issues = list_issues("test_owner", "test_repo", "open", 10)
    json.dumps(issues)  # This will raise an exception if not valid JSON
    
    # Test get output can be parsed as JSON
    issue = get_issue_details("test_owner", "test_repo", 123)
    json.dumps(issue)  # This will raise an exception if not valid JSON
    
    print("✓ JSON output format is valid")

if __name__ == "__main__":
    print("Testing edge cases and error handling...")
    print("=" * 50)
    
    test_empty_results()
    test_nonexistent_issue()
    test_invalid_create()
    test_invalid_modify()
    test_invalid_comment()
    test_json_output()
    
    print("=" * 50)
    print("✅ All edge cases handled correctly!")