@echo off
REM LTR Converter Bot - APK Build Script for Windows
REM This script automates the APK building process

echo 🤖 LTR Converter Bot - APK Builder
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.7+ first.
    pause
    exit /b 1
)

REM Check if buildozer is installed
python -c "import buildozer" >nul 2>&1
if errorlevel 1 (
    echo ❌ Buildozer not found. Installing...
    pip install buildozer
    if errorlevel 1 (
        echo ❌ Failed to install buildozer. Please install manually:
        echo    pip install buildozer
        pause
        exit /b 1
    )
)

REM Check if Cython is installed
python -c "import Cython" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Cython...
    pip install Cython
)

REM Initialize buildozer if needed
if not exist "buildozer.spec" (
    echo 🔧 Initializing buildozer...
    python -m buildozer init
)

REM Clean previous builds
echo 🧹 Cleaning previous builds...
python -m buildozer android clean

REM Build the APK
echo 🔨 Building APK...
echo This may take 10-30 minutes on first build...

python -m buildozer android debug

REM Check if build was successful
if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    echo 📋 Common solutions:
    echo 1. Install WSL (Windows Subsystem for Linux) for better compatibility
    echo 2. Use Ubuntu or Linux for building
    echo 3. Check buildozer.spec configuration
    echo 4. Try cleaning and rebuilding:
    echo    buildozer android clean
    echo    buildozer android debug
    pause
    exit /b 1
) else (
    echo.
    echo ✅ APK built successfully!
    echo 📱 APK location: bin\ltrconverter-1.0-debug.apk
    echo.
    echo 📋 Next steps:
    echo 1. Transfer the APK to your Android device
    echo 2. Enable 'Install from unknown sources' in Android settings
    echo 3. Install the APK
    echo 4. Open the app and configure your bot settings
    echo.
    echo 🔧 To install via ADB:
    echo    adb install bin\ltrconverter-1.0-debug.apk
)

pause
