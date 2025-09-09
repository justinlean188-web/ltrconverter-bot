#!/usr/bin/env python3
"""
Environment Checker for LTR Converter Bot APK Building
This script checks your environment and provides guidance for building APK
"""

import sys
import platform
import subprocess
import os

def check_python():
    """Check Python version and installation"""
    print("🐍 Checking Python...")
    version = sys.version_info
    print(f"   Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("   ❌ Python 3.7+ required")
        return False
    else:
        print("   ✅ Python version is compatible")
        return True

def check_platform():
    """Check operating system"""
    print(f"\n💻 Checking platform...")
    system = platform.system()
    print(f"   Operating System: {system}")
    
    if system == "Windows":
        print("   ⚠️  Windows detected - Buildozer only supports iOS on Windows")
        print("   📋 Solutions:")
        print("      1. Use WSL (Windows Subsystem for Linux)")
        print("      2. Use Linux Virtual Machine")
        print("      3. Use online build services")
        return False
    elif system == "Linux":
        print("   ✅ Linux detected - Perfect for Android APK building")
        return True
    elif system == "Darwin":  # macOS
        print("   ✅ macOS detected - Can build Android APK")
        return True
    else:
        print(f"   ❓ Unknown system: {system}")
        return False

def check_buildozer():
    """Check if buildozer is installed"""
    print(f"\n🔨 Checking Buildozer...")
    try:
        import buildozer
        print("   ✅ Buildozer is installed")
        return True
    except ImportError:
        print("   ❌ Buildozer not installed")
        print("   📋 Install with: pip install buildozer")
        return False

def check_java():
    """Check if Java is installed"""
    print(f"\n☕ Checking Java...")
    try:
        result = subprocess.run(['java', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stderr.split('\n')[0]
            print(f"   ✅ Java found: {version_line}")
            return True
        else:
            print("   ❌ Java not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ❌ Java not found")
        print("   📋 Install Java 8: sudo apt install openjdk-8-jdk")
        return False

def check_android_sdk():
    """Check if Android SDK is available"""
    print(f"\n📱 Checking Android SDK...")
    # This is a simplified check - in reality, buildozer handles SDK download
    print("   ℹ️  Android SDK will be downloaded automatically by buildozer")
    return True

def check_project_files():
    """Check if required project files exist"""
    print(f"\n📁 Checking project files...")
    required_files = [
        'main.py',
        'api_wrapper.py', 
        'bot_wrapper.py',
        'buildozer.spec',
        'requirements_kivy.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - Missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"   ❌ Missing {len(missing_files)} required files")
        return False
    else:
        print("   ✅ All required files present")
        return True

def provide_solutions():
    """Provide solutions based on environment"""
    print(f"\n🔧 SOLUTIONS FOR BUILDING ANDROID APK:")
    print("=" * 50)
    
    system = platform.system()
    
    if system == "Windows":
        print("\n🪟 WINDOWS SOLUTIONS:")
        print("1. 🐧 WSL (Recommended):")
        print("   - Install WSL: wsl --install")
        print("   - Install Ubuntu from Microsoft Store")
        print("   - Run: setup_wsl.bat")
        print()
        print("2. 🖥️  Virtual Machine:")
        print("   - Install VirtualBox/VMware")
        print("   - Install Ubuntu in VM")
        print("   - Follow Linux instructions")
        print()
        print("3. ☁️  Online Build Services:")
        print("   - GitHub Actions (free)")
        print("   - GitLab CI/CD (free)")
        print("   - Google Colab (free)")
        print()
        print("4. 🏢 Cloud Development:")
        print("   - Use cloud Linux instances")
        print("   - AWS, Google Cloud, Azure")
    
    elif system == "Linux":
        print("\n🐧 LINUX BUILD INSTRUCTIONS:")
        print("1. Install dependencies:")
        print("   sudo apt update")
        print("   sudo apt install openjdk-8-jdk python3-pip buildozer")
        print()
        print("2. Build APK:")
        print("   chmod +x build_apk.sh")
        print("   ./build_apk.sh")
        print()
        print("3. Or build manually:")
        print("   buildozer android debug")
    
    elif system == "Darwin":  # macOS
        print("\n🍎 MACOS BUILD INSTRUCTIONS:")
        print("1. Install dependencies:")
        print("   brew install openjdk@8 python3")
        print("   pip3 install buildozer")
        print()
        print("2. Build APK:")
        print("   chmod +x build_apk.sh")
        print("   ./build_apk.sh")

def main():
    """Main function"""
    print("🤖 LTR Converter Bot - Environment Checker")
    print("=" * 45)
    
    checks = [
        check_python,
        check_platform,
        check_buildozer,
        check_java,
        check_android_sdk,
        check_project_files
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Error during check: {e}")
            results.append(False)
    
    print(f"\n📊 ENVIRONMENT SUMMARY:")
    print("=" * 25)
    passed = sum(results)
    total = len(results)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Environment is ready for APK building!")
        print("Run: ./build_apk.sh (Linux/macOS) or setup_wsl.bat (Windows)")
    else:
        print(f"\n⚠️  {total - passed} issue(s) found. See solutions below.")
        provide_solutions()
    
    print(f"\n📚 For detailed instructions, see:")
    print("   - README_ANDROID.md")
    print("   - SETUP_GUIDE.md")
    print("   - PROJECT_SUMMARY.md")

if __name__ == "__main__":
    main()
