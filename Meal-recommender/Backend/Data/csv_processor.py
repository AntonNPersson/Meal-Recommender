import pandas as pd
from typing import Optional, Dict
from .Utils.parser import ProductNameParser
from .Utils.translator import IngredientTranslator
from .Utils.csv_utils import parse_r_vector, parse_r_vector_to_string, parse_ISO_8601_duration
import re

class MercadonaCSVProcessor:
    """
    A class to process CSV files from Mercadona and extract ingredient information.
    """

    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.parser = ProductNameParser()
        self.translator = IngredientTranslator()
        self._price_cache = None

    def get_ingredient_price(self, ingredient_name: str) -> Optional[float]:
        """
        Get the price per unit for a given ingredient name.
        """
        if self._price_cache is None:
            self._build_price_cache()

        # Normalize the ingredient name
        normalized_name = ingredient_name.lower()

        if normalized_name in self._price_cache:
            return self._price_cache[ingredient_name.lower()]
        
        for cached_name, price in self._price_cache.items():
            if normalized_name in cached_name or cached_name in normalized_name:
                return price
        
        # Check if the ingredient is in the cache
        return None

    def _build_price_cache(self) -> Dict[str, float]:
        """
        Build a cache of prices for each product in the CSV file.
        """
        df = pd.read_csv(self.csv_file)

        price_cache = {}

        for _, row in df.iterrows():
            clean_name, volume, brand = self.parser.parse_product_name(row['name'])
            english_name = self.translator.translate_ingredient(clean_name)

            if not english_name:
                continue

            price_per_unit = self._calculate_price_per_unit(row['price'], volume)
            if price_per_unit is not None:
                price_cache[english_name] = price_per_unit
        self._price_cache = price_cache
        return price_cache

    
    def _calculate_price_per_unit(self, price: float, volume: str) -> Optional[float]:
        """
        Calculate the price per unit for a given row in the DataFrame.
        """
        if not volume:
            return price
        
        # if volume cant be converted to float, return price
        try:
            float(volume.split()[0])
        except ValueError:
            return price
        
        return float(price) / float(volume.split()[0])  # Assuming volume is in the format "X units"
    
class FoodCSVProcessor:
    """
    A class to process CSV files from food databases and extract ingredient information.
    """

    def __init__(self, csv_file: str, review_csv_file: Optional[str] = None):
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)

        if review_csv_file:
            self.review_df = pd.read_csv(review_csv_file)
            self.df = self._merge_with_reviews()
        else:
            self.review_df = None

    def _merge_with_reviews(self):
        """
        Merge the recipes dataframe with the reviews dataframe.
        Assumes both have a common 'RecipeId' column (adjust as needed).
        """
        # Group reviews by recipe and calculate aggregate ratings
        review_aggregates = self.review_df.groupby('RecipeId').agg({
            'Rating': ['mean', 'count', 'std']
        }).round(2)
        
        # Flatten column names
        review_aggregates.columns = ['avg_rating', 'review_count', 'rating_std']
        review_aggregates = review_aggregates.reset_index()
        
        # Merge with recipes dataframe
        merged_df = self.df.merge(
            review_aggregates, 
            on='RecipeId', 
            how='left'  # Keep all recipes, even those without reviews
        )
        
        return merged_df

    def get_ingredients(self) -> list:
        """
        Get a list of ingredients from the CSV file.
        """
        ingredients_raw = self.df['RecipeIngredientParts'].to_string()

        ingredients = []
        for r_vector in ingredients_raw:
            ingredient_list = parse_r_vector(r_vector)
            ingredients.append(ingredient_list)
        return ingredients
    
    def get_instructions(self) -> list:
        """
        Get a list of instructions from the CSV file.
        """
        instructions_raw = self.df['RecipeInstructions'].tolist()
        instructions = []
        for r_vector in instructions_raw:
            instruction_list = parse_r_vector_to_string(r_vector)
            instructions.append(instruction_list)
        return instructions
    
    def get_category(self) -> str:
        """
        Get a list of categories from the CSV file.
        """
        categories = self.df['RecipeCategory'].tolist()
        return categories[0]
    
    def get_keywords(self) -> list:
        """
        Get a list of keywords from the CSV file.
        """
        keywords_raw = self.df['Keywords'].tolist()
        keywords = []
        for r_vector in keywords_raw:
            keyword_list = parse_r_vector(r_vector)
            keywords.append(keyword_list)
        return keywords
    
    def get_prep_time(self) -> int:
        """
        Get a list of preparation times from the CSV file.
        """
        prep_times = self.df['PrepTime'].tolist()

        parsed_prep_times = []

        for prep_time in prep_times:

            if not prep_time or pd.isna(prep_time):
                return 0
            
            clean_prep_time = parse_ISO_8601_duration(prep_time)
            if clean_prep_time is None:
                clean_prep_time = 0
            
            parsed_prep_times.append(clean_prep_time)

        return parsed_prep_times
    
    def get_all_data(self) -> list:
        """
        Get all data from the CSV file.
        """
        data = []
        for _, row in self.df.iterrows():

            recipe_data = ({
                'ingredients': parse_r_vector(row['RecipeIngredientParts']),
                'instructions': parse_r_vector_to_string(row['RecipeInstructions']),
                'category': row['RecipeCategory'],
                'keywords': parse_r_vector(row['Keywords']),
                'prep_time': parse_ISO_8601_duration(row['PrepTime'])
            })

            if recipe_data['prep_time'] is None:
                recipe_data['prep_time'] = 0
            
            if recipe_data['prep_time'] <= 0 or recipe_data['prep_time'] > 1440:
                continue # Skip recipes with invalid prep times

            if not self.review_df.empty:
                recipe_data.update({
                    'rating': row['avg_rating'],
                    'review_count': row['review_count'],
                    'rating_std': row['rating_std']
                })
            else:
                recipe_data.update({
                    'rating': None,
                    'review_count': 0,
                    'rating_std': None
                })
            data.append(recipe_data)
        return data
        