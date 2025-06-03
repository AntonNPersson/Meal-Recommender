from Backend.Data.meal_feature_manager import MealFeatureManager
from Backend.Recommender.meal_model_manager import MealModelManager
from Backend.Data.meal_data_manager import MealDataManager
from Backend.models.user import User
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
        
        self.recommendation_model = self.model_manager.get_recommendation_model()
        if not self.recommendation_model:
            raise RuntimeError("Failed to load or train recommendation model")

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

        # Extract recommendation features for enriched meals
        recommendation_features = self.meal_feature_manager.get_recommendation_features(enriched_meals)
        if recommendation_features is None or recommendation_features.empty:
            return None
        
        # Predict recommendations for enriched meals
        binary_prediction, probabilities = self.model_manager.recommendation_model.predict(recommendation_features)
        if binary_prediction is None or len(binary_prediction) == 0:
            return None
        
        # Combine enriched meals with their recommendation predictions
        for meal, is_recommended, prob in zip(enriched_meals, binary_prediction, probabilities):
            meal.is_recommended = is_recommended
            meal.recommendation_score = round(prob * 5, 1) if prob is not None else None
        
        return enriched_meals
    
    def get_enriched_meal_user_preferences(self, search_term: str, user: User) -> list:
        """Get enriched meals based on a search term and user preferences."""
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

        # Extract recommendation features for enriched meals
        recommendation_features = self.meal_feature_manager.get_recommendation_features(enriched_meals)
        if recommendation_features is None or recommendation_features.empty:
            return None
        
        # Create user preference features
        feature_columns = [
                "ingredient_count", "instruction_length", "type_of_meal",
                "is_vegetarian", "has_dairy", "has_gluten", "prep_time",
                "flavor_profile", "complexity_score"
            ]
        
        user_preference_features = {"type_of_meal": user.prefered_types,
                                    "flavor_profile": user.prefered_flavors}
        
        # Predict recommendations for enriched meals
        binary_prediction, probabilities = self.model_manager.recommendation_model.predict_with_score_boost_simple(
            recommendation_features, feature_columns, user_preference_features)
        if binary_prediction is None or len(binary_prediction) == 0:
            return None
        
        # Combine enriched meals with their recommendation predictions
        for meal, is_recommended, prob in zip(enriched_meals, binary_prediction, probabilities):
            meal.is_recommended = is_recommended
            meal.recommendation_score = round(prob * 5, 1) if prob is not None else None

        enriched_meals.sort(key=lambda meal: meal.recommendation_score if meal.recommendation_score is not None else 0, 
                    reverse=True)
        
        return enriched_meals
    
    def get_all_enriched_meals(self) -> list:
        """Get all enriched meals from the API."""
        enriched_meals = self.data_merger.get_all_enriched_meals()
        
        if not enriched_meals or len(enriched_meals) == 0:
            return None
        
        # Extract features for all enriched meals
        enriched_features = self.meal_feature_manager.get_prep_time_features(enriched_meals)
        if enriched_features is None or enriched_features.empty:
            return None
        
        # Calculate preparation times for all enriched meals
        enriched_prep_times = self.prep_time_model.predict(enriched_features)
        if enriched_prep_times is None or len(enriched_prep_times) == 0:
            return None
        
        # Combine all enriched meals with their predicted preparation times
        for meal, prep_time in zip(enriched_meals, enriched_prep_times):
            meal.prep_time = round(prep_time, 0) if prep_time is not None else None

        # Extract recommendation features for all enriched meals
        recommendation_features = self.meal_feature_manager.get_recommendation_features(enriched_meals)
        if recommendation_features is None or recommendation_features.empty:
            return None
        
        # Predict recommendations for all enriched meals
        binary_prediction, probabilities = self.model_manager.recommendation_model.predict(recommendation_features)
        if binary_prediction is None or len(binary_prediction) == 0:
            return None
        
        # Combine all enriched meals with their recommendation predictions
        for meal, is_recommended, prob in zip(enriched_meals, binary_prediction, probabilities):
            meal.is_recommended = is_recommended
            meal.recommendation_score = round(prob * 5, 1) if prob is not None else None
        
        return enriched_meals