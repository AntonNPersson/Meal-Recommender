import pandas as pd
from typing import Optional, Dict
from .parser import ProductNameParser
from .translator import IngredientTranslator

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