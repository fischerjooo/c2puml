@echo off
echo WARNING: This will reset all local changes and pull from remote!
echo.
echo Proceeding with git reset --hard...
git reset --hard

echo.
echo Checking current branch and remote status...

REM Get current branch name
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Current branch: %CURRENT_BRANCH%

REM Check if branch has upstream tracking
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if %errorlevel% equ 0 (
    echo Branch has upstream tracking, pulling from remote...
    git pull
) else (
    echo Branch has no upstream tracking, attempting to set it up...
    
    REM Try to set upstream to origin with same branch name
    git branch --set-upstream-to=origin/%CURRENT_BRANCH% %CURRENT_BRANCH% >nul 2>&1
    if %errorlevel% equ 0 (
        echo Successfully set upstream to origin/%CURRENT_BRANCH%
        echo Pulling from remote...
        git pull
    ) else (
        echo Failed to set upstream automatically.
        echo.
        echo Available options:
        echo 1. Set upstream manually: git branch --set-upstream-to=origin/BRANCH_NAME %CURRENT_BRANCH%
        echo 2. Pull from specific remote/branch: git pull origin BRANCH_NAME
        echo 3. Push current branch to remote: git push -u origin %CURRENT_BRANCH%
        echo.
        echo Current remotes:
        git remote -v
        echo.
        echo Available remote branches:
        git branch -r
        echo.
        pause
        exit /b 1
    )
)

if %errorlevel% equ 0 (
    echo ✅ Git reset and pull completed successfully!
) else (
    echo ❌ Git pull failed. Please check the error messages above.
    pause
)