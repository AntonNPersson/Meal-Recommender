from typing import List, Dict, Optional, Any
import requests
import json
import time

class TelegramBotAPI:
    """A class to interact with the Telegram Bot API.
    
    Token is required to authenticate the bot, get it from @BotFather on telegram."""

    def __init__(self, token: str, timeout: Optional[int] = None):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.session = requests.Session()
        self.timeout = timeout if timeout is not None else 30
        self._validate_token()  # Validate token on initialization


    def _validate_token(self):
        """Validate bot token by making a test request."""
        try:
            response = self.get_me()
            if response.get('ok'):
                bot_info = response.get('result', {})
                print(f"✅ Bot connected: @{bot_info.get('username')} ({bot_info.get('first_name')})")
            else:
                raise Exception(f"Invalid bot token: {response}")
        except Exception as e:
            raise Exception(f"Failed to connect to Telegram: {e}")

    def _make_request(self, method: str, data: Optional[Dict] = None, 
                     files: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a request to Telegram Bot API.
        
        Args:
            method: API method name
            data: Request data
            files: Files to upload
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}/{method}"
        
        try:
            if files:
                # For file uploads, don't set Content-Type header
                response = self.session.post(url, data=data, files=files, timeout=self.timeout)
            else:
                # For regular requests, use JSON
                headers = {'Content-Type': 'application/json'}
                response = self.session.post(url, data=json.dumps(data) if data else None, 
                                           headers=headers, timeout=self.timeout)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return {"ok": False, "error": str(e)}
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {"ok": False, "error": "Invalid JSON response"}

    # API Methods
    def get_me(self) -> Dict[str, Any]:
        """Get basic information about the bot."""
        response = self._make_request("getMe")
        return response
    
    def get_updates(self, offset: Optional[int] = None, 
                     limit: Optional[int] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Get updates for the bot."""
        data = {
            "offset": offset,
            "limit": limit,
            "timeout": timeout
        }
        response = self._make_request("getUpdates", data=data)
        return response
    
    # Messaging Methods
    def send_message(self, chat_id: int, text: str, parse_mode: Optional[str] = None, entities: Optional[List[Dict]] = None, disable_web_page_preview: bool = False,
                     disable_notification: bool = False, reply_to_message_id: Optional[int] = None, reply_markup: Optional[Dict] = None) -> Dict[str, Any]:
        """Send a text message to a chat."""
        data = {
            "chat_id": chat_id,
            "text": text,
        }

        if parse_mode:
            data["parse_mode"] = parse_mode

        if entities:
            data["entities"] = entities

        if disable_web_page_preview:
            data["disable_web_page_preview"] = disable_web_page_preview

        if disable_notification:
            data["disable_notification"] = disable_notification

        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        if reply_markup:
            data["reply_markup"] = reply_markup

        
        response = self._make_request("sendMessage", data=data)
        return response
    
    # Keyboard Methods
    def create_inline_keyboard(self, buttons: List[List[Dict[str, str]]]) -> Dict:
        """
        Create inline keyboard markup.
        
        Args:
            buttons: 2D array of button objects
                    Each button: {"text": "Button Text", "callback_data": "data"}
                    or {"text": "URL Button", "url": "https://example.com"}
        
        Example:
            buttons = [
                [{"text": "Option 1", "callback_data": "opt1"}],
                [{"text": "Option 2", "callback_data": "opt2"}],
                [{"text": "Visit Website", "url": "https://example.com"}]
            ]
        """
        return {"inline_keyboard": buttons}
    
    def create_reply_keyboard(self, buttons: List[List[str]], 
                             resize_keyboard: bool = True,
                             one_time_keyboard: bool = False,
                             selective: bool = False) -> Dict:
        """
        Create custom reply keyboard.
        
        Args:
            buttons: 2D array of button text
            resize_keyboard: Requests clients to resize keyboard
            one_time_keyboard: Hide keyboard after use
            selective: Show keyboard to specific users only
        
        Example:
            buttons = [
                ["🍕 Pizza", "🍔 Burger"],
                ["🍝 Pasta", "🥗 Salad"],
                ["❌ Cancel"]
            ]
        """
        keyboard = [[{"text": btn} for btn in row] for row in buttons]
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard,
            "selective": selective
        }

    def remove_keyboard(self) -> Dict:
        """Remove custom keyboard."""
        return {"remove_keyboard": True}

    # Callback Query Methods
    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None,
                             show_alert: bool = False, url: Optional[str] = None,
                             cache_time: int = 0) -> Dict[str, Any]:
        """Answer callback query from inline keyboard."""
        data = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
            "cache_time": cache_time
        }
        
        if text:
            data["text"] = text
        if url:
            data["url"] = url
            
        return self._make_request("answerCallbackQuery", data)
    
class TelegramBot:
    """A class to interact with the Telegram Bot API."""

    def __init__(self, token: str):
        self.api = TelegramBotAPI(token=token)
        self.handlers = {
            "message": [],
            "callback_query": [],
            "command": {}
        }

        self.running = False

    def add_message_handler(self, handler):
        """Add a message handler."""
        self.handlers["message"].append(handler)

    def add_callback_query_handler(self, handler):
        """Add a callback query handler."""
        self.handlers["callback_query"].append(handler)

    def add_command_handler(self, command: str, handler):
        """Add a command handler."""
        self.handlers['command'][command] = handler

    def start_polling(self, interval: int = 1):
        """Start polling for updates."""
        print("🤖 Bot started polling...")
        self.running = True
        offset = None
        
        while self.running:
            try:
                updates = self.api.get_updates(offset=offset, timeout=30)
                
                if updates.get('ok'):
                    for update in updates.get('result', []):
                        self._handle_update(update)
                        offset = update['update_id'] + 1
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n🛑 Bot stopped by user")
                self.running = False
            except Exception as e:
                print(f"❌ Error in polling: {e}")
                time.sleep(5)

    def stop(self):
        """Stop the bot."""
        self.running = False

    def _handle_update(self, update: Dict[str, Any]):
        """Handle incoming updates from Telegram."""
        try:
            # Handle messages (including commands)
            if 'message' in update:
                message = update['message']
                
                # Check for commands FIRST
                if 'text' in message and message['text'].startswith('/'):
                    command_text = message['text']
                    command = command_text.split()[0][1:]  # Remove '/'
                    
                    print(f"🔍 Command detected: '{command}'")
                    
                    if command in self.handlers['command']:
                        print(f"✅ Executing command: /{command}")
                        self.handlers['command'][command](message)
                        return  # Don't process as regular message
                
                # Handle regular messages
                for handler in self.handlers['message']:
                    handler(message)
            
            # Handle callback queries
            elif 'callback_query' in update:
                callback_query = update['callback_query']
                for handler in self.handlers['callback_query']:
                    handler(callback_query)
                
                # Answer callback query
                self.api.answer_callback_query(callback_query['id'])
                
        except Exception as e:
            print(f"❌ Error handling update: {e}")
            import traceback
            traceback.print_exc()

