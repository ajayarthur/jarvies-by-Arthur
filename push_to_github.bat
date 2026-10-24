@echo off
setlocal enabledelayedexpansion
title Push to GitHub - Jarvies 4.0
cd /d "%~dp0"

echo =====================================================================
echo              JARVIES 4.0 - GITHUB AUTOMATION TOOL
echo =====================================================================
echo.

:: 1. Check for Git in PATH or common directories
set "GIT_CMD=git"
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if exist "C:\Program Files\Git\cmd\git.exe" (
        set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
    ) else if exist "C:\Program Files\Git\bin\git.exe" (
        set "GIT_CMD=C:\Program Files\Git\bin\git.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" (
        set "GIT_CMD=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"
    ) else if exist "C:\Program Files (x86)\Git\cmd\git.exe" (
        set "GIT_CMD=C:\Program Files (x86)\Git\cmd\git.exe"
    ) else (
        echo [ERROR] Git is not installed or not found in PATH.
        echo.
        echo You can install Git quickly by running this in PowerShell/Terminal:
        echo    winget install --id Git.Git -e --source winget
        echo.
        echo Or download the installer directly from:
        echo    https://git-scm.com/download/win
        echo.
        echo After installing, restart this script.
        echo =====================================================================
        pause
        exit /b 1
    )
)

echo [OK] Using Git: "%GIT_CMD%"
echo.

:: 2. Check if git repository exists
if not exist ".git" (
    echo [INFO] Git repository not initialized. Initializing now...
    "%GIT_CMD%" init
    echo.
)

:: 3. Configure/Verify Remote Origin
set "REMOTE_URL="
for /f "delims=" %%i in ('"%GIT_CMD%" remote get-url origin 2^>nul') do (
    set "REMOTE_URL=%%i"
)

if "%REMOTE_URL%"=="" (
    echo [INFO] No remote repository configured yet.
    set /p "USER_REMOTE=Enter your GitHub repository URL (e.g., https://github.com/ajayarthur/jarvies-by-Arthur.git): "
    if "!USER_REMOTE!"=="" (
        set "USER_REMOTE=https://github.com/ajayarthur/jarvies-by-Arthur.git"
    )
    "%GIT_CMD%" remote add origin "!USER_REMOTE!"
    echo [OK] Remote origin set to: !USER_REMOTE!
) else (
    echo [OK] Current GitHub Remote: %REMOTE_URL%
    echo If you want to change it, press C, otherwise press Enter to continue.
    set /p "CHANGE_REMOTE=Choice [Enter=Keep / C=Change]: "
    if /i "!CHANGE_REMOTE!"=="C" (
        set /p "NEW_REMOTE=Enter new GitHub repository URL: "
        if not "!NEW_REMOTE!"=="" (
            "%GIT_CMD%" remote set-url origin "!NEW_REMOTE!"
            echo [OK] Remote updated to: !NEW_REMOTE!
        )
    )
)
echo.

:: 4. Ensure branch is main
"%GIT_CMD%" branch -M main >nul 2>nul

:: 5. Display Status
echo =====================================================================
echo Current Changes:
echo =====================================================================
"%GIT_CMD%" status --short
echo =====================================================================
echo.

:: 6. Stage files
echo Staging all files (git add .)...
"%GIT_CMD%" add .
echo [OK] All modified files staged.
echo.

:: 7. Commit Message
set "DEFAULT_MSG=Update Jarvies 4.0 - Arthur"
echo Enter your commit message (or press ENTER to use default):
echo Default: "%DEFAULT_MSG%"
set /p "COMMIT_MSG=> "
if "%COMMIT_MSG%"=="" set "COMMIT_MSG=%DEFAULT_MSG%"

echo.
echo Committing changes...
"%GIT_CMD%" commit -m "%COMMIT_MSG%"
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Nothing new to commit or working tree clean.
)
echo.

:: 8. Push to GitHub
echo =====================================================================
echo Pushing to GitHub (origin main)...
echo =====================================================================
"%GIT_CMD%" push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo [SUCCESS] Code pushed successfully to GitHub!
    echo =====================================================================
) else (
    echo.
    echo =====================================================================
    echo [NOTICE] Push encountered an issue.
    echo This often happens if the remote repository has newer commits,
    echo or if authentication is required.
    echo.
    echo Would you like to try pulling remote changes first (git pull --rebase)?
    set /p "TRY_PULL=[Y/N] (Default=Y): "
    if "!TRY_PULL!"=="" set "TRY_PULL=Y"
    if /i "!TRY_PULL!"=="Y" (
        echo.
        echo Pulling remote changes...
        "%GIT_CMD%" pull --rebase origin main
        echo Pushing again...
        "%GIT_CMD%" push -u origin main
        if !ERRORLEVEL! EQU 0 (
            echo.
            echo [SUCCESS] Code pushed successfully to GitHub!
        ) else (
            echo.
            echo [ERROR] Push failed. Please check your GitHub credentials or permissions.
        )
    )
    echo =====================================================================
)

echo.
pause
