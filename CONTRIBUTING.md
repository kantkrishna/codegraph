# Contributing to CodeGraph

## Branching Strategy
* Main branch: `main` (Protected, requires passing CI)
* Feature branches: `feat/US-<id>-<short-description>`
* Bug fixes: `fix/<short-description>`

## Code Quality Quality Gates
We strictly enforce type hints and linting. Before pushing your code, our pre-commit hooks will run `Ruff` and `Mypy`. If you bypass these, the GitHub Actions CI pipeline will reject your PR.