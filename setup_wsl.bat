@echo off
REM WSL Setup Script for LTR Converter Bot APK Building
echo 🤖 LTR Converter Bot - WSL Setup for Android APK Building
echo ========================================================

echo.
echo ⚠️  IMPORTANT: Buildozer on Windows only supports iOS, not Android!
echo    To build Android APK, you need Linux environment.
echo.

echo 📋 This script will help you set up WSL (Windows Subsystem for Linux)
echo    which allows you to run Linux commands on Windows.
echo.

echo 🔧 Step 1: Installing WSL...
echo    This may require Administrator privileges.
echo.

REM Check if WSL is already installed
wsl --status >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL not found. Installing...
    echo    Please run PowerShell as Administrator and execute:
    echo    wsl --install
    echo.
    echo    Then restart your computer and run this script again.
    pause
    exit /b 1
) else (
    echo ✅ WSL is already installed!
)

echo.
echo 🔧 Step 2: Setting up Ubuntu...
echo    This will install Ubuntu and required packages.
echo.

echo 📦 Installing build dependencies in WSL...
wsl -e bash -c "
    sudo apt update && \
    sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev && \
    pip3 install buildozer cython
"

if errorlevel 1 (
    echo ❌ Failed to install dependencies in WSL
    echo    Please run the following commands manually in WSL:
    echo    sudo apt update
    echo    sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
    echo    pip3 install buildozer cython
    pause
    exit /b 1
)

echo.
echo 🔧 Step 3: Building APK in WSL...
echo    This will take 10-30 minutes on first build.
echo.

wsl -e bash -c "
    cd /mnt/d/bot/ltrconverter-android-update && \
    chmod +x build_apk.sh && \
    ./build_apk.sh
"

if errorlevel 1 (
    echo ❌ APK build failed in WSL
    echo    Please check the error messages above.
    echo    You can also try building manually in WSL:
    echo    wsl
    echo    cd /mnt/d/bot/ltrconverter-android-update
    echo    ./build_apk.sh
    pause
    exit /b 1
)

echo.
echo ✅ APK built successfully!
echo 📱 APK location: bin/ltrconverter-1.0-debug.apk
echo.
echo 📋 Next steps:
echo 1. Transfer the APK to your Android device
echo 2. Enable 'Install from unknown sources' in Android settings
echo 3. Install the APK
echo 4. Open the app and configure your bot settings
echo.

pause
