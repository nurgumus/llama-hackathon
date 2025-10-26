@echo off
echo ======================================================================
echo Istanbul Neighborhood Recommendation System - Full Stack Launcher
echo ======================================================================
echo.
echo This will start BOTH servers:
echo   1. API Backend (port 5001)
echo   2. Frontend Server (port 8000)
echo.
echo Press any key to start...
pause > nul
echo.

REM Start API in new window
echo Starting API Server...
start "API Server (5001)" cmd /k "cd /d %~dp0 && python api_endpoint_v2.py"
timeout /t 3 /nobreak > nul

REM Start Frontend in new window
echo Starting Frontend Server...
start "Frontend Server (8000)" cmd /k "cd /d %~dp0frontend && python serve_frontend.py"
timeout /t 2 /nobreak > nul

echo.
echo ======================================================================
echo ✅ Both servers started!
echo ======================================================================
echo.
echo 🔗 Open in browser: http://localhost:8000
echo.
echo 📊 API Health Check: http://localhost:5001/health
echo.
echo Two new windows opened:
echo   - API Server (port 5001)
echo   - Frontend Server (port 8000)
echo.
echo ⚠️  DO NOT close those windows while using the app!
echo.
echo Press any key to exit this launcher...
echo ======================================================================
pause > nul
