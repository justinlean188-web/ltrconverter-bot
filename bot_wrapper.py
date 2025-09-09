"""
Bot Wrapper for Kivy App
Simplified version of perser.py for mobile app usage
"""
import requests
import socket
import subprocess
import platform
import telebot
from telebot.types import ReactionTypeEmoji, Message

# Global configuration (will be set by Kivy app)
TOKEN = ""
TARGET_GROUP_ID = ""

def get_local_ip():
    """Auto-detect local IP address"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        try:
            if platform.system() == "Windows":
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                for line in result.stdout.split('\n'):
                    if 'IPv4 Address' in line and '192.168.' in line:
                        return line.split(':')[-1].strip()
            elif platform.system() in ["Linux", "Android"]:
                try:
                    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
                    if result.returncode == 0:
                        ips = result.stdout.strip().split()
                        for ip in ips:
                            if ip.startswith('192.168.'):
                                return ip
                except:
                    pass
        except Exception:
            pass
    return "192.168.1.107"  # Fallback

def safe_react(bot, chat_id, message_id, emoji):
    """Safely add reaction with error handling"""
    try:
        bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[ReactionTypeEmoji(emoji)]
        )
        return True
    except Exception:
        return False

class TelegramBot:
    """Telegram bot wrapper for Kivy app"""
    
    def __init__(self, token, chat_id, api_port=5001):
        self.token = token
        self.chat_id = int(chat_id)
        self.api_port = api_port
        self.bot = None
        self.is_running = False
        self.local_ip = get_local_ip()
        self.api_url = f"http://{self.local_ip}:{self.api_port}/send_command"
    
    def start(self):
        """Start the bot"""
        try:
            self.bot = telebot.TeleBot(self.token)
            self._register_handlers()
            self.is_running = True
            self.bot.infinity_polling(none_stop=True, interval=0)
        except Exception as e:
            raise Exception(f"Failed to start bot: {str(e)}")
    
    def stop(self):
        """Stop the bot"""
        self.is_running = False
        # Note: telebot doesn't have a clean stop method
        # The polling will stop when is_running is False
    
    def _register_handlers(self):
        """Register bot message handlers"""
        
        @self.bot.message_handler(commands=['cf', 'confirm'])
        def confirm_invoice(message: Message):
            """Handle confirm command"""
            command_parts = message.text.split()
            if len(command_parts) < 4:
                self.bot.reply_to(message, "Usage: /cf <id> <name> <time>")
                return
            
            invoice_id = command_parts[1]
            invoice_name = command_parts[2]
            invoice_time = command_parts[3]
            
            payload = {"text": f"CONFIRM {invoice_id} {invoice_name} {invoice_time}"}
            
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"❌ Error: {response.text}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands=['send'])
        def resend_photo(message: Message):
            """Handle send command"""
            payload = {"text": "SEND"}
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"❌ Error: {response.text}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands=['setup_bot'])
        def setup_bot(message: Message):
            """Handle setup_bot command"""
            payload = {"text": "SETUP_BOT"}
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"❌ Error: {response.text}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands=['start'])
        def start(message: Message):
            """Handle start command"""
            welcome_msg = """🤖 **LTR Converter Bot**

**Available Commands:**
• `/start` - Show this help message
• `/cf <id> <name> <time>` - Confirm invoice
• `/send` - Send resend command to Android
• `/setup_bot` - Send setup_bot command to Android

**Examples:**
• `/cf 19 chan 7:30` - Confirm invoice
• `/cf 1 nich vn` - Confirm with VN time

Send me multi-line text to parse or a photo to forward! 📸"""
            
            self.bot.reply_to(message, welcome_msg, parse_mode='Markdown')
        
        @self.bot.message_handler(content_types=['photo'])
        def handle_photo(message: Message):
            """Handle photo messages"""
            if message.photo:
                photo = message.photo[-1]
                file_id = photo.file_id
                
                try:
                    self.bot.send_photo(chat_id=self.chat_id, photo=file_id)
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                except Exception as e:
                    self.bot.reply_to(message, f"Sorry, I couldn't forward the photo. Error: {e}")
        
        @self.bot.message_handler(commands=['add'])
        def handle_add(message: Message):
            """Handle add command"""
            if not message.text:
                return
            
            lines = message.text.splitlines()
            if not lines:
                return
            
            header_parts = lines[0].split()
            if len(header_parts) < 4:
                self.bot.reply_to(message, "Usage: /add <id> <name> <time>\\nText")
                return
            
            payload = {"text": message.text.strip()}
            
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"❌ Error: {response.text}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(content_types=['text'])
        def handle_text(message: Message):
            """Handle text messages"""
            if message.text and message.text.startswith('/'):
                return
            
            if not message.text:
                return
            
            user_input_text = message.text.strip()
            payload = {"text": user_input_text}
            
            try:
                response = requests.post(self.api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    safe_react(self.bot, message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"Error sending command to API. Status: {response.status_code}")
            except Exception as e:
                self.bot.reply_to(message, f"An unexpected error occurred: {e}")
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"http://{self.local_ip}:{self.api_port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
