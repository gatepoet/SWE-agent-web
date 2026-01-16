#!/usr/bin/env python3
"""
Test script for GitHub Issues tool.
This tests the internal functions without requiring actual GitHub API calls.
Follows the pattern of other tool tests in tests/tools/
"""

import sys
from pathlib import Path

# Add the tools directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parents[2] / "tools" / "github_issues" / "bin"))

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

def test_list_issues():
    """Test list_issues function filters out PRs and returns correct data."""
    issues = gh_module.list_issues("test", "repo", state="open", max_results=10)
    
    # Should have 2 issues (PR filtered out)
    assert len(issues) == 2
    assert all(isinstance(i, dict) for i in issues)
    assert all("number" in i and "title" in i and "state" in i for i in issues)
    # Verify PR was filtered out
    assert not any("PR Issue" in i["title"] for i in issues)


def test_get_issue_details():
    """Test get_issue_details function returns correct structure."""
    issue = gh_module.get_issue_details("test", "repo", 1)
    
    assert issue is not None
    assert isinstance(issue, dict)
    required_fields = ["number", "title", "state", "html_url", "body", "labels", "assignees"]
    for field in required_fields:
        assert field in issue, f"Missing required field: {field}"
    
    # Verify labels and assignees are lists
    assert isinstance(issue["labels"], list)
    assert isinstance(issue["assignees"], list)
    assert len(issue["labels"]) == 2
    assert len(issue["assignees"]) == 1


def test_create_issue():
    """Test create_issue function returns correct structure."""
    issue = gh_module.create_issue("test", "repo", "New Bug", "Bug description", ["bug", "critical"])
    
    assert issue is not None
    assert isinstance(issue, dict)
    required_fields = ["number", "title", "html_url", "state"]
    for field in required_fields:
        assert field in issue, f"Missing required field: {field}"
    
    assert issue["title"] == "New Bug"


def test_modify_issue():
    """Test modify_issue function returns success."""
    success = gh_module.modify_issue("test", "repo", 1, title="Updated Title", body="Updated body")
    
    assert success is True


def test_add_comment():
    """Test add_comment function returns success."""
    success = gh_module.add_comment("test", "repo", 1, "This is a test comment")
    
    assert success is True


def test_add_comment_empty_body():
    """Test add_comment function handles empty body correctly."""
    # Empty body should fail
    success = gh_module.add_comment("test", "repo", 1, "")
    assert success is False
    
    # Whitespace-only body should also fail
    success = gh_module.add_comment("test", "repo", 1, "   ")
    assert success is False