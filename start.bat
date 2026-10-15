@echo off
rem Runs Taskvane from source (no console window). Use build.ps1 to make Taskvane.exe.
cd /d "%~dp0"
python -c "import psutil, webview, pystray, PIL" 2>nul || python -m pip install -r requirements.txt
start "" pythonw app.py
