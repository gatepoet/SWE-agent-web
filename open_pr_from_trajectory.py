#!/usr/bin/env python3
"""
Script to run the open_pr hook from a trajectory folder.

Usage: python open_pr_from_trajectory.py <trajectory_folder>

Assumes the current directory is the repository root with changes committed.
"""

import json
import os
import sys
from pathlib import Path

import yaml

from sweagent.environment.swe_env import EnvironmentConfig, SWEEnv
from sweagent.run.hooks.open_pr import open_pr
from sweagent.utils.log import get_logger


class MockEnv:
    """Mock environment that runs commands in the current directory."""

    def communicate(self, input, error_msg, timeout=10, check=True):
        import subprocess
        result = subprocess.run(
            input,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getcwd()
        )
        if check and result.returncode != 0:
            raise Exception(f"{error_msg}: {result.stderr}")
        return result.stdout


def parse_github_url_from_folder(folder_path):
    """Parse GitHub URL from trajectory folder name."""
    folder_name = Path(folder_path).name
    # Expected format: replay__owner__repo-issue__...
    parts = folder_name.split('__')
    if len(parts) < 3:
        raise ValueError(f"Cannot parse GitHub URL from folder name: {folder_name}")
    
    owner_repo_issue = parts[1] + '__' + parts[2]
    try:
        owner, repo_issue = owner_repo_issue.split('__')
        repo, issue = repo_issue.split('-')
        return f"https://github.com/{owner}/{repo}/issues/{issue}"
    except ValueError:
        raise ValueError(f"Cannot parse owner/repo/issue from folder name: {folder_name}")


def main(trajectory_folder):
    # Parse GitHub URL
    try:
        github_url = parse_github_url_from_folder(trajectory_folder)
    except ValueError as e:
        print(f"Error: {e}")
        print("Please ensure the trajectory folder follows the expected naming convention.")
        sys.exit(1)
    
    print(f"Parsed GitHub URL: {github_url}")
    
    # Find trajectory file
    traj_file = None
    for file_path in Path(trajectory_folder).iterdir():
        if file_path.suffix == '.traj':
            traj_file = file_path
            break
    
    if not traj_file:
        print(f"Error: No .traj file found in {trajectory_folder}")
        sys.exit(1)
    
    # Load trajectory
    with open(traj_file, 'r') as f:
        data = json.load(f)
    
    trajectory = data['trajectory']
    print(f"Loaded trajectory with {len(trajectory)} steps")
    
    # Setup logger
    logger = get_logger("open_pr_script")
    
    # Get token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    config = None
    # Create mock environment
    with open(Path(trajectory_folder).joinpath("config.yaml").resolve()) as f:
        file_config = yaml.safe_load(f)
        config = EnvironmentConfig.model_validate(file_config)
    env = SWEEnv.from_config(config)
    
    # Run open_pr
    try:
        open_pr(
            logger=logger,
            token=token,
            env=env,
            github_url=github_url,
            trajectory=trajectory,
            _dry_run=False
        )
        print("Successfully opened PR!")
    except Exception as e:
        print(f"Error opening PR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python open_pr_from_trajectory.py <trajectory_folder>")
        sys.exit(1)
    
    trajectory_folder = sys.argv[1]
    if not Path(trajectory_folder).is_dir():
        print(f"Error: {trajectory_folder} is not a directory")
        sys.exit(1)
    
    main(trajectory_folder)