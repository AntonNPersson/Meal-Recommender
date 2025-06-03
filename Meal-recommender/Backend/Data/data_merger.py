from Backend.Api.themealdb import MealDBAPI
from Backend.Data.csv_processor import MercadonaCSVProcessor, FoodCSVProcessor
from Backend.models.meal import Meal
from Backend.models.ingredient import Ingredient
from typing import List

class DataMerger:
    def __init__(self, mercadona_csv_file_path: str = None, food_csv_file_path: str = None, review_csv_file_path: str = None):
        self.mercadona_csv_file_path = mercadona_csv_file_path
        self.food_csv_file_path = food_csv_file_path
        self.review_csv_file_path = review_csv_file_path

        self.meal_api = MealDBAPI()
        self.price_processor = MercadonaCSVProcessor(mercadona_csv_file_path)

        self.is_training = False
        if food_csv_file_path:
            self.training_processor = FoodCSVProcessor(food_csv_file_path, review_csv_file_path)
            self.is_training = True
    
    def get_enriched_meals(self, search_term: str) -> List[Meal]:
        """Get meals from API and enrich with pricing data"""
        search_methods = [
            ('search_by_ingredient', self.meal_api.search_by_ingredient),
            ('search_by_category', self.meal_api.search_by_category),
            ('search_by_area', self.meal_api.search_by_area)
        ]

        api_meals = []
        for method_name, method in search_methods:
            try:
                meals = method(search_term)
                if meals:
                    api_meals.extend(meals)
            except Exception as e:
                print(f"Error in {method_name} for search term '{search_term}': {e}")
        
        enriched_meals = []
        for meal_data in api_meals:
            full_meal = self.meal_api.get_meal_details(meal_data['idMeal'])
            meal = self._convert_to_meal_model(full_meal)
            enriched_meals.append(meal)
        
        return enriched_meals
    
    def get_all_enriched_meals(self) -> List[Meal]:
        categories = ['Beef', 'Chicken', 'Dessert', 'Pasta', 'Seafood', 'Vegetarian']
        """Get all meals from API and enrich with pricing data"""
        enriched_meals = []

        api_meals = []
        for category in categories:
            api_meals.extend(self.meal_api.search_by_category(category))

        for meal_data in api_meals:
            full_meal = self.meal_api.get_meal_details(meal_data['idMeal'])
            meal = self._convert_to_meal_model(full_meal)
            enriched_meals.append(meal)

        return enriched_meals
    
    def get_all_training_meals(self) -> List[Meal]:
        """Get all training meals from CSV and convert to Meal model with pricing"""
        if not self.is_training:
            raise RuntimeError("DataMerger is not initialized for training data. Provide a food CSV file path.")
        
        if not self.training_processor:
            raise RuntimeError("Training processor is not initialized. Provide a food CSV file path.")

        training_data = self.training_processor.get_all_data()
        if not training_data:
            return []

        training_meals = []
        for data in training_data:
            meal = self._convert_training_data_to_meal_model(data)
            training_meals.append(meal)
        
        return training_meals
    
    def _convert_training_data_to_meal_model(self, training_data: dict) -> Meal:
        """Convert training data to Meal model with pricing"""

        ingredients = []
        for ingredient in training_data.get('ingredients', []):
            # Get price from CSV processor
            price = self.price_processor.get_ingredient_price(ingredient)
            ingredients.append(Ingredient(
                name=ingredient,
                amount=1, # Assuming amount is always 1 for training data
                price_per_unit=price
            ))
        
        return Meal(
            id=training_data.get('id', None),
            name=training_data.get('name', 'Unknown Meal'),
            category=training_data['category'],
            instructions=training_data['instructions'],
            ingredients=ingredients,
            image_url=training_data.get('image_url'),
            prep_time=training_data.get('prep_time', 0),
            keywords=training_data.get('keywords', []),
            estimated_cost=training_data.get('estimated_cost', 0.0),
            rating=training_data.get('rating', None),
            review_count=training_data.get('review_count', 0),
        )
    
    def _convert_to_meal_model(self, api_data: dict) -> Meal:
        """Convert TheMealDB data to Meal model with pricing"""
        ingredients = []
        total_cost = 0
        
        for i in range(1, 21):
            ingredient_key = f'strIngredient{i}'
            measure_key = f'strMeasure{i}'
            
            if api_data.get(ingredient_key):
                ingredient_name = api_data[ingredient_key]
                measure = api_data.get(measure_key, '')
                
                # Get price from CSV processor
                price = self.price_processor.get_ingredient_price(ingredient_name)
                
                # Create Ingredient with pricing
                ingredient = Ingredient(
                    name=ingredient_name,
                    amount=measure,
                    price_per_unit=price
                )
                ingredients.append(ingredient)
                
                if price:
                    total_cost += float(price)
        
        return Meal(
            id=api_data['idMeal'],
            name=api_data['strMeal'],
            category=api_data['strCategory'],
            instructions=api_data['strInstructions'],
            ingredients=ingredients,
            image_url=api_data.get('strMealThumb'),
            estimated_cost=round(total_cost, 2)
        )