@echo off
setlocal
title Yogyakarta Residency Letters - Local Server

:: Navigate to repository root directory
cd /d "%~dp0"

:: Launch local server via Python helper
if exist "scripts\serve.py" (
    python scripts\serve.py %*
) else (
    echo Starting fallback Python HTTP server on port 8000...
    start "" http://localhost:8000/
    python -m http.server 8000 --bind 127.0.0.1
)

if errorlevel 1 (
    echo.
    echo ======================================================================
    echo An error occurred while launching the server.
    echo Please make sure Python is installed and available in your system PATH.
    echo ======================================================================
    echo.
    pause
)
