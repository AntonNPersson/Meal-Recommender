import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from .data_merger import DataMerger
from ..models.meal import Meal

class MealFeatureExtractor:
    def __init__(self, mercadona_csv_path: str, food_csv_path: str, training_limit: int = 1000):
        self.data_merger = DataMerger(mercadona_csv_path, food_csv_path, training_limit)
        self.prep_keywords = [
            "chop", "slice", "dice", "mince", "grate", "peel", "wash",
            "soak", "marinate", "mix", "stir", "blend", "whisk", "beat",
            "fold", "knead", "roll", "shape", "oven", "bake", "fry", "boil",
            "steam", "roast", "grill", "sear", "sauté", "cook", "prepare",
            "european", "asian", "american", "mexican", "indian", "mediterranean"
            "stove top", "slow cooker", "pressure cooker", "air fryer", "microwave"
        ]
        self.fresh_ingredients = ['onion', 'garlic', 'tomato', 'pepper', 'herb', 'lemon', 'lime',
                                  'cucumber', 'carrot', 'celery', 'spinach', 'broccoli', 'cauliflower',
                                  'zucchini', 'eggplant', 'mushroom', 'green bean', 'peas', 'corn',
                                  'potato', 'sweet potato', 'pumpkin', 'squash', 'radish', 'beet']

    def extract_features(self, limit: int) -> Dict:
        """
        Extract features from meal data for machine learning models.
        """

        details = self.data_merger.get_all_enriched_meals()
        if not details:
            return {}
        
        features = []
        current_count = 0
        
        for meal in details:
            if current_count >= limit:
                break
            instruction_text = meal.instructions.lower() if meal.instructions else ""
            fresh_count = sum(
                ingredient.name.lower() in self.fresh_ingredients for ingredient in meal.ingredients)
            fresh_ratio = fresh_count / len(meal.ingredients) if meal.ingredients else 0

            feature = {
                "ingredient_count": len(meal.ingredients),
                "instruction_length": len(instruction_text.split()),
                "prep_keyworks_count": sum(
                    instruction_text.count(keyword) for keyword in self.prep_keywords
                ),
                "fresh_ratio": fresh_ratio
            }

            features.append(feature)
            current_count += 1
        return features
    
    def extract_features_from_meals(self, meals: List[Meal]) -> List[Dict]:
        """
        Extract features from a list of Meal objects.
        """
        if not meals:
            return []

        features = []
        
        for meal in meals:
            instruction_text = meal.instructions.lower() if meal.instructions else ""
            fresh_count = sum(
                ingredient.name.lower() in self.fresh_ingredients for ingredient in meal.ingredients)
            fresh_ratio = fresh_count / len(meal.ingredients) if meal.ingredients else 0

            feature = {
                "ingredient_count": len(meal.ingredients),
                "instruction_length": len(instruction_text.split()),
                "prep_keyworks_count": sum(
                    instruction_text.count(keyword) for keyword in self.prep_keywords
                ),
                "fresh_ratio": fresh_ratio
            }

            features.append(feature)
        return features

    
    def extract_training_features(self, limit: int) -> List[Dict]:
        """
        Extract features from training meal data for machine learning models.
        """
        training_meals = self.data_merger.get_all_training_meals()
        if not training_meals:
            return []

        features = []
        current_count = 0
        
        for meal in training_meals:
            if current_count >= limit:
                break
            instruction_text = meal.instructions.lower() if meal.instructions else ""
            fresh_count = sum(
                ingredient.name.lower() in self.fresh_ingredients for ingredient in meal.ingredients)
            fresh_ratio = fresh_count / len(meal.ingredients) if meal.ingredients else 0

            prep_keywords = sum(
                instruction_text.count(keyword) for keyword in self.prep_keywords
            ) + sum(
                meal.keywords.count(keyword) for keyword in self.prep_keywords
            )

            feature = {
                "ingredient_count": len(meal.ingredients),
                "instruction_length": len(instruction_text.split()),
                "prep_keyworks_count": prep_keywords,
                "fresh_ratio": fresh_ratio,
                "estimated_prep_time": meal.prep_time if meal.prep_time else None,
            }

            features.append(feature)
            current_count += 1
        return features

    def estimate_prep_time(self, features: Dict) -> Optional[int]:
        """
        Estimate preparation time based on feature heuristics, need to get actual data for this.
        """
        if not features:
            return None
        
        base_time = features['ingredient_count'] * 2  # Base time per ingredient
        instruction_time = min(features['instruction_length'] / 50, 20)  # Max 20 min for instructions
        if features['prep_keyworks_count'] > 0:
            instruction_time += features['prep_keyworks_count'] * 2

        category_modifiers = {
            "Beef": 1.3,
            "Chicken": 1.3, 
            "Lamb": 1.3,
            "Pork": 1.3,
            "Dessert": 0.8,
            "Pasta": 0.7,
            "Seafood": 1.4,
            "Vegetarian": 1.1
        }

        modifier = category_modifiers.get(features['category'], 1.0)
        fresh_time = features['fresh_ratio'] * 3  # Extra time for fresh ingredients

        estimated_time = int((base_time + instruction_time + fresh_time) * modifier)

        noise = np.random.randint(0, 5)  # Add some noise

        total_time = max(5, min(120, estimated_time + noise))
        return total_time
    
    def prepare_training_data(self, limit: int) -> pd.DataFrame:
        """
        Prepare the training feature data for machine learning.
        """
        features = self.extract_training_features(limit)
        if not features:
            return pd.DataFrame()

        df = pd.DataFrame(features)
        df.fillna(0, inplace=True)
        return df
    
    def prepare_data(self, limit: int) -> pd.DataFrame:
        """
        Prepare the feature data for machine learning.
        """
        features = self.extract_features(limit)
        if not features:
            return pd.DataFrame()

        df = pd.DataFrame(features)
        df.fillna(0, inplace=True)
        return df
        
        