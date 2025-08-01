#!/usr/bin/env python3
"""
c2puml Example Runner - Automatic Setup and Execution

This script automatically:
1. Detects if c2puml is installed
2. Installs it in development mode if needed
3. Sets up the environment
4. Runs the example workflow
5. Provides helpful error messages and troubleshooting steps
"""

import os
import sys
import subprocess
import shutil
import tempfile
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a command and return the result."""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, check=check, 
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        if not check:
            return e
        raise e


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Error: Python 3.7+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True


def check_c2puml_installed():
    """Check if c2puml module is installed."""
    try:
        import c2puml
        print("✅ c2puml module found")
        return True
    except ImportError:
        print("❌ c2puml module not found")
        return False


def install_c2puml():
    """Install c2puml in development mode."""
    print("🔧 Installing c2puml in development mode...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Please run this script from the project root.")
        return False
    
    # Try standard installation
    try:
        run_command("python -m pip install -e .")
        print("✅ Installation successful!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Standard installation failed, trying with --break-system-packages...")
        
        # Try with --break-system-packages
        try:
            run_command("python -m pip install -e . --break-system-packages")
            print("✅ Installation successful with --break-system-packages!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Installation failed. Trying user installation...")
            
            # Try user installation
            try:
                run_command("python -m pip install -e . --user")
                print("✅ Installation successful with --user!")
                return True
            except subprocess.CalledProcessError:
                print("❌ All installation methods failed.")
                return False


def clean_output_directories():
    """Clean previous output directories."""
    print("🧹 Cleaning previous output...")
    
    dirs_to_clean = [
        "artifacts/output_example",
        "tests/example/artifacts/output_example"
    ]
    
    for dir_path in dirs_to_clean:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
            print(f"   Removed: {dir_path}")


def run_c2puml_example():
    """Run the c2puml example."""
    print("🚀 Running c2puml example...")
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = 'src'
    
    try:
        # Run the c2puml command
        cmd = [
            sys.executable, "-m", "c2puml.main",
            "--config", "tests/example/config.json",
            "--verbose"
        ]
        
        result = subprocess.run(cmd, env=env, check=True)
        print("✅ c2puml example completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ c2puml execution failed with exit code {e.returncode}")
        return False


def run_assertions():
    """Run the test assertions."""
    print("🧪 Running assertions...")
    
    try:
        # Change to tests/example directory
        original_dir = os.getcwd()
        os.chdir("tests/example")
        
        # Run the test script
        result = subprocess.run([sys.executable, "test-example.py"], check=True)
        
        # Change back to original directory
        os.chdir(original_dir)
        
        print("✅ Assertions passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Assertions failed with exit code {e.returncode}")
        return False


def show_troubleshooting():
    """Show troubleshooting information."""
    print("\n" + "="*60)
    print("🔧 TROUBLESHOOTING GUIDE")
    print("="*60)
    print("If you're still having issues, try these steps:")
    print()
    print("1. Check Python installation:")
    print("   python --version")
    print()
    print("2. Check pip installation:")
    print("   python -m pip --version")
    print()
    print("3. Manual installation:")
    print("   python -m pip install -e . --break-system-packages")
    print()
    print("4. Create virtual environment:")
    print("   python -m venv venv")
    print("   venv\\Scripts\\activate  # Windows")
    print("   source venv/bin/activate  # Linux/Mac")
    print("   python -m pip install -e .")
    print()
    print("5. Check the WINDOWS_SETUP.md file for more help")
    print()
    print("6. Verify c2puml installation:")
    print("   python -c \"import c2puml; print('Success!')\"")
    print("="*60)


def main():
    """Main function."""
    print("c2puml Example Runner - Automatic Setup")
    print("=" * 50)
    
    # Step 1: Check Python version
    if not check_python_version():
        show_troubleshooting()
        return 1
    
    # Step 2: Check if c2puml is installed
    if not check_c2puml_installed():
        if not install_c2puml():
            show_troubleshooting()
            return 1
        
        # Verify installation
        if not check_c2puml_installed():
            print("❌ Installation verification failed")
            show_troubleshooting()
            return 1
    
    # Step 3: Clean output directories
    clean_output_directories()
    
    # Step 4: Run c2puml example
    if not run_c2puml_example():
        show_troubleshooting()
        return 1
    
    # Step 5: Run assertions
    if not run_assertions():
        print("⚠️  Example completed but assertions failed")
        return 1
    
    print("\n" + "="*50)
    print("🎉 SUCCESS! Example completed successfully!")
    print("📁 Check the generated diagrams in: ./artifacts/output_example")
    print("="*50)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        show_troubleshooting()
        sys.exit(1)