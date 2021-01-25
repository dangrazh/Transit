@echo off
@title Launching the Web App

set batchpath=%~dp0

echo %time%
echo Starting local Web Server...
start "Local Web Server - press <Ctrl+C> followed by <exit> to stop the local Web Server" %windir%\System32\cmd.exe /k %batchpath%\flask_env\Scripts\python.exe %batchpath%\run.py

timeout 6 > NUL

echo %time%
"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" http://localhost:5000
echo Web App started in chrome... please switch to chrome!

timeout 6 > NUL
echo This window is no longer needed - closing it now...