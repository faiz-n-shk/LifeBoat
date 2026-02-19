@echo off
echo Starting Lifeboat...

cd /d "%~dp0\.."

venv\Scripts\python.exe main.py

pause
