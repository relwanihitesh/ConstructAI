@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3.11 or newer is required. Install it from python.org and enable Add to PATH.
  pause
  exit /b 1
)
python launch.py
if errorlevel 1 pause
