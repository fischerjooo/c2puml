### Working Context for Future Sessions (AI Assistant)

This project is a Python tool that converts C/C++ codebases into PlantUML diagrams. Keep these principles and workflows in mind for all future work in this repository.

## Project Overview
- Pipeline steps:
  1) Parse C/C++ files → model.json
  2) Verify model sanity
  3) Transform model based on configuration
  4) Generate PlantUML files
- Priorities: test-driven development, single responsibility per file, modern Python packaging via pyproject.toml, concise practical docs.

## Code Style & Quality
- Naming: variables/functions snake_case; classes PascalCase
- Formatting: 4 spaces; line length ~88 (Black)
- Type hints required on all functions
- Do not use wildcard imports or mutable defaults
- Prefer early returns; avoid deep nesting
- Static analysis: Flake8, Pylint, Mypy
- Public APIs: Google-style docstrings

## Tests & Workflow
- Tests layout:
  - tests/unit/: individual components
  - tests/feature/: full workflows
  - tests/integration/: end-to-end scenarios
- Aim for 90%+ coverage (pytest). Note: repo also supports unittest execution via scripts.
- Helpful scripts:
  - ./scripts/run_all_tests.sh (main test run)
  - ./scripts/run_example.sh (integration/example)
  - ./scripts/run_all.sh (full regression incl. PNG generation)
  - ./scripts/picgen.sh (PlantUML → PNG)
- TDD loop:
  1) Write failing test for requirement/bug
  2) Implement minimal solution
  3) Refactor with tests green
  4) Add edge-case/error-path tests

## Pre-Merge Checklist
- All tests green: ./scripts/run_all_tests.sh
- Code formatted (Black, isort)
- Static analysis clean (Flake8, Pylint, Mypy)
- Public APIs documented and tested
- Integration/example flow passes: ./scripts/run_example.sh

## Remember
- Maintain high signal-to-noise in changes and messages
- Use YAML test data structure and respect the multi-document format
- Prefer safe, incremental edits; run scripts to validate
- Keep output diagrams consistent with PlantUML template and spec in docs/
- Always validate changes by running ./scripts/run_all.sh after any development or modification; it must be green before commit/merge
- Any temporary/worker scripts must live in scripts/ and be named like temp_###.py (these are gitignored)
- Before starting work or making changes, read README.md (repo root) and tests/README.md to align with project behavior and the test framework