@echo off
REM GitHub Actions Setup Helper
echo 🤖 LTR Converter Bot - GitHub Actions Setup
echo ===========================================

echo.
echo 📋 This script will help you set up GitHub Actions for APK building
echo.

echo 🔧 Step 1: Create GitHub Repository
echo    - Go to https://github.com
echo    - Click "New repository"
echo    - Name: ltrconverter-bot
echo    - Make it PUBLIC (required for free GitHub Actions)
echo    - Don't initialize with README
echo.

echo 📁 Step 2: Upload Project Files
echo    - Click "uploading an existing file" in your repository
echo    - Upload ALL files from this folder
echo    - Commit message: "Initial commit - LTR Converter Bot"
echo.

echo 🚀 Step 3: Enable GitHub Actions
echo    - Go to "Actions" tab in your repository
echo    - Click "I understand my workflows, go ahead and enable them"
echo.

echo 🔨 Step 4: Build APK
echo    - Go to "Actions" tab
echo    - Click "Build Android APK" workflow
echo    - Click "Run workflow" button
echo    - Wait for build to complete (10-30 minutes)
echo.

echo 📱 Step 5: Download APK
echo    - Click on completed workflow
echo    - Scroll to "Artifacts" section
echo    - Download "ltrconverter-apk"
echo    - Extract ZIP to get your APK file
echo.

echo ✅ That's it! Your APK will be built in the cloud for free!
echo.

echo 📚 For detailed instructions, see:
echo    - upload_to_github.md
echo    - setup_github_actions.md
echo.

pause
