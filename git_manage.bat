@echo off
setlocal enabledelayedexpansion

echo 🚀 Git Management Script
echo =======================

REM Get current branch name
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Current branch: %CURRENT_BRANCH%

echo.
echo Available options:
echo 1. Reset and pull (with auto-upstream setup)
echo 2. Set upstream tracking
echo 3. Push current branch to remote
echo 4. Show git status
echo 5. Show available remotes and branches
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto :reset_pull
if "%choice%"=="2" goto :set_upstream
if "%choice%"=="3" goto :push_branch
if "%choice%"=="4" goto :show_status
if "%choice%"=="5" goto :show_info
if "%choice%"=="6" goto :exit
echo Invalid choice. Please try again.
goto :exit

:reset_pull
echo.
echo 🔄 Reset and Pull with Auto-Upstream Setup
echo ==========================================

echo WARNING: This will reset all local changes!
echo.
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto :exit

echo.
echo Proceeding with git reset --hard...
git reset --hard

echo.
echo Checking branch tracking status...

REM Check if branch has upstream tracking
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Branch has upstream tracking
    echo Pulling from remote...
    git pull
    if %errorlevel% equ 0 (
        echo ✅ Git reset and pull completed successfully!
    ) else (
        echo ❌ Git pull failed
    )
) else (
    echo ⚠️  Branch has no upstream tracking
    echo Attempting to set up tracking automatically...
    
    REM Try to set upstream to origin with same branch name
    git branch --set-upstream-to=origin/%CURRENT_BRANCH% %CURRENT_BRANCH% >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Successfully set upstream to origin/%CURRENT_BRANCH%
        echo Pulling from remote...
        git pull
        if %errorlevel% equ 0 (
            echo ✅ Git reset and pull completed successfully!
        ) else (
            echo ❌ Git pull failed
        )
    ) else (
        echo ❌ Failed to set upstream automatically
        echo.
        echo Manual setup required. Available options:
        echo 1. Set upstream manually: git branch --set-upstream-to=origin/BRANCH_NAME %CURRENT_BRANCH%
        echo 2. Pull from specific remote/branch: git pull origin BRANCH_NAME
        echo 3. Push current branch to remote: git push -u origin %CURRENT_BRANCH%
    )
)
goto :exit

:set_upstream
echo.
echo 🔗 Set Upstream Tracking
echo =======================

echo Current branch: %CURRENT_BRANCH%
echo.
echo Available remote branches:
git branch -r
echo.

set /p remote_branch="Enter remote branch name (e.g., main, develop): "
if "%remote_branch%"=="" goto :exit

echo Setting upstream to origin/%remote_branch%...
git branch --set-upstream-to=origin/%remote_branch% %CURRENT_BRANCH%
if %errorlevel% equ 0 (
    echo ✅ Upstream tracking set successfully!
) else (
    echo ❌ Failed to set upstream tracking
)
goto :exit

:push_branch
echo.
echo 📤 Push Current Branch to Remote
echo ================================

echo Current branch: %CURRENT_BRANCH%
echo.

set /p confirm="Push current branch to origin/%CURRENT_BRANCH%? (y/N): "
if /i not "%confirm%"=="y" goto :exit

echo Pushing to remote...
git push -u origin %CURRENT_BRANCH%
if %errorlevel% equ 0 (
    echo ✅ Branch pushed successfully and upstream tracking set!
) else (
    echo ❌ Push failed
)
goto :exit

:show_status
echo.
echo 📊 Git Status
echo =============
git status
echo.
echo Recent commits:
git log --oneline -5
goto :exit

:show_info
echo.
echo ℹ️  Git Information
echo ==================

echo Current branch: %CURRENT_BRANCH%
echo.

echo Remotes:
git remote -v
echo.

echo Local branches:
git branch
echo.

echo Remote branches:
git branch -r
echo.

echo Upstream tracking:
git rev-parse --abbrev-ref --symbolic-full-name @{u} >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref --symbolic-full-name @{u}') do echo Upstream: %%i
) else (
    echo Upstream: Not set
)
goto :exit

:exit
echo.
echo Press any key to exit...
pause >nul