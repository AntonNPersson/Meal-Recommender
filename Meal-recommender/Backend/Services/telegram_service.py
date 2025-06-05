from enum import Enum
from ..Services.meal_prediction_service import MealPredictionService
from ..Services.user_service import UserService
from ..Api.telegram_bot import TelegramBot
from typing import Dict, Any
from ..models.user import User

class SurveyState(Enum):
    """Survey states for new users."""
    MEAL_TYPE = "type_of_meal"
    DIETARY_RESTRICTIONS = "dietary_restrictions"
    FLAVOR_PROFILE = "flavor_profile"
    COMPLETED = "completed"

class TelegramBotService:
    """Telegram bot for meal recommendations based on user preferences."""

    def __init__(self, token: str):
        """Initialize the bot with the provided token."""
        self.token = token
        self.bot = TelegramBot(token)
        self.user_service = UserService()
        self.meal_prediction_service = MealPredictionService()

        self.user_states = {}
        self.user_survey_data = {}

        self._setup_handlers()

    def _setup_handlers(self):
        """Setup message and callback query handlers."""

        self.bot.add_command_handler('start', self._handle_start_command)
        self.bot.add_command_handler('help', self._handle_help_command)
        self.bot.add_command_handler('search', self._handle_search_command)
        self.bot.add_command_handler('preferences', self._handle_preferences_command)

        self.bot.add_message_handler(self._handle_message)
        self.bot.add_callback_query_handler(self._handle_callback_query)

    def _handle_start_command(self, message: Dict[str, Any]):
        """Handle /start command - register new user or greet existing user."""

        user_id = message['from']['id']
        chat_id = message['chat']['id']
        first_name = message['from'].get('first_name', 'User')

        print(f"🤖 New user started the bot: {first_name} (ID: {user_id})")

        existing_user = self.user_service.user_exists(user_id)

        if existing_user:
            # Welcome back existing user
            self.bot.api.send_message(
                chat_id=chat_id,
                text=f"Welcome back, {first_name}! 🍽️\n\n"
                     f"I'm ready to help you find delicious meals.\n"
                     f"Use /help to see available commands.",
                reply_markup=self._create_main_menu_keyboard()
            )
        else:
            # New user - start survey
            self.user_service.get_or_create_user(user_id)
            self._start_user_survey(user_id, chat_id, first_name)

    def _start_user_survey(self, user_id: int, chat_id: int, first_name: str):
        """Start the user preference survey."""
        self.user_states[user_id] = SurveyState.MEAL_TYPE
        self.user_survey_data[user_id] = {
            'chat_id': chat_id,
            'first_name': first_name,
            'type_of_meals': [],
            'dietary_restrictions': [],
            'flavor_profiles': []
        }
        
        welcome_text = (
            f"Welcome to Meal Recommender Bot, {first_name}! 🍽️\n\n"
            f"I'll help you discover amazing meals based on your preferences.\n"
            f"Let's start with a quick survey to personalize your experience.\n\n"
            f"<b>Question 1/3:</b> What types of meals do you enjoy?\n"
            f"(You can select multiple options)"
        )
        
        keyboard = self._create_meal_type_keyboard()
        
        self.bot.api.send_message(
            chat_id=chat_id,
            text=welcome_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )

    def _create_meal_type_keyboard(self):
        """Create inline keyboard for meal type selection."""
        meal_types = [
            [{"text": "🍕 Italian", "callback_data": "type_of_meal:italian"}],
            [{"text": "🍜 Asian", "callback_data": "type_of_meal:asian"}],
            [{"text": "🌮 Mexican", "callback_data": "type_of_meal:mexican"}],
            [{"text": "🍔 American", "callback_data": "type_of_meal:american"}],
            [{"text": "🥗 Mediterranean", "callback_data": "type_of_meal:mediterranean"}],
            [{"text": "🍛 Indian", "callback_data": "type_of_meal:indian"}],
            [{"text": "✅ Done with meal types", "callback_data": "type_of_meal:done"}]
        ]
        return self.bot.api.create_inline_keyboard(meal_types)
    
    def _create_dietary_keyboard(self):
        """Create inline keyboard for dietary restrictions."""
        dietary_options = [
            [{"text": "🌱 Vegetarian", "callback_data": "dietary:vegetarian"}],
            [{"text": "🥬 Vegan", "callback_data": "dietary:vegan"}],
            [{"text": "🚫 Gluten-Free", "callback_data": "dietary:gluten_free"}],
            [{"text": "🥛 Dairy-Free", "callback_data": "dietary:dairy_free"}],
            [{"text": "🥩 Keto", "callback_data": "dietary:keto"}],
            [{"text": "🍖 Paleo", "callback_data": "dietary:paleo"}],
            [{"text": "❌ No restrictions", "callback_data": "dietary:none"}],
            [{"text": "✅ Done with dietary", "callback_data": "dietary:done"}]
        ]
        return self.bot.api.create_inline_keyboard(dietary_options)
    
    def _create_flavor_profile_keyboard(self):
        """Create inline keyboard for flavor profiles."""
        flavor_options = [
            [{"text": "🌶️ Spicy", "callback_data": "flavor:spicy"}],
            [{"text": "🧂 Savory", "callback_data": "flavor:savory"}],
            [{"text": "🍯 Sweet", "callback_data": "flavor:sweet"}],
            [{"text": "🍋 Tangy", "callback_data": "flavor:tangy"}],
            [{"text": "🧄 Mild", "callback_data": "flavor:mild"}],
            [{"text": "🌿 Fresh", "callback_data": "flavor:fresh"}],
            [{"text": "✅ Done with flavors", "callback_data": "flavor:done"}]
        ]
        return self.bot.api.create_inline_keyboard(flavor_options)
    
    def _create_main_menu_keyboard(self):
        """Create main menu keyboard for registered users."""
        menu_buttons = [
            [{"text": "🔍 Search Meals", "callback_data": "menu:search"}],
            [{"text": "🎲 Random Meal", "callback_data": "menu:random"}],
            [{"text": "⚙️ My Preferences", "callback_data": "menu:preferences"}],
            [{"text": "❓ Help", "callback_data": "menu:help"}]
        ]
        return self.bot.api.create_inline_keyboard(menu_buttons)
    
    def _handle_callback_query(self, callback_query: Dict[str, Any]):
        """Handle inline keyboard button presses."""
        user_id = callback_query['from']['id']
        chat_id = callback_query['message']['chat']['id']
        data = callback_query['data']
        
        print(f"Callback from user {user_id}: {data}")
        
        # Handle survey callbacks
        if user_id in self.user_states:
            self._handle_survey_callback(user_id, chat_id, data, callback_query['id'])
        # Handle menu callbacks
        elif data.startswith('menu:'):
            self._handle_menu_callback(user_id, chat_id, data, callback_query['id'])
        
        # Always answer the callback query
        self.bot.api.answer_callback_query(callback_query['id'])

    def _handle_survey_callback(self, user_id: int, chat_id: int, data: str, callback_query_id: str):
        """Handle survey-related callback queries."""
        current_state = self.user_states[user_id]
        survey_data = self.user_survey_data[user_id]
        
        if current_state == SurveyState.MEAL_TYPE:
            if data.startswith('type_of_meal:'):
                meal_type = data.split(':')[1]
                if meal_type == 'done':
                    # Move to dietary restrictions
                    self._advance_to_dietary_survey(user_id, chat_id)
                else:
                    # Add meal type to selections
                    if meal_type not in survey_data['type_of_meals']:
                        survey_data['type_of_meals'].append(meal_type)
                        self.bot.api.answer_callback_query(
                            callback_query_id,
                            text=f"Added {meal_type.title()}! ✅"
                        )
        
        elif current_state == SurveyState.DIETARY_RESTRICTIONS:
            if data.startswith('dietary:'):
                dietary = data.split(':')[1]
                if dietary == 'done':
                    # Move to flavor profiles
                    self._advance_to_flavor_survey(user_id, chat_id)
                elif dietary == 'none':
                    # No dietary restrictions
                    survey_data['dietary_restrictions'] = []
                    self._advance_to_flavor_survey(user_id, chat_id)
                else:
                    # Add dietary restriction
                    if dietary not in survey_data['dietary_restrictions']:
                        survey_data['dietary_restrictions'].append(dietary)
                        self.bot.api.answer_callback_query(
                            callback_query_id,
                            text=f"Added {dietary.replace('_', ' ').title()}! ✅"
                        )
        
        elif current_state == SurveyState.FLAVOR_PROFILE:
            if data.startswith('flavor:'):
                flavor = data.split(':')[1]
                if flavor == 'done':
                    # Complete survey
                    self._complete_user_survey(user_id, chat_id)
                else:
                    # Add flavor profile
                    if flavor not in survey_data['flavor_profiles']:
                        survey_data['flavor_profiles'].append(flavor)
                        self.bot.api.answer_callback_query(
                            callback_query_id,
                            text=f"Added {flavor.title()}! ✅"
                        )

    def _advance_to_dietary_survey(self, user_id: int, chat_id: int):
        """Move to dietary restrictions question."""
        self.user_states[user_id] = SurveyState.DIETARY_RESTRICTIONS
        
        selected_types = self.user_survey_data[user_id]['type_of_meals']
        types_text = ", ".join([t.title() for t in selected_types]) if selected_types else "None selected"
        
        text = (
            f"Great! You selected: {types_text}\n\n"
            f"<b>Question 2/3:</b> Do you have any dietary restrictions?\n"
            f"(Select all that apply)"
        )
        
        self.bot.api.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=self._create_dietary_keyboard()
        )

    def _advance_to_flavor_survey(self, user_id: int, chat_id: int):
        """Move to flavor profiles question."""
        self.user_states[user_id] = SurveyState.FLAVOR_PROFILE
        
        selected_dietary = self.user_survey_data[user_id]['dietary_restrictions']
        dietary_text = ", ".join([d.replace('_', ' ').title() for d in selected_dietary]) if selected_dietary else "None"
        
        text = (
            f"Perfect! Dietary restrictions: {dietary_text}\n\n"
            f"<b>Question 3/3:</b> What flavor profiles do you enjoy?\n"
            f"(Select all that apply)"
        )
        
        self.bot.api.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="HTML",
            reply_markup=self._create_flavor_profile_keyboard()
        )
    
    def _complete_user_survey(self, user_id: int, chat_id: int):
        """Complete the user survey and save to database."""
        survey_data = self.user_survey_data[user_id]
        
        # Create user in database
        try:
            # Create user with survey data
            user = self.user_service.update_user_preferences(
                user_id=user_id,
                prefered_types=survey_data['type_of_meals'],
                dietary_restrictions=survey_data['dietary_restrictions'],
                prefered_flavors=survey_data['flavor_profiles']
            )
            
            # Clean up survey state
            del self.user_states[user_id]
            del self.user_survey_data[user_id]
            
            # Send completion message
            summary_text = self._format_preferences_summary(survey_data)
            
            completion_text = (
                f"🎉 Survey completed! Welcome to Meal Recommender Bot!\n\n"
                f"<b>Your Preferences:</b>\n{summary_text}\n\n"
                f"I'm now ready to recommend personalized meals for you!\n"
                f"Use the menu below or type /help for commands."
            )
            
            self.bot.api.send_message(
                chat_id=chat_id,
                text=completion_text,
                parse_mode="HTML",
                reply_markup=self._create_main_menu_keyboard()
            )
            
            print(f"User {user_id} survey completed and saved to database")
            
        except Exception as e:
            print(f"Error saving user {user_id}: {e}")
            self.bot.api.send_message(
                chat_id=chat_id,
                text="❌ Sorry, there was an error saving your preferences. Please try /start again."
            )

    def _format_preferences_summary(self, survey_data: Dict) -> str:
        """Format user preferences for display."""
        meal_types = ", ".join([t.title() for t in survey_data['type_of_meals']]) or "Any"
        dietary = ", ".join([d.replace('_', ' ').title() for d in survey_data['dietary_restrictions']]) or "None"
        flavors = ", ".join([f.title() for f in survey_data['flavor_profiles']]) or "Any"
        
        return (
            f"🍽️ Meal Types: {meal_types}\n"
            f"🥗 Dietary: {dietary}\n"
            f"👅 Flavors: {flavors}"
        )
    
    def _handle_menu_callback(self, user_id: int, chat_id: int, data: str, callback_query_id: str):
        """Handle main menu callbacks."""
        action = data.split(':')[1]
        
        if action == 'search':
            self.bot.api.send_message(
                chat_id=chat_id,
                text="🔍 What ingredient or meal would you like to search for?\n\nJust type your search term (e.g., 'chicken', 'pasta', 'vegetarian'):",
                parse_mode="HTML"
            )
        elif action == 'random':
            self._send_random_meal(user_id, chat_id)
        elif action == 'preferences':
            self._show_user_preferences(user_id, chat_id)
        elif action == 'help':
            self._send_help_message(chat_id)

    def _handle_message(self, message: Dict[str, Any]):
        """Handle regular text messages."""
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        first_name = message['from'].get('first_name', 'User')
        
        # Skip if user is in survey
        if user_id in self.user_states:
            return
        
        # Skip commands (handled separately)
        if text.startswith('/'):
            return
        
        # Check if user exists - if not, auto-register them
        user = self.user_service.user_exists(user_id)
        user_object = self.user_service.get_or_create_user(user_id)
        if not user:
            print(f"New user {user_id} detected, starting auto-registration")
            self._start_user_survey(user_id, chat_id, first_name)
            return
        
        # Treat any message as a search query
        if text.strip():
            self._search_meals(user_object, chat_id, text.strip())

    def _handle_help_command(self, message: Dict[str, Any]):
        """Handle /help command."""
        chat_id = message['chat']['id']
        self._send_help_message(chat_id)

    def _send_help_message(self, chat_id: int):
        """Send help message with available commands."""
        help_text = (
            "🤖 <b>Meal Recommender Bot - Help</b>\n\n"
            "<b>Commands:</b>\n"
            "• /start - Register or restart the bot\n"
            "• /search [term] - Search for meals (e.g., /search chicken)\n"
            "• /random - Get a random meal recommendation\n"
            "• /preferences - View your current preferences\n"
            "• /help - Show this help message\n\n"
            "<b>Quick Actions:</b>\n"
            "• Just type any ingredient or meal name to search\n"
            "• Use the menu buttons for easy navigation\n\n"
            "🍽️ I'll recommend meals based on your preferences!"
        )
        
        self.bot.api.send_message(
            chat_id=chat_id,
            text=help_text,
            parse_mode="HTML",
            reply_markup=self._create_main_menu_keyboard()
        )

    def _send_random_meal(self, user_id: int, chat_id: int):
        """Send a random meal recommendation based on user preferences."""
        try:
            user = self.user_service.get_or_create_user(user_id)
            if not user:
                self.bot.api.send_message(
                    chat_id=chat_id,
                    text="Please start with /start to register first! 😊"
                )
                return
            
            # Get a random meal based on user preferences
            meal = self.meal_prediction_service.get_random_enriched_meals_user_preferences(5, user)[0] # Get highest recommended random meal
            
            if not meal:
                self.bot.api.send_message(
                    chat_id=chat_id,
                    text="😔 No meals found based on your preferences. Try updating your preferences!"
                )
                return
            
            # Format and send the meal details
            response_text = (
                f"🍽️ <b>Random Meal Recommendation:</b>\n\n"
                f"<b>{meal.name}</b>\n"
                f"⭐ Recommendation Score: {meal.recommendation_score or 0}/5.0\n"
                f"⏱️ Prep Time: {meal.prep_time or 'Unknown'} min\n"
                f"💰 Estimated Cost: ${meal.estimated_cost or 0:.2f}\n"
                f"📝 Category: {meal.category}\n"
                f"📋 Instructions: {meal.instructions}\n"
                f"🍽️ Ingredients: {', '.join([ingredient.name for ingredient in meal.ingredients])}\n\n"
                "Use the menu for more options! 👇"
            )
            
            self.bot.api.send_message(
                chat_id=chat_id,
                text=response_text,
                parse_mode="HTML",
                reply_markup=self._create_main_menu_keyboard()
            )
            
        except Exception as e:
            print(f"Error sending random meal: {e}")
            self.bot.api.send_message(
                chat_id=chat_id,
                text="❌ Sorry, there was an error getting a random meal. Please try again!"
            )

    def _handle_search_command(self, message: Dict[str, Any]):
        """Handle /search command."""
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        first_name = message['from'].get('first_name', 'User')
        
        # Check if user exists - if not, auto-register them
        user = self.user_service.user_exists(user_id)
        user_object = self.user_service.get_or_create_user(user_id)
        if not user:
            print(f"New user {user_id} detected during search, starting auto-registration")
            self._start_user_survey(user_id, chat_id, first_name)
            return
        
        # Extract search term
        parts = text.split(' ', 1)
        if len(parts) > 1:
            search_term = parts[1].strip()
            self._search_meals(user_object, chat_id, search_term)
        else:
            self.bot.api.send_message(
                chat_id=chat_id,
                text="Please provide a search term!\nExample: /search chicken"
            )

    def _handle_preferences_command(self, message: Dict[str, Any]):
        """Handle /preferences command."""
        user_id = message['from']['id']
        chat_id = message['chat']['id']
        self._show_user_preferences(user_id, chat_id)

    def _search_meals(self, user: User, chat_id: int, search_term: str):
        """Search for meals and send recommendations."""
        try:
            search_term.lower()
            self.bot.api.send_message(
                chat_id=chat_id,
                text=f"🔍 Searching for '{search_term}'..."
            )
            
            # Use your meal service to get recommendations
            meals = self.meal_prediction_service.get_enriched_meal_user_preferences(search_term, user)
            
            if not meals:
                self.bot.api.send_message(
                    chat_id=chat_id,
                    text=f"😔 No meals found for '{search_term}'. Try a different search term!"
                )
                return
            
            # Send top 3 recommendations
            response_text = f"🍽️ <b>Top recommendations for '{search_term}':</b>\n\n"
            
            for i, meal in enumerate(meals[:3], 1):
                score = meal.recommendation_score or 0
                prep_time = meal.prep_time or "Unknown"
                cost = meal.estimated_cost or 0
                
                response_text += (
                    f"<b>{i}. {meal.name}</b>\n"
                    f"⭐ Score: {score}/5.0\n"
                    f"⏱️ Prep: {prep_time} min\n"
                    f"💰 Cost: ${cost:.2f}\n"
                    f"📝 Category: {meal.category}\n"
                    f"📋 Instructions: {meal.instructions}\n"
                    f"🍽️ Ingredients: {', '.join([ingredient.name for ingredient in meal.ingredients])}\n\n"
                )
            
            response_text += "Use the menu for more options! 👇"
            
            self.bot.api.send_message(
                chat_id=chat_id,
                text=response_text,
                parse_mode="HTML",
                reply_markup=self._create_main_menu_keyboard()
            )
            
        except Exception as e:
            print(f"Error searching meals: {e}")
            self.bot.api.send_message(
                chat_id=chat_id,
                text="❌ Sorry, there was an error searching for meals. Please try again!"
            )

    def _show_user_preferences(self, user_id: int, chat_id: int):
        """Show user's current preferences."""
        try:
            user = self.user_service.get_or_create_user(user_id)
            if not user:
                self.bot.api.send_message(
                    chat_id=chat_id,
                    text="Please start with /start to register first! 😊"
                )
                return
            
            meal_types = ", ".join(user.prefered_types) if user.prefered_types else "Any"
            dietary = ", ".join(user.dietary_restrictions) if user.dietary_restrictions else "None"
            flavors = ", ".join(user.prefered_flavors) if user.prefered_flavors else "Any"
            
            preferences_text = (
                f"⚙️ <b>Your Current Preferences:</b>\n\n"
                f"🍽️ <b>Meal Types:</b> {meal_types}\n"
                f"🥗 <b>Dietary Restrictions:</b> {dietary}\n"
                f"👅 <b>Flavor Profiles:</b> {flavors}\n\n"
                f"To update your preferences, use /start to retake the survey!"
            )
            
            self.bot.api.send_message(
                chat_id=chat_id,
                text=preferences_text,
                parse_mode="HTML",
                reply_markup=self._create_main_menu_keyboard()
            )
            
        except Exception as e:
            print(f"Error showing preferences: {e}")
            self.bot.api.send_message(
                chat_id=chat_id,
                text="❌ Sorry, there was an error loading your preferences."
            )

    def start(self):
        """Start the bot."""
        print("🚀 Starting Meal Recommendation Bot...")
        self.bot.start_polling()

    def stop(self):
        """Stop the bot."""
        self.bot.stop()