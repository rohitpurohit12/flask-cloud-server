@echo off
echo Starting Python Cloud Server...
cd /d %~dp0

REM Start Flask server in a new window
start cmd /k python rohit.py

REM Wait a few seconds to let server start
timeout /t 3 /nobreak >nul

REM Open default browser
start http://127.0.0.1:5000
