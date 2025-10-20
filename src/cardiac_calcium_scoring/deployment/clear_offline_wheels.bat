@echo off
REM Clear offline wheels to force online installation
REM Use this if you have platform-mismatched wheel files

echo ==========================================
echo Clear Offline Wheels
echo ==========================================
echo.
echo This will delete all offline wheel files and force online installation.
echo.
echo Current location:
cd
echo.

set "WHEELS_DIR=deployment\offline_wheels"

if not exist "%WHEELS_DIR%" (
    echo [INFO] No offline_wheels directory found - nothing to clear
    pause
    exit /b 0
)

echo [WARNING] This will delete:
echo   - %WHEELS_DIR%\cpu\*
echo   - %WHEELS_DIR%\gpu\*
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/2] Clearing CPU wheels...
if exist "%WHEELS_DIR%\cpu\*.whl" (
    del /Q "%WHEELS_DIR%\cpu\*.whl" 2>nul
    echo   [OK] CPU wheels cleared
) else (
    echo   [INFO] No CPU wheels found
)

echo.
echo [2/2] Clearing GPU wheels...
if exist "%WHEELS_DIR%\gpu\*.whl" (
    del /Q "%WHEELS_DIR%\gpu\*.whl" 2>nul
    echo   [OK] GPU wheels cleared
) else (
    echo   [INFO] No GPU wheels found
)

echo.
echo ==========================================
echo Done!
echo ==========================================
echo.
echo Next steps:
echo   1. Run start_nb10.bat
echo   2. Installation will now use online mode (PyPI)
echo   3. Requires internet connection
echo.
pause
