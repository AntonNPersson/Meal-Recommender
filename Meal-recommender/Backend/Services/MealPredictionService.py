from Backend.Data.MealFeatureManager import MealFeatureManager
from Backend.Recommender.MealModelManager import MealModelManager
from Backend.Data.MealDataManager import MealDataManager
import pandas as pd
import os

class MealPredictionService:
    def __init__(self):

        self.meal_feature_manager = MealFeatureManager()
        self.data_merger = MealDataManager()
        self.model_manager = MealModelManager()

        self.prep_time_model = self.model_manager.get_prep_time_model()
        if not self.prep_time_model:
            raise RuntimeError("Failed to load or train preparation time model")

    def get_enriched_meals(self, search_term: str) -> list:
        """Get enriched meals based on a search term."""
        enriched_meals = self.data_merger.get_enriched_meals(search_term)
        
        if not enriched_meals or len(enriched_meals) == 0:
            return None
        
        # Extract features for enriched meals
        enriched_features = self.meal_feature_manager.get_prep_time_features(enriched_meals)
        if enriched_features is None or enriched_features.empty:
            return None
        
        # Calculate preparation times for enriched meals
        enriched_prep_times = self.prep_time_model.predict(enriched_features)
        if enriched_prep_times is None or len(enriched_prep_times) == 0:
            return None
        
        # Combine enriched meals with their predicted preparation times
        for meal, prep_time in zip(enriched_meals, enriched_prep_times):
            meal.prep_time = round(prep_time, 0) if prep_time is not None else None
        
        return enriched_meals