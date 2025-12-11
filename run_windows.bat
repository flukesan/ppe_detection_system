@echo off
REM Launcher script for PPE Detection System on Windows

echo Starting PPE Detection System...

REM Run the application
python main.py %*

REM Pause on error
if errorlevel 1 (
    echo.
    echo Error occurred! Press any key to exit...
    pause >nul
)
