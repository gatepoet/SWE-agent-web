#!/usr/bin/env python3
"""
Unit tests for GitHub Issues tool.
This tests the core functionality of the github_issues module.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from tests.utils import make_python_tool_importable

# Make the github_issues tool importable
make_python_tool_importable("tools/github_issues/bin/github_issues.py", "github_issues")
from github_issues import (  # type: ignore[import]
    add_comment,
    create_issue,
    get_issue_details,
    list_issues,
    modify_issue,
    set_api_class,
)


class MockIssue:
    """Mock GitHub issue object."""
    
    def __init__(self, number=1, title="Test Issue", state="open", html_url="https://github.com/test/test/1", body="Test body", labels=None, assignees=None):
        self.number = number
        self.title = title
        self.state = state
        self.html_url = html_url
        self.body = body
        self.labels = labels or []
        self.assignees = assignees or []
        self.pull_request = None  # Not a PR
        self.created_at = "2023-01-01T00:00:00Z"
        self.updated_at = "2023-01-02T00:00:00Z"


class MockIssuesAPI:
    """Mock GitHub Issues API class."""
    
    @staticmethod
    def list_for_repo(owner, repo, state="open", per_page=100):
        """Mock list issues for repo."""
        # Return mock issues
        yield MockIssue(number=1, title="First Issue", state=state)
        yield MockIssue(number=2, title="Second Issue", state=state)
    
    @staticmethod
    def get(owner, repo, issue_number):
        """Mock get issue."""
        if issue_number == 1:
            # Create mock label and assignee objects
            class MockLabel:
                def __init__(self, name):
                    self.name = name
            
            class MockAssignee:
                def __init__(self, login):
                    self.login = login
            
            return MockIssue(
                number=1,
                title="Test Issue",
                state="open",
                body="This is a test issue",
                labels=[MockLabel("bug"), MockLabel("enhancement")],
                assignees=[MockAssignee("user1")]
            )
        return None
    
    @staticmethod
    def create(owner, repo, **kwargs):
        """Mock create issue."""
        mock_issue = MockIssue(
            number=999,
            title=kwargs.get("title", "New Issue"),
            state="open",
            body=kwargs.get("body", "")
        )
        return mock_issue
    
    @staticmethod
    def update(owner, repo, issue_number, **kwargs):
        """Mock update issue."""
        return True
    
    @staticmethod
    def create_comment(owner, repo, issue_number, body):
        """Mock create comment."""
        return True


class MockAPI:
    """Mock GitHub API class."""
    
    def __init__(self, token=None):
        self.token = token
        self.issues = MockIssuesAPI()


@pytest.fixture
def mock_api():
    """Fixture providing a mock API."""
    api = MockAPI()
    set_api_class(api.__class__)
    yield api
    # Reset to None after test
    set_api_class(None)


def test_list_issues(mock_api):
    """Test listing issues."""
    issues = list_issues("test_owner", "test_repo", state="open", max_results=10)
    
    assert len(issues) == 2
    assert issues[0]["number"] == 1
    assert issues[0]["title"] == "First Issue"
    assert issues[0]["state"] == "open"
    assert "html_url" in issues[0]
    assert "body" in issues[0]


def test_list_issues_filter_prs():
    """Test that pull requests are filtered out."""
    # Create a mock issue with PR
    pr_mock = MockIssue()
    pr_mock.pull_request = {"url": "https://api.github.com/repos/test/test/pulls/1"}
    
    # Patch the static method directly
    with patch.object(MockIssuesAPI, 'list_for_repo', return_value=[pr_mock]):
        issues = list_issues("test_owner", "test_repo", state="open", max_results=10)
        assert len(issues) == 0


def test_list_issues_max_results(mock_api):
    """Test that max_results parameter works."""
    issues = list_issues("test_owner", "test_repo", state="open", max_results=1)
    assert len(issues) == 1


def test_get_issue_details(mock_api):
    """Test getting issue details."""
    issue = get_issue_details("test_owner", "test_repo", 1)
    
    assert issue is not None
    assert issue["number"] == 1
    assert issue["title"] == "Test Issue"
    assert issue["state"] == "open"
    assert issue["body"] == "This is a test issue"
    assert "labels" in issue
    assert len(issue["labels"]) == 2
    assert "bug" in issue["labels"]
    assert "assignees" in issue
    assert len(issue["assignees"]) == 1
    assert "user1" in issue["assignees"]


def test_get_issue_details_not_found(mock_api):
    """Test getting details for non-existent issue."""
    issue = get_issue_details("test_owner", "test_repo", 999)
    assert issue is None


def test_create_issue(mock_api):
    """Test creating a new issue."""
    issue = create_issue(
        "test_owner",
        "test_repo",
        title="New Bug",
        body="This is a bug report",
        labels=["bug", "critical"]
    )
    
    assert issue is not None
    assert issue["number"] == 999
    assert issue["title"] == "New Bug"
    assert issue["state"] == "open"
    assert "html_url" in issue


def test_create_issue_minimal(mock_api):
    """Test creating an issue with minimal parameters."""
    issue = create_issue("test_owner", "test_repo", title="Minimal Issue")
    
    assert issue is not None
    assert issue["title"] == "Minimal Issue"


def test_modify_issue(mock_api):
    """Test modifying an existing issue."""
    result = modify_issue(
        "test_owner",
        "test_repo",
        1,
        title="Updated Title",
        body="Updated body content",
        state="closed",
        labels=["updated"]
    )
    
    assert result is True


def test_modify_issue_no_changes(mock_api):
    """Test modifying issue with no changes."""
    result = modify_issue("test_owner", "test_repo", 1)
    # Should return True for no-op
    assert result is True


def test_add_comment(mock_api):
    """Test adding a comment to an issue."""
    result = add_comment("test_owner", "test_repo", 1, "This is a test comment")
    
    assert result is True


def test_add_comment_empty_body(mock_api):
    """Test that empty comment body returns False."""
    result = add_comment("test_owner", "test_repo", 1, "")
    assert result is False


def test_add_comment_whitespace_only(mock_api):
    """Test that whitespace-only comment body returns False."""
    result = add_comment("test_owner", "test_repo", 1, "   ")
    assert result is False


def test_get_github_token_from_env(tmp_path):
    """Test getting GitHub token from environment variable."""
    with patch.dict("os.environ", {"GITHUB_TOKEN": "test_token_123"}):
        make_python_tool_importable("tools/github_issues/bin/github_issues.py", "github_issues")
        from github_issues import get_github_token  # type: ignore[import]
        
        token = get_github_token()
        assert token == "test_token_123"


def test_get_github_token_from_registry(tmp_path):
    """Test getting GitHub token from registry file."""
    # Create a temporary registry file
    registry_file = tmp_path / "registry.json"
    registry_file.write_text(json.dumps({"GITHUB_TOKEN": "registry_token_456"}))
    
    with patch("os.environ", {}), \
         patch("builtins.open", create=True) as mock_open:
        # Setup the mock to return our file
        mock_file = MagicMock()
        mock_file.read.return_value = registry_file.read_text()
        mock_open.return_value.__enter__.return_value = mock_file
        
        make_python_tool_importable("tools/github_issues/bin/github_issues.py", "github_issues")
        from github_issues import get_github_token  # type: ignore[import]
        
        token = get_github_token()
        assert token == "registry_token_456"


def test_get_github_token_fallback():
    """Test that empty string is returned when no token is available."""
    with patch.dict("os.environ", {}, clear=True):
        make_python_tool_importable("tools/github_issues/bin/github_issues.py", "github_issues")
        from github_issues import get_github_token  # type: ignore[import]
        
        token = get_github_token()
        assert token == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])