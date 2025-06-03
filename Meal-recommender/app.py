from Backend.Services.meal_prediction_service import MealPredictionService
from Backend.Services.meal_training_service import MealTrainingService
from Backend.Services.user_service import UserService
from Backend.Scrapers.mercadona_scraper import MercadonaScraper

def main():
    prediction_service = MealPredictionService()
    mercadona_scraper = MercadonaScraper()
    training_service = MealTrainingService()
    user_service = UserService()
    print("Loading...")
    print("Loaded successfully!")

    if not user_service.has_cli_device_id():
        user = user_service.get_or_create_cli_user()
        print(f"Welcome! Your user ID is {user.id}.")
        print("Please set your meal preferences to get personalized recommendations.")
        print("You can change these preferences later using the '-preferences' command.")
        preferences = get_user_preferences()
        user_service.update_user_preferences(
            user.id,
            prefered_flavors=preferences.get('flavors', []),
            prefered_types=[preferences.get('cuisine', '')],
            dietary_restrictions=preferences.get('diet', [])
        )
    else:
        user = user_service.get_or_create_cli_user()
        print(f"Welcome back! Your user ID is {user.id}.")
        
    print("Meal Recommender App - Type '--quit' or '--exit' to stop, and '--help' for options/commands.")

    while True:
        try:
            user_input = input("meal-app> ").strip()

            if not user_input:
                continue

            if user_input.startswith('-q') or user_input.startswith('-quit') or user_input.startswith('-e') or user_input.startswith('-exit'):
                print("Exiting the Meal Recommender App. Goodbye!")
                break

            if user_input.startswith("--help") or user_input.startswith('--h'):
                print_help()
                continue

            if user_input.startswith('-s ') or user_input.startswith('-search '):
                search_term = user_input.split(maxsplit=1)[1]
                print_meal_from_search_term(search_term, prediction_service, user_service)
                continue

            if user_input.startswith('-scrape'):
                print("Starting scraping process...")
                mercadona_scraper.run()
                print("Scraping completed successfully!")
                continue
            
            if user_input.startswith('-retrain'):
                train_models(user_input, training_service)
                continue
            
            print("Invalid command. Type 'help' for available commands.")
        except IndexError:
            print("Please provide a search term after the command.")
            continue
        except KeyboardInterrupt:
            print("\nExiting the Meal Recommender App. Goodbye!")
            break
            

def print_meal_from_search_term(search_term: str, service: MealPredictionService, user_service: UserService) -> list:
    meals = service.get_enriched_meal_user_preferences(search_term, user_service.get_or_create_cli_user())
    
    if not meals:
        print(f"No meals found for search term: {search_term}")
        return []
    
    count = 0
    for meal in meals:
        count += 1
        if count > 5:
            break
        print(f"Meal: {meal.name}")
        print(f"Personalized Score: {meal.recommendation_score}")
        print(f"Preparation Time: {meal.prep_time} minutes")
        print(f"Estimated Cost: {meal.estimated_cost} EUR")
        print(f"Ingredients: {[ingredient.name for ingredient in meal.ingredients]}")
        print(f"Instructions: {meal.instructions}")
        print("-" * 40)
        print("\n")

def print_help():
    print("Available commands:")
    print("1. -s <search_term> / -search <search_term> - Search for meals by ingredient or category.")
    print("2. -quit / -q or -exit / -e - Exit the application.")
    print("3. -help / -h - Show this help message.")
    print("4. -scrape - Scrape the latest mercadona price data.")
    print("5. -retrain <model> <limit> - Retrain the model with a specified limit. (model names: prep_time, recommendation)")

def train_models(user_input: str, training_service: MealTrainingService) -> bool:
    parts = user_input.split()
    if len(parts) < 3:
        print("Usage: -retrain <model> <limit>")
        return
    
    model_name = parts[1]
    try:
        limit = int(parts[2])
        if model_name == "prep_time":
            training_service.train_prep_time_model(limit)
            print(f"Retrained {model_name} model with limit {limit}.")
        elif model_name == "recommendation":
            training_service.train_recommendation_model(limit)
            print(f"Retrained {model_name} model with limit {limit}.")
        else:
            print(f"Model '{model_name}' not recognized.")
    except ValueError:
        print("Limit must be a valid integer.")

def get_user_preferences():
    """Get user preferences for meal recommendations."""
    preferences = {}
    preferences['cuisine'] = input("Preferred cuisine (e.g., Italian, Mexican): ").strip()
    preferences['diet'] = input("Dietary restrictions (e.g., vegetarian, dairy) (comma-seperated): ").strip().split(',')
    preferences['flavors'] = input("Preferred flavors (e.g., spicy, sweet) (comma-seperated): ").strip().split(',')
    return preferences

if __name__ == "__main__":
    main()