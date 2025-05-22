from Backend.Api.themealdb import MealDBAPI
from Backend.Data.csv_processor import MercadonaCSVProcessor
from Backend.models.meal import Meal
from Backend.models.ingredient import Ingredient
from typing import List

class DataMerger:
    def __init__(self, csv_file_path: str):
        self.meal_api = MealDBAPI()
        self.price_processor = MercadonaCSVProcessor(csv_file_path)
    
    def get_enriched_meals(self, search_term: str) -> List[Meal]:
        """Get meals from API and enrich with pricing data"""
        api_meals = self.meal_api.search_by_ingredient(search_term)
        
        enriched_meals = []
        for meal_data in api_meals:
            full_meal = self.meal_api.get_meal_details(meal_data['idMeal'])
            meal = self._convert_to_meal_model(full_meal)
            enriched_meals.append(meal)
        
        return enriched_meals
    
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