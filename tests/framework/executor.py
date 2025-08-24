"""
TestExecutor - CLI-Only Execution Engine for C2PUML Tests

This module provides the TestExecutor class that executes c2puml through
the CLI interface only, ensuring no internal API access during testing.

The actual c2puml CLI interface is:
- c2puml --config config.json [parse|transform|generate]
- c2puml config_folder [parse|transform|generate]
- c2puml [parse|transform|generate]  # Uses current directory as config folder
- c2puml              # Full workflow (parse, transform, generate)

Key points:
- No --output-dir parameter - output directory is in config
- No --input-path parameter - source folders are in config
- Config can be file or directory (directory merges all .json files)
- Working directory matters for relative paths
"""

import os
import sys
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CLIResult:
    """Standard result from CLI execution"""

    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: List[str]
    working_dir: str


class TestExecutor:
    """
    Executes c2puml through CLI interface only - no internal API access

    This class provides methods to execute c2puml through the command line
    interface, ensuring that tests only interact with the public API and
    maintain clear boundaries between test and application code.
    """

    def __init__(self):
        """Initialize the TestExecutor"""
        # Try different ways to run c2puml
        self.c2puml_command = "c2puml"
        # Prefer the current interpreter for maximum portability
        self.python_module_command = [sys.executable, "-m", "c2puml.main"]

        # Use absolute path to main.py
        # __file__ is tests/framework/executor.py, so go up 2 levels to workspace root
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        main_script_path = os.path.join(workspace_root, "main.py")
        self.main_script_command = [sys.executable, main_script_path]

    def run_full_pipeline(self, config_path: str, working_dir: str = None) -> CLIResult:
        """
        Run the complete c2puml pipeline (parse → transform → generate)

        Args:
            config_path: Path to config.json file or config directory
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path])
        return self._execute_command(command, working_dir)

    def run_parse_only(self, config_path: str, working_dir: str = None) -> CLIResult:
        """
        Run only the parse step

        Args:
            config_path: Path to config.json file or config directory
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path, "parse"])
        return self._execute_command(command, working_dir)

    def run_transform_only(self, config_path: str, working_dir: str = None) -> CLIResult:
        """
        Run only the transform step (requires existing model.json)

        Args:
            config_path: Path to config.json file or config directory
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path, "transform"])
        return self._execute_command(command, working_dir)

    def run_generate_only(self, config_path: str, working_dir: str = None) -> CLIResult:
        """
        Run only the generate step (requires existing model.json)

        Args:
            config_path: Path to config.json file or config directory
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path, "generate"])
        return self._execute_command(command, working_dir)

    def run_with_verbose(self, config_path: str, working_dir: str = None) -> CLIResult:
        """
        Run with verbose output for debugging

        Args:
            config_path: Path to config.json file or config directory
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path, "--verbose"])
        return self._execute_command(command, working_dir)

    def run_with_env_vars(self, config_path: str, env: dict, working_dir: str = None) -> CLIResult:
        """
        Run with custom environment variables

        Args:
            config_path: Path to config.json file or config directory
            env: Dictionary of environment variables
            working_dir: Working directory for execution (defaults to config directory)

        Returns:
            CLIResult with execution details
        """
        if working_dir is None:
            working_dir = (
                os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
            )

        command = self._build_command(["--config", config_path])
        return self._execute_command(command, working_dir, env=env)

    # === Output Management ===

    def get_test_output_dir(self, test_name: str, scenario: str = None) -> str:
        """
        Returns output directory path next to test file (output/ or output-<scenario>/)

        Args:
            test_name: Name of the test
            scenario: Optional scenario name

        Returns:
            Path to the output directory
        """
        test_dir = f"tests/{self._get_test_category(test_name)}/{test_name}"
        if scenario:
            return os.path.join(test_dir, f"output-{scenario}")
        else:
            return os.path.join(test_dir, "output")

    def cleanup_output_dir(self, output_dir: str) -> None:
        """
        Cleans output directory before test execution

        Args:
            output_dir: Path to the output directory
        """
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

    # === Private Methods ===

    def _build_command(self, args: List[str]) -> List[str]:
        """
        Build the command to execute c2puml

        Args:
            args: Additional arguments to pass to c2puml

        Returns:
            Complete command list
        """
        # Try different ways to run c2puml
        commands_to_try = [
            self.main_script_command + args,  # Try python main.py first (most reliable)
            [self.c2puml_command] + args,  # Try installed c2puml command
            self.python_module_command + args,  # Try python -m c2puml.main
        ]

        # Return the first command that should work
        # The actual command validation happens in _execute_command
        return commands_to_try[0]

    def _execute_command(
        self,
        command: List[str],
        working_dir: str,
        timeout: Optional[int] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> CLIResult:
        """
        Execute a command and return the result

        Args:
            command: Command to execute
            working_dir: Working directory for execution
            timeout: Optional timeout in seconds
            env: Optional environment variables

        Returns:
            CLIResult with execution details
        """
        start_time = time.time()

        # Try different command variations if the first one fails
        commands_to_try = [
            command,
            (
                self.main_script_command + command[1:]
                if command[0] == self.c2puml_command
                else command
            ),
            (
                self.python_module_command + command[1:]
                if command[0] == self.c2puml_command
                else command
            ),
        ]

        last_error = None

        for cmd in commands_to_try:
            try:
                # Prepare environment
                process_env = os.environ.copy()
                if env:
                    process_env.update(env)

                # Execute command
                result = subprocess.run(
                    cmd,
                    cwd=working_dir,
                    env=process_env,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                execution_time = time.time() - start_time

                return CLIResult(
                    exit_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    execution_time=execution_time,
                    command=cmd,
                    working_dir=working_dir,
                )

            except subprocess.TimeoutExpired as e:
                execution_time = time.time() - start_time
                last_error = e
                continue
            except FileNotFoundError as e:
                last_error = e
                continue
            except Exception as e:
                last_error = e
                continue

        # If all commands failed, return error result
        execution_time = time.time() - start_time

        if isinstance(last_error, subprocess.TimeoutExpired):
            return CLIResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                command=command,
                working_dir=working_dir,
            )
        else:
            return CLIResult(
                exit_code=-1,
                stdout="",
                stderr=f"All command variations failed: {last_error}",
                execution_time=execution_time,
                command=command,
                working_dir=working_dir,
            )

    def _get_test_category(self, test_name: str) -> str:
        """
        Determine test category from test name

        Args:
            test_name: Name of the test

        Returns:
            Test category ('unit', 'feature', 'integration', or 'example')
        """
        if test_name.startswith("test_example_"):
            return "example"
        elif "integration" in test_name:
            return "integration"
        elif "feature" in test_name or "comprehensive" in test_name:
            return "feature"
        else:
            return "unit"
