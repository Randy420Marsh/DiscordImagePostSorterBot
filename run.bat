@echo off

setlocal enabledelayedexpansion

set "PYTHON=python"

echo "Launching..."

call .\venv\scripts\activate.bat

python -s autosorter.py

REM Bot permission integer: 515396200512

REM Bot invite link: https://discord.com/oauth2/authorize?client_id=1325982487448653894

REM OAuth2: https://discord.com/oauth2/authorize?client_id=1325982487448653894&permissions=377957247040&integration_type=0&scope=bot

pause
