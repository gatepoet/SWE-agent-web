"""GitHub API integration for the SWE-agent web interface."""

from __future__ import annotations

import logging
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)

# Global cache for GitHub search results to avoid duplicate API calls
github_search_cache = {}
github_search_cache_timestamp = {}


def parse_github_query(query: str) -> str:
    """
    Parse user input query and convert it to optimal GitHub search format.
    """
    query = query.strip()

    if not query:
        return ""

    # If query already contains GitHub search operators, use as-is
    github_operators = ["in:", "user:", "org:", "repo:", "language:", "stars:", "forks:", "owner:"]
    if any(op in query for op in github_operators):
        return query

    # Check if it looks like a full repository path (owner/repo)
    if "/" in query:
        parts = query.split("/")
        if len(parts) == 2 and all(part.strip() for part in parts):
            owner, repo = parts
            # Search for repository belonging to owner
            return f"{repo} in:name owner:{owner}"

    # Default: search for the query in repository names
    return f"{query} in:name OR {query} in:owner"


def search_github_repos(query: str, max_results: int = 10, github_token: str = "") -> list[dict[str, Any]]:
    """Search for GitHub repositories using the GitHub API with caching and improved query parsing."""
    # Normalize query
    normalized_query = parse_github_query(query)
    if not normalized_query:
        return []

    # Check cache first (cache for 30 seconds to avoid duplicate API calls)
    current_time = time.time()
    cache_key = f"{normalized_query}:{max_results}"

    if cache_key in github_search_cache:
        if current_time - github_search_cache_timestamp.get(cache_key, 0) < 30:
            logger.debug(f"Using cached results for query: {query}")
            return github_search_cache[cache_key].copy()

    # Use provided token or fall back to environment variable
    token = github_token if github_token else os.getenv("GITHUB_TOKEN", "")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    headers["Accept"] = "application/vnd.github+json"

    # Build search URL
    search_url = (
        f"https://api.github.com/search/repositories?q={normalized_query}&per_page={max_results}&sort=stars&order=desc"
    )

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        repositories = []

        for repo in data.get("items", []):
            repo_info = {
                "full_name": repo.get("full_name", ""),
                "name": repo.get("name", ""),
                "owner": repo.get("owner", {}).get("login", ""),
                "html_url": repo.get("html_url", ""),
                "description": repo.get("description", ""),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
            }
            repositories.append(repo_info)

        # Cache the results
        github_search_cache[cache_key] = repositories.copy()
        github_search_cache_timestamp[cache_key] = current_time

        return repositories

    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        # Return empty results on error
        return []