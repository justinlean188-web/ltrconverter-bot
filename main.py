import os
import json
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.logger import Logger
import requests
import socket
import subprocess
import platform
from telegram import Update
import telebot
from telebot.types import ReactionTypeEmoji, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import our modules
from api import app as flask_app, command_queue, INCOMPLETE_BETS_LIST
import perser

class ConfigManager:
    """Manages app configuration storage"""
    
    def __init__(self):
        self.config_file = "bot_config.json"
        self.default_config = {
            "bot_token": "8083952920:AAFQD3RGAW_OdM2pZscy5NeReqUq-GytXrI",
            "chat_id": "-4938742244",
            "api_port": "5001",
            "auto_start": False
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            Logger.error(f"Error loading config: {e}")
        return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            Logger.error(f"Error saving config: {e}")
            return False

class BotManager:
    """Manages the Telegram bot and Flask API"""
    
    def __init__(self):
        self.bot = None
        self.flask_thread = None
        self.bot_thread = None
        self.is_running = False
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
    
    def start_services(self, config):
        """Start both Flask API and Telegram bot"""
        try:
            self.config = config
            self.config_manager.save_config(config)
            
            # Start Flask API in background thread
            self.flask_thread = threading.Thread(target=self._start_flask, daemon=True)
            self.flask_thread.start()
            
            # Wait a moment for Flask to start
            time.sleep(2)
            
            # Start Telegram bot in background thread
            self.bot_thread = threading.Thread(target=self._start_bot, daemon=True)
            self.bot_thread.start()
            
            self.is_running = True
            return True, "Services started successfully"
            
        except Exception as e:
            Logger.error(f"Error starting services: {e}")
            return False, f"Error: {str(e)}"
    
    def stop_services(self):
        """Stop all services"""
        try:
            self.is_running = False
            if self.bot:
                # Stop the bot (this might need adjustment based on telebot version)
                pass
            return True, "Services stopped"
        except Exception as e:
            Logger.error(f"Error stopping services: {e}")
            return False, f"Error: {str(e)}"
    
    def _start_flask(self):
        """Start Flask API server"""
        try:
            # Update the global variables in api.py
            import api
            api.BOT_TOKEN = self.config["bot_token"]
            api.CHAT_ID = int(self.config["chat_id"])
            
            # Start Flask app
            flask_app.run(host='0.0.0.0', port=int(self.config["api_port"]), debug=False, use_reloader=False)
        except Exception as e:
            Logger.error(f"Flask error: {e}")
    
    def _start_bot(self):
        """Start Telegram bot"""
        try:
            # Update perser.py configuration
            perser.TOKEN = self.config["bot_token"]
            perser.TARGET_GROUP_ID = int(self.config["chat_id"])
            
            # Create bot instance
            self.bot = telebot.TeleBot(self.config["bot_token"])
            
            # Register handlers
            self._register_handlers()
            
            # Start polling
            self.bot.infinity_polling(none_stop=True, interval=0)
            
        except Exception as e:
            Logger.error(f"Bot error: {e}")
    
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
                api_url = f"http://localhost:{self.config['api_port']}/send_command"
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    self._safe_react(message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"❌ Error: {response.text}")
            except Exception as e:
                self.bot.reply_to(message, f"Error: {e}")
        
        @self.bot.message_handler(commands=['send'])
        def resend_photo(message: Message):
            """Handle send command"""
            payload = {"text": "SEND"}
            try:
                api_url = f"http://localhost:{self.config['api_port']}/send_command"
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    self._safe_react(message.chat.id, message.message_id, "👌")
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
                    self.bot.send_photo(chat_id=int(self.config["chat_id"]), photo=file_id)
                    self._safe_react(message.chat.id, message.message_id, "👌")
                except Exception as e:
                    self.bot.reply_to(message, f"Sorry, I couldn't forward the photo. Error: {e}")
        
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
                api_url = f"http://localhost:{self.config['api_port']}/send_command"
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code == 200:
                    self._safe_react(message.chat.id, message.message_id, "👌")
                else:
                    self.bot.reply_to(message, f"Error sending command to API. Status: {response.status_code}")
            except Exception as e:
                self.bot.reply_to(message, f"An unexpected error occurred: {e}")
    
    def _safe_react(self, chat_id, message_id, emoji):
        """Safely add reaction with error handling"""
        try:
            self.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=message_id,
                reaction=[ReactionTypeEmoji(emoji)]
            )
            return True
        except Exception as e:
            Logger.error(f"Failed to set reaction: {e}")
            return False

class BotConfigScreen(BoxLayout):
    """Main configuration screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        self.bot_manager = BotManager()
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Title
        title = Label(
            text='🤖 LTR Converter Bot',
            size_hint_y=None,
            height=50,
            font_size=24,
            bold=True
        )
        self.add_widget(title)
        
        # Scrollable content
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Bot Token
        content.add_widget(Label(text='Bot Token:', size_hint_y=None, height=30))
        self.bot_token_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='Enter your Telegram bot token'
        )
        content.add_widget(self.bot_token_input)
        
        # Chat ID
        content.add_widget(Label(text='Chat/Group ID:', size_hint_y=None, height=30))
        self.chat_id_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='Enter target chat/group ID (with - for groups)'
        )
        content.add_widget(self.chat_id_input)
        
        # API Port
        content.add_widget(Label(text='API Port:', size_hint_y=None, height=30))
        self.api_port_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=40,
            hint_text='API port (default: 5001)',
            text='5001'
        )
        content.add_widget(self.api_port_input)
        
        # Auto Start Switch
        auto_start_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        auto_start_layout.add_widget(Label(text='Auto Start on App Launch:', size_hint_x=0.7))
        self.auto_start_switch = Switch(size_hint_x=0.3)
        auto_start_layout.add_widget(self.auto_start_switch)
        content.add_widget(auto_start_layout)
        
        # Status
        content.add_widget(Label(text='Status:', size_hint_y=None, height=30))
        self.status_label = Label(
            text='Stopped',
            size_hint_y=None,
            height=40,
            color=(1, 0, 0, 1)  # Red color
        )
        content.add_widget(self.status_label)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        
        self.start_button = Button(text='Start Bot', size_hint_x=0.5)
        self.start_button.bind(on_press=self.start_bot)
        button_layout.add_widget(self.start_button)
        
        self.stop_button = Button(text='Stop Bot', size_hint_x=0.5)
        self.stop_button.bind(on_press=self.stop_bot)
        button_layout.add_widget(self.stop_button)
        
        content.add_widget(button_layout)
        
        # Test Connection Button
        test_button = Button(
            text='Test API Connection',
            size_hint_y=None,
            height=40
        )
        test_button.bind(on_press=self.test_connection)
        content.add_widget(test_button)
        
        # Logs
        content.add_widget(Label(text='Logs:', size_hint_y=None, height=30))
        self.log_text = TextInput(
            multiline=True,
            readonly=True,
            size_hint_y=None,
            height=200,
            hint_text='Bot logs will appear here...'
        )
        content.add_widget(self.log_text)
        
        scroll.add_widget(content)
        self.add_widget(scroll)
        
        # Update status periodically
        Clock.schedule_interval(self.update_status, 1)
    
    def load_current_config(self):
        """Load current configuration into UI"""
        config = self.bot_manager.config
        self.bot_token_input.text = config.get('bot_token', '')
        self.chat_id_input.text = config.get('chat_id', '')
        self.api_port_input.text = config.get('api_port', '5001')
        self.auto_start_switch.active = config.get('auto_start', False)
    
    def start_bot(self, instance):
        """Start the bot with current configuration"""
        try:
            # Validate inputs
            if not self.bot_token_input.text.strip():
                self.show_popup("Error", "Please enter a bot token")
                return
            
            if not self.chat_id_input.text.strip():
                self.show_popup("Error", "Please enter a chat/group ID")
                return
            
            try:
                int(self.chat_id_input.text)
            except ValueError:
                self.show_popup("Error", "Chat ID must be a number")
                return
            
            try:
                port = int(self.api_port_input.text)
                if port < 1024 or port > 65535:
                    raise ValueError()
            except ValueError:
                self.show_popup("Error", "API port must be a number between 1024-65535")
                return
            
            # Create config
            config = {
                'bot_token': self.bot_token_input.text.strip(),
                'chat_id': self.chat_id_input.text.strip(),
                'api_port': self.api_port_input.text.strip(),
                'auto_start': self.auto_start_switch.active
            }
            
            # Start services
            success, message = self.bot_manager.start_services(config)
            
            if success:
                self.log_message("✅ " + message)
                self.start_button.disabled = True
                self.stop_button.disabled = False
            else:
                self.log_message("❌ " + message)
                self.show_popup("Error", message)
                
        except Exception as e:
            error_msg = f"Error starting bot: {str(e)}"
            self.log_message("❌ " + error_msg)
            self.show_popup("Error", error_msg)
    
    def stop_bot(self, instance):
        """Stop the bot"""
        try:
            success, message = self.bot_manager.stop_services()
            
            if success:
                self.log_message("🛑 " + message)
                self.start_button.disabled = False
                self.stop_button.disabled = True
            else:
                self.log_message("❌ " + message)
                self.show_popup("Error", message)
                
        except Exception as e:
            error_msg = f"Error stopping bot: {str(e)}"
            self.log_message("❌ " + error_msg)
            self.show_popup("Error", error_msg)
    
    def test_connection(self, instance):
        """Test API connection"""
        try:
            port = self.api_port_input.text.strip()
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            
            if response.status_code == 200:
                self.log_message("✅ API connection successful")
                self.show_popup("Success", "API connection successful!")
            else:
                self.log_message(f"❌ API returned status: {response.status_code}")
                self.show_popup("Error", f"API returned status: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            self.log_message("❌ Cannot connect to API")
            self.show_popup("Error", "Cannot connect to API. Make sure the bot is running.")
        except Exception as e:
            error_msg = f"Connection test failed: {str(e)}"
            self.log_message("❌ " + error_msg)
            self.show_popup("Error", error_msg)
    
    def update_status(self, dt):
        """Update status display"""
        if self.bot_manager.is_running:
            self.status_label.text = "Running"
            self.status_label.color = (0, 1, 0, 1)  # Green
        else:
            self.status_label.text = "Stopped"
            self.status_label.color = (1, 0, 0, 1)  # Red
    
    def log_message(self, message):
        """Add message to log display"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.text += log_entry
        # Auto-scroll to bottom
        self.log_text.cursor = (len(self.log_text.text), 0)
    
    def show_popup(self, title, message):
        """Show popup message"""
        popup = Popup(
            title=title,
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

class LTRConverterApp(App):
    """Main Kivy application"""
    
    def build(self):
        """Build the app"""
        self.title = 'LTR Converter Bot'
        return BotConfigScreen()

if __name__ == '__main__':
    LTRConverterApp().run()
