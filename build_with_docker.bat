@echo off
REM Docker Build Script for LTR Converter Bot APK
echo 🤖 LTR Converter Bot - Docker APK Builder
echo ==========================================

echo.
echo 📋 This script will build your APK using Docker
echo    No sudo required - Docker handles everything!
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found!
    echo.
    echo 📋 Please install Docker Desktop:
    echo    1. Download from: https://www.docker.com/products/docker-desktop
    echo    2. Install Docker Desktop
    echo    3. Start Docker Desktop
    echo    4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Docker found!
echo.

echo 🔨 Building APK with Docker...
echo    This may take 10-30 minutes on first build...
echo.

REM Build Docker image and create APK
docker build -t ltrconverter-builder .

if errorlevel 1 (
    echo ❌ Docker build failed!
    echo    Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Docker build successful!
echo.

echo 📱 Extracting APK from Docker container...
docker run --rm -v "%cd%\output:/output" ltrconverter-builder cp /app/bin/*.apk /output/

if errorlevel 1 (
    echo ❌ Failed to extract APK
    echo    Trying alternative method...
    
    REM Alternative: Run container and copy files
    docker run --name temp-container ltrconverter-builder
    docker cp temp-container:/app/bin/ ./output/
    docker rm temp-container
)

echo.
echo ✅ APK extraction complete!
echo.

REM Check if APK was created
if exist "output\*.apk" (
    echo 🎉 APK built successfully!
    echo 📱 APK location: output\
    echo.
    echo 📋 Next steps:
    echo 1. Transfer the APK to your Android device
    echo 2. Enable 'Install from unknown sources' in Android settings
    echo 3. Install the APK
    echo 4. Open the app and configure your bot settings
    echo.
    
    REM List APK files
    echo 📁 APK files:
    dir /b output\*.apk
) else (
    echo ❌ APK not found in output directory
    echo    Please check the build logs above for errors.
)

echo.
pause
