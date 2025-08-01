# Windows Setup Guide for c2puml

This guide helps you set up and run c2puml on Windows systems.

## Prerequisites

1. **Python 3.7 or higher** - Download from [python.org](https://www.python.org/downloads/)
2. **pip** - Usually comes with Python
3. **Git** - Download from [git-scm.com](https://git-scm.com/download/win)

## Quick Start

### Option 1: Automatic Setup (Recommended)

1. **Run the setup script:**
   ```cmd
   scripts\setup.bat
   ```

2. **Run the example:**
   ```cmd
   scripts\run_example.bat
   ```

### Option 2: Manual Setup

1. **Install the package in development mode:**
   ```cmd
   python -m pip install -e .
   ```

2. **Set environment variables:**
   ```cmd
   set PYTHONPATH=src
   ```

3. **Run the example:**
   ```cmd
   python -m c2puml.main --config tests/example/config.json --verbose
   ```

## Troubleshooting

### Error: "No module named 'c2puml'"

**Cause:** The c2puml package is not installed or not in the Python path.

**Solutions:**

1. **Install in development mode:**
   ```cmd
   python -m pip install -e .
   ```

2. **If you get an "externally managed environment" error:**
   ```cmd
   python -m pip install -e . --break-system-packages
   ```

3. **Check if the package is installed:**
   ```cmd
   python -c "import c2puml; print('c2puml is installed')"
   ```

### Error: "python is not recognized"

**Cause:** Python is not in your system PATH.

**Solutions:**

1. **Reinstall Python** and check "Add Python to PATH" during installation
2. **Add Python manually to PATH:**
   - Find your Python installation directory (e.g., `C:\Python39`)
   - Add it to your system PATH environment variable
3. **Use the full path:**
   ```cmd
   C:\Python39\python.exe -m c2puml.main --config tests/example/config.json --verbose
   ```

### Error: "pip is not recognized"

**Cause:** pip is not installed or not in PATH.

**Solutions:**

1. **Install pip:**
   ```cmd
   python -m ensurepip --upgrade
   ```

2. **Use python -m pip instead:**
   ```cmd
   python -m pip install -e .
   ```

### Error: "Permission denied" or "Access denied"

**Cause:** Insufficient permissions to install packages.

**Solutions:**

1. **Run Command Prompt as Administrator**
2. **Use user installation:**
   ```cmd
   python -m pip install -e . --user
   ```

### Error: "externally managed environment"

**Cause:** Your Python installation is managed by the system.

**Solutions:**

1. **Use the --break-system-packages flag:**
   ```cmd
   python -m pip install -e . --break-system-packages
   ```

2. **Create a virtual environment:**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   python -m pip install -e .
   ```

## Alternative Methods

### Using PowerShell

If you prefer PowerShell, use the PowerShell script:

```powershell
# Run with verbose output
.\scripts\run_example.ps1 -Verbose

# Run without verbose output
.\scripts\run_example.ps1
```

### Using Virtual Environment

1. **Create a virtual environment:**
   ```cmd
   python -m venv venv
   ```

2. **Activate it:**
   ```cmd
   venv\Scripts\activate
   ```

3. **Install the package:**
   ```cmd
   python -m pip install -e .
   ```

4. **Run the example:**
   ```cmd
   python -m c2puml.main --config tests/example/config.json --verbose
   ```

### Using the c2puml Command

After installation, you can use the `c2puml` command directly:

```cmd
c2puml --config tests/example/config.json --verbose
```

## Environment Variables

The following environment variables are used:

- **PYTHONPATH=src** - Tells Python where to find the c2puml module
- **PATH** - Should include Python and pip directories

## Verification

To verify your installation:

1. **Check Python version:**
   ```cmd
   python --version
   ```

2. **Check if c2puml is installed:**
   ```cmd
   python -c "import c2puml; print('Success!')"
   ```

3. **Check c2puml help:**
   ```cmd
   python -m c2puml.main --help
   ```

## Common Commands

```cmd
# Install in development mode
python -m pip install -e .

# Run with verbose output
python -m c2puml.main --config tests/example/config.json --verbose

# Run without verbose output
python -m c2puml.main --config tests/example/config.json

# Get help
python -m c2puml.main --help

# Run individual steps
python -m c2puml.main --config tests/example/config.json parse
python -m c2puml.main --config tests/example/config.json transform
python -m c2puml.main --config tests/example/config.json generate
```

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Run the setup script: `scripts\setup.bat`
3. Check the Python and pip versions
4. Try running in a virtual environment
5. Check the project's README.md for more information