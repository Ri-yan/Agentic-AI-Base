@echo off
setlocal EnableDelayedExpansion

:: === Check for Miniconda/Conda ===
echo Checking for Conda...

where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Conda is not installed or not in PATH.
    goto end
)

echo ✅ Conda is available.

:: === User Confirmation ===
echo.
set /p proceed=Proceed to create environment 'dev_env' with Python 3.11 and install requirements.txt? (Y/N):
if /i not "%proceed%"=="Y" (
    echo Aborted by user.
    goto end
)

:: === Create Conda Environment ===
echo.
echo Creating conda environment: dev_env with Python 3.11...
conda create -y -n dev_env python=3.11

if %errorlevel% neq 0 (
    echo ❌ Failed to create conda environment.
    goto end
)

:: === Activate Environment and Install Requirements ===
echo.
echo Activating environment and installing requirements...

call conda activate dev_env

if exist requirements.txt (
    pip install --upgrade pip
    pip install -r requirements.txt
    echo ✅ Environment setup complete.
) else (
    echo ❌ requirements.txt not found in current directory.
)

:end
echo.
pause
