#!/usr/bin/env python3
"""
Test script for GitHub Issues tool logic.
This tests the internal functions without requiring actual GitHub API calls.
"""

import sys
import os
sys.path.insert(0, '/gatepoet__SWE-agent-web/tools/github_issues/bin')

# Import the module directly
import github_issues as gh_module

# Mock the GhApi to avoid real API calls
class MockIssue:
    def __init__(self, number=1, title="Test Issue", state="open", html_url="https://github.com/test/test/issues/1", 
                 body="Test body", labels=None, assignees=None):
        self.number = number
        self.title = title
        self.state = state
        self.html_url = html_url
        self.body = body
        self.labels = labels or []
        self.assignees = assignees or []
        self.created_at = "2023-01-01T00:00:00Z"
        self.updated_at = "2023-01-01T00:00:00Z"
        self.pull_request = None

class MockLabel:
    def __init__(self, name):
        self.name = name

class MockAssignee:
    def __init__(self, login):
        self.login = login

class MockApi:
    def __init__(self, token=""):
        self.token = token
        # Create issues attribute with all the methods
        self.issues = type('', (), {
            'list_for_repo': self.list_for_repo,
            'get': self.get,
            'create': self.create,
            'update': self.update,
            'create_comment': self.create_comment
        })()
    
    def list_for_repo(self, owner, repo, state="open", per_page=100):
        """Mock list_for_repo - returns a list of mock issues."""
        # Return 2 issues (one is actually a PR to test filtering)
        issues = [
            MockIssue(number=1, title="Bug Report", state=state),
            MockIssue(number=2, title="Feature Request", state=state),
        ]
        
        # Simulate the third issue being a PR (has pull_request field)
        pr_issue = MockIssue(number=3, title="PR Issue", state=state)
        pr_issue.pull_request = {"url": "https://api.github.com/repos/test/test/pulls/1"}
        
        issues.append(pr_issue)
        return issues
    
    def get(self, owner, repo, issue_number):
        """Mock get - returns a single mock issue."""
        if issue_number == 999:
            raise Exception("Issue not found")
        return MockIssue(number=issue_number, title=f"Issue #{issue_number}", 
                        labels=[MockLabel("bug"), MockLabel("enhancement")],
                        assignees=[MockAssignee("user1")])
    
    def create(self, owner, repo, **kwargs):
        """Mock create - returns a new mock issue."""
        return MockIssue(number=42, title=kwargs.get("title", "New Issue"), 
                        body=kwargs.get("body", ""), state="open")
    
    def update(self, owner, repo, issue_number, **kwargs):
        """Mock update - returns True on success."""
        return True
    
    def create_comment(self, owner, repo, issue_number, body):
        """Mock create_comment - returns True on success."""
        return True

# Set up mock API for testing
gh_module.set_api_class(MockApi)

def test_get_github_token():
    """Test token retrieval logic."""
    print("Testing get_github_token...")
    
    # Test with empty environment
    old_env = os.environ.get("GITHUB_TOKEN", "")
    try:
        os.environ["GITHUB_TOKEN"] = ""
        token = gh_module.get_github_token()
        assert token == "", f"Expected empty token, got {token}"
        print("PASS: Empty environment token works")
    finally:
        if old_env:
            os.environ["GITHUB_TOKEN"] = old_env
    
    # Test with set environment
    try:
        os.environ["GITHUB_TOKEN"] = "test_token"
        token = gh_module.get_github_token()
        assert token == "test_token", f"Expected test_token, got {token}"
        print("PASS: Environment token works")
    finally:
        os.environ["GITHUB_TOKEN"] = old_env
    
    return True

def test_list_issues():
    """Test list_issues function."""
    print("Testing list_issues...")
    issues = gh_module.list_issues("test", "repo", state="open", max_results=10)
    
    # Should have 2 issues (PR filtered out)
    assert len(issues) == 2, f"Expected 2 issues, got {len(issues)}"
    assert all("pull_request" not in i for i in issues), "PRs should be filtered out"
    print("PASS: list_issues works correctly")
    return True

def test_get_issue_details():
    """Test get_issue_details function."""
    print("Testing get_issue_details...")
    issue = gh_module.get_issue_details("test", "repo", 1)
    
    assert issue is not None, "Issue should not be None"
    assert issue["number"] == 1, f"Expected number 1, got {issue['number']}"
    assert "labels" in issue, "Labels should be present"
    assert len(issue["labels"]) == 2, f"Expected 2 labels, got {len(issue['labels'])}"
    print("PASS: get_issue_details works correctly")
    return True

def test_create_issue():
    """Test create_issue function."""
    print("Testing create_issue...")
    issue = gh_module.create_issue("test", "repo", "New Bug", "Bug description", ["bug", "critical"])
    
    assert issue is not None, "Issue should not be None"
    assert issue["title"] == "New Bug", f"Expected 'New Bug', got {issue['title']}"
    print("PASS: create_issue works correctly")
    return True

def test_modify_issue():
    """Test modify_issue function."""
    print("Testing modify_issue...")
    success = gh_module.modify_issue("test", "repo", 1, title="Updated Title", body="Updated body")
    
    assert success is True, "Modify should succeed"
    print("PASS: modify_issue works correctly")
    return True

def test_add_comment():
    """Test add_comment function."""
    print("Testing add_comment...")
    success = gh_module.add_comment("test", "repo", 1, "This is a test comment")
    
    assert success is True, "Comment should succeed"
    print("PASS: add_comment works correctly")
    return True

def main():
    """Run all tests."""
    print("Running GitHub Issues tool logic tests...\n")
    
    tests = [
        test_get_github_token,
        test_list_issues,
        test_get_issue_details,
        test_create_issue,
        test_modify_issue,
        test_add_comment,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} raised exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())