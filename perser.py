import json
import requests
import socket
import subprocess
import platform
from telegram import Update
import telebot
from telebot.types import ReactionTypeEmoji , Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---

# This is the URL where your Flask API is running
TOKEN = "8083952920:AAFQD3RGAW_OdM2pZscy5NeReqUq-GytXrI"

def get_local_ip():
    """Auto-detect local IP address for API connection"""
    try:
        # Method 1: Try to connect to a remote address to get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to a remote address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            print(f"🔍 Auto-detected local IP: {local_ip}")
            return local_ip
    except Exception as e:
        print(f"⚠️  Could not auto-detect IP: {e}")
        
        # Method 2: Try platform-specific commands
        try:
            if platform.system() == "Windows":
                # Windows: ipconfig
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if 'IPv4 Address' in line and '192.168.' in line:
                        ip = line.split(':')[-1].strip()
                        print(f"🔍 Found Windows IP: {ip}")
                        return ip
            elif platform.system() == "Linux" or platform.system() == "Android":
                # Linux/Android: hostname -I or ip route
                try:
                    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                    if result.returncode == 0:
                        ips = result.stdout.strip().split()
                        for ip in ips:
                            if ip.startswith('192.168.'):
                                print(f"🔍 Found Linux/Android IP: {ip}")
                                return ip
                except:
                    pass
                    
                try:
                    result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'src' in line:
                                ip = line.split('src')[-1].strip()
                                if ip.startswith('192.168.'):
                                    print(f"🔍 Found IP via route: {ip}")
                                    return ip
                except:
                    pass
        except Exception as e2:
            print(f"⚠️  Platform-specific IP detection failed: {e2}")
    
    # Fallback to default IP
    default_ip = "192.168.1.107"
    print(f"⚠️  Using fallback IP: {default_ip}")
    return default_ip

# Auto-detect API URL
LOCAL_IP = get_local_ip()
API_URL = f"http://{LOCAL_IP}:5001/send_command"
API_URL_CONFIRM = f"http://{LOCAL_IP}:5001/confirm_invoice"

print(f"🚀 API URLs configured:")
print(f"   Main API: {API_URL}")
print(f"   Confirm API: {API_URL_CONFIRM}")

def refresh_api_urls():
    """Refresh API URLs with current IP address"""
    global API_URL, API_URL_CONFIRM, LOCAL_IP
    new_ip = get_local_ip()
    if new_ip != LOCAL_IP:
        LOCAL_IP = new_ip
        API_URL = f"http://{LOCAL_IP}:5001/send_command"
        API_URL_CONFIRM = f"http://{LOCAL_IP}:5001/confirm_invoice"
        print(f"🔄 API URLs refreshed:")
        print(f"   Main API: {API_URL}")
        print(f"   Confirm API: {API_URL_CONFIRM}")
        return True
    return False

def test_api_connection():
    """Test if API is reachable"""
    try:
        response = requests.get(f"http://{LOCAL_IP}:5001/", timeout=5)
        return response.status_code == 200
    except:
        return False

# This is the ID of the group you want to send images TO


# TARGET_GROUP_ID = -1002886297196 # nich
TARGET_GROUP_ID = -4938742244 # bot2
# TARGET_GROUP_ID = -1002793925276  # testing 
# --- END CONFIGURATION --- 

bot = telebot.TeleBot(TOKEN)

def safe_react(chat_id, message_id, emoji):
    """Safely add reaction with error handling"""
    try:
        bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[ReactionTypeEmoji(emoji)]
        )
        return True
    except Exception as e:
        print(f"Failed to set reaction: {e}")
        return False

@bot.message_handler(commands=['cf', 'confirm'])
def confirm_invoice(message: Message):
    """
    Usage: /cf <id> <name> <time> or /confirm <id> <name> <time>
    Sends a special confirmation command to the API for Android processing.
    """
    # Parse command arguments
    command_parts = message.text.split()
    print(command_parts)
    if len(command_parts) < 4:
        bot.reply_to(message, "Usage: /cf <id> <name> <time>\nExample: /cf 1 nich 10:30 or /cf 1 nich vn or /cf 1 nich kh or /cf 1 nich usa")
        return

    invoice_id = command_parts[1]
    invoice_name = command_parts[2]
    invoice_time = command_parts[3]
    
    # Send as a special command to /send_command
    payload = {"text": f"CONFIRM {invoice_id} {invoice_name} {invoice_time}"}
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            safe_react(message.chat.id, message.message_id, "👌")
        else:
            bot.reply_to(message, f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        # Try to refresh IP and retry once
        print("⚠️  Connection failed, trying to refresh IP...")
        if refresh_api_urls():
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(message.chat.id, message.message_id, "👌")
                    bot.reply_to(message, "✅ Command sent after refreshing IP address")
                else:
                    bot.reply_to(message, f"❌ Error: {response.text}")
            except:
                bot.reply_to(message, "Error: Cannot connect to the parsing API even after IP refresh. Please ensure api.py is running.")
        else:
            bot.reply_to(message, "Error: Cannot connect to the parsing API. Please ensure api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['send'])
def resend_photo(message: Message):
    """
    Usage: /send
    Sends a special send command to the API for Android processing.
    """
    command_parts = message.text.split()
    print(command_parts)
    
    payload = {"text": "SEND"}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            safe_react(message.chat.id, message.message_id, "👌")
        else:
            bot.reply_to(message, f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        # Try to refresh IP and retry once
        print("⚠️  Connection failed, trying to refresh IP...")
        if refresh_api_urls():
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(message.chat.id, message.message_id, "👌")
                    bot.reply_to(message, "✅ Command sent after refreshing IP address")
                else:
                    bot.reply_to(message, f"❌ Error: {response.text}")
            except:
                bot.reply_to(message, "Error: Cannot connect to the parsing API even after IP refresh. Please ensure api.py is running.")
        else:
            bot.reply_to(message, "Error: Cannot connect to the parsing API. Please ensure api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['setup_bot'])
def setup_bot(message: Message):
    """
    Usage: /setup_bot
    Sends a special setup_bot command to the API for Android processing.
    """
    command_parts = message.text.split()
    print(command_parts)
    
    payload = {"text": "SETUP_BOT"}
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            safe_react(message.chat.id, message.message_id, "👌")
        else:
            bot.reply_to(message, f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        # Try to refresh IP and retry once
        print("⚠️  Connection failed, trying to refresh IP...")
        if refresh_api_urls():
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(message.chat.id, message.message_id, "👌")
                    bot.reply_to(message, "✅ Command sent after refreshing IP address")
                else:
                    bot.reply_to(message, f"❌ Error: {response.text}")
            except:
                bot.reply_to(message, "Error: Cannot connect to the parsing API even after IP refresh. Please ensure api.py is running.")
        else:
            bot.reply_to(message, "Error: Cannot connect to the parsing API. Please ensure api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['start'])
def start(message: Message):
    """Sends a welcome message."""
    welcome_msg = """🤖 **LTR Converter Bot**

**Available Commands:**
• `/start` - Show this help message
• `/cf <id> <name> <time>` - Confirm invoice
• `/add <id> <name> <time>\\nText` - Add betting data
• `/send` - Send resend command to Android
• `/setup_bot` - Send setup_bot command to Android
• `/refresh_ip` - Refresh IP addresses
• `/status` - Show bot status

**Examples:**
• `/cf 19 chan 7:30` - Confirm invoice
• `/cf 1 nich vn` - Confirm with VN time
• `/add 1 nich 10:30\\nABCD 10-1000 20-2000` - Add betting data

Send me multi-line text to parse or a photo to forward! 📸"""
    
    bot.reply_to(message, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['refresh_ip'])
def refresh_ip_command(message: Message):
    """Manually refresh IP addresses and test API connection"""
    try:
        if refresh_api_urls():
            bot.reply_to(message, f"🔄 IP addresses refreshed!\nMain API: {API_URL}\nConfirm API: {API_URL_CONFIRM}")
        else:
            bot.reply_to(message, f"ℹ️ IP addresses unchanged\nMain API: {API_URL}\nConfirm API: {API_URL_CONFIRM}")
        
        # Test connection
        if test_api_connection():
            bot.reply_to(message, "✅ API connection test successful!")
        else:
            bot.reply_to(message, "❌ API connection test failed. Check if api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error refreshing IP: {e}")

@bot.message_handler(commands=['status'])
def status_command(message: Message):
    """Show current bot status and API configuration"""
    try:
        status_msg = f"🤖 **Bot Status**\n\n"
        status_msg += f"🔗 **API URLs:**\n"
        status_msg += f"   Main: `{API_URL}`\n"
        status_msg += f"   Confirm: `{API_URL_CONFIRM}`\n\n"
        status_msg += f"🌐 **Local IP:** `{LOCAL_IP}`\n"
        status_msg += f"📱 **Target Group:** `{TARGET_GROUP_ID}`\n\n"
        
        # Test API connection
        if test_api_connection():
            status_msg += "✅ **API Status:** Connected"
        else:
            status_msg += "❌ **API Status:** Disconnected"
        
        bot.reply_to(message, status_msg, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"❌ Error getting status: {e}")

@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
    """Handles photo messages and forwards them."""
    # Get the largest photo (last in the list)
    if message.photo:
        photo = message.photo[-1]
        file_id = photo.file_id
        
        try:
            bot.send_photo(chat_id=TARGET_GROUP_ID, photo=file_id)
            safe_react(message.chat.id, message.message_id, "👌")
            print(f"Photo forwarded to group {TARGET_GROUP_ID}")
        except Exception as e:
            bot.reply_to(message, f"Sorry, I couldn't forward the photo. Error: {e}")

@bot.message_handler(commands=['add'])
def handle_add(message: Message):
    """
    Usage: /add <id> <name> <time>\nText
    Sends the entire message (first line command + following text) to the API.
    """
    if not message.text:
        return
    lines = message.text.splitlines()
    if not lines:
        return
    header_parts = lines[0].split()
    if len(header_parts) < 4:
        bot.reply_to(message, "Usage: /add <id> <name> <time>\\nText")
        return

    payload = {"text": message.text.strip()}
    
    # Try to send with current API URL, refresh IP if it fails
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            safe_react(message.chat.id, message.message_id, "👌")
            print("Add command sent to API successfully")
        else:
            bot.reply_to(message, f"❌ Error: {response.text}")
    except requests.exceptions.ConnectionError:
        # Try to refresh IP and retry once
        print("⚠️  Connection failed, trying to refresh IP...")
        if refresh_api_urls():
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(message.chat.id, message.message_id, "👌")
                    print("Add command sent to API successfully after IP refresh")
                    bot.reply_to(message, "✅ Command sent after refreshing IP address")
                else:
                    bot.reply_to(message, f"❌ Error: {response.text}")
            except:
                bot.reply_to(message, "Error: Cannot connect to the parsing API even after IP refresh. Please ensure api.py is running.")
        else:
            bot.reply_to(message, "Error: Cannot connect to the parsing API. Please ensure api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(content_types=['text'])
def handle_text(message: Message):
    """Receives a text message, sends it to the API, and replies."""
    # Skip if it's a command (already handled by command handlers)
    if message.text and message.text.startswith('/'):
        return
    
    if not message.text:
        return
        
    user_input_text = message.text.strip()
    print(f"Received text, sending to API...")
    
    payload = {"text": user_input_text}
    
    # Try to send with current API URL, refresh IP if it fails
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        if response.status_code == 200:
            safe_react(message.chat.id, message.message_id, "👌")
            print("Text sent to API successfully")
        else:
            bot.reply_to(message, f"Error sending command to API. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        # Try to refresh IP and retry once
        print("⚠️  Connection failed, trying to refresh IP...")
        if refresh_api_urls():
            try:
                response = requests.post(API_URL, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(message.chat.id, message.message_id, "👌")
                    print("Text sent to API successfully after IP refresh")
                    bot.reply_to(message, "✅ Message sent after refreshing IP address")
                else:
                    bot.reply_to(message, f"Error sending command to API. Status: {response.status_code}")
            except:
                bot.reply_to(message, "Error: Cannot connect to the parsing API even after IP refresh. Please ensure api.py is running.")
        else:
            bot.reply_to(message, "Error: Cannot connect to the parsing API. Please ensure api.py is running.")
    except Exception as e:
        bot.reply_to(message, f"An unexpected error occurred: {e}")

def main():
    """Starts the bot and registers all handlers."""
    print("Combined bot is starting...")
    
    # Try to get bot info, but don't crash if it fails
    try:
        bot_info = bot.get_me()
        print(f"Bot username: {bot_info.username}")
        print(f"Bot name: {bot_info.first_name}")
    except Exception as e:
        print(f"⚠️  Warning: Could not get bot info: {e}")
        print("Bot will continue running...")
    
    try:
        bot.infinity_polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")

if __name__ == '__main__':
    main()