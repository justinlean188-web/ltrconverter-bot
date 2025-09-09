# LTR Converter Bot - Android APK

This project creates an Android APK for the LTR Converter Bot using Kivy and Buildozer.

## Features

- 🤖 **Telegram Bot Integration**: Full Telegram bot functionality
- 📱 **Mobile Interface**: Easy-to-use Kivy GUI for configuration
- ⚙️ **Configurable Settings**: Set bot token and group ID through the app
- 🔄 **Background Services**: Flask API and Telegram bot run in background
- 📊 **Real-time Status**: Monitor bot status and logs
- 🔗 **API Integration**: Complete betting parsing and command processing

## Prerequisites

### For Building APK (Linux/Ubuntu recommended)

1. **Install Buildozer dependencies**:
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev
```

2. **Install Buildozer**:
```bash
pip3 install buildozer
```

3. **Install Cython**:
```bash
pip3 install cython
```

### For Development/Testing

1. **Install Python dependencies**:
```bash
pip install -r requirements_kivy.txt
```

## Project Structure

```
├── main.py                 # Main Kivy application
├── api.py                  # Original Flask API
├── perser.py              # Original Telegram bot
├── api_wrapper.py         # Simplified API for mobile
├── bot_wrapper.py         # Simplified bot for mobile
├── buildozer.spec         # Buildozer configuration
├── requirements_kivy.txt  # Python dependencies
└── README_ANDROID.md      # This file
```

## Building the APK

### 1. Prepare the Environment

```bash
# Clone or download the project
cd ltrconverter-android-update

# Initialize buildozer (first time only)
buildozer init
```

### 2. Build the APK

```bash
# Build debug APK
buildozer android debug

# Build release APK (requires signing)
buildozer android release
```

The APK will be created in the `bin/` directory.

### 3. Install on Device

```bash
# Install debug APK
adb install bin/ltrconverter-1.0-debug.apk

# Or transfer the APK file to your device and install manually
```

## Usage

### 1. First Launch

1. Open the LTR Converter Bot app
2. Enter your Telegram bot token
3. Enter the target chat/group ID (with minus sign for groups)
4. Set the API port (default: 5001)
5. Optionally enable "Auto Start on App Launch"

### 2. Starting the Bot

1. Tap "Start Bot" button
2. Wait for "Running" status
3. The bot will start processing messages

### 3. Bot Commands

The bot supports these commands:
- `/start` - Show help message
- `/cf <id> <name> <time>` - Confirm invoice
- `/send` - Send resend command
- `/setup_bot` - Send setup command
- `/add <id> <name> <time>\nText` - Add betting data

### 4. Monitoring

- Check the "Status" field for bot state
- View logs in the "Logs" section
- Use "Test API Connection" to verify connectivity

## Configuration

### Bot Token
Get your bot token from [@BotFather](https://t.me/botfather) on Telegram.

### Chat/Group ID
- For groups: Use the group ID (usually negative number)
- For private chats: Use the user ID (positive number)
- You can get IDs using [@userinfobot](https://t.me/userinfobot)

### API Port
Default port is 5001. Change if needed for your network setup.

## Troubleshooting

### Build Issues

1. **Java version error**:
```bash
sudo update-alternatives --config java
# Select Java 8
```

2. **Permission denied**:
```bash
sudo chown -R $USER:$USER ~/.buildozer
```

3. **Missing dependencies**:
```bash
sudo apt install python3-dev python3-venv
```

### Runtime Issues

1. **Bot not starting**:
   - Check bot token format
   - Verify internet connection
   - Check chat ID format

2. **API connection failed**:
   - Ensure API port is not blocked
   - Check firewall settings
   - Try different port number

3. **Permission errors**:
   - Grant all required permissions to the app
   - Check Android security settings

## Development

### Testing on Desktop

```bash
# Run the Kivy app directly
python main.py
```

### Modifying the App

1. Edit `main.py` for GUI changes
2. Edit `api_wrapper.py` for API modifications
3. Edit `bot_wrapper.py` for bot behavior changes
4. Update `buildozer.spec` for build configuration

### Adding Features

1. Add new UI elements in `main.py`
2. Implement backend logic in wrapper files
3. Update requirements if new packages needed
4. Test thoroughly before building APK

## Security Notes

- Bot tokens are stored locally on device
- No data is sent to external servers (except Telegram)
- All processing happens locally
- Configuration is saved in app's private storage

## Support

For issues or questions:
1. Check the logs in the app
2. Verify configuration settings
3. Test API connection
4. Check network connectivity

## License

This project is for educational and personal use. Ensure compliance with Telegram's Terms of Service and your local laws.
