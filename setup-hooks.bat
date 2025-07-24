@echo off
REM Setup script to install git hooks on Windows

echo Setting up git hooks...

REM Create symbolic link for pre-commit hook
if exist ".git\hooks\pre-commit" (
    echo Removing existing pre-commit hook...
    del .git\hooks\pre-commit
)

echo Installing pre-commit hook...
mklink .git\hooks\pre-commit ..\..\hooks\pre-commit

echo ✅ Git hooks setup complete!
echo The pre-commit hook will now run Black and isort checks before each commit.