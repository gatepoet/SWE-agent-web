"""Data models for the SWE-agent API."""

from __future__ import annotations

from typing import Any

from sweagent.api.websocket_hook import WebSocketHook


class RunState:
    """Track the state of a running SWE-agent instance."""

    def __init__(self, run_id: str):
        self.run_id = run_id
        self.started = False
        self.completed = False
        self.error = None
        self.trajectory_steps: list[dict[str, Any]] = []
        self.config = None
        self.problem_statement = ""
        self.exit_status = None
        self.model_stats = {}
        self.websocket_hook: WebSocketHook | None = None

    def to_dict(self):
        # Get current step info if available
        current_action = ""
        current_observation = ""
        current_thought = ""

        if (
            self.websocket_hook
            and hasattr(self.websocket_hook, "trajectory_steps")
            and self.websocket_hook.trajectory_steps
        ):
            last_step = self.websocket_hook.trajectory_steps[-1]
            current_action = last_step.get("action", "")
            current_observation = (
                last_step.get("observation", "")[:200] + "..."
                if last_step.get("observation") and len(last_step.get("observation")) > 200
                else last_step.get("observation", "")
            )
            current_thought = (
                last_step.get("thought", "")[:150] + "..."
                if last_step.get("thought") and len(last_step.get("thought")) > 150
                else last_step.get("thought", "")
            )

        return {
            "run_id": self.run_id,
            "started": self.started,
            "completed": self.completed,
            "error": self.error,
            "steps": len(self.trajectory_steps),
            "exit_status": self.exit_status,
            "model_stats": self.model_stats,
            "problem_statement": (
                self.problem_statement[:100] + "..."
                if self.problem_statement and len(self.problem_statement) > 100
                else (self.problem_statement if self.problem_statement else "")
            ),
            "current_action": current_action,
            "current_observation": current_observation,
            "current_thought": current_thought,
        }