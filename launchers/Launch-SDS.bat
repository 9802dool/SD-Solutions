@echo off
setlocal
pushd "%~dp0.."

where python >nul 2>&1
if errorlevel 1 (
    msg * "SD Solutions: Python was not found. Install Python 3 and try again."
    exit /b 1
)

echo Starting SD Solutions (SDS)...
python -m pip install -r requirements.txt -q >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8501" ^| findstr "LISTENING"') do (
    start "" http://localhost:8501
    popd
    exit /b 0
)

start "SD Solutions (SDS)" /MIN /D "%CD%" cmd /c "python -m streamlit run sds\app.py --server.headless true --browser.gatherUsageStats false"

set /a tries=0
:waitloop
set /a tries+=1
if %tries% gtr 30 (
    msg * "SD Solutions: The app is taking too long to start. Check that port 8501 is free."
    popd
    exit /b 1
)
timeout /t 1 /nobreak >nul
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri 'http://localhost:8501' -UseBasicParsing -TimeoutSec 2).StatusCode | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 goto waitloop

start "" http://localhost:8501
popd
exit /b 0
