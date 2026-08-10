# tests/unit/foundation/test_ci_pipeline.py

# This test file is used to parse and validate the GitHub Actions YAML file.
# It checks for basic structure and type validation.

from pathlib import Path
from typing import Any

import yaml


# Change the return type from `dict` to `dict[Any, Any]`
def load_ci_workflow() -> dict[Any, Any]:
    ci_path = Path(".github/workflows/ci.yml")
    if not ci_path.exists():
        raise FileNotFoundError("CI workflow file missing (Red Phase)")
    with open(ci_path, "r") as f:
        # yaml.safe_load returns Any, so we cast/return it implicitly as our typed dict
        return yaml.safe_load(f) or {}


def test_ci_file_exists() -> None:
    """Verify the GitHub Actions workflow file exists."""
    assert Path(".github/workflows/ci.yml").exists(), "ci.yml is missing"


def test_ci_triggers_on_pr_to_main() -> None:
    """Verify CI is configured to run on PRs to the main branch."""
    config = load_ci_workflow()
    
    # CRITICAL FIX: PyYAML parses the unquoted YAML key 'on:' as the boolean True.
    # We must check for both the string 'on' and the boolean True.
    triggers = config.get("on", config.get(True, {}))
    
    assert "pull_request" in triggers, "Missing pull_request trigger"
    
    pr_branches = triggers["pull_request"].get("branches", [])
    assert "main" in pr_branches, "Pipeline does not trigger on PRs to main"


def test_ci_runs_quality_gates() -> None:
    """Verify Ruff, Mypy, and Pytest are executed in the pipeline."""
    config = load_ci_workflow()

    # Extract all steps from the first job (assuming single job for simplicity)
    jobs = config.get("jobs", {})
    job_name = list(jobs.keys())[0]
    steps = jobs[job_name].get("steps", [])

    # Concatenate all commands run in the pipeline
    run_commands = " ".join([step.get("run", "") for step in steps if "run" in step])

    assert "ruff" in run_commands.lower(), "Ruff linting is missing from CI"
    assert "mypy" in run_commands.lower(), "Mypy type checking is missing from CI"
    assert "pytest" in run_commands.lower(), "Pytest execution is missing from CI"


def test_ci_builds_docker_image() -> None:
    """Verify the pipeline builds the Docker image to prevent regressions."""
    config = load_ci_workflow()
    jobs = config.get("jobs", {})
    job_name = list(jobs.keys())[0]
    steps = jobs[job_name].get("steps", [])

    run_commands = " ".join([step.get("run", "") for step in steps if "run" in step])
    assert "docker-compose build" in run_commands or "docker compose build" in run_commands, (
        "Docker image build step is missing from CI"
    )


def test_ci_uses_caching() -> None:
    """Verify dependency caching is enabled to speed up CI runs."""
    config = load_ci_workflow()
    jobs = config.get("jobs", {})
    job_name = list(jobs.keys())[0]
    steps = jobs[job_name].get("steps", [])

    # Astral's setup-uv action natively supports caching via the enable-cache property
    caching_enabled = False
    for step in steps:
        if "astral-sh/setup-uv" in step.get("uses", ""):
            if step.get("with", {}).get("enable-cache"):
                caching_enabled = True
                break

    assert caching_enabled, "uv dependency caching is not explicitly enabled in CI"
