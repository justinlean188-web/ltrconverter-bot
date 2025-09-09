#!/bin/bash

# LTR Converter Bot - APK Build Script
# This script automates the APK building process

echo "🤖 LTR Converter Bot - APK Builder"
echo "=================================="

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer not found. Installing..."
    pip3 install buildozer
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install buildozer. Please install manually:"
        echo "   pip3 install buildozer"
        exit 1
    fi
fi

# Check if Cython is installed
if ! python3 -c "import Cython" &> /dev/null; then
    echo "📦 Installing Cython..."
    pip3 install Cython
fi

# Initialize buildozer if needed
if [ ! -f "buildozer.spec" ]; then
    echo "🔧 Initializing buildozer..."
    buildozer init
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
buildozer android clean

# Build the APK
echo "🔨 Building APK..."
echo "This may take 10-30 minutes on first build..."

buildozer android debug

# Check if build was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ APK built successfully!"
    echo "📱 APK location: bin/ltrconverter-1.0-debug.apk"
    echo ""
    echo "📋 Next steps:"
    echo "1. Transfer the APK to your Android device"
    echo "2. Enable 'Install from unknown sources' in Android settings"
    echo "3. Install the APK"
    echo "4. Open the app and configure your bot settings"
    echo ""
    echo "🔧 To install via ADB:"
    echo "   adb install bin/ltrconverter-1.0-debug.apk"
else
    echo ""
    echo "❌ Build failed!"
    echo "📋 Common solutions:"
    echo "1. Check Java version (should be Java 8):"
    echo "   java -version"
    echo "2. Install missing dependencies:"
    echo "   sudo apt install openjdk-8-jdk python3-dev"
    echo "3. Check buildozer.spec configuration"
    echo "4. Try cleaning and rebuilding:"
    echo "   buildozer android clean"
    echo "   buildozer android debug"
fi
