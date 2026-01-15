"""Run management for the SWE-agent API."""

from __future__ import annotations
from sweagent.utils.github import _get_gh_issue_data

import asyncio
import logging
import os
import threading
import time
from typing import Any

from sweagent.api.models import RunState
from sweagent.api.websocket_hook import WebSocketHook
from sweagent.run.run_single import RunSingleConfig
from sweagent.types import AgentRunResult

logger = logging.getLogger(__name__)

# Global state for active runs
active_runs: dict[str, Any] = {}
runs_lock = threading.Lock()


def get_run_state(run_id: str) -> RunState | None:
    """Get run state by ID."""
    with runs_lock:
        return active_runs.get(run_id)


def set_run_state(run_id: str, state: RunState):
    """Set run state by ID."""
    with runs_lock:
        active_runs[run_id] = state


def remove_run_state(run_id: str):
    """Remove run state by ID."""
    with runs_lock:
        if run_id in active_runs:
            del active_runs[run_id]


def generate_run_id() -> str:
    """Generate a unique run ID."""
    return f"run_{int(time.time() * 1000)}"


def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries. Values from dict2 take precedence."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = deep_merge(result[key], value)
        else:
            # Override with value from dict2
            result[key] = value
    return result


def create_agent_config(
    problem_statement: str, config_path: str | None = None, inline_config: dict[str, Any] | None = None
) -> RunSingleConfig:
    """Create a configuration for the SWE-agent."""
    import os
    import yaml
    
    # Load default config
    config_dict = {"problem_statement": {}}

    # Handle different problem statement formats
    if isinstance(problem_statement, dict):
        # Problem statement is already a structured config (e.g., GitHub issue)
        config_dict["problem_statement"] = problem_statement
    elif isinstance(problem_statement, str):
        # Simple text problem statement
        config_dict["problem_statement"]["text"] = problem_statement

    # Determine which config file to use
    if not config_path:
        config_path = "./config/api_default.yaml"

    # Load from file and merge
    with open(config_path) as f:
        file_config = yaml.safe_load(f)

    # Merge configurations (file config takes precedence over our minimal config)
    config_dict = deep_merge(config_dict, file_config)

    # Apply inline configuration overrides if provided
    if inline_config:
        config_dict = deep_merge(config_dict, inline_config)

    return RunSingleConfig.model_validate(config_dict)


def _run_single_with_result(config: RunSingleConfig, websocket_hook: WebSocketHook | None = None) -> AgentRunResult:
    """Wrapper around run_from_config that returns the result."""
    from sweagent.run.run_single import RunSingle

    # Create RunSingle instance from config
    run_single_instance = RunSingle.from_config(config)

    # Add WebSocket hook if provided
    if websocket_hook:
        run_single_instance.agent.add_hook(websocket_hook)

    # Run and return the result
    run_single_instance.run()

    data = run_single_instance.agent.get_trajectory_data()
    return AgentRunResult(info=data["info"], trajectory=data["trajectory"])


async def run_agent_async(
    run_id: str,
    problem_statement: str | dict[str,str],
    config_path: str | None = None,
    inline_config: dict[str, Any] | None = None,
    github_token: str = "",
    emit_update_callback=None,
):
    """Run SWE-agent asynchronously and emit updates via Socket.IO."""
    state = RunState(run_id)
    if "type" in problem_statement and problem_statement["type"] == "github":
        issue = _get_gh_issue_data(problem_statement["github_url"], token=github_token)
        state.problem_statement = f"{issue.title} - {issue.body}"
    else:
        state.problem_statement = problem_statement
    set_run_state(run_id, state)

    try:
        # Emit start event
        if emit_update_callback:
            emit_update_callback(run_id, "start", {"run_id": run_id, "status": "started"})

        # If a github_token was provided via API request, set it in the environment so
        # downstream components (e.g., repo cloning, OpenPRHook, problem statement fetchers)
        # will pick it up via os.getenv("GITHUB_TOKEN"). Do not log the raw token.
        if github_token:
            os.environ["GITHUB_TOKEN"] = github_token
            logger.debug("GITHUB_TOKEN set for run %s (token redacted)", run_id)

        # Create config
        config = create_agent_config(problem_statement, config_path, inline_config)
        state.config = config

        # Create WebSocket hook and attach it to the state
        websocket_hook = WebSocketHook(run_id)
        if emit_update_callback:
            websocket_hook._emit_function = emit_update_callback
        state.websocket_hook = websocket_hook

        # Run the agent with the WebSocket hook in a separate thread
        result = await asyncio.to_thread(
            _run_single_with_result,
            config,
            websocket_hook,
        )

        # Update state with results from the hook if available
        if state.websocket_hook and state.websocket_hook.trajectory_steps:
            state.trajectory_steps = state.websocket_hook.trajectory_steps
        else:
            state.trajectory_steps = result.trajectory

        state.exit_status = result.info.get("exit_status")
        state.model_stats = result.info.get("model_stats", {})

        # Emit completion event
        if emit_update_callback:
            emit_update_callback(
                run_id,
                "complete",
                {
                    "run_id": run_id,
                    "status": "completed",
                    "exit_status": state.exit_status,
                    "steps": len(state.trajectory_steps),
                    "model_stats": state.model_stats,
                },
            )

    except Exception as e:
        logger.error(f"Error in run {run_id}: {e}")
        state.error = str(e)
        if emit_update_callback:
            emit_update_callback(
                run_id,
                "error",
                {
                    "run_id": run_id,
                    "status": "error",
                    "error": str(e),
                },
            )

    # Mark as completed but keep the state for retrieval
    state.completed = True