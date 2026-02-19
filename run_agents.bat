@echo off
REM Simple Windows batch launcher for the multilingual agents project.

SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

IF NOT EXIST ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt
python agents.py %*
pause
