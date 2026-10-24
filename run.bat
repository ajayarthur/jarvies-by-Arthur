@echo off
title Jarvies 4.0 - Advanced AI Desktop Assistant
cd /d "%~dp0"

echo ==========================================================
echo        Jarvies 4.0 - Advanced AI Desktop Assistant
echo ==========================================================
echo Starting Jarvies Holographic HUD ^& Web Services...

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv.
    pause
    exit /b 1
)

.venv\Scripts\python.exe web_server.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Jarvies stopped or encountered an error.
    pause
)
