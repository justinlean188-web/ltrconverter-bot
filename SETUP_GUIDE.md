# LTR Converter Bot - Complete Setup Guide

This guide will help you build an Android APK for your LTR Converter Bot.

## 📋 Overview

The project creates a mobile app that:
- Runs your Telegram bot on Android
- Provides a GUI to configure bot settings
- Processes betting commands through a Flask API
- Forwards photos and handles text messages

## 🛠️ Prerequisites

### Option 1: Linux/Ubuntu (Recommended)

```bash
# Update system
sudo apt update

# Install build dependencies
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# Install Python dependencies
pip3 install buildozer cython
```

### Option 2: Windows with WSL

1. Install Windows Subsystem for Linux (WSL)
2. Install Ubuntu from Microsoft Store
3. Follow Linux instructions in WSL terminal

### Option 3: Windows Native (Limited Support)

```cmd
# Install Python 3.7+
# Download from python.org

# Install dependencies
pip install buildozer cython kivy requests telebot flask
```

## 📁 Project Files

```
ltrconverter-android-update/
├── main.py                 # Main Kivy application
├── api.py                  # Original Flask API (keep as reference)
├── perser.py              # Original Telegram bot (keep as reference)
├── api_wrapper.py         # Simplified API for mobile
├── bot_wrapper.py         # Simplified bot for mobile
├── buildozer.spec         # Buildozer configuration
├── requirements_kivy.txt  # Python dependencies
├── build_apk.sh          # Linux build script
├── build_apk.bat         # Windows build script
├── test_app.py           # Test script
└── README_ANDROID.md     # Detailed documentation
```

## 🚀 Quick Start

### 1. Test the App First

```bash
# Install Python dependencies
pip install -r requirements_kivy.txt

# Run tests
python test_app.py

# Test GUI (optional)
python main.py
```

### 2. Build APK

#### Linux/Ubuntu:
```bash
chmod +x build_apk.sh
./build_apk.sh
```

#### Windows:
```cmd
build_apk.bat
```

#### Manual Build:
```bash
buildozer android debug
```

### 3. Install APK

```bash
# Via ADB
adb install bin/ltrconverter-1.0-debug.apk

# Or transfer APK file to device and install manually
```

## ⚙️ Configuration

### Bot Token
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create new bot with `/newbot`
3. Copy the token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Chat/Group ID
1. Add your bot to the target group
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find the chat ID (negative number for groups)

### App Settings
- **Bot Token**: Your Telegram bot token
- **Chat ID**: Target group ID (with minus sign)
- **API Port**: Default 5001 (change if needed)
- **Auto Start**: Enable to start bot when app opens

## 🔧 Troubleshooting

### Build Issues

#### Java Version Error
```bash
# Check Java version
java -version

# Install Java 8 if needed
sudo apt install openjdk-8-jdk

# Set Java 8 as default
sudo update-alternatives --config java
```

#### Permission Errors
```bash
# Fix buildozer permissions
sudo chown -R $USER:$USER ~/.buildozer
```

#### Missing Dependencies
```bash
# Install additional packages
sudo apt install python3-dev python3-venv libssl-dev
```

### Runtime Issues

#### Bot Not Starting
- ✅ Check bot token format
- ✅ Verify internet connection
- ✅ Confirm chat ID is correct
- ✅ Check app permissions

#### API Connection Failed
- ✅ Ensure API port is not blocked
- ✅ Check firewall settings
- ✅ Try different port number
- ✅ Restart the app

#### App Crashes
- ✅ Check logs in the app
- ✅ Verify all settings are correct
- ✅ Try clearing app data
- ✅ Reinstall the APK

## 📱 App Usage

### First Launch
1. Open the app
2. Enter bot token and chat ID
3. Tap "Start Bot"
4. Wait for "Running" status

### Bot Commands
- `/start` - Show help
- `/cf <id> <name> <time>` - Confirm invoice
- `/send` - Send resend command
- `/setup_bot` - Send setup command

### Monitoring
- Check status indicator (green = running)
- View logs for debugging
- Use "Test API Connection" button

## 🔒 Security Notes

- Bot tokens are stored locally on device
- No data sent to external servers (except Telegram)
- All processing happens locally
- Configuration saved in app's private storage

## 📞 Support

### Common Issues
1. **Build fails**: Use Linux/WSL for better compatibility
2. **Bot doesn't respond**: Check token and chat ID
3. **App crashes**: Verify all permissions granted
4. **API errors**: Check network connectivity

### Getting Help
1. Check app logs first
2. Verify configuration settings
3. Test API connection
4. Check network connectivity
5. Review this guide for solutions

## 🎯 Next Steps

After successful setup:
1. Test all bot commands
2. Configure auto-start if desired
3. Set up proper bot permissions
4. Monitor logs for any issues
5. Consider building release APK for distribution

## 📄 License

This project is for educational and personal use. Ensure compliance with:
- Telegram's Terms of Service
- Your local laws and regulations
- App store policies (if distributing)

---

**Happy Bot Building! 🤖📱**
