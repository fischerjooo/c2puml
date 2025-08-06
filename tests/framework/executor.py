"""
TestExecutor - CLI-Only Execution Engine for C2PUML Tests

This module provides the TestExecutor class that executes c2puml through
the CLI interface only, ensuring no internal API access during testing.
"""

import os
import subprocess
import time
import shutil
from dataclasses import dataclass
from typing import List, Dict, Optional
import psutil


@dataclass
class CLIResult:
    """Standard result from CLI execution"""
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: List[str]
    working_dir: str


@dataclass
class TimedCLIResult(CLIResult):
    """CLI result with detailed timing information"""
    parse_time: float
    transform_time: float
    generate_time: float
    total_time: float


@dataclass
class MemoryCLIResult(CLIResult):
    """CLI result with memory usage tracking"""
    peak_memory_mb: int
    memory_samples: List[int]
    memory_timeline: List[tuple]  # (timestamp, memory_mb)


class TestExecutor:
    """
    Executes c2puml through CLI interface only - no internal API access
    
    This class provides methods to execute c2puml through the command line
    interface, ensuring that tests only interact with the public API and
    maintain clear boundaries between test and application code.
    """
    
    def __init__(self):
        """Initialize the TestExecutor"""
        self.python_executable = "python3"
        self.main_script = "main.py"
        
    def run_full_pipeline(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """
        Run the complete c2puml pipeline (parse → transform → generate)
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        return self._execute_command(command, input_path)
    
    def run_parse_only(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """
        Run only the parse step
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir,
            "parse"
        ]
        
        return self._execute_command(command, input_path)
    
    def run_transform_only(self, config_path: str, output_dir: str) -> CLIResult:
        """
        Run only the transform step (requires existing model.json)
        
        Args:
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir,
            "transform"
        ]
        
        return self._execute_command(command, output_dir)
    
    def run_generate_only(self, config_path: str, output_dir: str) -> CLIResult:
        """
        Run only the generate step (requires existing model.json)
        
        Args:
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir,
            "generate"
        ]
        
        return self._execute_command(command, output_dir)
    
    def run_with_verbose(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """
        Run with verbose output for debugging
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir,
            "--verbose"
        ]
        
        return self._execute_command(command, input_path)
    
    def run_with_timeout(self, input_path: str, config_path: str, output_dir: str, timeout: int) -> CLIResult:
        """
        Run with timeout protection
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            timeout: Timeout in seconds
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        return self._execute_command(command, input_path, timeout=timeout)
    
    def run_with_env_vars(self, input_path: str, config_path: str, output_dir: str, env: dict) -> CLIResult:
        """
        Run with custom environment variables
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            env: Dictionary of environment variables
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        return self._execute_command(command, input_path, env=env)
    
    def run_expecting_failure(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """
        Run expecting the command to fail (for error testing)
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        return self._execute_command(command, input_path)
    
    def run_and_capture_stderr(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """
        Run and capture stderr for error analysis
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            CLIResult with execution details including stderr
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        return self._execute_command(command, input_path)
    
    def run_with_timing(self, input_path: str, config_path: str, output_dir: str) -> TimedCLIResult:
        """
        Run with detailed timing information
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            TimedCLIResult with detailed timing information
        """
        start_time = time.time()
        
        # Run parse step
        parse_start = time.time()
        parse_result = self.run_parse_only(input_path, config_path, output_dir)
        parse_time = time.time() - parse_start
        
        # Run transform step
        transform_start = time.time()
        transform_result = self.run_transform_only(config_path, output_dir)
        transform_time = time.time() - transform_start
        
        # Run generate step
        generate_start = time.time()
        generate_result = self.run_generate_only(config_path, output_dir)
        generate_time = time.time() - generate_start
        
        total_time = time.time() - start_time
        
        # Combine results (use the last result for stdout/stderr)
        return TimedCLIResult(
            exit_code=generate_result.exit_code,
            stdout=generate_result.stdout,
            stderr=generate_result.stderr,
            execution_time=total_time,
            command=generate_result.command,
            working_dir=generate_result.working_dir,
            parse_time=parse_time,
            transform_time=transform_time,
            generate_time=generate_time,
            total_time=total_time
        )
    
    def run_with_memory_tracking(self, input_path: str, config_path: str, output_dir: str) -> MemoryCLIResult:
        """
        Run with memory usage tracking
        
        Args:
            input_path: Path to input directory or file
            config_path: Path to config.json file
            output_dir: Path to output directory
            
        Returns:
            MemoryCLIResult with memory usage information
        """
        command = [
            self.python_executable, self.main_script,
            "--config", config_path,
            "--output-dir", output_dir
        ]
        
        # Start memory monitoring
        process = psutil.Process()
        memory_samples = []
        memory_timeline = []
        
        start_time = time.time()
        
        # Execute command
        result = self._execute_command(command, input_path)
        
        # Get peak memory usage
        peak_memory_mb = process.memory_info().rss / 1024 / 1024
        
        return MemoryCLIResult(
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            execution_time=result.execution_time,
            command=result.command,
            working_dir=result.working_dir,
            peak_memory_mb=int(peak_memory_mb),
            memory_samples=memory_samples,
            memory_timeline=memory_timeline
        )
    
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
    
    def preserve_output_for_review(self, output_dir: str) -> None:
        """
        Marks output directory to be preserved for manual review
        
        Args:
            output_dir: Path to the output directory
        """
        # Create a marker file to indicate this output should be preserved
        marker_file = os.path.join(output_dir, ".preserve_for_review")
        with open(marker_file, 'w') as f:
            f.write(f"Preserved for review at {time.time()}\n")
    
    # === Private Methods ===
    
    def _execute_command(self, command: List[str], working_dir: str, 
                        timeout: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> CLIResult:
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
        
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Execute command
            result = subprocess.run(
                command,
                cwd=working_dir,
                env=process_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return CLIResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                command=command,
                working_dir=working_dir
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return CLIResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds",
                execution_time=execution_time,
                command=command,
                working_dir=working_dir
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return CLIResult(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                command=command,
                working_dir=working_dir
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
        elif "feature" in test_name or "integration" in test_name or "comprehensive" in test_name:
            return "feature"
        else:
            return "unit"