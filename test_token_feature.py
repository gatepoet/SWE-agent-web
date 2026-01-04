#!/usr/bin/env python3
"""
Test script to verify GitHub token feature implementation.
This tests the new API endpoints and functionality.
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_token_validation_endpoint():
    """Test the GitHub token validation endpoint."""
    print("Testing GitHub token validation endpoint...")
    
    from sweagent.api.server import app
    
    with app.test_client() as client:
        # Test 1: Missing token
        response = client.post('/api/github/validate', json={})
        print(f"Test 1 - Missing token: Status {response.status_code}")
        data = response.get_json()
        assert response.status_code == 400
        assert "error" in data
        print("✓ Correctly returns error for missing token")
        
        # Test 2: Empty token
        response = client.post('/api/github/validate', json={"token": ""})
        print(f"Test 2 - Empty token: Status {response.status_code}")
        data = response.get_json()
        assert response.status_code == 400
        assert "error" in data
        print("✓ Correctly returns error for empty token")
        
        # Test 3: Invalid token format (this would fail authentication)
        response = client.post('/api/github/validate', json={"token": "invalid_token_12345"})
        print(f"Test 3 - Invalid token: Status {response.status_code}")
        data = response.get_json()
        assert "valid" in data
        assert data["valid"] == False
        print("✓ Correctly validates invalid token")
    
    print("✓ Token validation endpoint tests passed!")

def test_token_in_search_endpoint():
    """Test that GitHub search endpoint accepts token."""
    print("\nTesting GitHub search endpoint with token...")
    
    from sweagent.api.server import app
    
    with app.test_client() as client:
        # Test that the endpoint accepts github_token parameter
        response = client.get('/api/github/search?q=test')
        print(f"Search without token: Status {response.status_code}")
        assert response.status_code == 200
        
        # Test with JSON body containing token (this tests our new functionality)
        response = client.post('/api/github/search', json={
            "q": "test",
            "github_token": "test_token_123"
        })
        print(f"Search with token: Status {response.status_code}")
        assert response.status_code == 200
    
    print("✓ Search endpoint accepts token parameter!")

def test_create_run_with_token():
    """Test that create run endpoint accepts GitHub token."""
    print("\nTesting create run endpoint with token...")
    
    from sweagent.api.server import app
    
    with app.test_client() as client:
        # Test creating a run with GitHub token
        response = client.post('/api/runs', json={
            "problem_statement": "Test problem",
            "github_token": "test_github_token_123"
        })
        print(f"Create run with token: Status {response.status_code}")
        assert response.status_code == 202
        data = response.get_json()
        assert "run_id" in data
    
    print("✓ Create run endpoint accepts GitHub token!")

def test_frontend_elements():
    """Test that frontend HTML contains the new elements."""
    print("\nTesting frontend HTML elements...")
    
    from sweagent.api.server import app
    
    with app.test_client() as client:
        response = client.get('/')
        html_content = response.data.decode('utf-8')
        
        # Check for GitHub token input field
        assert 'id="githubToken"' in html_content, "GitHub token input field not found"
        print("✓ Found GitHub token input field")
        
        # Check for validation button
        assert 'id="validateTokenBtn"' in html_content, "Validation button not found"
        print("✓ Found validation button")
        
        # Check for validation status display
        assert 'id="tokenValidationStatus"' in html_content, "Validation status display not found"
        print("✓ Found validation status display")
    
    print("✓ Frontend elements are present!")

if __name__ == "__main__":
    try:
        test_token_validation_endpoint()
        test_token_in_search_endpoint()
        test_create_run_with_token()
        test_frontend_elements()
        print("\n🎉 All tests passed! GitHub token feature is working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)