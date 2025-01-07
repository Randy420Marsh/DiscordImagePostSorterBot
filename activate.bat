@echo off

SET current_path=%CD%

cd %current_path%

setlocal enabledelayedexpansion

REM pip install -r requirements.txt

REM python.exe -m pip install --upgrade pip

IF exist ./venv (cmd /k call .\venv\scripts\activate.bat)  ELSE (cmd /k python -m venv venv && cmd /k call .\venv\scripts\activate.bat)

