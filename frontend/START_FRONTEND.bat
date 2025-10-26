@echo off
echo ========================================
echo Starting Frontend Server
echo ========================================
echo.
echo Make sure API is running on port 5001!
echo If not, run: python ..\api_endpoint_v2.py
echo.
echo Starting frontend on http://localhost:8000
echo.
python serve_frontend.py
pause
