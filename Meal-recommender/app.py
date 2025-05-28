from Backend.Recommender.MealPredictionService import MealPredictionService
from Backend.Scrapers.MercadonaScraper import MercadonaScraper

def main():
    service = MealPredictionService(limit=1000)
    mercadona_scraper = MercadonaScraper()
    print("Loading...")
    service.prepare_model(limit=1000)
    print("Loaded successfully!")
    print("Meal Recommender App - Type '--quit' or '--exit' to stop, and '--help' for options/commands.")

    while True:
        try:
            user_input = input("meal-app> ").strip()

            if not user_input:
                continue

            if user_input.startswith('--q') or user_input.startswith('--quit') or user_input.startswith('--e') or user_input.startswith('--exit'):
                print("Exiting the Meal Recommender App. Goodbye!")
                break

            if user_input.startswith("--help") or user_input.startswith('--h'):
                print("Available commands:")
                print("1. --s <search_term> / --search <search_term> - Search for meals by ingredient or category.")
                print("2. --quit / --q or --exit / --e - Exit the application.")
                print("3. --help / --h - Show this help message.")
                print("4. --scrape - Scrape the latest mercadona price data.")
                continue

            if user_input.startswith('--s ') or user_input.startswith('--search '):
                search_term = user_input.split(maxsplit=1)[1]
                print_meal_from_search_term(search_term, service)
                continue

            if user_input.startswith('--scrape'):
                print("Starting scraping process...")
                mercadona_scraper.run()
                print("Scraping completed successfully!")
                continue
            
            print("Invalid command. Type 'help' for available commands.")
        except IndexError:
            print("Please provide a search term after the command.")
            continue
        except KeyboardInterrupt:
            print("\nExiting the Meal Recommender App. Goodbye!")
            break
            

def print_meal_from_search_term(search_term: str, service: MealPredictionService) -> list:
    meals = service.get_enriched_meals(search_term)
    
    if not meals:
        print(f"No meals found for search term: {search_term}")
        return []
    
    for meal in meals:
        print(f"Meal: {meal.name}")
        print(f"Preparation Time: {meal.prep_time} minutes")
        print(f"Ingredients: {[ingredient.name for ingredient in meal.ingredients]}")
        print(f"Instructions: {meal.instructions}")
        print("-" * 40)

if __name__ == "__main__":
    main()
