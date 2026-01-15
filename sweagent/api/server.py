"""Flask API server for SWE-agent web interface."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import threading
from typing import Any
import uuid

import requests
import yaml
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO

# Import SWE-agent components
from sweagent.api.github_api import search_github_repos
from sweagent.api.models import RunState
from sweagent.api.run_manager import (
    active_runs,
    create_agent_config,
    generate_run_id,
    get_run_state,
    remove_run_state,
    run_agent_async,
    runs_lock,
)
from sweagent.run.run_single import RunSingleConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")


def emit_update(run_id: str, event: str, data: Any):
    """Emit an update to all connected clients for a run."""
    socketio.emit(f"run_{run_id}_{event}", data)
    socketio.emit("update", {"run_id": run_id, **data})


@app.route("/api/runs", methods=["GET"])
def list_runs():
    """List all active and completed runs."""
    with runs_lock:
        runs = [state.to_dict() for state in active_runs.values()]
    return jsonify({"runs": runs})


@app.route("/api/runs/<run_id>", methods=["GET"])
def get_run(run_id: str):
    """Get information about a specific run."""
    state = get_run_state(run_id)
    if not state:
        return jsonify({"error": f"Run {run_id} not found"}), 404

    return jsonify(state.to_dict())


@app.route("/api/runs/<run_id>/trajectory", methods=["GET"])
def get_trajectory(run_id: str):
    """Get the trajectory for a specific run."""
    state = get_run_state(run_id)
    if not state:
        return jsonify({"error": f"Run {run_id} not found"}), 404

    # Get trajectory from WebSocket hook if available, otherwise use stored steps
    trajectory_steps = []
    if state.websocket_hook and state.websocket_hook.trajectory_steps:
        trajectory_steps = state.websocket_hook.trajectory_steps
    elif state.trajectory_steps:
        trajectory_steps = state.trajectory_steps

    # Return the full trajectory with history
    result = {
        "trajectory": trajectory_steps,
        "problem_statement": state.problem_statement,
        "exit_status": state.exit_status,
        "model_stats": state.model_stats,
    }
    return jsonify(result)


@app.route("/api/runs", methods=["POST"])
def create_run():
    """Create a new SWE-agent run."""
    data = request.get_json()

    if not data or "problem_statement" not in data:
        return jsonify({"error": "problem_statement is required"}), 400

    problem_statement = data["problem_statement"]
    config_path = data.get("config_path", "./config/api_default.yaml")
    inline_config = data.get("config")
    github_token = data.get("github_token", "")

    # Validate configuration if provided
    # if inline_config:
    #     try:
    #         # Try to validate the structure
    #         test_config = RunSingleConfig.model_validate(inline_config)
    #     except Exception as e:
    #         return jsonify({
    #             "error": f"Invalid configuration: {str(e)}",
    #             "details": "Please check your configuration format and values."
    #         }), 400

    run_id = generate_run_id()

    # Start the agent in a background thread
    # Use threading to avoid async issues with Flask
    def start_agent_task():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                run_agent_async(run_id, problem_statement, config_path, inline_config, github_token, emit_update)
            )
        finally:
            loop.close()

    thread = threading.Thread(target=start_agent_task, daemon=True)
    thread.start()

    return jsonify({"run_id": run_id, "status": "started", "message": f"Run {run_id} started"}), 202

def is_production():
    return os.getenv('NODE_ENV') == 'production'

if not is_production():
    @app.route('/favicon.ico')
    def ignore_favicon():
        return ''  # Chrome devtools requires this
    
@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def serve_dev_server():
    if not is_production():
        return jsonify({
            "workspace": {
                "root": str(Path(__file__).parent.resolve()),
                "uuid": str(uuid.uuid4())
            }
        })
    return '', 204  # No content in production

@app.route("/api/models", methods=["GET"])
def get_models():
    """Get available models from models.json."""
    try:
        # Look for models.json in the root directory
        models_path = Path(__file__).parent.parent.parent / "models.json"

        if not models_path.exists():
            return jsonify({"error": "models.json not found", "available_models": []}), 404

        with open(models_path) as f:
            models_data = json.load(f)

        # Extract just the model names for the dropdown
        model_names = list(models_data.keys())

        return jsonify({"models": models_data, "model_names": model_names})
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        return jsonify({"error": str(e), "available_models": []}), 500


@app.route("/api/github/validate", methods=["POST"])
def validate_github_token():
    """Validate a GitHub token."""
    try:
        data = request.get_json()
        if not data or "token" not in data:
            return jsonify({"error": "GitHub token is required", "valid": False}), 400
        
        token = data["token"].strip()
        if not token:
            return jsonify({"error": "GitHub token cannot be empty", "valid": False}), 400
        
        # Validate the GitHub token by making a test API call
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                return jsonify({"valid": True, "message": "GitHub token is valid"}), 200
            elif response.status_code == 401:
                return jsonify({"error": "Invalid GitHub token: authentication failed", "valid": False}), 401
            else:
                return jsonify({"error": f"GitHub API error: {response.status_code}", "valid": False}), response.status_code
        except requests.exceptions.RequestException as e:
            logger.error(f"Error validating GitHub token: {e}")
            if "Connection error" in str(e) or "timeout" in str(e):
                return jsonify({"error": "Failed to connect to GitHub API. Please check your internet connection.", "valid": False}), 503
            else:
                return jsonify({"error": f"Error validating token: {str(e)}", "valid": False}), 500
    
    except Exception as e:
        logger.error(f"Error in token validation endpoint: {e}")
        return jsonify({"error": "Internal server error", "valid": False}), 500


@app.route("/api/github/search", methods=["GET", "POST"])
def search_github_repositories():
    """Search for GitHub repositories by name or query."""
    try:
        # Get search query from either GET params or POST body
        if request.method == "GET":
            query = request.args.get("q", "")
        else:  # POST
            # Try JSON first, then form data
            json_data = request.get_json(silent=True)
            if json_data and "q" in json_data:
                query = json_data["q"]
            elif request.form and "q" in request.form:
                query = request.form["q"]
            else:
                query = ""

        if not query:
            return jsonify({"error": "Search query 'q' is required", "repositories": []}), 400

        # Get GitHub token from request if provided (for authenticated searches)
        github_token = ""
        json_data = request.get_json(silent=True)
        if json_data and "github_token" in json_data:
            github_token = json_data["github_token"]
        
        # Use GitHub API to search for repositories
        results = search_github_repos(query, github_token=github_token)

        return jsonify({"query": query, "repositories": results})
    except Exception as e:
        logger.error(f"Error searching GitHub repositories: {e}")
        return jsonify({"error": str(e), "repositories": []}), 500


@app.route("/api/github/issues", methods=["GET"])
def get_github_issues():
    """Get open issues for a specific GitHub repository."""
    try:
        # Get repository parameter from query string
        repo = request.args.get("repo", "")

        if not repo:
            return jsonify({"error": "Repository parameter 'repo' is required (format: owner/repo)", "issues": []}), 400

        # Get GitHub token from query string or use environment variable
        github_token = request.args.get("github_token", os.getenv("GITHUB_TOKEN", ""))
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        headers["Accept"] = "application/vnd.github+json"

        # Build GitHub API URL for repository issues
        # Format: https://api.github.com/repos/owner/repo/issues
        api_url = f"https://api.github.com/repos/{repo}/issues"

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            issues = []

            for issue in data:
                # Only include open issues
                if issue.get("state") == "open":
                    issue_info = {
                        "number": issue.get("number", 0),
                        "title": issue.get("title", ""),
                        "url": issue.get("html_url", ""),
                        "body": issue.get("body", ""),
                        "created_at": issue.get("created_at", ""),
                        "updated_at": issue.get("updated_at", ""),
                        "comments": issue.get("comments", 0),
                    }
                    issues.append(issue_info)

            return jsonify({"repository": repo, "issues": issues})

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            # Return empty results on error
            return jsonify(
                {"error": f"Failed to fetch issues from GitHub: {str(e)}", "repository": repo, "issues": []}
            ), 500

    except Exception as e:
        logger.error(f"Error getting GitHub issues: {e}")
        return jsonify({"error": str(e), "issues": []}), 500


@app.route("/api/github/branches", methods=["GET"])
def get_github_branches():
    """Get branches for a specific GitHub repository."""
    try:
        # Get repository parameter from query string
        repo = request.args.get("repo", "")

        if not repo:
            return jsonify({"error": "Repository parameter 'repo' is required (format: owner/repo)", "branches": []}), 400

        # Get GitHub token from query string or use environment variable
        github_token = request.args.get("github_token", os.getenv("GITHUB_TOKEN", ""))
        headers = {}
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        headers["Accept"] = "application/vnd.github+json"

        # Build GitHub API URL for repository branches
        # Format: https://api.github.com/repos/owner/repo/branches
        api_url = f"https://api.github.com/repos/{repo}/branches"

        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            branches = []

            for branch in data:
                if "name" in branch:
                    branches.append(branch["name"])

            return jsonify({"repository": repo, "branches": branches})

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            # Return empty results on error
            return jsonify(
                {"error": f"Failed to fetch branches from GitHub: {str(e)}", "repository": repo, "branches": []}
            ), 500

    except Exception as e:
        logger.error(f"Error getting GitHub branches: {e}")
        return jsonify({"error": str(e), "branches": []}), 500


@app.route("/api/status", methods=["GET"])
def get_status():
    """Get server status."""
    import time
    return jsonify(
        {
            "status": "running",
            "active_runs": len(active_runs),
            "timestamp": time.time(),
        }
    )


@app.route("/api/config/schema", methods=["GET"])
def get_config_schema():
    """Get the configuration schema for SWE-agent."""
    try:
        # Get JSON schema from RunSingleConfig
        schema = RunSingleConfig.model_json_schema()

        return jsonify(
            {
                "schema": schema,
                "description": "Configuration schema for SWE-agent runs. Use this to understand available options.",
                "example_configs": {
                    "simple_text": {
                        "problem_statement": "Fix the bug in login.py",
                        "config": {"agent": {"model": {"temperature": 0.7}}},
                    },
                    "github_issue": {
                        "problem_statement": {
                            "type": "github",
                            "github_url": "https://github.com/owner/repo/issues/123",
                        }
                    },
                },
            }
        )
    except Exception as e:
        logger.error(f"Error generating config schema: {e}")
        return jsonify({"error": "Unable to generate configuration schema"}), 500


@app.route("/", methods=["GET"])
def serve_index():
    """Serve the main HTML page."""
    return send_from_directory(app.static_folder, "index.html")


# Serve all the images in the workspace root folders /assets and /docs/assets
@app.route("/assets/<path:filename>", methods=["GET"])
def serve_static(filename: str):
    """Serve static files."""
    return send_from_directory(Path(app.static_folder).joinpath("assets"), filename)


@app.route("/docs/assets/<path:filename>", methods=["GET"])
def serve_docs_static(filename: str):
    """Serve static files."""
    return send_from_directory(os.path.join(app.static_folder, "docs/assets"), filename)

@socketio.on("connect")
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")


def get_parser() -> argparse.ArgumentParser:
    """Get argument parser for the API server."""
    parser = argparse.ArgumentParser(description="SWE-agent API Server")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    return parser


async def main(args: list[str] | None = None):
    """Main entry point for the API server."""
    import threading
    import time
    
    parser = get_parser()
    args_parsed = parser.parse_args(args)

    logger.info(f"Starting SWE-agent API server on {args_parsed.host}:{args_parsed.port}")

    # Create static directory if it doesn't exist
    static_dir = Path(app.static_folder)
    static_dir.mkdir(exist_ok=True)

    try:
        socketio.run(
            app,
            host=args_parsed.host,
            port=args_parsed.port,
            debug=args_parsed.debug,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server...")


def run_from_cli(args: list[str] | None = None):
    """Run the API server from command line arguments."""
    asyncio.run(main(args))


if __name__ == "__main__":
    run_from_cli()