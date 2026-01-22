@echo off

REM 设置字符编码为UTF-8
chcp 65001 >nul

REM 加载.env文件中的环境变量
if exist .env (
    for /f "tokens=1* delims==" %%a in (.env) do (
        if not "%%a"=="" set "%%a=%%b"
    )
)

REM 设置默认环境变量
if "%BACKEND_PORT%"=="" set "BACKEND_PORT=8000"
if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=3000"
if "%MYSQL_PORT%"=="" set "MYSQL_PORT=3306"
if "%USE_MYSQL%"=="" set "USE_MYSQL=true"
if "%C_LIBRARY_PATH%"=="" set "C_LIBRARY_PATH=./libs"


echo ================================
echo   Algorithm Testing Platform Startup
echo ================================
echo.

REM 检查环境依赖

echo Checking environment dependencies...

REM 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not detected, please install Python 3.8+
    pause
    exit /b 1
) else (
    echo [INFO] Python detected
)

REM 检查Node.js环境
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not detected, please install Node.js 16+
    pause
    exit /b 1
) else (
    echo [INFO] Node.js detected
)

REM 检查C库
set "lib_check=1"
if %lib_check% equ 1 (
    echo [INFO] Checking C libraries...
    if exist "%C_LIBRARY_PATH%\oqs.dll" (
        echo [INFO] ✓ Found oqs.dll library
    ) else (
        echo [WARNING] ✗ oqs.dll library not found
        set "use_mock=true"
    )
    
    dir /b "%C_LIBRARY_PATH%\libpqclean_*.dll" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [INFO] ✓ Found PQClean libraries
    ) else (
        echo [WARNING] ✗ PQClean libraries not found
        set "use_mock=true"
    )
    
    if "%use_mock%"=="true" (
        echo [WARNING] Some C library files are missing, the system will run in mock mode
        echo [WARNING] Please refer to INSTALLATION_GUIDE.md for compiling C libraries
    )
    echo.
)

REM 检查数据库配置
if "%USE_MYSQL%"=="true" (
    netstat -ano | findstr :%MYSQL_PORT% >nul
    if %errorlevel% neq 0 (
        echo [WARNING] MySQL service not detected on port %MYSQL_PORT%
        echo [WARNING] Please ensure MySQL service is running, or set USE_MYSQL=false to use SQLite
    )
) else (
    echo [INFO] Using SQLite database
)

REM 显示当前环境配置
echo [INFO] Current environment configuration:
echo [INFO] - Database: %if %USE_MYSQL%==true (MySQL) else (SQLite)%
echo [INFO] - Backend Port: %BACKEND_PORT%
echo [INFO] - Frontend Port: %FRONTEND_PORT%
echo [INFO] - C Library Status: %if "%use_mock%"=="true" (Mock Mode) else (Normal Mode)%
echo.

echo [INFO] Environment check completed
echo.

echo Select startup option:
echo 1. Start Backend Service (Python FastAPI)
echo 2. Start Frontend Service (Vue3)
echo 3. Start Full Service (Backend + Frontend)
echo 4. Initialize Database
echo 5. Generate .env.example File
echo 6. Exit
echo.

set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_frontend  
if "%choice%"=="3" goto start_full
if "%choice%"=="4" goto init_database
if "%choice%"=="5" goto create_env_example
if "%choice%"=="6" goto exit
goto invalid_choice

:start_backend
echo.
echo ================================
echo     Starting Backend Service
echo ================================
cd backend
echo [INFO] Installing backend dependencies...
pip install -r requirements.txt
echo [INFO] Starting FastAPI service...
echo [INFO] Backend will start at http://localhost:%BACKEND_PORT%
echo [INFO] API Docs: http://localhost:%BACKEND_PORT%/docs
python -m uvicorn main:app --reload --port %BACKEND_PORT%
goto end

:start_frontend
echo.
echo ================================
echo     Starting Frontend Service
echo ================================
cd frontend
echo [INFO] Installing frontend dependencies...
npm install
echo [INFO] Starting Vue3 development server...
echo [INFO] Frontend will start at http://localhost:%FRONTEND_PORT%
npm run dev -- --port %FRONTEND_PORT%
goto end

:start_full
echo.
echo ================================
echo     Starting Full Service
echo ================================
echo [INFO] Starting both backend and frontend services...
echo [INFO] Backend will start first, then frontend in new window
echo.
echo 1. Backend Service: http://localhost:%BACKEND_PORT%
echo 2. Frontend Service: http://localhost:%FRONTEND_PORT%
echo 3. API Documentation: http://localhost:%BACKEND_PORT%/docs
echo.
echo [TIP] Two command windows will open simultaneously
echo.

REM Start backend
start "Algorithm-Platform-Backend" cmd /k "cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port %BACKEND_PORT%"

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Start frontend
start "Algorithm-Platform-Frontend" cmd /k "cd frontend && npm install && npm run dev -- --port %FRONTEND_PORT%"

echo [INFO] Services are starting, please wait...
echo [INFO] Visit http://localhost:%FRONTEND_PORT% when startup completes
goto end

:init_database
echo.
echo ================================
echo     Initialize Database
echo ================================
echo [INFO] Preparing to create database and table structure...
echo.
echo Please ensure:
echo 1. MySQL service is running (if using MySQL)
echo 2. You have correct database credentials
echo.
set /p confirm="Confirm to continue? (y/n): "
if /i "%confirm%" neq "y" goto end

if "%USE_MYSQL%"=="true" (
    echo [INFO] Importing MySQL database structure...
    mysql -u root -p algorithm_testing < database/schema.sql
) else (
    echo [INFO] Initializing SQLite database...
    cd backend
    python -c "from app.db.database import init_db; init_db()"
    cd ..
)

if %errorlevel% equ 0 (
    echo [SUCCESS] Database initialization completed!
) else (
    echo [ERROR] Database initialization failed, please check:
    echo 1. Is MySQL service running? (if using MySQL)
    echo 2. Are database credentials correct?
    echo 3. Does the database exist?
)
goto end

:create_env_example
echo.
echo ================================
echo   Generating .env.example File
echo ================================
echo [INFO] Preparing environment configuration template...

if exist .env.example (
    echo [INFO] .env.example file already exists
    set /p overwrite="Do you want to overwrite it? (y/n): "
    if /i "%overwrite%" neq "y" goto end
)
 
echo # Database Configuration> .env.example
echo MYSQL_HOST=localhost>> .env.example
echo MYSQL_PORT=3306>> .env.example
echo MYSQL_USER=alg_test>> .env.example
echo MYSQL_PASSWORD=alg_test123>> .env.example
echo MYSQL_DATABASE=algorithm_testing>> .env.example
echo USE_MYSQL=true>> .env.example
echo.>> .env.example
echo # Backend Configuration>> .env.example
echo BACKEND_PORT=8000>> .env.example
echo SECRET_KEY=your-secret-key-here>> .env.example
echo DEBUG=true>> .env.example
echo ENVIRONMENT=development>> .env.example
echo.>> .env.example
echo # Frontend Configuration>> .env.example
echo FRONTEND_PORT=3000>> .env.example
echo VITE_API_BASE_URL=http://localhost:8000>> .env.example
echo.>> .env.example
echo # C Library Configuration>> .env.example
echo C_LIBRARY_PATH=./libs>> .env.example
echo.>> .env.example
echo # Reports Configuration>> .env.example
echo REPORTS_PATH=./reports>> .env.example
 
echo [SUCCESS] .env.example file generated successfully!
echo [INFO] Please copy it to .env and modify according to your environment
goto end

:invalid_choice
echo [ERROR] Invalid choice, please enter 1-6
pause
goto end

:exit
echo [INFO] Exiting startup script
goto end

:end
echo.
echo ================================
echo For help, check docs/manual-setup.md
echo ================================
pause