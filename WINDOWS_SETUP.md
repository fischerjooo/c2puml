# Windows Setup Guide for PlantUML PNG Generation

This guide helps you set up and run the PlantUML to PNG conversion on Windows systems.

## Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
.\picgen.ps1
```

### Option 2: Batch File
```cmd
picgen.bat
```

### Option 3: Linux/Mac Script (if using WSL or Git Bash)
```bash
./picgen.sh
```

## Prerequisites

### 1. Java Runtime Environment (JRE)
PlantUML requires Java to run. Download and install from:
- **Official**: https://adoptium.net/
- **Oracle**: https://www.oracle.com/java/technologies/downloads/

**Verify Java installation:**
```cmd
java -version
```

### 2. PlantUML JAR File
The scripts will automatically download PlantUML if not found, but you can also:

#### Manual Download
1. Go to: https://github.com/plantuml/plantuml/releases
2. Download the latest `plantuml-*.jar` file
3. Rename it to `plantuml.jar`
4. Place it in your project directory

#### Package Manager Installation
```cmd
# Using Chocolatey
choco install plantuml

# Using Scoop
scoop install plantuml
```

## Troubleshooting

### Network Download Issues

If the automatic download fails, try these solutions:

#### 1. Check Internet Connection
- Ensure you have a stable internet connection
- Try accessing https://github.com in your browser

#### 2. Corporate Firewall
- Use a VPN if behind a corporate firewall
- Ask your IT department to whitelist GitHub domains

#### 3. Manual Download
If automatic download fails, manually download:
1. Visit: https://github.com/plantuml/plantuml/releases
2. Download `plantuml-1.2024.0.jar` (or latest version)
3. Rename to `plantuml.jar`
4. Place in your project directory

#### 4. Alternative Download Sources
- **PlantUML Website**: https://plantuml.com/download
- **Maven Central**: https://repo1.maven.org/maven2/net/sourceforge/plantuml/

### PowerShell Execution Policy

If you get execution policy errors:

```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run the script with bypass
PowerShell -ExecutionPolicy Bypass -File picgen.ps1
```

### Java Issues

#### Java Not Found
```cmd
# Check if Java is installed
java -version

# If not found, add Java to PATH or install it
```

#### Wrong Java Version
PlantUML works with Java 8 or higher:
```cmd
java -version
# Should show version 1.8.0 or higher
```

### File Permission Issues

#### Cannot Create Files
- Ensure you have write permissions in the project directory
- Run as administrator if needed
- Check antivirus software isn't blocking file creation

#### Cannot Access Output Directory
```cmd
# Check if output directory exists
dir output

# Create if missing
mkdir output
```

## Script Comparison

| Feature | picgen.ps1 | picgen.bat | picgen.sh |
|---------|------------|------------|-----------|
| **Platform** | Windows PowerShell | Windows CMD | Linux/Mac/WSL |
| **Error Handling** | Excellent | Good | Good |
| **Download Methods** | Multiple fallbacks | Multiple fallbacks | Single method |
| **Color Output** | Yes | Limited | Yes |
| **Execution Policy** | May need adjustment | None | None |

## Advanced Usage

### PowerShell Script Options
```powershell
# Force re-download of PlantUML
.\picgen.ps1 -ForceDownload

# Run with verbose output
.\picgen.ps1 -Verbose
```

### Custom PlantUML Options
Edit the scripts to add custom PlantUML parameters:
```cmd
# Example: Add custom theme
plantuml -tpng -theme=bluegray "file.puml"
```

## Common Error Messages

### "The request was aborted: The connection was closed unexpectedly"
- **Cause**: Network connectivity issue
- **Solution**: Try manual download or use VPN

### "Java is not recognized as an internal or external command"
- **Cause**: Java not installed or not in PATH
- **Solution**: Install Java and add to PATH

### "Access is denied"
- **Cause**: Permission issues
- **Solution**: Run as administrator or check file permissions

### "Execution policy prevents running scripts"
- **Cause**: PowerShell security policy
- **Solution**: Use `Set-ExecutionPolicy` or run with bypass

## Getting Help

If you continue to have issues:

1. **Check the logs**: Look for detailed error messages in the script output
2. **Verify prerequisites**: Ensure Java and network connectivity
3. **Try manual download**: Download PlantUML JAR manually
4. **Use alternative script**: Try the batch file if PowerShell fails

## File Structure

After successful execution, you should have:
```
project/
├── plantuml.jar          # PlantUML JAR file (auto-downloaded)
├── picgen.ps1            # PowerShell script
├── picgen.bat            # Batch script
├── picgen.sh             # Linux/Mac script
├── output/               # Generated files
│   ├── *.puml           # PlantUML source files
│   └── *.png            # Generated PNG images
└── WINDOWS_SETUP.md     # This file
```