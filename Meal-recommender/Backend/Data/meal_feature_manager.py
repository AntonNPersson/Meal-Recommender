from Backend.Data.prep_time_extraction import PrepTimeFeatureExtractor
from Backend.Data.recommendation_extraction import RecommendationFeatureExtraction
from typing import List
import pandas as pd
from Backend.models.meal import Meal

class MealFeatureManager:
    """Manages the extraction of all meal features from CSV files."""

    def __init__(self):
        self.prep_time_extractor = PrepTimeFeatureExtractor()
        self.recommendation_extractor = RecommendationFeatureExtraction()
        
    def get_prep_time_features(self, meals: List[Meal], include_target = False) -> pd.DataFrame:
        """
        Extract preparation time features from a list of Meal objects.
        """

        return self.prep_time_extractor.prepare_features_dataframe(meals, include_target=include_target)
    
    def get_recommendation_features(self, meals: List[Meal], include_target = False) -> pd.DataFrame:
        """
        Extract recommendation features from a list of Meal objects.
        """
        return self.recommendation_extractor.prepare_features_dataframe(meals, include_target=include_target)