#!/usr/bin/env python3
"""
Test script for LTR Converter Bot Kivy App
Run this to test the app before building APK
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import kivy
        print(f"✅ Kivy {kivy.__version__}")
    except ImportError as e:
        print(f"❌ Kivy import failed: {e}")
        return False
    
    try:
        import requests
        print(f"✅ Requests {requests.__version__}")
    except ImportError as e:
        print(f"❌ Requests import failed: {e}")
        return False
    
    try:
        import telebot
        print("✅ PyTelegramBotAPI")
    except ImportError as e:
        print(f"❌ PyTelegramBotAPI import failed: {e}")
        return False
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration system"""
    print("\n🔧 Testing configuration...")
    
    try:
        from main import ConfigManager
        config_manager = ConfigManager()
        config = config_manager.load_config()
        print("✅ Configuration system working")
        print(f"   Default bot token: {config['bot_token'][:10]}...")
        print(f"   Default chat ID: {config['chat_id']}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_api_wrapper():
    """Test API wrapper"""
    print("\n🌐 Testing API wrapper...")
    
    try:
        from api_wrapper import app, add_command_to_queue
        print("✅ API wrapper imports successful")
        
        # Test command queue
        test_command = {"type": "test", "data": "test"}
        command_id = add_command_to_queue(test_command)
        print(f"✅ Command queue working (ID: {command_id})")
        return True
    except Exception as e:
        print(f"❌ API wrapper test failed: {e}")
        return False

def test_bot_wrapper():
    """Test bot wrapper"""
    print("\n🤖 Testing bot wrapper...")
    
    try:
        from bot_wrapper import TelegramBot, get_local_ip
        print("✅ Bot wrapper imports successful")
        
        # Test IP detection
        ip = get_local_ip()
        print(f"✅ IP detection working: {ip}")
        return True
    except Exception as e:
        print(f"❌ Bot wrapper test failed: {e}")
        return False

def test_kivy_app():
    """Test Kivy app initialization"""
    print("\n📱 Testing Kivy app...")
    
    try:
        from main import LTRConverterApp
        print("✅ Kivy app imports successful")
        
        # Don't actually run the app, just test imports
        print("✅ App structure is valid")
        return True
    except Exception as e:
        print(f"❌ Kivy app test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 LTR Converter Bot - App Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_api_wrapper,
        test_bot_wrapper,
        test_kivy_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results:")
    print(f"   Passed: {passed}/{total}")
    print(f"   Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! The app is ready for building.")
        print("\n📋 Next steps:")
        print("1. Run: python main.py (to test GUI)")
        print("2. Build APK: ./build_apk.sh (Linux) or build_apk.bat (Windows)")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please fix issues before building.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
