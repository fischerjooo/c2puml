# PlantUML Configuration Guide

This document explains how the PlantUML configuration system works in this project.

## Overview

The project now uses VS Code's configuration system with `${config:plantumlPath}` to automatically pass the PlantUML jar path to the `picgen.bat` and `picgen.sh` scripts.

## Configuration Files

### 1. VS Code Settings (`.vscode/settings.json`)

The main configuration is stored in VS Code settings:

```json
{
    "plantumlPath": "${env:USERPROFILE}\\.vscode\\extensions\\jebbs.plantuml-2.18.1\\plantuml.jar",
    "plantumlPath.windows": "${env:USERPROFILE}\\.vscode\\extensions\\jebbs.plantuml-2.18.1\\plantuml.jar",
    "plantumlPath.linux": "${env:HOME}/.vscode/extensions/jebbs.plantuml-2.18.1/plantuml.jar",
    "plantumlPath.osx": "${env:HOME}/.vscode/extensions/jebbs.plantuml-2.18.1/plantuml.jar"
}
```

### 2. Workspace Settings (`workspace.code-workspace`)

The same configuration is also stored in the workspace file for consistency.

### 3. Task Configuration (`.vscode/tasks.json`)

The "Generate Pictures" task uses the configuration:

```json
{
    "label": "# Generate Pictures",
    "type": "shell",
    "command": "${workspaceFolder}/picgen.bat",
    "args": ["${config:plantumlPath}"],
    "group": "build"
}
```

## How It Works

1. **Configuration Resolution**: VS Code resolves `${config:plantumlPath}` to the actual configured value
2. **Platform Detection**: VS Code automatically selects the appropriate platform-specific configuration
3. **Argument Passing**: The resolved path is passed as a command-line argument to the script
4. **Script Processing**: The script receives the path and uses it to locate the PlantUML jar file

## Platform-Specific Configurations

The system supports platform-specific configurations:

- **Windows**: `plantumlPath.windows` - Uses `${env:USERPROFILE}` for Windows paths
- **Linux**: `plantumlPath.linux` - Uses `${env:HOME}` for Unix-style paths
- **macOS**: `plantumlPath.osx` - Uses `${env:HOME}` for Unix-style paths

## Usage

### VS Code Task (Recommended)

1. Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. Select "Tasks: Run Task"
3. Choose "# Generate Pictures"
4. The task will automatically use the configured PlantUML path

### Command Line (Manual Override)

You can still manually specify a path:

```bash
# Windows
picgen.bat "C:\path\to\plantuml.jar"

# Linux/macOS
./picgen.sh "/path/to/plantuml.jar"
```

## Customization

### Override Default Configuration

Users can override the default configuration in their VS Code settings:

1. Open VS Code Settings (`Ctrl+,` / `Cmd+,`)
2. Search for "plantumlPath"
3. Add your custom configuration:

```json
{
    "plantumlPath": "/your/custom/path/to/plantuml.jar"
}
```

### Platform-Specific Override

You can also override for specific platforms:

```json
{
    "plantumlPath.windows": "C:\\your\\windows\\path\\plantuml.jar",
    "plantumlPath.linux": "/your/linux/path/plantuml.jar",
    "plantumlPath.osx": "/your/macos/path/plantuml.jar"
}
```

## Environment Variables

The configuration uses environment variables that VS Code automatically resolves:

- **Windows**: `${env:USERPROFILE}` - Points to the user's home directory
- **Linux/macOS**: `${env:HOME}` - Points to the user's home directory

## Fallback Behavior

If the configured PlantUML jar path is not found, the scripts will:

1. Check for a PlantUML installation in the system PATH
2. Look for `plantuml.jar` in the current directory
3. Look for `plantuml.jar` in the parent directory
4. Download PlantUML automatically if none of the above are found

## Troubleshooting

### Common Issues

1. **Path Not Found**: Ensure the PlantUML jar file exists at the configured path
2. **Permission Issues**: Make sure the script has execute permissions (Linux/macOS)
3. **Java Not Found**: Ensure Java is installed and accessible in the PATH

### Debugging

To debug configuration issues:

1. Check the VS Code output panel for task execution details
2. Verify the configuration values in VS Code settings
3. Test the path manually by running the script with the path as an argument

## Migration from Environment Variables

If you were previously using environment variables, the new configuration system:

- ✅ Provides better platform support
- ✅ Uses VS Code's native configuration system
- ✅ Allows for easier customization
- ✅ Maintains backward compatibility with manual command-line usage

The scripts still accept command-line arguments, so existing workflows continue to work.