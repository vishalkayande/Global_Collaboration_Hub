@echo off
echo ============================================================
echo 🎯 NGO Collaboration Hub - Single Command Launcher
echo ============================================================
echo.
echo 🚀 Starting Backend Server...
start "Backend Server" cmd /k "cd backend && .\venv\Scripts\Activate.ps1 && python app.py"
echo.
echo ⏳ Waiting for backend to start...
timeout /t 3 /nobreak >nul
echo.
echo 🌐 Opening Frontend...
start "" "frontend\index.html"
echo.
echo ✅ Project Started Successfully!
echo 📋 Available URLs:
echo    • Frontend: frontend\index.html
echo    • Backend API: http://localhost:5000/api
echo    • Health Check: http://localhost:5000/api/health
echo.
echo 📝 Close the backend command window to stop the server
pause

