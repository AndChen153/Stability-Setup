@echo off
REM Find the location of the "stabilitySetup" Conda environment
for /f "tokens=*" %%i in ('conda env list ^| find "stabilitySetup"') do (
    set ENV_LINE=%%i
)

REM Check if the environment was found
if "%ENV_LINE%"=="" (
    echo Error: 'stabilitySetup' Conda environment not found.
    pause
    exit /b 1
)

REM Extract the full path from the environment line
for /f "tokens=1,*" %%a in ("%ENV_LINE%") do set ENV_PATH=%%b

REM Optionally, trim spaces (if needed)

REM Activate the Conda environment
call conda activate "%ENV_PATH%"
if errorlevel 1 (
    echo Error: Failed to activate the 'stabilitySetup' Conda environment.
    pause
    exit /b 1
)

REM Run the Python script
python ./Stability-Setup_Python/app.py
if errorlevel 1 (
    echo Error: Failed to run the Python script.
    pause
    exit /b 1
)

echo Script executed successfully.
exit /b 0
