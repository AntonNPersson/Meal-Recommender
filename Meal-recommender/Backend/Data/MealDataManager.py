from Backend.Data.data_merger import DataMerger
from Backend.Api.themealdb import MealDBAPI
import os
import pandas as pd

class MealDataManager:
    """Central manager for meal data operations, including fetching and merging data."""

    def __init__(self):
        # Always needed CSV file paths
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(backend_dir))
        self.mercadona_csv_file_path = os.path.join(project_root, "data", "raw", "mercadona_products_latest.csv")

        # Optional CSV file path for training data
        self.food_csv_file_path = os.path.join(project_root, "data", "raw", "recipes.csv")
        self.has_training_data = os.path.exists(self.food_csv_file_path)

        # API Service
        self.meal_api = MealDBAPI()

        # Data Merger (Lazy initialization)
        self._data_merger = self._create_data_merger()

    def _create_data_merger(self) -> DataMerger:
        """Create the DataMerger instance"""
        if not os.path.exists(self.mercadona_csv_file_path):
            raise FileNotFoundError(f"Mercadona CSV required: {self.mercadona_csv_file_path}")
        
        food_path = self.food_csv_file_path if self.has_training_data else None
        if not self.has_training_data:
            print("Food CSV not found. Training functionality will be disabled.")
        
        return DataMerger(
            mercadona_csv_file_path=self.mercadona_csv_file_path,
            food_csv_file_path=food_path
        )
    
    # API Methods
    def get_enriched_meals(self, search_term: str) -> list:
        """Get enriched meals based on a search term."""
        return self._data_merger.get_enriched_meals(search_term)
    
    def get_all_enriched_meals(self) -> list:
        """Get all enriched meals from the API."""
        return self._data_merger.get_all_enriched_meals()
        
    # Training Data Methods
    def get_all_training_meals(self) -> list:
        """Get all training meals from the CSV file."""
        if not self.has_training_data:
            raise RuntimeError("Training data is not available. Provide a food CSV file path.")
        return self._data_merger.get_all_training_meals()
    
    def can_train(self) -> bool:
        """Check if training data is available."""
        return self.has_training_data